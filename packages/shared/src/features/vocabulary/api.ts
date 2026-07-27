import { useMutation } from "@tanstack/react-query";

import { apiRequest } from "../../api/client";

import type { VocabularyCheckRequest, VocabularyCheckResponse } from "./types";

export function useVocabularyCheck() {
  return useMutation({
    mutationFn: (payload: VocabularyCheckRequest) =>
      apiRequest<VocabularyCheckResponse>("/vocabulary/check", { method: "POST", body: payload }),
  });
}
