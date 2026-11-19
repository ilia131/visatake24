import { useEffect, useState } from "react";
import {
  Link,
  Navigate,
  Outlet,
  useLocation,
  useNavigate,
} from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { ShieldCheck } from "lucide-react";
import { code, paths, post, queryClient, resetCsrf } from "../../lib/api";
import { useAction, useApiQuery } from "../../lib/query";
import { latinDigits } from "../../lib/format";
import type { User } from "../../lib/types";
import {
  Button,
  ErrorState,
  Input,
  LoadingSkeleton,
} from "../../components/ui";

const phoneSchema = z.object({
  phone: z
    .string()
    .trim()
    .transform(latinDigits)
    .transform((s) => s.replace(/[ ()-]/g, "").replace(/^09/, "+989"))
    .pipe(
      z
        .string()
        .regex(
          /^\+[1-9]\d{7,14}$/,
          "شماره را به شکل ۰۹… یا با پیش‌شماره بین‌المللی وارد کنید.",
        ),
    ),
});
const verifySchema = z.object({
  otp: z
    .string()
    .trim()
    .transform(latinDigits)
    .pipe(z.string().regex(/^\d{6}$/, "کد باید ۶ رقم باشد.")),
});
const userKey = ["private", "user"];
export const useUser = () =>
  useApiQuery<{ user: User } | null>(userKey, paths.auth + "me/");
export function useLogout() {
  return useAction(async () => {
    await post(paths.auth + "logout/");
    resetCsrf();
    await queryClient.cancelQueries({ queryKey: ["private"] });
    queryClient.removeQueries({
      predicate: ({ queryKey }) =>
        queryKey[0] === "private" && queryKey[1] !== "user",
    });
    queryClient.setQueryData(userKey, null);
  }, "از حساب خارج شدید.");
}
export function RequireUser() {
  const query = useUser();
  const location = useLocation();
  if (query.isPending) return <LoadingSkeleton />;
  if (query.error && code(query.error) !== 401)
    return <ErrorState error={query.error} retry={query.refetch} />;
  if (!query.data?.user)
    return (
      <Navigate
        to="/auth/login"
        replace
        state={{ from: location.pathname + location.search }}
      />
    );
  return <Outlet />;
}
function redirect(from: unknown) {
  return typeof from === "string" &&
    from.startsWith("/") &&
    !from.startsWith("//") &&
    !from.includes("\\") &&
    !from.startsWith("/auth/")
    ? from
    : "/dashboard";
}

export function Login() {
  const location = useLocation();
  const navigate = useNavigate();
  const request = useAction((phone: string) =>
    post(paths.auth + "otp/request/", { phone_number: phone }),
  );
  const form = useForm({
    resolver: zodResolver(phoneSchema),
    defaultValues: { phone: "" },
  });
  return (
    <div className="auth-shell">
      <section className="panel auth-card">
        <ShieldCheck size={34} />
        <h1>ورود یا ثبت‌نام</h1>
        <p>برای دریافت کد تأیید، شماره موبایل خود را وارد کنید.</p>
        <form
          onSubmit={form.handleSubmit(({ phone }) =>
            request.mutate(phone, {
              onSuccess: () =>
                navigate("/auth/verify", {
                  state: {
                    phone,
                    from: location.state?.from,
                    sentAt: Date.now(),
                  },
                }),
            }),
          )}
        >
          <Input
            label="شماره موبایل"
            dir="ltr"
            type="tel"
            autoComplete="tel"
            placeholder="0912 345 6789"
            {...form.register("phone")}
          />
          {form.formState.errors.phone && (
            <p role="alert" className="error">
              {form.formState.errors.phone.message}
            </p>
          )}
          <Button full disabled={request.isPending}>
            {request.isPending ? "در حال ارسال…" : "دریافت کد تأیید"}
          </Button>
        </form>
        <Link to="/privacy">حریم خصوصی</Link>
      </section>
    </div>
  );
}
export function Verify() {
  const location = useLocation();
  const navigate = useNavigate();
  const phone: string | undefined = location.state?.phone;
  const [sentAt, setSentAt] = useState<number>(location.state?.sentAt ?? 0);
  const [now, setNow] = useState(Date.now);
  const remaining = Math.max(0, Math.ceil((sentAt + 60_000 - now) / 1000));
  useEffect(() => {
    const timer = window.setInterval(() => setNow(Date.now()), 1000);
    return () => window.clearInterval(timer);
  }, []);
  const resend = useAction(
    () => post(paths.auth + "otp/request/", { phone_number: phone }),
    "کد دوباره ارسال شد.",
  );
  const verify = useAction(async (otp: string) => {
    await post(paths.auth + "otp/verify/", { phone_number: phone, code: otp });
    resetCsrf();
    queryClient.removeQueries({
      predicate: ({ queryKey }) =>
        queryKey[0] === "private" && queryKey[1] !== "user",
    });
    await queryClient.invalidateQueries({ queryKey: userKey });
    navigate(redirect(location.state?.from), { replace: true });
  });
  const form = useForm({
    resolver: zodResolver(verifySchema),
    defaultValues: { otp: "" },
  });
  if (!phone) return <Navigate to="/auth/login" replace />;
  return (
    <div className="auth-shell">
      <section className="panel auth-card">
        <ShieldCheck size={34} />
        <h1>تأیید شماره موبایل</h1>
        <p>
          کد ارسال‌شده برای <bdi>{phone}</bdi> را وارد کنید.
        </p>
        <form onSubmit={form.handleSubmit(({ otp }) => verify.mutate(otp))}>
          <Input
            label="کد تأیید"
            dir="ltr"
            inputMode="numeric"
            maxLength={6}
            autoComplete="one-time-code"
            {...form.register("otp")}
          />
          {form.formState.errors.otp && (
            <p className="error" role="alert">
              {form.formState.errors.otp.message}
            </p>
          )}
          <Button full disabled={verify.isPending}>
            {verify.isPending ? "در حال بررسی…" : "تأیید و ورود"}
          </Button>
        </form>
        <div className="between">
          <Link to="/auth/login" state={{ from: location.state?.from }}>
            تغییر شماره
          </Link>
          <button
            type="button"
            className="text-button"
            disabled={remaining > 0 || resend.isPending}
            onClick={() =>
              resend.mutate(undefined, {
                onSuccess: () => setSentAt(Date.now()),
              })
            }
          >
            {remaining
              ? `ارسال مجدد تا ${remaining.toLocaleString("fa-IR")} ثانیه`
              : resend.isPending
                ? "در حال ارسال…"
                : "ارسال مجدد"}
          </button>
        </div>
      </section>
    </div>
  );
}
