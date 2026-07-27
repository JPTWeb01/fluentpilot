import { configureApiClient } from "@fluentpilot/shared";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import { App } from "./App";
import { useAuthStore } from "./stores/auth-store";
import "./index.css";

configureApiClient({
  baseUrl: import.meta.env.VITE_API_URL,
  getAccessToken: () => useAuthStore.getState().accessToken,
  getRefreshToken: () => useAuthStore.getState().refreshToken,
  onSession: (accessToken, refreshToken) => useAuthStore.getState().setSession(accessToken, refreshToken),
  onSessionCleared: () => useAuthStore.getState().clearSession(),
});

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
