import { createAuthStore } from "@fluentpilot/shared";
import * as SecureStore from "expo-secure-store";
import { useEffect, useState } from "react";

export const useAuthStore = createAuthStore({
  getItem: (key) => SecureStore.getItemAsync(key),
  setItem: (key, value) => SecureStore.setItemAsync(key, value),
  removeItem: (key) => SecureStore.deleteItemAsync(key),
});

/**
 * SecureStore-backed persistence rehydrates asynchronously, so route guards
 * must wait for this before trusting `accessToken === null` to mean "logged out"
 * rather than "not loaded yet".
 */
export function useAuthHydrated() {
  const [hydrated, setHydrated] = useState(() => useAuthStore.persist.hasHydrated());

  useEffect(() => {
    if (hydrated) return;
    return useAuthStore.persist.onFinishHydration(() => setHydrated(true));
  }, [hydrated]);

  return hydrated;
}
