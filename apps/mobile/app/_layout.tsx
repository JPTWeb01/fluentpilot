import { configureApiClient } from "@fluentpilot/shared";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Stack } from "expo-router";
import { useState } from "react";
import { SafeAreaProvider } from "react-native-safe-area-context";

import { useAuthStore } from "@/stores/auth-store";

import "../global.css";

configureApiClient({
  baseUrl: process.env.EXPO_PUBLIC_API_URL,
  getAccessToken: () => useAuthStore.getState().accessToken,
  getRefreshToken: () => useAuthStore.getState().refreshToken,
  onSession: (accessToken, refreshToken) => useAuthStore.getState().setSession(accessToken, refreshToken),
  onSessionCleared: () => useAuthStore.getState().clearSession(),
});

export default function RootLayout() {
  const [queryClient] = useState(() => new QueryClient());

  return (
    <SafeAreaProvider>
      <QueryClientProvider client={queryClient}>
        <Stack screenOptions={{ headerShown: false }} />
      </QueryClientProvider>
    </SafeAreaProvider>
  );
}
