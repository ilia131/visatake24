# رزرو مشاوره و بررسی پرداخت

مسیرهای جدول نسبت به `/api/v1/appointments/` نوشته شده‌اند. Swagger پروژه در `/api/docs/` و نسخهٔ قابل استفادهٔ OpenAPI در `schema.yml` قرار دارد. مسیرهای خصوصی به کوکی JWT نیاز دارند و درخواست‌های تغییردهنده با CSRF محافظت می‌شوند.

| متد | مسیر | دسترسی | بدنه | پاسخ موفق | خطا |
|---|---|---|---|---|---|
| GET | `/` | کاربر واردشده | — | 200، فهرست رزروهای خودش | 401، 403 |
| POST | `/` | کاربر واردشده | `availability_id` و `user_note` اختیاری | 201، رزرو `pending` با مبلغ ثبت‌شده | 400، 401، 403، 404 |
| GET | `/{id}/` | مالک | — | 200، جزئیات رزرو | 401، 403، 404 |
| POST | `/{id}/cancel/` | مالک | — | 200، رزرو `cancelled` | 400، 401، 403، 404 |
| POST | `/{id}/payment-receipt/` | مالک | فرم multipart با `payment_receipt` | 200، رزرو `payment_submitted` | 400، 401، 403، 404، 415 |
| GET | `/{id}/payment-receipt/download/` | مالک، مشاور رزرو، بررسی‌کننده | — | 200، فایل دانلودی | 401، 403، 404 |
| GET | `/consultant/` | مشاور | فیلترهای اختیاری `status`، `date` و `page` | 200، فهرست صفحه‌بندی‌شده | 400، 401، 403، 404 |
| GET | `/consultant/{id}/` | مشاور رزرو | — | 200، جزئیات | 401، 403، 404 |
| POST | `/consultant/{id}/approve/` | مشاور رزرو | — | 200، رزرو `awaiting_payment` | 400، 401، 403، 404 |
| POST | `/consultant/{id}/reject/` | مشاور رزرو | `rejection_reason` | 200، رزرو `rejected` | 400، 401، 403، 404 |
| POST | `/consultant/{id}/complete/` | مشاور رزرو، پس از پایان جلسه | — | 200، رزرو `completed` | 400، 401، 403، 404 |
| GET | `/admin/payments/` | بررسی‌کننده | `page` اختیاری | 200، صف صفحه‌بندی‌شدهٔ رسیدها | 401، 403، 404 |
| GET | `/admin/payments/{id}/` | بررسی‌کننده | — | 200، جزئیات و لینک دانلود | 401، 403، 404 |
| POST | `/admin/payments/{id}/approve/` | بررسی‌کننده | — | 200، رزرو `confirmed` | 400، 401، 403، 404 |
| POST | `/admin/payments/{id}/reject/` | بررسی‌کننده | `payment_note` | 200، رزرو `payment_rejected` | 400، 401، 403، 404 |

- بررسی‌کننده می‌تواند کاربر `is_staff`، کاربر با نقش `manager`، یا دارندهٔ مجوز `appointments.review_payment` باشد.
- تاریخ فیلتر مشاور به شکل `YYYY-MM-DD` و بر اساس منطقهٔ زمانی تهران تفسیر می‌شود.
- تعرفه به تومان در مسیر عمومی مشاوران نمایش داده می‌شود. مدیریت تعرفه از مسیر `/api/v1/consultants/manage/{id}/` انجام می‌شود.
- شماره کارت با `APPOINTMENT_PAYMENT_CARD` تنظیم می‌شود. فقط مالک پس از تأیید مشاور آن را می‌بیند.
- رد پرداخت زمان را آزاد می‌کند. رسید جایگزین تنها در صورتی پذیرفته می‌شود که زمان هنوز آزاد، قابل رزرو و در آینده باشد. تأیید مشاور و تأیید پرداخت هم به زمان معتبر نیاز دارند. لغو توسط مالک طبق قاعدهٔ قبلی در وضعیت `pending` یا `confirmed` مجاز است.
- رسید JPG، JPEG، PNG یا PDF حداکثر ۵ مگابایت است. پوشهٔ `private_media/appointment_receipts` باید خارج از مسیرهای عمومی سرور وب نگه داشته شود.
- رزروهای قدیمی وضعیت فعلی خود را حفظ می‌کنند. مبلغ تاریخی برای آن‌ها موجود نبود و فیلد جدید با صفر مقداردهی می‌شود. زمان‌ها و مدرک تأیید تاریخی نیز خودکار ساخته نمی‌شوند.
- سیگنال `appointment_event` پس از ثبت تراکنش، شناسه و وضعیت جدید رزرو را به دریافت‌کننده‌ها می‌دهد. `remind_appointment` امکان انتشار رویداد یادآوری برای رزرو قطعی را فراهم می‌کند. اتصال دریافت‌کننده برای ارسال پیام و زمان‌بندی یادآوری به زیرساخت اطلاع‌رسانی نیاز دارد.

## اجرا و آزمون

متغیرهای `POSTGRES_DB`، `POSTGRES_USER`، `POSTGRES_PASSWORD`، `POSTGRES_HOST` و `POSTGRES_PORT` را برای PostgreSQL تنظیم کنید. کاربر پایگاه دادهٔ آزمون باید بتواند پایگاه آزمایشی بسازد. آزمون هم‌زمانی روی SQLite رد می‌شود، چون SQLite قفل ردیفی `SELECT FOR UPDATE` ندارد.

```sh
python manage.py check
python manage.py makemigrations
python manage.py migrate
python manage.py spectacular --validate --file schema.yml
python -m pytest --ds=config.settings apps/appointments/ apps/consultants/ -v
```

## فهرست فایل‌ها

### ایجادشده

- `APPOINTMENTS.md`
- `apps/appointments/api/permissions.py`
- `apps/appointments/migrations/0002_appointmenthistory_alter_appointment_options_and_more.py`
- `apps/appointments/receipts.py`
- `apps/appointments/services/notifications.py`
- `apps/appointments/tests/test_booking_workflow.py`
- `apps/consultants/migrations/0003_consultant_consultation_fee_and_more.py`
- `apps/consultants/tests/test_consultation_fee.py`
- `apps/visas/migrations/0006_alter_visaapplicationdocument_file.py`

### تغییرکرده

- `.env.example`
- `.gitignore`
- `apps/appointments/admin.py`
- `apps/appointments/api/serializers/appointment.py`
- `apps/appointments/api/serializers/availability.py`
- `apps/appointments/api/urls.py`
- `apps/appointments/api/views/appointment.py`
- `apps/appointments/models/appointment.py`
- `apps/appointments/selectors/appointments.py`
- `apps/appointments/selectors/availability.py`
- `apps/appointments/services/booking.py`
- `apps/consultants/api/serializers/consultant.py`
- `apps/consultants/api/serializers/consultant_admin.py`
- `apps/consultants/api/urls.py`
- `apps/consultants/api/views/assignment.py`
- `apps/consultants/models/consultant.py`
- `apps/dashboard/api/views/overview.py`
- `apps/dashboard/api/views/profile.py`
- `apps/visas/models/application_document.py`
- `config/settings.py`
- `config/urls.py`
- `requirements-lock.txt`
- `schema.yml`
