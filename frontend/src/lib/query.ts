import { useMutation, useQuery } from "@tanstack/react-query";
import { toast } from "sonner";
import { get, message, queryClient } from "./api";

export function useApiQuery<T>(
  key: readonly unknown[],
  url: string,
  enabled = true,
  params?: Record<string, unknown>,
) {
  return useQuery({
    queryKey: key,
    queryFn: ({ signal }) => get<T>(url, signal, params),
    enabled,
  });
}
export function useAction<T, V>(
  action: (value: V) => Promise<T>,
  success?: string,
  keys: readonly unknown[][] = [],
) {
  return useMutation({
    mutationFn: action,
    onSuccess: async () => {
      if (success) toast.success(success);
      await Promise.all(
        keys.map((queryKey) => queryClient.invalidateQueries({ queryKey })),
      );
    },
    onError: (error) => toast.error(message(error)),
  });
}
