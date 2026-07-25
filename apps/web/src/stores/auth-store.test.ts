import { beforeEach, describe, expect, it } from "vitest";

import { useAuthStore } from "./auth-store";

describe("useAuthStore", () => {
  beforeEach(() => {
    useAuthStore.setState({ accessToken: null, refreshToken: null });
  });

  it("starts with no session", () => {
    const state = useAuthStore.getState();
    expect(state.accessToken).toBeNull();
    expect(state.refreshToken).toBeNull();
  });

  it("setSession stores both tokens", () => {
    useAuthStore.getState().setSession("access-1", "refresh-1");

    const state = useAuthStore.getState();
    expect(state.accessToken).toBe("access-1");
    expect(state.refreshToken).toBe("refresh-1");
  });

  it("setAccessToken updates only the access token", () => {
    useAuthStore.getState().setSession("access-1", "refresh-1");
    useAuthStore.getState().setAccessToken("access-2");

    const state = useAuthStore.getState();
    expect(state.accessToken).toBe("access-2");
    expect(state.refreshToken).toBe("refresh-1");
  });

  it("clearSession resets both tokens", () => {
    useAuthStore.getState().setSession("access-1", "refresh-1");
    useAuthStore.getState().clearSession();

    const state = useAuthStore.getState();
    expect(state.accessToken).toBeNull();
    expect(state.refreshToken).toBeNull();
  });
});
