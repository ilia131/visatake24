import { useId } from "react";
import type { ReactNode } from "react";
import {
  AlertCircle,
  ChevronRight,
  FolderOpen,
  Search,
  UploadCloud,
} from "lucide-react";
import { Link } from "react-router-dom";
import { message } from "../lib/api";
import { fileError, number } from "../lib/format";
import { appointmentStatus } from "../lib/types";

export function LoadingSkeleton() {
  return (
    <div className="skeletons" aria-busy="true" aria-label="در حال بارگذاری">
      {[1, 2, 3].map((n) => (
        <div key={n} className="skeleton" />
      ))}
    </div>
  );
}
export function EmptyState({
  title = "موردی برای نمایش وجود ندارد",
}: {
  title?: string;
}) {
  return (
    <div className="state">
      <FolderOpen size={31} />
      <p>{title}</p>
    </div>
  );
}
export function ErrorState({
  error,
  retry,
}: {
  error: unknown;
  retry?: () => void;
}) {
  return (
    <div className="state" role="alert">
      <AlertCircle size={30} />
      <p>{message(error)}</p>
      {retry && (
        <button
          type="button"
          className="button outline"
          onClick={() => retry()}
        >
          تلاش دوباره
        </button>
      )}
    </div>
  );
}
export function QueryState({
  query,
  children,
}: {
  query: { isPending: boolean; error: unknown; refetch: () => unknown };
  children: ReactNode;
}) {
  if (query.isPending) return <LoadingSkeleton />;
  if (query.error)
    return <ErrorState error={query.error} retry={query.refetch} />;
  return children;
}
export function SearchBox({
  value,
  onChange,
  placeholder,
}: {
  value: string;
  onChange: (value: string) => void;
  placeholder: string;
}) {
  return (
    <label className="search-box">
      <Search size={19} />
      <input
        type="search"
        aria-label={placeholder}
        placeholder={placeholder}
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />
    </label>
  );
}
export function Breadcrumb({
  title,
  parent,
}: {
  title: string;
  parent?: [string, string];
}) {
  return (
    <nav className="breadcrumbs" aria-label="مسیر صفحه">
      <Link to="/">خانه</Link>
      <ChevronRight size={14} />
      {parent && (
        <>
          <Link to={parent[1]}>{parent[0]}</Link>
          <ChevronRight size={14} />
        </>
      )}
      <span>{title}</span>
    </nav>
  );
}
export function StatusBadge({
  status,
  label,
}: {
  status: string;
  label?: string;
}) {
  return (
    <span className={`status status-${status}`}>
      {label ||
        appointmentStatus[status as keyof typeof appointmentStatus] ||
        status}
    </span>
  );
}
export function Pagination({
  page,
  next,
  previous,
  onChange,
}: {
  page: number;
  next: boolean;
  previous: boolean;
  onChange: (page: number) => void;
}) {
  return (
    <nav className="pagination" aria-label="صفحه‌بندی">
      <button
        className="button outline"
        disabled={!previous}
        onClick={() => onChange(page - 1)}
      >
        صفحه قبل
      </button>
      <span>صفحه {number(page)}</span>
      <button
        className="button outline"
        disabled={!next}
        onClick={() => onChange(page + 1)}
      >
        صفحه بعد
      </button>
    </nav>
  );
}
export function FileUploader({
  label,
  file,
  onChange,
  onError,
}: {
  label: string;
  file: File | null;
  onChange: (file: File | null) => void;
  onError: (error: string) => void;
}) {
  const id = useId();
  return (
    <div className="file-zone">
      <UploadCloud size={26} />
      <label htmlFor={id}>{file?.name || label}</label>
      <input
        id={id}
        key={file?.name ?? "empty"}
        type="file"
        accept=".jpg,.jpeg,.png,.pdf"
        onChange={(event) => {
          const selected = event.target.files?.[0];
          if (!selected) return;
          const invalid = fileError(selected);
          if (invalid) {
            event.target.value = "";
            onError(invalid);
            return;
          }
          onChange(selected);
        }}
      />
      <small>JPG، PNG یا PDF، حداکثر ۵ مگابایت</small>
      {file && (
        <button
          type="button"
          className="text-button"
          onClick={() => onChange(null)}
        >
          حذف فایل
        </button>
      )}
    </div>
  );
}
export function Stepper({
  labels,
  current,
}: {
  labels: string[];
  current: number;
}) {
  return (
    <ol className="stepper">
      {labels.map((label, index) => (
        <li
          key={label}
          aria-current={current === index ? "step" : undefined}
          data-done={index < current}
        >
          <span>{number(index + 1)}</span>
          {label}
        </li>
      ))}
    </ol>
  );
}
export function PageHeading({
  title,
  intro,
}: {
  title: string;
  intro?: string;
}) {
  return (
    <header className="page-heading">
      <h1>{title}</h1>
      {intro && <p>{intro}</p>}
    </header>
  );
}

export function Button({
  variant = "primary",
  full = false,
  className = "",
  ...props
}: React.ComponentProps<"button"> & {
  variant?: "primary" | "outline" | "danger" | "white";
  full?: boolean;
}) {
  return (
    <button
      className={`button ${variant}${full ? " full" : ""} ${className}`}
      {...props}
    />
  );
}

export function Input({
  label,
  ...props
}: React.ComponentProps<"input"> & { label: string }) {
  return (
    <label>
      {label}
      <input {...props} />
    </label>
  );
}

export function Select({
  label,
  children,
  ...props
}: React.ComponentProps<"select"> & { label: string }) {
  return (
    <label>
      {label}
      <select {...props}>{children}</select>
    </label>
  );
}

export function DatePicker(
  props: Omit<React.ComponentProps<typeof Input>, "type">,
) {
  return <Input {...props} type="date" />;
}

export function Modal({
  dialog,
  title,
  children,
}: {
  dialog: React.Ref<HTMLDialogElement>;
  title: string;
  children: ReactNode;
}) {
  const titleId = useId();
  return (
    <dialog ref={dialog} aria-labelledby={titleId}>
      <h2 id={titleId}>{title}</h2>
      {children}
    </dialog>
  );
}
