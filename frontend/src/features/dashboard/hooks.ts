import { api, paths } from "../../lib/api";
import { useAction, useApiQuery } from "../../lib/query";
import type { Overview, Profile } from "../../lib/types";
export const useDashboardOverview = () =>
  useApiQuery<Overview>(["private", "overview"], paths.dashboard + "overview/");
export const useProfile = () =>
  useApiQuery<Profile>(["private", "profile"], paths.dashboard + "profile/");
export const useSaveProfile = () =>
  useAction(
    async (profile: Omit<Profile, "phone_number">) =>
      (await api.patch<Profile>(paths.dashboard + "profile/", profile)).data,
    "اطلاعات حساب ذخیره شد.",
    [
      ["private", "profile"],
      ["private", "user"],
    ],
  );
