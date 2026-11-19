import { useRef, useState } from "react";
import { CalendarDays, Copy, Download, UserRound } from "lucide-react";
import { Link, useLocation, useNavigate, useParams } from "react-router-dom";
import { toast } from "sonner";
import {
  Breadcrumb,
  Button,
  DatePicker,
  EmptyState,
  ErrorState,
  FileUploader,
  Modal,
  PageHeading,
  Pagination,
  QueryState,
  Select,
  StatusBadge,
} from "../../components/ui";
import { assets, code } from "../../lib/api";
import { date, latinDigits, number, toman } from "../../lib/format";
import { appointmentStatus } from "../../lib/types";
import type { Appointment, AppointmentStatus, Review } from "../../lib/types";
import { useUser } from "../auth/auth";
import { useConsultant, useSlots } from "../public/catalog";
import {
  useAppointment,
  useAppointments,
  useApproveAppointment,
  useApprovePayment,
  useCancelAppointment,
  useCompleteAppointment,
  useConsultantAppointments,
  useCreateAppointment,
  useDownloadReceipt,
  useOwnerAppointments,
  usePayments,
  useRejectAppointment,
  useRejectPayment,
  useReview,
  useSubmitPaymentReceipt,
} from "./hooks";

export function ConsultantProfile() {
  const { slug = "" } = useParams();
  const person = useConsultant(slug);
  const slots = useSlots(person.data?.id);
  const user = useUser();
  const location = useLocation();
  const navigate = useNavigate();
  const booking = useCreateAppointment();
  const [selected, setSelected] = useState<number>();
  const [note, setNote] = useState("");
  const activeSelection = slots.data?.some((slot) => slot.id === selected)
    ? selected
    : undefined;
  return (
    <div className="container page">
      <Breadcrumb
        title={person.data?.full_name || "پروفایل مشاور"}
        parent={["مشاوران", "/consultants"]}
      />
      <QueryState query={person}>
        {person.data && (
          <div className="grid two detail-grid">
            <article className="panel">
              <div className="person">
                {person.data.avatar ? (
                  <img
                    src={assets(person.data.avatar)}
                    alt={person.data.full_name}
                  />
                ) : (
                  <span className="avatar">
                    <UserRound />
                  </span>
                )}
                <div>
                  <h1>{person.data.full_name}</h1>
                  <p>{person.data.title}</p>
                </div>
              </div>
              <p className="preline">{person.data.bio}</p>
              <p>{person.data.specialties.map((s) => s.name).join("، ")}</p>
              <div className="between">
                <span>{number(person.data.experience_years)} سال سابقه</span>
                <strong>{toman(person.data.consultation_fee)}</strong>
              </div>
            </article>
            <article className="panel">
              <h2>زمان‌های آزاد</h2>
              <QueryState query={slots}>
                {slots.data?.length ? (
                  <form
                    onSubmit={(e) => {
                      e.preventDefault();
                      if (!activeSelection) return;
                      if (!user.data?.user) {
                        navigate("/auth/login", {
                          state: { from: location.pathname + location.search },
                        });
                        return;
                      }
                      booking.mutate(
                        {
                          availability_id: activeSelection,
                          user_note: note.trim(),
                        },
                        {
                          onSuccess: (result) =>
                            navigate("/dashboard/appointments/" + result.id),
                          onError: (error) => {
                            if (code(error) === 400 || code(error) === 404)
                              void slots.refetch();
                          },
                        },
                      );
                    }}
                  >
                    <fieldset className="slot-list">
                      <legend className="sr-only">زمان جلسه</legend>
                      {slots.data.map((slot) => (
                        <label key={slot.id} className="slot">
                          <input
                            type="radio"
                            name="slot"
                            checked={selected === slot.id}
                            onChange={() => setSelected(slot.id)}
                          />
                          <CalendarDays size={18} />
                          {date(slot.start_at, true)}
                        </label>
                      ))}
                    </fieldset>
                    <label>
                      یادداشت برای مشاور (اختیاری)
                      <textarea
                        value={note}
                        onChange={(e) => setNote(e.target.value)}
                      />
                    </label>
                    <button
                      className="button primary full"
                      disabled={
                        !activeSelection || booking.isPending || user.isPending
                      }
                    >
                      {booking.isPending
                        ? "در حال ثبت…"
                        : user.data?.user
                          ? "ثبت درخواست رزرو"
                          : "ورود برای رزرو"}
                    </button>
                    {booking.error && <ErrorState error={booking.error} />}
                  </form>
                ) : (
                  <EmptyState title="زمان آزادی برای رزرو وجود ندارد." />
                )}
              </QueryState>
            </article>
          </div>
        )}
      </QueryState>
    </div>
  );
}
export function AppointmentList() {
  const list = useAppointments();
  const owner = useOwnerAppointments();
  const privateRecords = new Map(owner.data?.map((item) => [item.id, item]));
  return (
    <>
      <PageHeading title="رزروهای من" />
      <QueryState query={list}>
        {list.data?.length ? (
          <div className="stack">
            {list.data.map((item) => (
              <Link
                key={item.id}
                className="panel row-panel"
                to={String(item.id)}
              >
                <div>
                  <strong>{item.consultant_name}</strong>
                  <p>{date(item.start_at, true)}</p>
                  {privateRecords.has(item.id) && (
                    <small>
                      {toman(privateRecords.get(item.id)!.consultation_fee)}
                    </small>
                  )}
                </div>
                <StatusBadge status={item.status} label={item.status_display} />
              </Link>
            ))}
          </div>
        ) : (
          <EmptyState title="هنوز رزروی ثبت نشده است." />
        )}
      </QueryState>
      <Link className="button primary" to="/consultants?booking=1">
        رزرو مشاوره
      </Link>
    </>
  );
}
function ReceiptLink({ item }: { item: Appointment }) {
  const mutation = useDownloadReceipt(item.id);
  if (!item.payment_receipt_url) return null;
  return (
    <button
      type="button"
      className="button outline"
      disabled={mutation.isPending}
      onClick={() => mutation.mutate()}
    >
      <Download size={18} />
      {mutation.isPending ? "در حال دریافت…" : "دانلود امن رسید"}
    </button>
  );
}
export function PaymentCard({ item }: { item: Appointment }) {
  const [file, setFile] = useState<File | null>(null);
  const mutation = useSubmitPaymentReceipt(String(item.id));
  const allowed =
    item.status === "awaiting_payment" || item.status === "payment_rejected";
  return (
    <div className="panel stack">
      <h2>پرداخت مشاوره</h2>
      <div className="between">
        <span>تعرفه ثبت‌شده</span>
        <strong>{toman(item.consultation_fee)}</strong>
      </div>
      {item.payment_note && (
        <p role="status" className="warning">
          {item.payment_note}
        </p>
      )}
      {allowed && item.payment_card && (
        <>
          <p>
            مبلغ درج‌شده را به شماره کارت زیر واریز کنید. سپس رسید را برای بررسی
            بفرستید.
          </p>
          <div className="card-number">
            <bdi>{item.payment_card}</bdi>
            <button
              className="icon-button"
              type="button"
              aria-label="کپی شماره کارت"
              onClick={async () => {
                try {
                  await navigator.clipboard.writeText(item.payment_card!);
                  toast.success("شماره کارت کپی شد.");
                } catch {
                  toast.error(
                    "کپی خودکار انجام نشد. شماره را انتخاب و کپی کنید.",
                  );
                }
              }}
            >
              <Copy size={18} />
            </button>
          </div>
        </>
      )}
      {allowed && (
        <form
          onSubmit={(e) => {
            e.preventDefault();
            if (file) mutation.mutate(file, { onSuccess: () => setFile(null) });
          }}
        >
          <FileUploader
            label={
              item.status === "payment_rejected"
                ? "انتخاب رسید جایگزین"
                : "انتخاب تصویر یا فایل رسید"
            }
            file={file}
            onChange={setFile}
            onError={toast.error}
          />
          <Button full disabled={!file || mutation.isPending}>
            {mutation.isPending ? "در حال ارسال…" : "ارسال رسید پرداخت"}
          </Button>
          {mutation.error && <ErrorState error={mutation.error} />}
        </form>
      )}
      <ReceiptLink item={item} />
    </div>
  );
}
export function AppointmentDetail() {
  const { id = "" } = useParams();
  const detail = useAppointment(id);
  const summary = useAppointments();
  const cancel = useCancelAppointment(id);
  const metadata = summary.data?.find((item) => String(item.id) === id);
  const item = detail.data;
  return (
    <>
      <Breadcrumb
        title="جزئیات رزرو"
        parent={["رزروها", "/dashboard/appointments"]}
      />
      <PageHeading title={"رزرو " + number(id)} />
      <QueryState query={detail}>
        {item && (
          <div className="grid two detail-grid">
            <div className="panel stack">
              <StatusBadge status={item.status} />
              {metadata && (
                <>
                  <h2>{metadata.consultant_name}</h2>
                  <p>{metadata.consultant_title}</p>
                  <p>
                    {date(metadata.start_at, true)} <span>تا</span>{" "}
                    {date(metadata.end_at, true)}
                  </p>
                </>
              )}
              {summary.error && (
                <ErrorState error={summary.error} retry={summary.refetch} />
              )}
              {item.user_note && <p>{item.user_note}</p>}
              {item.rejection_reason && (
                <p className="warning">{item.rejection_reason}</p>
              )}
              {["pending", "confirmed"].includes(item.status) && (
                <button
                  className="button danger"
                  disabled={cancel.isPending}
                  onClick={() => {
                    if (window.confirm("رزرو لغو شود؟")) cancel.mutate();
                  }}
                >
                  {cancel.isPending ? "در حال لغو…" : "لغو رزرو"}
                </button>
              )}
            </div>
            <PaymentCard key={item.id} item={item} />
          </div>
        )}
      </QueryState>
    </>
  );
}
function ReviewList({ items, prefix }: { items: Review[]; prefix: string }) {
  return items.length ? (
    <div className="stack">
      {items.map((item) => (
        <Link key={item.id} className="panel row-panel" to={prefix + item.id}>
          <div>
            <strong>
              {item.applicant_name || "متقاضی رزرو " + number(item.id)}
            </strong>
            <p>
              {item.consultant_name} · {date(item.start_at, true)}
            </p>
            <small>{toman(item.consultation_fee)}</small>
          </div>
          <StatusBadge status={item.status} />
        </Link>
      ))}
    </div>
  ) : (
    <EmptyState />
  );
}
export function ConsultantDashboard() {
  const [page, setPage] = useState(1);
  const [status, setStatus] = useState<AppointmentStatus | "">("");
  const [day, setDay] = useState("");
  const list = useConsultantAppointments(page, status, day);
  return (
    <>
      <PageHeading
        title="پنل مشاور"
        intro="درخواست‌ها و برنامه جلسات خود را بررسی کنید."
      />
      {code(list.error) !== 403 && (
        <div className="toolbar">
          <Select
            label="وضعیت"
            value={status}
            onChange={(e) => {
              setStatus(e.target.value as AppointmentStatus | "");
              setPage(1);
            }}
          >
            <option value="">همه وضعیت‌ها</option>
            {Object.entries(appointmentStatus).map(([key, label]) => (
              <option key={key} value={key}>
                {label}
              </option>
            ))}
          </Select>
          <DatePicker
            label="تاریخ جلسه (میلادی)"
            value={day}
            onChange={(e) => {
              setDay(e.target.value);
              setPage(1);
            }}
          />
        </div>
      )}
      <QueryState query={list}>
        {list.data && (
          <>
            <ReviewList
              items={list.data.results}
              prefix="/consultant/dashboard/"
            />
            <Pagination
              page={page}
              next={!!list.data.next}
              previous={!!list.data.previous}
              onChange={setPage}
            />
          </>
        )}
      </QueryState>
    </>
  );
}
export function AdminPayments() {
  const [page, setPage] = useState(1);
  const [id, setId] = useState("");
  const list = usePayments(page);
  const navigate = useNavigate();
  return (
    <>
      <PageHeading
        title="بررسی پرداخت‌ها"
        intro="رسیدهای در انتظار بررسی را مشاهده کنید."
      />
      <QueryState query={list}>
        {list.data && (
          <>
            <ReviewList items={list.data.results} prefix="/admin/payments/" />
            <Pagination
              page={page}
              next={!!list.data.next}
              previous={!!list.data.previous}
              onChange={setPage}
            />
            <form
              className="panel toolbar"
              onSubmit={(e) => {
                e.preventDefault();
                if (/^[1-9]\d*$/.test(id)) navigate("/admin/payments/" + id);
              }}
            >
              <label>
                شناسهٔ رزرو برای مشاهده پرداخت پیشین
                <input
                  inputMode="numeric"
                  pattern="[1-9][0-9]*"
                  value={id}
                  onChange={(e) => setId(latinDigits(e.target.value))}
                  required
                />
              </label>
              <button className="button outline">مشاهده پرداخت</button>
            </form>
          </>
        )}
      </QueryState>
    </>
  );
}
function ReviewActions({
  item,
  kind,
}: {
  item: Review;
  kind: "consultant" | "admin/payments";
}) {
  const id = String(item.id);
  const isConsultant = kind === "consultant";
  const consultantApprove = useApproveAppointment(id);
  const consultantReject = useRejectAppointment(id);
  const sessionComplete = useCompleteAppointment(id);
  const paymentApprove = useApprovePayment(id);
  const paymentReject = useRejectPayment(id);
  const approve = isConsultant ? consultantApprove : paymentApprove;
  const reject = isConsultant ? consultantReject : paymentReject;
  const dialog = useRef<HTMLDialogElement>(null);
  const [reason, setReason] = useState("");
  const pending =
    approve.isPending || reject.isPending || sessionComplete.isPending;
  const reviewable = isConsultant
    ? item.status === "pending"
    : item.status === "payment_submitted";
  return (
    <div className="stack">
      <ReceiptLink item={item} />
      {reviewable && (
        <div className="row">
          <button
            className="button primary"
            disabled={pending}
            onClick={() => {
              if (
                window.confirm(
                  isConsultant
                    ? "درخواست رزرو تأیید شود؟"
                    : "پرداخت تأیید و رزرو قطعی شود؟",
                )
              )
                approve.mutate();
            }}
          >
            {approve.isPending
              ? "در حال تأیید…"
              : isConsultant
                ? "تأیید درخواست"
                : "تأیید پرداخت"}
          </button>
          <button
            className="button danger"
            disabled={pending}
            onClick={() => dialog.current?.showModal()}
          >
            {isConsultant ? "رد درخواست" : "رد پرداخت"}
          </button>
        </div>
      )}
      {isConsultant &&
        item.status === "confirmed" &&
        new Date(item.end_at).getTime() <= Date.now() && (
          <button
            className="button primary"
            disabled={pending}
            onClick={() => sessionComplete.mutate()}
          >
            {sessionComplete.isPending ? "در حال ثبت…" : "ثبت پایان جلسه"}
          </button>
        )}
      <Modal dialog={dialog} title="دلیل رد">
        <form
          className="stack"
          onSubmit={(e) => {
            e.preventDefault();
            if (reason.trim())
              reject.mutate(reason.trim(), {
                onSuccess: () => {
                  dialog.current?.close();
                  setReason("");
                },
              });
          }}
        >
          <label>
            دلیل قابل مشاهده برای متقاضی
            <textarea
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              maxLength={4000}
              required
            />
          </label>
          {reject.error && <ErrorState error={reject.error} />}
          <div className="row">
            <button
              className="button danger"
              disabled={!reason.trim() || pending}
            >
              {reject.isPending ? "در حال ثبت…" : "ثبت دلیل و رد"}
            </button>
            <button
              className="button outline"
              type="button"
              onClick={() => dialog.current?.close()}
            >
              بازگشت
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
export function ReviewDetail({
  kind,
}: {
  kind: "consultant" | "admin/payments";
}) {
  const { id = "" } = useParams();
  const detail = useReview(kind, id);
  const item = detail.data;
  const admin = kind === "admin/payments";
  const parent = admin
    ? ["بررسی پرداخت‌ها", "/admin/payments"]
    : ["پنل مشاور", "/consultant/dashboard"];
  return (
    <>
      <Breadcrumb
        title={admin ? "جزئیات پرداخت" : "جزئیات درخواست"}
        parent={[parent[0], parent[1]]}
      />
      <PageHeading
        title={(admin ? "پرداخت رزرو " : "درخواست رزرو ") + number(id)}
      />
      <QueryState query={detail}>
        {item && (
          <article className="panel stack">
            <StatusBadge status={item.status} />
            <dl className="data-list">
              <div>
                <dt>متقاضی</dt>
                <dd>{item.applicant_name || "—"}</dd>
              </div>
              <div>
                <dt>مشاور</dt>
                <dd>{item.consultant_name}</dd>
              </div>
              <div>
                <dt>زمان جلسه</dt>
                <dd>{date(item.start_at, true)}</dd>
              </div>
              <div>
                <dt>مبلغ</dt>
                <dd>{toman(item.consultation_fee)}</dd>
              </div>
              {admin && (
                <>
                  <div>
                    <dt>ارسال رسید</dt>
                    <dd>{date(item.payment_submitted_at, true)}</dd>
                  </div>
                  <div>
                    <dt>آخرین بررسی</dt>
                    <dd>{date(item.payment_reviewed_at, true)}</dd>
                  </div>
                </>
              )}
            </dl>
            {item.user_note && <p>{item.user_note}</p>}
            {(item.rejection_reason || item.payment_note) && (
              <p className="warning">
                {item.rejection_reason || item.payment_note}
              </p>
            )}
            <ReviewActions key={item.id} item={item} kind={kind} />
          </article>
        )}
      </QueryState>
    </>
  );
}
