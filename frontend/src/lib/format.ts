import { parseISO, isValid } from "date-fns";
export const number = (value: string | number) =>
  Number(value).toLocaleString("fa-IR");
export const toman = (value: string | number) => number(value) + " تومان";
export function date(value: string | null | undefined, time = false) {
  if (!value) return "—";
  const parsed = parseISO(value);
  return isValid(parsed)
    ? new Intl.DateTimeFormat("fa-IR", {
        dateStyle: "medium",
        ...(time ? { timeStyle: "short" } : {}),
        timeZone: "Asia/Tehran",
      }).format(parsed)
    : "—";
}
export const latinDigits = (value: string) =>
  value.replace(/[۰-۹٠-٩]/g, (c) => String(c.charCodeAt(0) % 16));
export function fileError(file: File) {
  if (!/\.(jpe?g|png|pdf)$/i.test(file.name))
    return "فرمت مجاز JPG، JPEG، PNG یا PDF است.";
  if (!file.size || file.size > 5 * 1024 * 1024)
    return "فایل باید بین ۱ بایت تا ۵ مگابایت باشد.";
  return "";
}

export function dateTime(value?: string | null): string {
  if (!value) return "—";

  const parsedDate = new Date(value);

  if (Number.isNaN(parsedDate.getTime())) return "—";

  return new Intl.DateTimeFormat("fa-IR", {
    timeZone: "Asia/Tehran",
    calendar: "gregory",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    hourCycle: "h23",
  }).format(parsedDate);
}