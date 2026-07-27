import { useMutation, useQuery } from "@tanstack/react-query";

import { apiRequest } from "../../api/client";

import type { UsageResponse, VoiceTurnRequest, VoiceTurnResponse } from "./types";

export function useVoiceTurn() {
  return useMutation({
    mutationFn: (payload: VoiceTurnRequest) =>
      apiRequest<VoiceTurnResponse>("/voice/turns", { method: "POST", body: payload }),
  });
}

export function useVoiceUsage() {
  return useQuery({
    queryKey: ["voice", "usage"],
    queryFn: () => apiRequest<UsageResponse>("/voice/usage"),
  });
}
