import { useMutation } from "@tanstack/react-query";

import { apiRequest } from "@/lib/api-client";

import type { PronunciationCheckRequest, PronunciationCheckResponse } from "./types";

export function usePronunciationCheck() {
  return useMutation({
    mutationFn: (payload: PronunciationCheckRequest) =>
      apiRequest<PronunciationCheckResponse>("/pronunciation/check", {
        method: "POST",
        body: payload,
      }),
  });
}
