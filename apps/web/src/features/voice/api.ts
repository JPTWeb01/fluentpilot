import { useMutation } from "@tanstack/react-query";

import { apiRequest } from "@/lib/api-client";

import type { VoiceTurnRequest, VoiceTurnResponse } from "./types";

export function useVoiceTurn() {
  return useMutation({
    mutationFn: (payload: VoiceTurnRequest) =>
      apiRequest<VoiceTurnResponse>("/voice/turns", { method: "POST", body: payload }),
  });
}
