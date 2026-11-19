import axios from "axios";
import type { AxiosRequestConfig } from "axios";
import { QueryClient } from "@tanstack/react-query";

const target = (import.meta.env.VITE_API_BASE_URL || "").replace(/\/$/, "");
const useProxy = import.meta.env.VITE_API_PROXY !== "false";
const baseURL = useProxy ? "" : target;
const wire = axios.create({ baseURL, withCredentials: true, timeout: 15000 });
export const api = axios.create({
  baseURL,
  withCredentials: true,
  timeout: 15000,
});
const prefix = "/api/v1/";
export const paths = {
  auth: prefix + "auth/",
  appointments: prefix + "appointments/",
  dashboard: prefix + "dashboard/",
  visas: prefix + "visas/",
  consultants: prefix + "consultants/",
};
export const code = (error: unknown) =>
  axios.isAxiosError(error) ? error.response?.status : undefined;
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      retry: (count, error) =>
        count < 1 && (!code(error) || Number(code(error)) >= 500),
    },
  },
});
let csrf: Promise<string> | undefined;
let refresh: Promise<void> | undefined;

api.interceptors.request.use(async (config) => {
  if (!["get", "head", "options"].includes(config.method || "get")) {
    csrf ??= wire
      .get<{ csrfToken: string }>(paths.auth + "csrf/")
      .then(({ data }) => data.csrfToken)
      .catch((error) => {
        csrf = undefined;
        throw error;
      });
    config.headers.set("X-CSRFToken", await csrf);
  }
  return config;
});

api.interceptors.response.use(undefined, async (error: unknown) => {
  if (!axios.isAxiosError(error) || !error.config || code(error) !== 401)
    throw error;
  const config = error.config as typeof error.config & { retried?: boolean };
  if (config.retried || config.url?.includes("/auth/otp/")) throw error;
  config.retried = true;
  refresh ??= wire
    .post(paths.auth + "token/refresh/")
    .then(() => undefined)
    .finally(() => {
      refresh = undefined;
    });
  try {
    await refresh;
  } catch (failure) {
    if (code(failure) === 401) {
      queryClient.removeQueries({
        predicate: ({ queryKey }) =>
          queryKey[0] === "private" && queryKey[1] !== "user",
      });
      queryClient.setQueryData(["private", "user"], null);
    }
    throw failure;
  }
  return api(config);
});

export function resetCsrf() {
  csrf = undefined;
}
export async function get<T>(
  url: string,
  signal?: AbortSignal,
  params?: AxiosRequestConfig["params"],
) {
  return (await api.get<T>(url, { signal, params })).data;
}
export async function post<T>(url: string, data?: unknown) {
  return (await api.post<T>(url, data)).data;
}
export function message(error: unknown): string {
  const status = code(error);
  if (status === 401) return "لطفاً دوباره وارد حساب شوید.";
  if (status === 403) return "دسترسی لازم برای این عملیات را ندارید.";
  if (status === 404) return "اطلاعات موردنظر در دسترس نیست.";
  if (status === 429)
    return "تعداد درخواست‌ها زیاد است. کمی بعد دوباره تلاش کنید.";
  if (status && status >= 500)
    return "خطای سرور رخ داد. لطفاً دوباره تلاش کنید.";
  if (axios.isAxiosError(error) && error.response?.data) {
    const data: unknown = error.response.data;
    if (typeof data === "object" && data !== null) {
      const detail = Object.values(data)
        .flat()
        .filter((item): item is string => typeof item === "string");
      if (detail.length) return detail.join(" ");
    }
  }
  return status
    ? "اطلاعات واردشده را بررسی کنید."
    : "ارتباط برقرار نشد. دوباره تلاش کنید.";
}
export function assets(url: string | null) {
  if (!url) return undefined;
  if (useProxy && /^https?:/.test(url)) {
    const parsed = new URL(url);
    if (parsed.pathname.startsWith("/media/"))
      return parsed.pathname + parsed.search;
  }
  return url.startsWith("/") ? baseURL + url : url;
}
export async function download(path: string, fallback: string) {
  const match =
    /^\/api\/v1\/(?:appointments\/\d+\/payment-receipt\/download|visas\/documents\/\d+\/download)\/$/;
  if (!match.test(path)) throw new Error("Invalid download path");
  const { data, headers } = await api.get<Blob>(path, { responseType: "blob" });
  const name =
    /filename="?([^";]+)"?/i.exec(
      String(headers["content-disposition"]),
    )?.[1] || fallback;
  const url = URL.createObjectURL(data);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = name;
  anchor.click();
  window.setTimeout(() => URL.revokeObjectURL(url), 1000);
}
