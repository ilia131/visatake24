# بک‌اند VisaTake

Django 6.1 و Django REST Framework برای احراز هویت، ویزا، داشبورد، مشاوره و بررسی پرداخت. دستورهای اجرای محلی در [راهنمای اصلی](../README.md) آمده‌اند. فایل خصوصی `.env` در کنار `manage.py` خوانده می‌شود و متغیرهای صادرشده در محیط اجرا اولویت دارند.

## تنظیمات

| متغیر | کاربرد |
|---|---|
| `DJANGO_DEBUG` | مقدار `True` برای توسعه. در تولید `False` باشد. |
| `DJANGO_SECRET_KEY` | کلید ثابت و محرمانه. در تولید الزامی است. برای حفظ نشست‌ها میان راه‌اندازی‌های توسعه هم تنظیم شود. |
| `DJANGO_ALLOWED_HOSTS` | نام میزبان‌ها با جداکنندهٔ کاما و بدون scheme. |
| `DJANGO_CORS_ALLOWED_ORIGINS` | مبدأهای مجاز درخواست مرورگر با scheme و پورت. برای پروکسی هم‌مبدأ خالی بماند. |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | مبدأهای مورد اعتماد Django برای درخواست تغییردهنده. از scheme و پورت واقعی استفاده کنید. |
| `DJANGO_COOKIE_SAMESITE` | پیش‌فرض `Lax`. مقدار `None` برای سایت‌های مجزا به HTTPS و پذیرش کوکی توسط مرورگر نیاز دارد. |
| `POSTGRES_DB`، `POSTGRES_USER`، `POSTGRES_PASSWORD`، `POSTGRES_HOST`، `POSTGRES_PORT` | تنظیمات PostgreSQL. SQLite در حالت توسعه و بدون `POSTGRES_DB` پیش‌فرض است. Docker Compose از PostgreSQL استفاده می‌کند. |
| `APPOINTMENT_PAYMENT_CARD` | شمارهٔ کارت دریافت هزینهٔ مشاوره. پیش از تأیید رزرو توسط مشاور، در محیط بک‌اند مقداردهی شود. |

نمونهٔ اتصال مستقیم توسعه با `VITE_API_PROXY=false` و `VITE_API_BASE_URL=http://localhost:8000`، وارد کردن `http://localhost:5173` در هر دو فهرست CORS و CSRF است. در هر دو آدرس از نام میزبان یکسان استفاده کنید تا سیاست کوکی محلی یکسان باشد. آدرس فایل‌های خصوصی از API دانلود مجاز دریافت می‌شود. فقط پوشهٔ `media/` برای فایل عمومی سرو می‌شود و `private_media/` باید خارج از مسیر عمومی وب باقی بماند.

## اجرا در توسعه و تولید

برای توسعه، `.env.example` را به `.env` کپی کنید. `DJANGO_DEBUG=True` و `DJANGO_USE_SQLITE=True` برای اجرای محلی با SQLite مناسب هستند. برای تولید هر دو را `False` بگذارید و کلید تصادفی Django، میزبان‌های واقعی، اطلاعات PostgreSQL را در ENV خصوصی قرار دهید. برای ساخت کلید Django از `django.core.management.utils.get_random_secret_key` استفاده کنید.

Compose اطلاعات پایگاه داده را از همان منبع به PostgreSQL و بک‌اند می‌دهد و بک‌اند را به `db:5432` متصل می‌کند. برای تغییر ENV کانتینرها، `docker compose up -d --force-recreate` را اجرا کنید. Compose فرانت‌اند را روی `127.0.0.1:8080` منتشر می‌کند. در تولید، از یک پراکسی HTTPS روی میزبان استفاده کنید که `Host` اصلی را حفظ کند و `X-Forwarded-Proto` را خودش روی `https` تنظیم کند. اگر فرانت‌اند و API هم‌مبدأ هستند، فهرست‌های CORS و CSRF را خالی بگذارید. برای مبدأ متفاوت، فقط نشانی‌های دقیق HTTPS را اضافه کنید. برای دامنه‌های واقعاً cross-site، مقدار `None` برای SameSite و پذیرش کوکی‌های cross-site از سوی مرورگر لازم است.

## بررسی پروژه

```sh
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py migrate
python manage.py spectacular --validate --file schema.yml
python -m pytest --ds=config.settings
```

برای آزمون هم‌زمانی رزرو، PostgreSQL و امکان ایجاد پایگاه دادهٔ آزمون لازم است. Swagger در `/api/docs/`، مشخصات OpenAPI در [`schema.yml`](schema.yml) و گردش رزرو در [`APPOINTMENTS.md`](APPOINTMENTS.md) در دسترس‌اند.

ثبت‌نام و ورود با شماره تلفن و رمز عبور انجام می‌شود. درخواست ابتدا توکن CSRF را از `GET /api/v1/auth/csrf/` می‌گیرد و سپس `POST /api/v1/auth/register/` یا `POST /api/v1/auth/login/` را با `X-CSRFToken` و کوکی ارسال می‌کند. فیلد `country_code` کد دوحرفی کشور مثل `IR` است و `phone_number` شمارهٔ ملی است. شماره با فرمت E.164 ذخیره می‌شود. تمدید و خروج هم به CSRF نیاز دارند.

برای محدودسازی تلاش‌های ورود، پشت Compose و یک پراکسی بیرونی مورد اعتماد، `DJANGO_AUTH_PROXY_HOPS=2` را تنظیم کنید. هر دو پراکسی باید نشانی مبدأ اتصال را به انتهای `X-Forwarded-For` اضافه کنند و دسترسی مستقیم به بک‌اند بسته باشد. در اجرای مستقیم مقدار `0` مناسب است.

حساب‌ها، نقش‌ها و وضعیت تاریخی تأیید تلفن حفظ می‌شوند. مدیر باید برای کاربران قدیمی که تنها با OTP وارد می‌شدند و رمز قابل‌استفاده ندارند، پس از احراز هویت خارج از برنامه با `python manage.py changepassword` یک رمز تعیین کند. ثبت‌نام دوباره روی شمارهٔ موجود پذیرفته نمی‌شود.
