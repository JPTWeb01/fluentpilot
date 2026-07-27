import { useMutation } from "@tanstack/react-query";

import { apiRequest } from "../../api/client";

import type { GrammarCheckRequest, GrammarCheckResponse } from "./types";

export function useGrammarCheck() {
  return useMutation({
    mutationFn: (payload: GrammarCheckRequest) =>
      apiRequest<GrammarCheckResponse>("/grammar/check", { method: "POST", body: payload }),
  });
}
