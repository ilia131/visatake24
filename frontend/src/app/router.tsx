import { lazy, Suspense } from "react";
import { BrowserRouter, Link, Route, Routes } from "react-router-dom";
import { DashboardLayout, SiteLayout } from "../components/layout";
import { LoadingSkeleton, PageHeading } from "../components/ui";
import { Login, RequireUser, Verify } from "../features/auth/auth";
const ApplicationDetail = lazy(() =>
  import("../features/applications/pages").then((module) => ({
    default: module.ApplicationDetail,
  })),
);
const ApplicationList = lazy(() =>
  import("../features/applications/pages").then((module) => ({
    default: module.ApplicationList,
  })),
);
const ApplicationWizard = lazy(() =>
  import("../features/applications/pages").then((module) => ({
    default: module.ApplicationWizard,
  })),
);
const Documents = lazy(() =>
  import("../features/applications/pages").then((module) => ({
    default: module.Documents,
  })),
);
const AdminPayments = lazy(() =>
  import("../features/appointments/pages").then((module) => ({
    default: module.AdminPayments,
  })),
);
const AppointmentDetail = lazy(() =>
  import("../features/appointments/pages").then((module) => ({
    default: module.AppointmentDetail,
  })),
);
const AppointmentList = lazy(() =>
  import("../features/appointments/pages").then((module) => ({
    default: module.AppointmentList,
  })),
);
const ConsultantDashboard = lazy(() =>
  import("../features/appointments/pages").then((module) => ({
    default: module.ConsultantDashboard,
  })),
);
const ConsultantProfile = lazy(() =>
  import("../features/appointments/pages").then((module) => ({
    default: module.ConsultantProfile,
  })),
);
const ReviewDetail = lazy(() =>
  import("../features/appointments/pages").then((module) => ({
    default: module.ReviewDetail,
  })),
);
const Dashboard = lazy(() =>
  import("../features/dashboard/pages").then((module) => ({
    default: module.Dashboard,
  })),
);
const ProfilePage = lazy(() =>
  import("../features/dashboard/pages").then((module) => ({
    default: module.ProfilePage,
  })),
);
import {
  Article,
  Consultants,
  Countries,
  CountryDetail,
  Home,
  InfoPage,
  ServiceDetail,
  Services,
} from "../features/public/pages";

export function Router() {
  return (
    <BrowserRouter>
      <Suspense fallback={<LoadingSkeleton />}>
        <Routes>
          <Route element={<SiteLayout />}>
            <Route index element={<Home />} />
            <Route path="countries" element={<Countries />} />
            <Route path="countries/:slug" element={<CountryDetail />} />
            <Route path="consultants" element={<Consultants />} />
            <Route path="consultants/:slug" element={<ConsultantProfile />} />
            <Route path="services" element={<Services />} />
            <Route path="services/:slug" element={<ServiceDetail />} />
            {["about", "contact", "faq", "blog", "privacy", "terms"].map(
              (name) => (
                <Route
                  key={name}
                  path={name}
                  element={<InfoPage name={name} />}
                />
              ),
            )}
            <Route path="blog/:slug" element={<Article />} />
            <Route path="auth/login" element={<Login />} />
            <Route path="auth/verify" element={<Verify />} />
            <Route element={<RequireUser />}>
              <Route path="applications/new" element={<ApplicationWizard />} />
              <Route element={<DashboardLayout />}>
                <Route path="dashboard" element={<Dashboard />} />
                <Route path="dashboard/profile" element={<ProfilePage />} />
                <Route
                  path="dashboard/applications"
                  element={<ApplicationList />}
                />
                <Route
                  path="dashboard/applications/:tracking"
                  element={<ApplicationDetail />}
                />
                <Route path="dashboard/documents" element={<Documents />} />
                <Route
                  path="dashboard/appointments"
                  element={<AppointmentList />}
                />
                <Route
                  path="dashboard/appointments/:id"
                  element={<AppointmentDetail />}
                />
                <Route
                  path="consultant/dashboard"
                  element={<ConsultantDashboard />}
                />
                <Route
                  path="consultant/dashboard/:id"
                  element={<ReviewDetail kind="consultant" />}
                />
                <Route path="admin/payments" element={<AdminPayments />} />
                <Route
                  path="admin/payments/:id"
                  element={<ReviewDetail kind="admin/payments" />}
                />
              </Route>
            </Route>
            <Route
              path="*"
              element={
                <div className="container page">
                  <PageHeading title="صفحه پیدا نشد" />
                  <Link className="button primary" to="/">
                    بازگشت به خانه
                  </Link>
                </div>
              }
            />
          </Route>
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}
