import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { apiRequest, getApiClientConfig } from "../../api/client";

import type { LoginRequest, RegisterRequest, TokenResponse, UserResponse } from "./types";

async function fetchMe(): Promise<UserResponse> {
  return apiRequest<UserResponse>("/auth/me");
}

export function useMe(enabled: boolean) {
  return useQuery({ queryKey: ["auth", "me"], queryFn: fetchMe, enabled });
}

function useStartSession() {
  const queryClient = useQueryClient();

  return async (tokens: TokenResponse) => {
    getApiClientConfig().onSession(tokens.access_token, tokens.refresh_token);
    await queryClient.invalidateQueries({ queryKey: ["auth", "me"] });
  };
}

export function useLogin() {
  const startSession = useStartSession();

  return useMutation({
    mutationFn: (payload: LoginRequest) =>
      apiRequest<TokenResponse>("/auth/login", { method: "POST", body: payload, auth: false }),
    onSuccess: startSession,
  });
}

export function useRegister() {
  const startSession = useStartSession();

  return useMutation({
    mutationFn: (payload: RegisterRequest) =>
      apiRequest<TokenResponse>("/auth/register", { method: "POST", body: payload, auth: false }),
    onSuccess: startSession,
  });
}

export function useLogout() {
  const queryClient = useQueryClient();

  return () => {
    getApiClientConfig().onSessionCleared();
    queryClient.clear();
  };
}
