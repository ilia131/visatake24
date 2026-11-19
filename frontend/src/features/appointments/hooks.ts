import { download, paths, post } from "../../lib/api";
import { useAction, useApiQuery } from "../../lib/query";
import type {
  Appointment,
  AppointmentStatus,
  DashboardAppointment,
  Page,
  Review,
} from "../../lib/types";

const root = paths.appointments;
const keys = [
  ["private", "appointments"],
  ["private", "overview"],
  ["availability"],
];
export const useAppointments = () =>
  useApiQuery<DashboardAppointment[]>(
    ["private", "appointments", "summary"],
    paths.dashboard + "appointments/",
  );
export const useOwnerAppointments = () =>
  useApiQuery<Appointment[]>(["private", "appointments", "owner"], root);
export const useAppointment = (id: string) =>
  useApiQuery<Appointment>(
    ["private", "appointments", "owner", id],
    root + id + "/",
  );
export const useCreateAppointment = () =>
  useAction(
    (input: { availability_id: number; user_note: string }) =>
      post<Appointment>(root, input),
    "درخواست رزرو ثبت شد.",
    keys,
  );
export const useCancelAppointment = (id: string) =>
  useAction(
    () => post<Appointment>(root + id + "/cancel/"),
    "رزرو لغو شد.",
    keys,
  );
export const useSubmitPaymentReceipt = (id: string) =>
  useAction(
    (file: File) => {
      const body = new FormData();
      body.append("payment_receipt", file);
      return post<Appointment>(root + id + "/payment-receipt/", body);
    },
    "رسید برای بررسی ارسال شد.",
    keys,
  );
export const useDownloadReceipt = (id: string | number) =>
  useAction(() =>
    download(root + id + "/payment-receipt/download/", "receipt"),
  );
export const useConsultantAppointments = (
  page: number,
  status: AppointmentStatus | "",
  date: string,
) =>
  useApiQuery<Page<Review>>(
    ["private", "appointments", "consultant", page, status, date],
    root + "consultant/",
    true,
    { page, status: status || undefined, date: date || undefined },
  );
export const useReview = (kind: "consultant" | "admin/payments", id: string) =>
  useApiQuery<Review>(
    ["private", "appointments", kind, id],
    root + kind + "/" + id + "/",
    Boolean(id),
  );
const consultant = (id: string, endpoint: string, data?: unknown) =>
  post<Review>(root + "consultant/" + id + "/" + endpoint + "/", data);
export const useApproveAppointment = (id: string) =>
  useAction(() => consultant(id, "approve"), "درخواست تأیید شد.", keys);
export const useRejectAppointment = (id: string) =>
  useAction(
    (reason: string) => consultant(id, "reject", { rejection_reason: reason }),
    "درخواست رد شد.",
    keys,
  );
export const useCompleteAppointment = (id: string) =>
  useAction(() => consultant(id, "complete"), "پایان جلسه ثبت شد.", keys);
export const usePayments = (page: number) =>
  useApiQuery<Page<Review>>(
    ["private", "appointments", "payments", page],
    root + "admin/payments/",
    true,
    { page },
  );
const payment = (id: string, endpoint: string, data?: unknown) =>
  post<Review>(root + "admin/payments/" + id + "/" + endpoint + "/", data);
export const useApprovePayment = (id: string) =>
  useAction(() => payment(id, "approve"), "پرداخت تأیید و رزرو قطعی شد.", keys);
export const useRejectPayment = (id: string) =>
  useAction(
    (note: string) => payment(id, "reject", { payment_note: note }),
    "رد پرداخت ثبت شد.",
    keys,
  );
