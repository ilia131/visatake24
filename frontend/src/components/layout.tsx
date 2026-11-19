import { useState } from "react";
import {
  CalendarDays,
  Compass,
  FileText,
  Globe2,
  LayoutDashboard,
  LogIn,
  LogOut,
  Menu,
  Plane,
  ReceiptText,
  UserRound,
  Users,
  X,
} from "lucide-react";
import { Link, NavLink, Outlet, useNavigate } from "react-router-dom";
import {
  useConsultantAppointments,
  usePayments,
} from "../features/appointments/hooks";
import { useLogout, useUser } from "../features/auth/auth";

export function Brand() {
  return (
    <Link to="/" className="brand" aria-label="VisaTake، خانه">
      <span className="brand-icon">
        <Plane size={22} />
      </span>
      <span dir="ltr">
        Visa<span>Take</span>
      </span>
    </Link>
  );
}
const nav = [
  ["صفحه اصلی", "/"],
  ["کشورها", "/countries"],
  ["خدمات", "/services"],
  ["مشاوران", "/consultants"],
  ["رزرو مشاوره", "/consultants?booking=1"],
  ["وقت سفارت", "/services/embassy"],
  ["مقالات", "/blog"],
  ["درباره ما", "/about"],
  ["تماس با ما", "/contact"],
];
export function Navbar() {
  const [open, setOpen] = useState(false);
  const user = useUser();
  return (
    <header className="site-header">
      <div className="container header-inner">
        <Brand />
        <button
          className="icon-button mobile-toggle"
          type="button"
          aria-label={open ? "بستن منو" : "باز کردن منو"}
          aria-expanded={open}
          onClick={() => setOpen(!open)}
        >
          {open ? <X /> : <Menu />}
        </button>
        <nav
          aria-label="منوی اصلی"
          className={open ? "nav-links open" : "nav-links"}
        >
          {nav.map(([label, url]) =>
            url.includes("?") ? (
              <Link to={url} key={url} onClick={() => setOpen(false)}>
                {label}
              </Link>
            ) : (
              <NavLink
                key={url}
                to={url}
                end={url === "/" || url === "/services"}
                onClick={() => setOpen(false)}
              >
                {label}
              </NavLink>
            ),
          )}
        </nav>
        <Link
          className="button outline login-link"
          to={user.data?.user ? "/dashboard" : "/auth/login"}
        >
          {user.data?.user ? <UserRound size={16} /> : <LogIn size={16} />}
          {user.data?.user ? "حساب کاربری" : "ورود / ثبت‌نام"}
        </Link>
      </div>
    </header>
  );
}
export function Footer() {
  return (
    <footer className="footer">
      <div className="container footer-grid">
        <div>
          <Brand />
          <p>جست‌وجوی مقصد، ثبت درخواست ویزا و رزرو مشاوره سفر.</p>
        </div>
        <div>
          <strong>دسترسی سریع</strong>
          <Link to="/countries">کشورها</Link>
          <Link to="/services">خدمات</Link>
          <Link to="/consultants">مشاوران</Link>
        </div>
        <div>
          <strong>راهنما</strong>
          <Link to="/blog">مقالات</Link>
          <Link to="/faq">سوالات متداول</Link>
          <Link to="/contact">تماس با ما</Link>
        </div>
        <div>
          <strong>ویزا‌تیک</strong>
          <Link to="/about">درباره ما</Link>
          <Link to="/privacy">حریم خصوصی</Link>
          <Link to="/terms">شرایط استفاده</Link>
        </div>
      </div>
      <div className="container footer-bottom">
        <span>تمام حقوق برای VisaTake محفوظ است.</span>
        <Globe2 size={19} />
      </div>
    </footer>
  );
}
export function SiteLayout() {
  return (
    <>
      <a className="skip" href="#main">
        رفتن به محتوای اصلی
      </a>
      <Navbar />
      <main id="main">
        <Outlet />
      </main>
      <Footer />
    </>
  );
}
const dashboardLinks = [
  { label: "نمای کلی", url: "/dashboard", Icon: LayoutDashboard },
  { label: "درخواست‌های من", url: "/dashboard/applications", Icon: FileText },
  { label: "مدارک من", url: "/dashboard/documents", Icon: ReceiptText },
  { label: "رزروهای من", url: "/dashboard/appointments", Icon: CalendarDays },
  { label: "اطلاعات حساب", url: "/dashboard/profile", Icon: UserRound },
  { label: "پنل مشاور", url: "/consultant/dashboard", Icon: Users },
  { label: "بررسی پرداخت‌ها", url: "/admin/payments", Icon: Compass },
];
export function DashboardSidebar() {
  const logout = useLogout();
  const navigate = useNavigate();
  const consultantAccess = useConsultantAppointments(1, "", "");
  const paymentAccess = usePayments(1);
  const visibleLinks = dashboardLinks.filter(({ url }) => {
    if (url === "/consultant/dashboard") return consultantAccess.isSuccess;
    if (url === "/admin/payments") return paymentAccess.isSuccess;
    return true;
  });
  return (
    <aside className="dashboard-sidebar">
      <nav aria-label="پنل کاربری">
        {visibleLinks.map(({ label, url, Icon }) => (
          <NavLink key={url} to={url} end={url === "/dashboard"}>
            <Icon size={19} />
            {label}
          </NavLink>
        ))}
      </nav>
      <button
        className="text-button"
        onClick={() =>
          logout.mutate(undefined, { onSuccess: () => navigate("/") })
        }
        disabled={logout.isPending}
      >
        <LogOut size={17} />
        {logout.isPending ? "در حال خروج…" : "خروج"}
      </button>
    </aside>
  );
}
export function DashboardHeader() {
  const user = useUser();
  return (
    <header className="dashboard-header">
      <span>حساب کاربری</span>
      {user.data?.user && (
        <span dir={user.data.user.first_name ? "rtl" : "ltr"}>
          {[user.data.user.first_name, user.data.user.last_name]
            .filter(Boolean)
            .join(" ") || user.data.user.phone_number}
        </span>
      )}
    </header>
  );
}
export function DashboardLayout() {
  return (
    <div className="container dashboard-layout">
      <DashboardSidebar />
      <div className="dashboard-content">
        <DashboardHeader />
        <Outlet />
      </div>
    </div>
  );
}
