import { download, paths, post } from "../../lib/api";
import { useAction, useApiQuery } from "../../lib/query";
import type {
  Application,
  VisaCreated,
  VisaDocument,
  VisaHistory,
  VisaInput,
} from "../../lib/types";

const applications = paths.dashboard + "applications/";
const visaApplications = paths.visas + "applications/";
export const useApplications = () =>
  useApiQuery<Application[]>(["private", "applications"], applications);
export const useApplication = (tracking: string) =>
  useApiQuery<Application>(
    ["private", "applications", tracking],
    applications + encodeURIComponent(tracking) + "/",
  );
export const useHistory = (tracking: string) =>
  useApiQuery<VisaHistory[]>(
    ["private", "applications", tracking, "history"],
    applications + encodeURIComponent(tracking) + "/history/",
  );
export const useCreateApplication = () =>
  useAction(
    (body: VisaInput) => post<VisaCreated>(visaApplications, body),
    "پرونده ثبت شد.",
    [
      ["private", "applications"],
      ["private", "overview"],
    ],
  );
export const useDocuments = () =>
  useApiQuery<VisaDocument[]>(
    ["private", "documents"],
    paths.dashboard + "documents/",
  );
export const useDownloadDocument = () =>
  useAction((id: number) =>
    download(paths.visas + "documents/" + id + "/download/", "document"),
  );
export const documentTypes = {
  passport: "پاسپورت",
  photo: "عکس پرسنلی",
  bank_statement: "گردش حساب",
  employment: "گواهی اشتغال",
  travel_insurance: "بیمه مسافرتی",
  other: "سایر مدارک",
};
export type DocumentInput = { file: File; type: keyof typeof documentTypes };
export function useUploadDocument() {
  return useAction(
    ({ tracking, file, type }: DocumentInput & { tracking: string }) => {
      const form = new FormData();
      form.append("file", file);
      form.append("document_type", type);
      return post(
        visaApplications + encodeURIComponent(tracking) + "/documents/",
        form,
      );
    },
    "مدرک بارگذاری شد.",
    [["private", "documents"]],
  );
}
