export type Country = {
  id: number;
  name: string;
  name_en: string;
  slug: string;
  flag: string;
  description: string;
};
export type Consultant = {
  id: number;
  full_name: string;
  slug: string;
  title: string;
  bio: string;
  avatar: string | null;
  specialties: {
    id: number;
    name: string;
    slug: string;
    description: string;
  }[];
  experience_years: number;
  consultation_fee: string;
  is_verified: boolean;
};
export type Slot = {
  id: number;
  consultant: number;
  consultant_name: string;
  consultant_slug: string;
  start_at: string;
  end_at: string;
  status: string;
};
export const appointmentStatus = {
  pending: "در انتظار تأیید مشاور",
  awaiting_payment: "در انتظار پرداخت",
  payment_submitted: "در انتظار بررسی رسید",
  confirmed: "رزرو قطعی",
  payment_rejected: "پرداخت رد شده",
  rejected: "رد شده توسط مشاور",
  cancelled: "لغو شده",
  completed: "جلسه انجام شده",
} as const;
export type AppointmentStatus = keyof typeof appointmentStatus;
export type Appointment = {
  id: number;
  availability: number;
  status: AppointmentStatus;
  user_note: string;
  consultation_fee: string;
  rejection_reason: string;
  payment_card: string | null;
  payment_receipt_url: string | null;
  payment_note: string;
  payment_submitted_at: string | null;
  payment_reviewed_at: string | null;
  consultant_approved_at: string | null;
  confirmed_at: string | null;
  created_at: string;
  updated_at: string;
};
export type DashboardAppointment = {
  id: number;
  consultant_name: string;
  consultant_title: string;
  start_at: string;
  end_at: string;
  status: AppointmentStatus;
  status_display: string;
};
export type Review = Appointment & {
  applicant_name: string;
  consultant_name: string;
  start_at: string;
  end_at: string;
  payment_reviewed_by: number | null;
};
export type Page<T> = {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
};
export type User = {
  id: number;
  phone_number: string;
  role: "customer" | "agent" | "manager";
  first_name: string;
  last_name: string;
  is_phone_verified: boolean;
};
export type Profile = {
  phone_number: string;
  first_name: string;
  last_name: string;
  email?: string | null;
};
export type Overview = {
  total_applications: number;
  active_applications: number;
  total_appointments: number;
  upcoming_appointments: number;
  status_counts: Record<string, number>;
};
export type VisaInput = {
  country: number;
  visa_type: string;
  travel_date: string;
  return_date: string | null;
  purpose: string;
  additional_notes: string;
};
export type VisaCreated = {
  tracking_code: string;
  country: Country;
  visa_type: string;
  status: string;
};
export type Application = {
  tracking_code: string;
  country_name: string;
  visa_type: string;
  travel_date: string;
  return_date: string | null;
  status: string;
  status_display: string;
  created_at: string;
  purpose?: string;
  additional_notes?: string;
  consultant?: { full_name: string; slug: string; title: string } | null;
};
export type VisaHistory = {
  previous_status_display: string;
  new_status_display: string;
  created_at: string;
};
export type VisaDocument = {
  id: number;
  tracking_code: string;
  document_type_display: string;
  status_display: string;
  uploaded_at: string;
};
