import { useState } from "react";
import {
  Link,
  useNavigate,
  useParams,
  useSearchParams,
} from "react-router-dom";
import {
  BadgeCheck,
  CalendarDays,
  ChevronDown,
  ClipboardList,
  Compass,
  FileCheck,
  Globe2,
  MapPin,
  PlaneTakeoff,
  Search,
  ShieldCheck,
  UserRound,
  Users,
} from "lucide-react";
import {
  Breadcrumb,
  EmptyState,
  PageHeading,
  QueryState,
  SearchBox,
} from "../../components/ui";
import { assets } from "../../lib/api";
import { number, toman } from "../../lib/format";
import type { Consultant, Country } from "../../lib/types";
import {
  articles,
  destinations,
  faqs,
  useConsultants,
  useCountries,
  visaTypes,
} from "./catalog";

const image = (slug: string) =>
  "/images/" +
  (destinations.some((d) => d.slug === slug) ? slug : "travel") +
  ".jpg";
export const services = [
  {
    slug: "visa",
    title: "درخواست ویزا",
    description: "انتخاب مقصد، ثبت اطلاعات سفر و پیگیری آنلاین پرونده.",
    Icon: FileCheck,
    href: "/applications/new",
    action: "شروع درخواست",
  },
  {
    slug: "consultation",
    title: "مشاوره تخصصی",
    description: "بررسی شرایط سفر و انتخاب زمان جلسه با مشاور.",
    Icon: Users,
    href: "/consultants",
    action: "انتخاب مشاور",
  },
  {
    slug: "embassy",
    title: "راهنمای وقت سفارت",
    description: "آشنایی با مراحل و آمادگی پیش از مراجعه به سفارت.",
    Icon: CalendarDays,
    href: "/blog/visa-checklist",
    action: "خواندن راهنما",
  },
];
type Destination = Pick<Country, "slug" | "name" | "name_en" | "flag">;
export function CountryCard({
  country,
  available = true,
  visa = "",
}: {
  country: Destination;
  available?: boolean;
  visa?: string;
}) {
  const filter = visa ? "?visa=" + encodeURIComponent(visa) : "";
  const href = available
    ? "/countries/" + country.slug + filter
    : "/countries?search=" + encodeURIComponent(country.name);
  return (
    <Link className="country-card" to={href}>
      <img loading="lazy" src={image(country.slug)} alt={country.name} />
      <div className="country-overlay">
        <span className="flag">{country.flag}</span>
        <div>
          <strong>{country.name}</strong>
          <small dir="ltr">{country.name_en}</small>
        </div>
      </div>
    </Link>
  );
}
export function ConsultantCard({ consultant }: { consultant: Consultant }) {
  return (
    <article className="panel consultant-card">
      <div className="person">
        {consultant.avatar ? (
          <img src={assets(consultant.avatar)} alt={consultant.full_name} />
        ) : (
          <span className="avatar">
            <UserRound />
          </span>
        )}
        <div>
          <h3>
            {consultant.full_name}{" "}
            {consultant.is_verified && (
              <BadgeCheck size={18} aria-label="تأییدشده" />
            )}
          </h3>
          <p>{consultant.title}</p>
        </div>
      </div>
      <p>
        {consultant.specialties.map((s) => s.name).join("، ") || "مشاوره ویزا"}
      </p>
      <div className="between">
        <span>{number(consultant.experience_years)} سال سابقه</span>
        <strong>{toman(consultant.consultation_fee)}</strong>
      </div>
      <Link
        className="button outline full"
        to={"/consultants/" + consultant.slug}
      >
        پروفایل و زمان‌های آزاد
      </Link>
    </article>
  );
}
export function ServiceCard({
  service,
}: {
  service: (typeof services)[number];
}) {
  return (
    <Link className="panel service-card" to={"/services/" + service.slug}>
      <span className="soft-icon">
        <service.Icon size={24} />
      </span>
      <h3>{service.title}</h3>
      <p>{service.description}</p>
      <span className="green-link">مشاهده جزئیات</span>
    </Link>
  );
}
function FaqList({ compact = false }: { compact?: boolean }) {
  return (
    <div className="faq-list">
      {faqs.slice(0, compact ? 3 : undefined).map(([question, answer]) => (
        <details key={question}>
          <summary>
            {question}
            <ChevronDown size={19} />
          </summary>
          <p>{answer}</p>
        </details>
      ))}
    </div>
  );
}
function ArticleCards() {
  return (
    <div className="grid two">
      {articles.map((article) => (
        <Link
          className="panel article-card"
          key={article.slug}
          to={"/blog/" + article.slug}
        >
          <img loading="lazy" src={`/images/${article.image}.jpg`} alt="" />
          <div>
            <small>{article.category}</small>
            <h3>{article.title}</h3>
            <span className="green-link">مطالعه راهنما</span>
          </div>
        </Link>
      ))}
    </div>
  );
}
export function Home() {
  const countries = useCountries();
  const consultants = useConsultants();
  const navigate = useNavigate();
  const [slug, setSlug] = useState("");
  const [visa, setVisa] = useState("");
  const popular = destinations.map((d) => ({
    country: countries.data?.find((c) => c.slug === d.slug) ?? d,
    available: !!countries.data?.some((c) => c.slug === d.slug),
  }));
  return (
    <>
      <section className="container hero-wrap">
        <div className="hero">
          <div className="hero-copy">
            <div className="hero-kicker">
              <Compass size={17} /> راهنمای سفرهای بین‌المللی
            </div>
            <h1>
              مسیر روشن
              <br />
              برای <em>سفرهای بزرگ</em>
            </h1>
            <p>
              مقصدتان را انتخاب کنید، درخواست ویزا را ثبت کنید و در هر مرحله
              مسیر پرونده‌تان را دنبال کنید.
            </p>
            <Link to="/applications/new" className="button primary hero-cta">
              شروع درخواست ویزا
            </Link>
          </div>
        </div>
        <form
          className="hero-search"
          onSubmit={(e) => {
            e.preventDefault();
            navigate(
              slug
                ? "/countries/" +
                    slug +
                    (visa ? "?visa=" + encodeURIComponent(visa) : "")
                : "/countries" +
                    (visa ? "?visa=" + encodeURIComponent(visa) : ""),
            );
          }}
        >
          <label>
            <MapPin size={23} />
            <span>
              کشور مقصد
              <select
                aria-label="کشور مقصد"
                value={slug}
                onChange={(e) => setSlug(e.target.value)}
              >
                <option value="">انتخاب کشور</option>
                {countries.data?.map((c) => (
                  <option value={c.slug} key={c.id}>
                    {c.name}
                  </option>
                ))}
              </select>
            </span>
          </label>
          <label>
            <ClipboardList size={23} />
            <span>
              نوع ویزا
              <select
                aria-label="نوع ویزا"
                value={visa}
                onChange={(e) => setVisa(e.target.value)}
              >
                <option value="">انتخاب نوع ویزا</option>
                {visaTypes.map((t) => (
                  <option key={t}>{t}</option>
                ))}
              </select>
            </span>
          </label>
          <button className="button primary" type="submit">
            <Search size={19} /> جست‌وجوی مقصد
          </button>
        </form>
      </section>
      <section className="container home-section popular">
        <div className="section-heading">
          <div>
            <span className="eyebrow">
              <Globe2 size={17} /> مقصد سفر
            </span>
            <h2>مقصدهای محبوب</h2>
            <p>برای شروع، مقصدی را که در ذهن دارید مرور کنید.</p>
          </div>
          <Link className="button outline" to="/countries">
            همه کشورها
          </Link>
        </div>
        <div className="grid four">
          {popular.map(({ country, available }) => (
            <CountryCard
              key={country.slug}
              country={country}
              available={available}
            />
          ))}
        </div>
      </section>
      <section className="section-soft">
        <div className="container home-section">
          <div className="section-heading">
            <div>
              <span className="eyebrow">
                <Compass size={17} /> خدمات ویزاتیک
              </span>
              <h2>برای مرحله بعدی سفر</h2>
            </div>
          </div>
          <div className="grid three">
            {services.map((service) => (
              <ServiceCard key={service.slug} service={service} />
            ))}
          </div>
        </div>
      </section>
      <section className="container home-section">
        <div className="section-heading">
          <div>
            <span className="eyebrow">
              <PlaneTakeoff size={17} /> از برنامه‌ریزی تا پیگیری
            </span>
            <h2>مراحل درخواست ویزا</h2>
          </div>
        </div>
        <div className="grid three steps">
          {[
            [
              Globe2,
              "انتخاب مقصد",
              "کشور و نوع ویزای موردنظرتان را انتخاب کنید.",
            ],
            [
              ClipboardList,
              "تکمیل درخواست",
              "اطلاعات سفر و مدارک را در پرونده ثبت کنید.",
            ],
            [
              ShieldCheck,
              "پیگیری پرونده",
              "از داشبورد وضعیت درخواست را دنبال کنید.",
            ],
          ].map(([Icon, title, body], index) => {
            const StepIcon = Icon as typeof Globe2;
            return (
              <article className="panel" key={String(title)}>
                <span className="soft-icon">
                  <StepIcon size={24} />
                </span>
                <small>مرحله {number(index + 1)}</small>
                <h3>{String(title)}</h3>
                <p>{String(body)}</p>
              </article>
            );
          })}
        </div>
      </section>
      <section className="section-soft">
        <div className="container home-section">
          <div className="section-heading">
            <div>
              <span className="eyebrow">
                <Users size={17} /> مشاوره پیش از اقدام
              </span>
              <h2>با یک مشاور گفتگو کنید</h2>
            </div>
            <Link className="button outline" to="/consultants">
              مشاهده مشاوران
            </Link>
          </div>
          <QueryState query={consultants}>
            {consultants.data?.length ? (
              <div className="grid three">
                {consultants.data.slice(0, 3).map((c) => (
                  <ConsultantCard consultant={c} key={c.id} />
                ))}
              </div>
            ) : (
              <EmptyState title="در حال حاضر پروفایل فعالی برای مشاوره وجود ندارد." />
            )}
          </QueryState>
        </div>
      </section>
      <section className="container home-section">
        <div className="benefits">
          <div>
            <ShieldCheck /> دانلود امن مدارک و رسیدها
          </div>
          <div>
            <CalendarDays /> انتخاب زمان مشاوره
          </div>
          <div>
            <ClipboardList /> پیگیری درخواست با کد پیگیری
          </div>
        </div>
      </section>
      <section className="container home-section">
        <div className="section-heading">
          <div>
            <span className="eyebrow">پیش از سفر</span>
            <h2>مقالات و راهنماها</h2>
          </div>
          <Link className="button outline" to="/blog">
            همه راهنماها
          </Link>
        </div>
        <ArticleCards />
      </section>
      <section className="container home-section faq-home">
        <h2>سوالات متداول</h2>
        <FaqList compact />
        <Link className="green-link" to="/faq">
          همه سوالات
        </Link>
      </section>
      <section className="container home-section">
        <div className="cta-band">
          <div>
            <h2>برای شروع سفر آماده‌اید؟</h2>
            <p>
              پرونده ویزا را ایجاد کنید و مراحل را از حساب کاربری دنبال کنید.
            </p>
          </div>
          <Link className="button white" to="/applications/new">
            شروع درخواست ویزا
          </Link>
        </div>
      </section>
    </>
  );
}
export function Countries() {
  const countries = useCountries();
  const [params, setParams] = useSearchParams();
  const search = params.get("search") || "";
  const [order, setOrder] = useState("default");
  const filtered = (countries.data || []).filter((c) =>
    [c.name, c.name_en, c.slug].some((value) =>
      value.toLowerCase().includes(search.trim().toLowerCase()),
    ),
  );
  if (order === "alphabet")
    filtered.sort((a, b) => a.name.localeCompare(b.name, "fa"));
  return (
    <div className="container page">
      <Breadcrumb title="کشورها" />
      <PageHeading
        title="کشورهای مقصد"
        intro="کشور مقصد را جست‌وجو کنید و درخواست ویزا را آغاز کنید."
      />
      <div className="toolbar">
        <SearchBox
          value={search}
          onChange={(value) =>
            setParams(
              (current) => {
                const next = new URLSearchParams(current);
                if (value) next.set("search", value);
                else next.delete("search");
                return next;
              },
              { replace: true },
            )
          }
          placeholder="نام کشور را جست‌وجو کنید"
        />
        <select
          aria-label="مرتب‌سازی"
          value={order}
          onChange={(e) => setOrder(e.target.value)}
        >
          <option value="default">ترتیب پیش‌فرض</option>
          <option value="alphabet">ترتیب الفبایی</option>
        </select>
      </div>
      <QueryState query={countries}>
        {filtered.length ? (
          <div className="grid four">
            {filtered.map((country) => (
              <CountryCard
                key={country.id}
                country={country}
                visa={params.get("visa") || ""}
              />
            ))}
          </div>
        ) : (
          <EmptyState title="کشوری مطابق جست‌وجو پیدا نشد." />
        )}
      </QueryState>
    </div>
  );
}
export function CountryDetail() {
  const { slug } = useParams();
  const [params, setParams] = useSearchParams();
  const countries = useCountries();
  const country = countries.data?.find((c) => c.slug === slug);
  const visa = params.get("visa") || "";
  return (
    <div className="container page">
      <Breadcrumb
        title={country?.name || "جزئیات کشور"}
        parent={["کشورها", "/countries"]}
      />
      <QueryState query={countries}>
        {country ? (
          <>
            <div
              className="detail-banner"
              style={{
                backgroundImage: `linear-gradient(270deg, #071c16e6, #071c1644), url(${image(country.slug)})`,
              }}
            >
              <h1>
                {country.flag} {country.name}
              </h1>
              <p>{country.description}</p>
            </div>
            <div className="grid two detail-grid">
              <article className="panel">
                <h2>راهنمای درخواست</h2>
                <p>
                  شرایط و مدارک را بر اساس نوع ویزا از مرجع رسمی کشور مقصد بررسی
                  کنید. اطلاعات سفر را وارد کنید و وضعیت را در داشبورد دنبال
                  کنید.
                </p>
                <Link className="green-link" to="/blog/visa-checklist">
                  چک‌لیست عمومی درخواست
                </Link>
                <FaqList compact />
              </article>
              <article className="panel">
                <h2>ثبت درخواست برای {country.name}</h2>
                <label>
                  نوع ویزا
                  <select
                    value={visa}
                    onChange={(e) =>
                      setParams(e.target.value ? { visa: e.target.value } : {})
                    }
                  >
                    <option value="">انتخاب نوع ویزا</option>
                    {visaTypes.map((t) => (
                      <option key={t}>{t}</option>
                    ))}
                  </select>
                </label>
                <Link
                  className="button primary full"
                  to={
                    "/applications/new?" +
                    new URLSearchParams({
                      country: String(country.id),
                      ...(visa ? { visa } : {}),
                    })
                  }
                >
                  شروع درخواست ویزا
                </Link>
                <p>برای بررسی شرایط فردی می‌توانید زمان مشاوره انتخاب کنید.</p>
                <Link to="/consultants" className="button outline full">
                  دیدن مشاوران
                </Link>
              </article>
            </div>
          </>
        ) : (
          <EmptyState title="مقصد موردنظر در فهرست فعال کشورها وجود ندارد." />
        )}
      </QueryState>
    </div>
  );
}
export function Consultants() {
  const [search, setSearch] = useState("");
  const [specialty, setSpecialty] = useState("");
  const catalog = useConsultants();
  const list = useConsultants(search.trim(), specialty);
  const choices = [
    ...new Map(
      catalog.data?.flatMap((c) => c.specialties).map((s) => [s.slug, s.name]),
    ).entries(),
  ];
  const [params] = useSearchParams();
  return (
    <div className="container page">
      <Breadcrumb title="مشاوران" />
      <PageHeading
        title={params.has("booking") ? "رزرو مشاوره" : "مشاوران ویزاتیک"}
        intro="پروفایل، تعرفه و زمان‌های آزاد هر مشاور را بررسی کنید."
      />
      <div className="toolbar">
        <SearchBox
          value={search}
          onChange={setSearch}
          placeholder="جست‌وجوی نام یا تخصص"
        />
        <select
          aria-label="تخصص"
          value={specialty}
          onChange={(e) => setSpecialty(e.target.value)}
        >
          <option value="">همه تخصص‌ها</option>
          {choices.map(([slug, label]) => (
            <option key={slug} value={slug}>
              {label}
            </option>
          ))}
        </select>
      </div>
      <QueryState query={list}>
        {list.data?.length ? (
          <div className="grid three">
            {list.data.map((c) => (
              <ConsultantCard key={c.id} consultant={c} />
            ))}
          </div>
        ) : (
          <EmptyState title="مشاوری مطابق جست‌وجو پیدا نشد." />
        )}
      </QueryState>
    </div>
  );
}
export function Services() {
  return (
    <div className="container page">
      <Breadcrumb title="خدمات" />
      <PageHeading title="خدمات ویزاتیک" />
      <div className="grid three">
        {services.map((s) => (
          <ServiceCard key={s.slug} service={s} />
        ))}
      </div>
    </div>
  );
}
export function ServiceDetail() {
  const { slug } = useParams();
  const service = services.find((s) => s.slug === slug);
  return (
    <div className="container page">
      <Breadcrumb
        title={service?.title || "خدمات"}
        parent={["خدمات", "/services"]}
      />
      {service ? (
        <article className="panel prose">
          <span className="soft-icon">
            <service.Icon />
          </span>
          <PageHeading title={service.title} intro={service.description} />
          {slug === "embassy" && (
            <p>
              زمان و شرایط مراجعه را از وب‌سایت سفارت یا کارگزار رسمی مقصد بررسی
              کنید.
            </p>
          )}
          <Link className="button primary" to={service.href}>
            {service.action}
          </Link>
        </article>
      ) : (
        <EmptyState title="خدمت موردنظر یافت نشد." />
      )}
    </div>
  );
}
const staticPages: Record<string, { title: string; paragraphs: string[] }> = {
  about: {
    title: "درباره ویزاتیک",
    paragraphs: [
      "ویزا‌تیک به شما امکان می‌دهد مقصدهای موجود را مرور کنید، درخواست ویزا ثبت کنید و در صورت نیاز جلسه مشاوره رزرو کنید.",
      "در حساب کاربری می‌توانید وضعیت پرونده و رزرو را دنبال کنید.",
    ],
  },
  contact: {
    title: "تماس با ما",
    paragraphs: [
      "برای گفت‌وگو درباره شرایط سفر، از فهرست مشاوران یک زمان انتخاب کنید. اطلاعات تماس عمومی در این نسخه منتشر نشده است.",
    ],
  },
  privacy: {
    title: "حریم خصوصی",
    paragraphs: [
      "شماره موبایل برای ورود به حساب استفاده می‌شود. مدارک و رسیدها از طریق مسیر دانلود دارای کنترل دسترسی دریافت می‌شوند.",
      "فایل را تنها در پرونده مرتبط بارگذاری کنید و اطلاعات غیرضروری را در توضیحات وارد نکنید.",
    ],
  },
  terms: {
    title: "شرایط استفاده",
    paragraphs: [
      "شرایط و مدارک ویزا بر اساس مقررات مرجع رسمی مقصد تعیین می‌شود. رزرو مشاوره پس از تأیید رسید قطعی است.",
      "پیش از ارسال، صحت اطلاعات پرونده و زمان جلسه انتخابی را بررسی کنید.",
    ],
  },
};
export function InfoPage({ name }: { name: string }) {
  const content = staticPages[name];
  const titles: Record<string, string> = {
    blog: "مقالات و راهنماها",
    faq: "سوالات متداول",
  };
  const title = content?.title || titles[name];
  return (
    <div className="container page">
      <Breadcrumb title={title} />
      <PageHeading title={title} />
      {name === "blog" ? (
        <ArticleCards />
      ) : name === "faq" ? (
        <FaqList />
      ) : (
        <article className="panel prose">
          {content.paragraphs.map((p) => (
            <p key={p}>{p}</p>
          ))}
          {name === "contact" && (
            <Link to="/consultants" className="button primary">
              انتخاب مشاور
            </Link>
          )}
        </article>
      )}
    </div>
  );
}
export function Article() {
  const { slug } = useParams();
  const article = articles.find((a) => a.slug === slug);
  return (
    <div className="container page">
      <Breadcrumb
        title={article?.title || "مقاله"}
        parent={["مقالات", "/blog"]}
      />
      {article ? (
        <article className="panel prose">
          <img
            className="article-cover"
            src={`/images/${article.image}.jpg`}
            alt=""
          />
          <PageHeading title={article.title} />
          {article.text.map((p) => (
            <p key={p}>{p}</p>
          ))}
        </article>
      ) : (
        <EmptyState title="مقاله یافت نشد." />
      )}
    </div>
  );
}
