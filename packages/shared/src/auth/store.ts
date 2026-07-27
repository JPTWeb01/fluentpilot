import { create } from "zustand";
import { createJSONStorage, persist, type StateStorage } from "zustand/middleware";

export interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  setSession: (accessToken: string, refreshToken: string) => void;
  setAccessToken: (accessToken: string) => void;
  clearSession: () => void;
}

export function createAuthStore(storage: StateStorage) {
  return create<AuthState>()(
    persist(
      (set) => ({
        accessToken: null,
        refreshToken: null,
        setSession: (accessToken, refreshToken) => set({ accessToken, refreshToken }),
        setAccessToken: (accessToken) => set({ accessToken }),
        clearSession: () => set({ accessToken: null, refreshToken: null }),
      }),
      { name: "fluentpilot-auth", storage: createJSONStorage(() => storage) },
    ),
  );
}
