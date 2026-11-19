# استقرار Production پروژهٔ VoyaVisa

## معماری

| دامنه | مقصد |
| --- | --- |
| `visatake.ir` | برنامهٔ React و API هم‌مبدأ از طریق Nginx داخلی |
| `www.visatake.ir` | تغییر مسیر ۳۰۱ به `https://visatake.ir` |
| `api.visatake.ir` | API جنگو در `/api/` و Django Admin در `/admin/` |
| `admin.visatake.ir` | مقصد در انتظار تصمیم مالک |

فرانت‌اند مستقل ادمین در مخزن وجود ندارد. صفحهٔ بررسی پرداخت در `https://visatake.ir/admin/payments` بخشی از برنامهٔ اصلی است. Nginx میزبان روی پورت‌های ۸۰ و ۴۴۳ به Nginx کانتینر روی `127.0.0.1:8080` متصل می‌شود. Django و PostgreSQL تنها روی شبکهٔ Compose با پورت‌های داخلی ۸۰۰۰ و ۵۴۳۲ در دسترس‌اند. Gunicorn با یک worker و دو thread اجرا می‌شود. فایل‌های کاربران و دیتابیس در Volumeهای پایدار قرار دارند و Volume خصوصی فقط به بک‌اند متصل است.

## بررسی و آماده‌سازی

ابتدا وضعیت Git، دیسک، Swap، سرویس‌های فعال، پورت‌ها و نام پروژهٔ Compose موجود را ثبت کنید. روی سرور دارای داده، نام پروژه و Volumeهای موجود را تغییر ندهید. Docker، Nginx و Certbot را طبق وضعیت موجود آماده کنید. دسترسی SSH روی ۹۰۱۱ را حفظ کنید.

از `.env.example` به‌عنوان فهرست متغیرها استفاده کنید. در `/opt/voyavisa/.env`، `DJANGO_DEBUG=False`، `DJANGO_USE_SQLITE=False`، `DJANGO_COOKIE_SAMESITE=Lax` و `DJANGO_AUTH_PROXY_HOPS=2` بگذارید. هر چهار دامنه را در `DJANGO_ALLOWED_HOSTS` تنظیم کنید. API مرورگر از همان مبدأ فرانت‌اند پراکسی می‌شود، بنابراین فهرست‌های CORS و CSRF می‌توانند خالی باشند. اگر یک کلاینت مرورگر واقعاً مستقیماً به دامنهٔ API متصل می‌شود، فقط مبدأ HTTPS همان کلاینت را به هر دو فهرست اضافه کنید. اطلاعات اتصال PostgreSQL موجود و کلید Django موجود را حفظ کنید. برای نصب تازه، مقادیر تصادفی بسازید و فایل را با مجوز ۶۰۰ ذخیره کنید.

## Backup قبل از Migration

دستورها را از `/opt/voyavisa` و با نام پروژهٔ موجود اجرا کنید. ابتدا با `docker compose ls` و `docker volume ls` مشخص کنید که سرویس `db` به کدام داده وصل است. آرشیو خصوصی را خارج از مخزن نگه دارید.

```sh
umask 077
backup_dir="/var/backups/voyavisa/$(date -u +%Y%m%dT%H%M%SZ)"
install -d -m 700 "$backup_dir"
docker compose -f docker-compose.yml -f compose.production.yml exec -T db \
  sh -ec 'pg_dump -Fc -U "$POSTGRES_USER" -d "$POSTGRES_DB"' > "$backup_dir/db.dump"
test -s "$backup_dir/db.dump"
docker compose -f docker-compose.yml -f compose.production.yml exec -T db \
  pg_restore --list < "$backup_dir/db.dump" > "$backup_dir/db.contents"
```

فایل‌های `media_data` و `private_media_data` را جداگانه از Volumeهای واقعی با اتصال فقط‌خواندنی آرشیو کنید و فهرست هر آرشیو را بررسی کنید. برای تمرین Restore، یک دیتابیس خالی و جدا بسازید و `pg_restore --exit-on-error --no-owner --dbname=نام_دیتابیس_آزمایشی db.dump` را روی آن اجرا کنید. آرشیو رسانه را در مسیر جدا باز کنید و پس از بررسی، برای بازگردانی Production دربارهٔ قطع سرویس و جایگزینی داده تصمیم بگیرید.

## Build و راه‌اندازی

```sh
docker compose -f docker-compose.yml -f compose.production.yml config --quiet
docker compose -f docker-compose.yml -f compose.production.yml build backend
docker compose -f docker-compose.yml -f compose.production.yml build frontend
docker compose -f docker-compose.yml -f compose.production.yml up -d --wait db
docker compose -f docker-compose.yml -f compose.production.yml run --rm --no-deps backend python manage.py migrate --plan
```

روی دیتابیس موجود، ابتدا Backup و برنامهٔ Migration را بررسی کنید. Migration `accounts.0003` جدول کدهای یک‌بارمصرف قدیمی را حذف می‌کند و برای اجرای آن روی دیتابیس موجود باید تأیید بگیرید. Compose تولید Migration را هنگام Start یا Restart خودکار اجرا نمی‌کند. پس از بررسی و در صورت نیاز اخذ تأیید، اجرا کنید.

```sh
docker compose -f docker-compose.yml -f compose.production.yml run --rm --no-deps backend python manage.py migrate
docker compose -f docker-compose.yml -f compose.production.yml run --rm --no-deps backend python manage.py collectstatic --noinput
docker compose -f docker-compose.yml -f compose.production.yml up -d --no-build --wait
docker compose -f docker-compose.yml -f compose.production.yml ps
docker compose -f docker-compose.yml -f compose.production.yml exec backend python manage.py createsuperuser
```

رمز را در ورودی تعاملی وارد کنید. برای Restart از `docker compose -f docker-compose.yml -f compose.production.yml restart backend frontend` استفاده کنید. برای بررسی لاگ‌ها، `docker compose -f docker-compose.yml -f compose.production.yml logs --tail=100 backend frontend db` را اجرا کنید. برای به‌روزرسانی پس از بررسی نبود تغییر محلی، `git pull --ff-only origin main` را بزنید و مراحل Build، Backup و بررسی Migration را تکرار کنید.

## Nginx و TLS

قبل از صدور گواهی، DNS و HTTP دامنه‌های فعال را بررسی کنید. ابتدا مسیر `/.well-known/acme-challenge/` را برای سایت، www و API در پورت ۸۰ با ریشهٔ `/var/www/voyavisa-acme` سرو کنید. پس از `nginx -t` و Reload، گواهی را بگیرید.

```sh
certbot certonly --webroot -w /var/www/voyavisa-acme --cert-name visatake.ir \
  -d visatake.ir -d www.visatake.ir -d api.visatake.ir
```

سپس `voyavisa.nginx.conf` را نصب کنید، `nginx -t` و `systemctl reload nginx` را اجرا کنید. تمدید را با `certbot renew --dry-run` بررسی کنید و Reload را پس از تمدید موفق به‌عنوان deploy hook ثبت کنید. دامنهٔ ادمین پس از تعیین مقصد و تأیید DNS و HTTP جداگانه فعال می‌شود.
