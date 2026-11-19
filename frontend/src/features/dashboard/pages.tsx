import { Link } from "react-router-dom";
import { CalendarDays, Clock, FileCheck, Files } from "lucide-react";
import { z } from "zod";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  EmptyState,
  ErrorState,
  PageHeading,
  QueryState,
} from "../../components/ui";
import { number } from "../../lib/format";
import type { Profile } from "../../lib/types";
import { ApplicationCard } from "../applications/pages";
import { useApplications } from "../applications/hooks";
import { useDashboardOverview, useProfile, useSaveProfile } from "./hooks";

export function Dashboard() {
  const overview = useDashboardOverview();
  const applications = useApplications();
  const metrics = overview.data
    ? [
        {
          label: "همه درخواست‌ها",
          count: overview.data.total_applications,
          Icon: Files,
        },
        {
          label: "پرونده‌های فعال",
          count: overview.data.active_applications,
          Icon: FileCheck,
        },
        {
          label: "همه رزروها",
          count: overview.data.total_appointments,
          Icon: CalendarDays,
        },
        {
          label: "رزروهای آینده",
          count: overview.data.upcoming_appointments,
          Icon: Clock,
        },
      ]
    : [];
  return (
    <>
      <PageHeading
        title="نمای کلی"
        intro="وضعیت پرونده‌ها و رزروها را در یک نگاه ببینید."
      />
      <QueryState query={overview}>
        <div className="grid four">
          {metrics.map(({ label, count, Icon }) => (
            <article className="panel metric" key={label}>
              <span className="soft-icon">
                <Icon size={21} />
              </span>
              <strong>{number(count)}</strong>
              <p>{label}</p>
            </article>
          ))}
        </div>
      </QueryState>
      <section className="stack">
        <div className="between">
          <h2>آخرین درخواست‌ها</h2>
          <Link className="green-link" to="/dashboard/applications">
            همه درخواست‌ها
          </Link>
        </div>
        <QueryState query={applications}>
          {applications.data?.length ? (
            <div className="stack">
              {applications.data.slice(0, 4).map((item) => (
                <ApplicationCard item={item} key={item.tracking_code} />
              ))}
            </div>
          ) : (
            <EmptyState title="هنوز درخواستی ثبت نشده است." />
          )}
        </QueryState>
      </section>
      <Link className="button primary" to="/applications/new">
        شروع درخواست ویزا
      </Link>
    </>
  );
}
const profileSchema = z.object({
  first_name: z.string().trim().max(150),
  last_name: z.string().trim().max(150),
  email: z.union([z.literal(""), z.email({ error: "ایمیل معتبر وارد کنید." })]),
});
function ProfileForm({ profile }: { profile: Profile }) {
  const save = useSaveProfile();
  const form = useForm({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      first_name: profile.first_name,
      last_name: profile.last_name,
      email: profile.email || "",
    },
  });
  return (
    <form
      className="panel stack"
      onSubmit={form.handleSubmit((input) => save.mutate(input))}
    >
      <div className="grid two">
        <label>
          نام
          <input
            autoComplete="given-name"
            maxLength={150}
            {...form.register("first_name")}
          />
        </label>
        <label>
          نام خانوادگی
          <input
            autoComplete="family-name"
            maxLength={150}
            {...form.register("last_name")}
          />
        </label>
      </div>
      <label>
        شماره موبایل
        <input dir="ltr" readOnly value={profile.phone_number} />
      </label>
      <label>
        ایمیل
        <input
          dir="ltr"
          type="email"
          autoComplete="email"
          {...form.register("email")}
        />
      </label>
      {Object.entries(form.formState.errors).map(([key, error]) => (
        <p className="error" key={key}>
          {error.message}
        </p>
      ))}
      {save.error && <ErrorState error={save.error} />}
      <button className="button primary" disabled={save.isPending}>
        {save.isPending ? "در حال ذخیره…" : "ذخیره تغییرات"}
      </button>
    </form>
  );
}
export function ProfilePage() {
  const profile = useProfile();
  return (
    <>
      <PageHeading title="اطلاعات حساب" />
      <QueryState query={profile}>
        {profile.data && <ProfileForm profile={profile.data} />}
      </QueryState>
    </>
  );
}
