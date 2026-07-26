import { useMutation } from "@tanstack/react-query";

import { apiRequest } from "@/lib/api-client";

import type { AccentCheckRequest, AccentCheckResponse } from "./types";

export function useAccentCheck() {
  return useMutation({
    mutationFn: (payload: AccentCheckRequest) =>
      apiRequest<AccentCheckResponse>("/accent/check", {
        method: "POST",
        body: payload,
      }),
  });
}
