# بک‌اند VisaTake

Django 6.1 و Django REST Framework برای احراز هویت، ویزا، داشبورد، مشاوره و بررسی پرداخت. دستورهای اجرای محلی در [راهنمای اصلی](../README.md) آمده‌اند. فایل `.env` در همین پوشه خوانده می‌شود و متغیرهای صادرشده در محیط اجرا اولویت دارند.

## تنظیمات

| متغیر | کاربرد |
|---|---|
| `DJANGO_DEBUG` | مقدار `True` برای توسعه. در تولید `False` باشد. |
| `DJANGO_SECRET_KEY` | کلید ثابت و محرمانه. در تولید الزامی است. برای حفظ نشست‌ها میان راه‌اندازی‌های توسعه هم تنظیم شود. |
| `DJANGO_ALLOWED_HOSTS` | نام میزبان‌ها با جداکنندهٔ کاما و بدون scheme. |
| `DJANGO_CORS_ALLOWED_ORIGINS` | مبدأهای مجاز درخواست مرورگر با scheme و پورت. برای پروکسی هم‌مبدأ خالی بماند. |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | مبدأهای مورد اعتماد Django برای درخواست تغییردهنده. از scheme و پورت واقعی استفاده کنید. |
| `DJANGO_COOKIE_SAMESITE` | پیش‌فرض `Lax`. مقدار `None` برای سایت‌های مجزا به HTTPS و پذیرش کوکی توسط مرورگر نیاز دارد. |
| `POSTGRES_DB`، `POSTGRES_USER`، `POSTGRES_PASSWORD`، `POSTGRES_HOST`، `POSTGRES_PORT` | تنظیمات PostgreSQL. با حذف `POSTGRES_DB`، SQLite محلی استفاده می‌شود. |
| `APPOINTMENT_PAYMENT_CARD` | شمارهٔ کارت دریافت هزینهٔ مشاوره. پیش از تأیید رزرو توسط مشاور، در محیط بک‌اند مقداردهی شود. |

نمونهٔ اتصال مستقیم توسعه با `VITE_API_PROXY=false` و `VITE_API_BASE_URL=http://localhost:8000`، وارد کردن `http://localhost:5173` در هر دو فهرست CORS و CSRF است. در هر دو آدرس از نام میزبان یکسان استفاده کنید تا سیاست کوکی محلی یکسان باشد. آدرس فایل‌های خصوصی از API دانلود مجاز دریافت می‌شود. فقط پوشهٔ `media/` برای فایل عمومی سرو می‌شود و `private_media/` باید خارج از مسیر عمومی وب باقی بماند.

## بررسی پروژه

```sh
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py migrate
python manage.py spectacular --validate --file schema.yml
python -m pytest --ds=config.settings
```

برای آزمون هم‌زمانی رزرو، PostgreSQL و امکان ایجاد پایگاه دادهٔ آزمون لازم است. Swagger در `/api/docs/`، مشخصات OpenAPI در [`schema.yml`](schema.yml) و گردش رزرو در [`APPOINTMENTS.md`](APPOINTMENTS.md) در دسترس‌اند.

تحویل OTP در توسعه از طریق لاگ است. اتصال پیامک تولید، دریافت‌کنندهٔ رویدادهای اطلاع‌رسانی و زمان‌بندی یادآوری جلسه به زیرساخت استقرار نیاز دارند.
