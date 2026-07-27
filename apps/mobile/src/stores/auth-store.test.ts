import { renderHook, waitFor } from "@testing-library/react-native";

import { useAuthHydrated } from "./auth-store";

jest.mock("expo-secure-store", () => ({
  getItemAsync: jest.fn(() => Promise.resolve(null)),
  setItemAsync: jest.fn(() => Promise.resolve()),
  deleteItemAsync: jest.fn(() => Promise.resolve()),
}));

describe("useAuthHydrated", () => {
  it("becomes true once SecureStore-backed persistence finishes hydrating", async () => {
    const { result } = renderHook(() => useAuthHydrated());

    await waitFor(() => {
      expect(result.current).toBe(true);
    });
  });
});
