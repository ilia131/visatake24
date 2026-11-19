import { useState } from "react";
import { useForm, useWatch } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Download, FileCheck } from "lucide-react";
import { Link, useParams, useSearchParams } from "react-router-dom";
import { toast } from "sonner";
import {
  Breadcrumb,
  EmptyState,
  ErrorState,
  FileUploader,
  PageHeading,
  QueryState,
  StatusBadge,
  Stepper,
} from "../../components/ui";
import { date } from "../../lib/format";
import type { Application, VisaDocument } from "../../lib/types";
import { useProfile } from "../dashboard/hooks";
import { useCountries, visaTypes } from "../public/catalog";
import {
  documentTypes,
  useApplication,
  useApplications,
  useCreateApplication,
  useDocuments,
  useDownloadDocument,
  useHistory,
  useUploadDocument,
} from "./hooks";
import type { DocumentInput } from "./hooks";

const labels = [
  "مقصد و ویزا",
  "اطلاعات حساب",
  "جزئیات سفر",
  "مدارک",
  "مرور و ثبت",
];
const schema = z
  .object({
    country: z.string().regex(/^[1-9]\d*$/, "کشور مقصد را انتخاب کنید."),
    visa_type: z
      .string()
      .trim()
      .min(1, "نوع ویزا الزامی است.")
      .max(100, "حداکثر ۱۰۰ نویسه وارد کنید."),
    travel_date: z.iso.date({ error: "تاریخ سفر را وارد کنید." }),
    return_date: z.union([z.literal(""), z.iso.date()]),
    purpose: z.string().trim().min(1, "هدف سفر را وارد کنید."),
    additional_notes: z.string(),
  })
  .refine(
    (value) => !value.return_date || value.return_date >= value.travel_date,
    {
      path: ["return_date"],
      message: "تاریخ بازگشت نمی‌تواند قبل از تاریخ سفر باشد.",
    },
  );

export function ApplicationWizard() {
  const [step, setStep] = useState(0);
  const [document, setDocument] = useState<DocumentInput | null>(null);
  const [tracking, setTracking] = useState("");
  const [done, setDone] = useState(false);
  const [params] = useSearchParams();
  const list = useCountries();
  const profile = useProfile();
  const create = useCreateApplication();
  const upload = useUploadDocument();
  const form = useForm({
    resolver: zodResolver(schema),
    defaultValues: {
      country: params.get("country") || "",
      visa_type: params.get("visa") || "",
      travel_date: "",
      return_date: "",
      purpose: "",
      additional_notes: "",
    },
  });
  const values = useWatch({ control: form.control });
  const busy = create.isPending || upload.isPending;
  const errors = form.formState.errors;
  const name = list.data?.find((c) => String(c.id) === values.country)?.name;
  async function next() {
    const valid =
      step === 0
        ? await form.trigger(["country", "visa_type"])
        : step === 2
          ? await form.trigger(["travel_date", "return_date", "purpose"])
          : true;
    if (valid) setStep(step + 1);
  }
  const submit = form.handleSubmit(async (values) => {
    if (busy || tracking) return;
    try {
      const result = await create.mutateAsync({
        ...values,
        country: Number(values.country),
        return_date: values.return_date || null,
      });
      setTracking(result.tracking_code);
      if (document)
        await upload.mutateAsync({
          ...document,
          tracking: result.tracking_code,
        });
      setDone(true);
    } catch {
      // Mutation hooks expose server feedback and preserve the form and tracking code.
    }
  });
  return (
    <div className="container page narrow">
      <Breadcrumb title="درخواست جدید" />
      <PageHeading
        title="ثبت درخواست ویزا"
        intro="اطلاعات سفر را در پنج مرحله تکمیل کنید."
      />
      {tracking ? (
        <section className="panel stack">
          <FileCheck size={30} />
          <h2>درخواست شما ثبت شد</h2>
          <p>
            کد پیگیری <bdi className="tracking">{tracking}</bdi>
          </p>
          {!done && document && (
            <>
              <p>
                {upload.isPending
                  ? "در حال بارگذاری مدرک…"
                  : "درخواست ثبت شده است. می‌توانید بارگذاری همین مدرک را دوباره امتحان کنید."}
              </p>
              {upload.error && <ErrorState error={upload.error} />}
              <button
                className="button outline"
                type="button"
                disabled={upload.isPending}
                onClick={() =>
                  upload.mutate(
                    { ...document, tracking },
                    { onSuccess: () => setDone(true) },
                  )
                }
              >
                تلاش دوباره برای بارگذاری
              </button>
            </>
          )}
          <Link
            className="button primary"
            to={"/dashboard/applications/" + tracking}
          >
            مشاهده پرونده
          </Link>
        </section>
      ) : (
        <>
          <Stepper labels={labels} current={step} />
          <form
            className="panel wizard stack"
            onSubmit={(e) => {
              if (step < 4) {
                e.preventDefault();
                void next();
              } else void submit(e);
            }}
          >
            <h2>{labels[step]}</h2>
            {step === 0 && (
              <>
                <QueryState query={list}>
                  <label>
                    کشور مقصد
                    <select {...form.register("country")}>
                      <option value="">انتخاب کنید</option>
                      {list.data?.map((c) => (
                        <option value={c.id} key={c.id}>
                          {c.name}
                        </option>
                      ))}
                    </select>
                  </label>
                </QueryState>
                <label>
                  نوع ویزا
                  <input
                    list="visa-types"
                    placeholder="مثلاً گردشگری"
                    {...form.register("visa_type")}
                  />
                  <datalist id="visa-types">
                    {visaTypes.map((t) => (
                      <option value={t} key={t} />
                    ))}
                  </datalist>
                </label>
                {[errors.country, errors.visa_type].map(
                  (error, index) =>
                    error && (
                      <p className="error" key={index}>
                        {error.message}
                      </p>
                    ),
                )}
              </>
            )}
            {step === 1 && (
              <QueryState query={profile}>
                {profile.data && (
                  <>
                    <p>این پرونده با حساب فعلی ثبت می‌شود.</p>
                    <dl className="data-list">
                      <div>
                        <dt>نام و نام خانوادگی</dt>
                        <dd>
                          {[profile.data.first_name, profile.data.last_name]
                            .filter(Boolean)
                            .join(" ") || "—"}
                        </dd>
                      </div>
                      <div>
                        <dt>شماره موبایل</dt>
                        <dd>
                          <bdi>{profile.data.phone_number}</bdi>
                        </dd>
                      </div>
                      <div>
                        <dt>ایمیل</dt>
                        <dd>{profile.data.email || "—"}</dd>
                      </div>
                    </dl>
                    <Link
                      className="green-link"
                      to="/dashboard/profile"
                      target="_blank"
                      rel="noreferrer"
                    >
                      ویرایش اطلاعات حساب در برگهٔ جدید
                    </Link>
                  </>
                )}
              </QueryState>
            )}
            {step === 2 && (
              <>
                <div className="grid two">
                  <label>
                    تاریخ سفر (میلادی)
                    <input type="date" {...form.register("travel_date")} />
                  </label>
                  <label>
                    تاریخ بازگشت (اختیاری)
                    <input type="date" {...form.register("return_date")} />
                  </label>
                </div>
                <label>
                  هدف سفر
                  <textarea {...form.register("purpose")} />
                </label>
                <label>
                  توضیحات تکمیلی
                  <textarea {...form.register("additional_notes")} />
                </label>
                {[errors.travel_date, errors.return_date, errors.purpose].map(
                  (error, index) =>
                    error && (
                      <p className="error" key={index}>
                        {error.message}
                      </p>
                    ),
                )}
              </>
            )}
            {step === 3 && (
              <DocumentFields value={document} onChange={setDocument} />
            )}
            {step === 4 && (
              <>
                <dl className="data-list">
                  <div>
                    <dt>مقصد</dt>
                    <dd>{name}</dd>
                  </div>
                  <div>
                    <dt>نوع ویزا</dt>
                    <dd>{values.visa_type}</dd>
                  </div>
                  <div>
                    <dt>زمان سفر و بازگشت</dt>
                    <dd>
                      {date(values.travel_date)} / {date(values.return_date)}
                    </dd>
                  </div>
                  <div>
                    <dt>هدف سفر</dt>
                    <dd>{values.purpose}</dd>
                  </div>
                  <div>
                    <dt>توضیحات تکمیلی</dt>
                    <dd>{values.additional_notes || "—"}</dd>
                  </div>
                  <div>
                    <dt>مدرک</dt>
                    <dd>{document?.file.name || "—"}</dd>
                  </div>
                </dl>
                {create.error && <ErrorState error={create.error} />}
              </>
            )}
            <div className="between">
              <button
                className="button outline"
                type="button"
                disabled={step === 0 || busy}
                onClick={() => setStep(step - 1)}
              >
                مرحله قبل
              </button>
              <button
                type="submit"
                className="button primary"
                disabled={
                  busy ||
                  (step === 0 && (!list.data || !name)) ||
                  (step === 1 && profile.isPending)
                }
              >
                {busy
                  ? "در حال ثبت…"
                  : step === 4
                    ? "تأیید و ثبت درخواست"
                    : "مرحله بعد"}
              </button>
            </div>
          </form>
        </>
      )}
    </div>
  );
}
function DocumentFields({
  value,
  onChange,
}: {
  value: DocumentInput | null;
  onChange: (value: DocumentInput | null) => void;
}) {
  const [type, setType] = useState<keyof typeof documentTypes>(
    value?.type || "passport",
  );
  return (
    <>
      <label>
        نوع مدرک
        <select
          value={type}
          onChange={(e) => {
            const next = e.target.value as keyof typeof documentTypes;
            setType(next);
            if (value) onChange({ ...value, type: next });
          }}
        >
          {Object.entries(documentTypes).map(([key, title]) => (
            <option value={key} key={key}>
              {title}
            </option>
          ))}
        </select>
      </label>
      <FileUploader
        label="انتخاب مدرک"
        file={value?.file || null}
        onChange={(file) => onChange(file ? { file, type } : null)}
        onError={toast.error}
      />
    </>
  );
}
export function ApplicationCard({ item }: { item: Application }) {
  return (
    <Link
      className="panel row-panel"
      to={"/dashboard/applications/" + item.tracking_code}
    >
      <div>
        <strong>
          {item.country_name} · {item.visa_type}
        </strong>
        <p>
          <bdi>{item.tracking_code}</bdi>
        </p>
        <small>{date(item.travel_date)}</small>
      </div>
      <StatusBadge status={item.status} label={item.status_display} />
    </Link>
  );
}
export function ApplicationList() {
  const list = useApplications();
  return (
    <>
      <PageHeading title="درخواست‌های من" />
      <QueryState query={list}>
        {list.data?.length ? (
          <div className="stack">
            {list.data.map((item) => (
              <ApplicationCard item={item} key={item.tracking_code} />
            ))}
          </div>
        ) : (
          <EmptyState title="هنوز پرونده‌ای ثبت نکرده‌اید." />
        )}
      </QueryState>
      <Link className="button primary" to="/applications/new">
        درخواست جدید
      </Link>
    </>
  );
}
function DocumentList({ items }: { items: VisaDocument[] }) {
  const download = useDownloadDocument();
  return items.length ? (
    <div className="stack">
      {items.map((item) => (
        <article className="panel row-panel" key={item.id}>
          <div>
            <strong>{item.document_type_display}</strong>
            <p>
              <bdi>{item.tracking_code}</bdi> · {item.status_display}
            </p>
            <small>{date(item.uploaded_at, true)}</small>
          </div>
          <button
            className="button outline"
            type="button"
            disabled={download.isPending}
            onClick={() => download.mutate(item.id)}
          >
            <Download size={16} />
            {download.isPending && download.variables === item.id
              ? "در حال دریافت…"
              : "دانلود امن"}
          </button>
        </article>
      ))}
    </div>
  ) : (
    <EmptyState title="مدرکی برای نمایش وجود ندارد." />
  );
}
export function Documents() {
  const docs = useDocuments();
  return (
    <>
      <PageHeading title="مدارک من" />
      <QueryState query={docs}>
        <DocumentList items={docs.data || []} />
      </QueryState>
    </>
  );
}
export function ApplicationDetail() {
  const { tracking = "" } = useParams();
  const detail = useApplication(tracking);
  const history = useHistory(tracking);
  const docs = useDocuments();
  const upload = useUploadDocument();
  const [file, setFile] = useState<DocumentInput | null>(null);
  return (
    <>
      <Breadcrumb
        title="جزئیات پرونده"
        parent={["درخواست‌ها", "/dashboard/applications"]}
      />
      <PageHeading title="جزئیات پرونده" />
      <QueryState query={detail}>
        {detail.data && (
          <>
            <article className="panel stack">
              <div className="between">
                <h2>
                  {detail.data.country_name} · {detail.data.visa_type}
                </h2>
                <StatusBadge
                  status={detail.data.status}
                  label={detail.data.status_display}
                />
              </div>
              <p>
                کد پیگیری <bdi>{tracking}</bdi>
              </p>
              <p>
                سفر {date(detail.data.travel_date)}، بازگشت{" "}
                {date(detail.data.return_date)}
              </p>
              <p>{detail.data.purpose}</p>
              {detail.data.consultant && (
                <Link
                  className="green-link"
                  to={"/consultants/" + detail.data.consultant.slug}
                >
                  {detail.data.consultant.full_name}
                </Link>
              )}
            </article>
            <section className="stack">
              <h2>تاریخچه پرونده</h2>
              <QueryState query={history}>
                {history.data?.length ? (
                  <ol className="panel timeline">
                    {history.data.map((event, index) => (
                      <li key={event.created_at + index}>
                        <strong>{event.new_status_display}</strong>
                        <span>{date(event.created_at, true)}</span>
                      </li>
                    ))}
                  </ol>
                ) : (
                  <EmptyState title="هنوز تغییری ثبت نشده است." />
                )}
              </QueryState>
            </section>
            <section className="stack">
              <h2>مدارک پرونده</h2>
              <QueryState query={docs}>
                <DocumentList
                  items={
                    docs.data?.filter(
                      (doc) => doc.tracking_code === tracking,
                    ) || []
                  }
                />
              </QueryState>
              <form
                className="panel stack"
                onSubmit={(e) => {
                  e.preventDefault();
                  if (file)
                    upload.mutate(
                      { ...file, tracking },
                      { onSuccess: () => setFile(null) },
                    );
                }}
              >
                <DocumentFields value={file} onChange={setFile} />
                <button
                  className="button primary"
                  disabled={!file || upload.isPending}
                >
                  {upload.isPending ? "در حال بارگذاری…" : "بارگذاری مدرک"}
                </button>
                {upload.error && <ErrorState error={upload.error} />}
              </form>
            </section>
          </>
        )}
      </QueryState>
    </>
  );
}
