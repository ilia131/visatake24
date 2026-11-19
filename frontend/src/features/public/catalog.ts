import { paths } from "../../lib/api";
import { useApiQuery } from "../../lib/query";
import type { Consultant, Country, Slot } from "../../lib/types";
export const useCountries = () =>
  useApiQuery<Country[]>(["countries"], paths.visas + "countries/");
export const useConsultants = (search = "", specialty = "") =>
  useApiQuery<Consultant[]>(
    ["consultants", search, specialty],
    paths.consultants,
    true,
    { search: search || undefined, specialties__slug: specialty || undefined },
  );
export const useConsultant = (slug: string) =>
  useApiQuery<Consultant>(
    ["consultant", slug],
    paths.consultants + encodeURIComponent(slug) + "/",
  );
export const useSlots = (id?: number) =>
  useApiQuery<Slot[]>(
    ["availability", id],
    paths.appointments + "availability/",
    !!id,
    { consultant: id },
  );
export const visaTypes = [
  "گردشگری",
  "تحصیلی",
  "کاری",
  "دیدار خانواده",
  "تجاری",
  "سایر",
];
export const destinations = [
  { slug: "canada", name: "کانادا", name_en: "Canada", flag: "🇨🇦" },
  { slug: "france", name: "فرانسه", name_en: "France", flag: "🇫🇷" },
  { slug: "germany", name: "آلمان", name_en: "Germany", flag: "🇩🇪" },
  { slug: "italy", name: "ایتالیا", name_en: "Italy", flag: "🇮🇹" },
];
export const articles = [
  {
    slug: "visa-checklist",
    title: "قبل از ثبت درخواست ویزا چه آماده کنیم؟",
    image: "guide",
    category: "مدارک ویزا",
    text: [
      "ابتدا در وب‌سایت رسمی مرجع صادرکننده، فهرست مدارک نوع ویزای خود را بررسی کنید. شرایط ممکن است با توجه به مقصد و هدف سفر متفاوت باشد.",
      "اعتبار گذرنامه، تاریخ‌های سفر و هماهنگی اطلاعات فرم‌ها را کنترل کنید. یک نسخهٔ خوانا از مدارک و رسیدها را نزد خود نگه دارید.",
    ],
  },
  {
    slug: "first-consultation",
    title: "چگونه برای جلسه مشاوره آماده شویم؟",
    image: "travel",
    category: "مشاوره سفر",
    text: [
      "کشور مقصد، هدف سفر و زمان‌بندی احتمالی را از قبل مشخص کنید. سوال‌های خود را بنویسید و اگر درخواست قبلی داشته‌اید، نتیجه و زمان آن را یادداشت کنید.",
      "در جلسه درباره گزینه‌های متناسب با شرایط خود، مدارک موردنیاز و مراحل بعدی بپرسید.",
    ],
  },
];
export const faqs = [
  [
    "چطور درخواست ویزا ثبت کنم؟",
    "پس از ورود، مقصد و نوع ویزا را انتخاب کنید و اطلاعات سفر را وارد کنید. پس از ثبت، کد پیگیری در داشبورد در دسترس خواهد بود.",
  ],
  [
    "رزرو مشاوره چه زمانی قطعی می‌شود؟",
    "پس از تأیید مشاور، اطلاعات پرداخت در رزرو نمایش داده می‌شود. وقتی مدیر رسید شما را تأیید کند، وضعیت رزرو قطعی خواهد شد.",
  ],
  [
    "رسید پرداخت و مدارک را کجا بارگذاری کنم؟",
    "رسید را از جزئیات رزرو و مدارک را از جزئیات پرونده بارگذاری کنید. فایل‌های خصوصی از مسیر دانلود امن قابل دریافت‌اند.",
  ],
  [
    "آیا ثبت درخواست به معنی صدور ویزاست؟",
    "تصمیم درباره صدور ویزا با مرجع رسمی کشور مقصد است.",
  ],
];
