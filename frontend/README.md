# VisaTake | ویزاتیک

فرانت‌اند فارسی و واکنش‌گرا برای مرور کشورها، ثبت درخواست ویزا، مدیریت مدارک و رزرو مشاوره. پروژه با React، TypeScript و Vite ساخته شده است. TanStack React Query وضعیت سرور را مدیریت می‌کند و React Hook Form و Zod برای فرم‌ها استفاده می‌شوند.

## اجرا در محیط توسعه

پیش‌نیازها Node.js نسخهٔ ۲۲.۱۲ یا جدیدتر و نسخهٔ به‌روزشدهٔ بک‌اند VoyaVisa با مسیرهای مشاوره و پرداخت هستند.

1. در پوشهٔ بک‌اند، تنظیمات پایگاه داده را آماده کنید و `python manage.py migrate` را اجرا کنید. برای دادهٔ اولیهٔ کشورها از `python manage.py seed_countries` استفاده کنید. زمان آزاد و پروفایل مشاور را در بک‌اند ثبت کنید.
2. بک‌اند را با `python manage.py runserver localhost:8000` اجرا کنید.
3. در پوشهٔ VisaTake دستورهای زیر را اجرا کنید.

```sh
npm ci
cp .env.example .env
npm run dev
```

4. آدرس چاپ‌شده توسط Vite را باز کنید. در توسعه، OTP پس از درخواست در لاگ بک‌اند ثبت می‌شود. برای تولید، بک‌اند به سرویس ارسال پیامک نیاز دارد.

### آدرس و کوکی

`VITE_API_BASE_URL` نشانی پایهٔ Django، بدون بخش `/api/v1`، است. به‌طور پیش‌فرض Vite مسیرهای `/api` و `/media` را به آن نشانی پروکسی می‌کند تا API و رابط برای مرورگر هم‌مبدأ باشند. در تولید، همین مسیرها را با reverse proxy به Django وصل کنید و سایر مسیرها را به `index.html` برگردانید. کلید `VITE_API_PROXY=false` اتصال مستقیم به نشانی تنظیم‌شده را فعال می‌کند. در این حالت اجازهٔ Origin، credential و CSRF را در Django و پروکسی مطابق دامنهٔ استقرار تنظیم کنید. نام متغیرهای CORS و CSRF در راهنمای بک‌اند آمده است. استقرار تولید باید HTTPS داشته باشد.

کوکی‌های احراز هویت را Django صادر می‌کند. فرانت‌اند JWT را در LocalStorage یا SessionStorage ذخیره نمی‌کند. توکن CSRF از API واقعی گرفته و در حافظه نگه داشته می‌شود. درخواست‌های ۴۰۱ یک عملیات refresh مشترک دارند و پس از انقضای نشست، داده‌های خصوصی کش پاک و مسیر خصوصی به ورود منتقل می‌شود.

## APIهای متصل

همهٔ مسیرهای زیر نسبت به `/api/v1/` هستند. قرارداد از `schema.yml`، `APPOINTMENTS.md` و پیاده‌سازی بک‌اند استخراج شده است.

| حوزه | متد و مسیر |
|---|---|
| ورود | GET `auth/csrf/`، POST `auth/otp/request/`، POST `auth/otp/verify/`، POST `auth/token/refresh/`، GET `auth/me/`، POST `auth/logout/` |
| مقصد و مشاور | GET `visas/countries/`، GET `consultants/` و `consultants/{slug}/`، GET `appointments/availability/?consultant={id}` |
| پرونده | POST `visas/applications/`، GET `dashboard/applications/`، GET `dashboard/applications/{tracking_code}/` و `…/history/` |
| مدارک | GET `dashboard/documents/`، POST `visas/applications/{tracking_code}/documents/`، GET `visas/documents/{id}/download/` |
| حساب | GET `dashboard/overview/`، GET و PATCH `dashboard/profile/`، GET `dashboard/appointments/` |
| رزرو | GET و POST `appointments/`، GET `appointments/{id}/`، POST `appointments/{id}/cancel/`، POST `appointments/{id}/payment-receipt/`، GET `appointments/{id}/payment-receipt/download/` |
| مشاور | GET `appointments/consultant/` و `appointments/consultant/{id}/`، POST جزئیات با پسوند `approve/`، `reject/` و `complete/` |
| بررسی پرداخت | GET `appointments/admin/payments/` و `appointments/admin/payments/{id}/`، POST جزئیات با پسوند `approve/` و `reject/` |

- فرم ویزا فیلدهای واقعی کشور، نوع ویزا، تاریخ سفر و بازگشت، هدف و توضیحات را می‌فرستد. مرحله اطلاعات متقاضی از پروفایل حساب خوانده می‌شود. مدرک پس از دریافت کد پیگیری ارسال می‌شود و در صورت خطا می‌توان فقط ارسال مدرک را تکرار کرد.
- مبلغ و شمارهٔ کارت از پاسخ رزرو دریافت می‌شوند. وضعیت رزرو از API خوانده می‌شود. لینک رسید تنها پس از وجود رسید نمایش داده می‌شود و دانلود از مسیر مجاز API انجام می‌شود.
- دسترسی مشاور و بررسی‌کننده از پاسخ API تعیین می‌شود. پس از بررسی پرداخت، سوابق در صورت داشتن شناسهٔ رزرو از API جزئیات قابل مشاهده هستند.
- خطاهای شبکه و HTTP با پیام در صفحه یا اعلان نمایش داده می‌شوند. Mutationها پس از موفقیت، Queryهای مرتبط را تازه می‌کنند.

## محدودهٔ محتوای محلی

- معرفی خدمات، راهنمای وقت سفارت، مقالات، سوالات متداول، درباره، تماس، حریم خصوصی و شرایط استفاده محتوای محلی‌اند. بک‌اند برای رزرو وقت سفارت، فرم تماس یا مدیریت این محتوا endpoint ندارد.
- صفحهٔ جزئیات کشور از همان فهرست کشورها استفاده می‌کند. اطلاعات تفصیلی شرایط ویزا، انواع ویزای مختص هر کشور، فهرست مدارک و ارتباط کشور با مشاور در API ارائه نشده‌اند. گزینه‌های نوع ویزا پیشنهاد متنی برای فیلد آزاد API هستند.
- API فهرست پرداخت، فقط صف رسیدهای در انتظار را برمی‌گرداند. صفحهٔ مدیر امکان مراجعه به جزئیات پرداخت‌های بررسی‌شده با شناسه را دارد.
- برای تصاویر مقصد و تصویر اصلی از عکس‌های Unsplash استفاده شده است. مقصدهای تصویری بخش محبوب، نمونه‌های معرفی مقاصد‌اند. فعال بودن مقصد برای ثبت درخواست از بک‌اند خوانده می‌شود.

## کنترل کیفیت و ساخت

```sh
npm run lint
npx tsc --noEmit
npm run build
npm run preview
```

پوشهٔ `dist` خروجی ساخت است. `node_modules`، `dist`، داده‌های آزمون و اطلاعات محیطی خصوصی در ZIP منبع قرار ندارند.
