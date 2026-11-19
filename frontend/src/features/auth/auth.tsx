import { useState, type FormEvent } from "react";
import { Link, Navigate, Outlet, useLocation, useNavigate } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";
import { ShieldCheck } from "lucide-react";
import type { CountryCode } from "libphonenumber-js";
import { code, message, paths, post, queryClient, resetCsrf } from "../../lib/api";
import { useAction, useApiQuery } from "../../lib/query";
import type { User } from "../../lib/types";
import { Button, ErrorState, Input, LoadingSkeleton } from "../../components/ui";
import { PhoneField, validPhone } from "./phone-field";

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

function CredentialsForm({ register }: { register: boolean }) {
  const location = useLocation();
  const navigate = useNavigate();
  const [country, setCountry] = useState<CountryCode>("IR");
  const [number, setNumber] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const action = useMutation({
    gcTime: 0,
    mutationFn: (payload: Record<string, string>) =>
      post<{ user: User }>(paths.auth + (register ? "register/" : "login/"), payload),
    onSuccess: async (result) => {
      resetCsrf();
      await queryClient.cancelQueries({ queryKey: ["private"] });
      queryClient.removeQueries({
        predicate: ({ queryKey }) => queryKey[0] === "private" && queryKey[1] !== "user",
      });
      queryClient.setQueryData(userKey, result);
      navigate(redirect(location.state?.from), { replace: true });
    },
    onError: (failure) => setError(
      code(failure) === 401 ? "شماره تلفن یا رمز عبور نادرست است." : message(failure),
    ),
  });

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!validPhone(number, country)) {
      setError("شماره تلفن برای کشور انتخاب‌شده معتبر نیست.");
      return;
    }
    const fields = Object.fromEntries(new FormData(event.currentTarget)) as Record<string, string>;
    if (!fields.password || (register && (!fields.first_name.trim() || !fields.last_name.trim()))) {
      setError("فیلدهای ضروری را تکمیل کنید.");
      return;
    }
    if (register && fields.password !== fields.password_confirmation) {
      setError("رمز عبور و تکرار آن یکسان نیستند.");
      return;
    }
    setError("");
    action.mutate({ ...fields, country_code: country, phone_number: number });
  }

  return (
    <div className="auth-shell">
      <section className="panel auth-card">
        <ShieldCheck size={34} />
        <h1>{register ? "ثبت‌نام" : "ورود"}</h1>
        <form noValidate onSubmit={submit}>
          {register && <>
            <Input label="نام" name="first_name" autoComplete="given-name" required maxLength={150} />
            <Input label="نام خانوادگی" name="last_name" autoComplete="family-name" required maxLength={150} />
          </>}
          <PhoneField country={country} number={number}
            onCountryChange={(value) => { setCountry(value); setError(""); }}
            onNumberChange={(value) => { setNumber(value); setError(""); }} />
          <Input label="رمز عبور" name="password" dir="ltr" required maxLength={128}
            type={showPassword ? "text" : "password"}
            autoComplete={register ? "new-password" : "current-password"} />
          {register && <Input label="تکرار رمز عبور" name="password_confirmation" dir="ltr"
            required maxLength={128} type={showPassword ? "text" : "password"} autoComplete="new-password" />}
          <button type="button" className="text-button password-toggle"
            aria-pressed={showPassword} onClick={() => setShowPassword(!showPassword)}>
            {showPassword ? "مخفی کردن رمز عبور" : "نمایش رمز عبور"}
          </button>
          {error && <p role="alert" className="error">{error}</p>}
          <Button full disabled={action.isPending}>
            {action.isPending ? "در حال بررسی…" : register ? "ثبت‌نام" : "ورود"}
          </Button>
        </form>
        <Link to={register ? "/auth/login" : "/auth/register"} state={{ from: location.state?.from }}>
          {register ? "ورود به حساب" : "ایجاد حساب"}
        </Link>
      </section>
    </div>
  );
}

export function Login() {
  return <CredentialsForm register={false} />;
}

export function Register() {
  return <CredentialsForm register />;
}
