# استقرار VoyaVisa

پروژه در `/opt/voyavisa` اجرا می‌شود. پیش از تغییر، وضعیت Git و Nginx، شناسهٔ پروژهٔ Compose و Volumeهای PostgreSQL و مدارک را ثبت کنید. از دیتابیس با `pg_dump` و از Volumeهای عمومی و خصوصی پشتیبان بگیرید. نام پروژهٔ Compose و Volumeهای موجود را حفظ کنید. فایل خصوصی ENV را با مجوز ۶۰۰ و با اطلاعات موجود دیتابیس نگه دارید.

در ENV تولید `DJANGO_DEBUG=False`، `DJANGO_USE_SQLITE=False`، `DJANGO_COOKIE_SAMESITE=Lax` و `DJANGO_AUTH_PROXY_HOPS=2` را تنظیم کنید. هر چهار میزبان را در `DJANGO_ALLOWED_HOSTS` بگذارید. مبدأهای HTTPS سایت، www و ادمین را در CORS و همان سه مبدأ به‌علاوهٔ API را در CSRF وارد کنید. `DJANGO_SECRET_KEY` باید خصوصی باشد.

با `docker compose -f docker-compose.yml -f compose.production.yml up -d --build --wait` سرویس‌ها را راه‌اندازی کنید. سایت روی loopback پورت ۸۰۸۰ و پنل ادمین روی ۸۰۸۱ در سرویس‌های جدا از یک بیلد فرانت‌اند اجرا می‌شوند. پنل پرداخت در `/admin/payments` و Django Admin در `https://api.visatake.ir/admin/` است.

برای اولین صدور گواهی، مسیر `/.well-known/acme-challenge/` را روی هر چهار دامنه با ریشهٔ `/var/www/voyavisa-acme` در پورت ۸۰ سرو کنید و پس از `nginx -t` تنظیمات را بازخوانی کنید. سپس اجرا کنید.

```sh
certbot certonly --webroot -w /var/www/voyavisa-acme --cert-name visatake.ir \
  -d visatake.ir -d www.visatake.ir -d api.visatake.ir -d admin.visatake.ir
```

پس از صدور، فایل `voyavisa.nginx.conf` را در تنظیمات میزبان نصب کنید. قبل از reload دستور `nginx -t` را اجرا کنید. مسیر ACME برای تمدید باقی می‌ماند. یک deploy hook برای reload پس از تمدید موفق تنظیم کنید و `certbot renew --dry-run` را بررسی کنید.
