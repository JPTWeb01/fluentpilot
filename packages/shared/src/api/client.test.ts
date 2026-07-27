import { beforeEach, describe, expect, it, vi } from "vitest";

import { apiRequest, ApiError, configureApiClient } from "./client";

interface MockResponseInit {
  ok?: boolean;
  status?: number;
  statusText?: string;
  body?: unknown;
}

function mockResponse({ ok = true, status = 200, statusText = "OK", body = {} }: MockResponseInit = {}) {
  return { ok, status, statusText, json: vi.fn().mockResolvedValue(body) } as unknown as Response;
}

describe("apiRequest", () => {
  const fetchMock = vi.fn();
  let accessToken: string | null = null;
  let refreshToken: string | null = null;

  beforeEach(() => {
    fetchMock.mockReset();
    vi.stubGlobal("fetch", fetchMock);
    accessToken = null;
    refreshToken = null;
    configureApiClient({
      baseUrl: "",
      getAccessToken: () => accessToken,
      getRefreshToken: () => refreshToken,
      onSession: (newAccessToken, newRefreshToken) => {
        accessToken = newAccessToken;
        refreshToken = newRefreshToken;
      },
      onSessionCleared: () => {
        accessToken = null;
        refreshToken = null;
      },
    });
  });

  it("attaches the Authorization header when a token is present", async () => {
    accessToken = "token-1";
    refreshToken = "refresh-1";
    fetchMock.mockResolvedValueOnce(mockResponse({ body: { foo: "bar" } }));

    const result = await apiRequest<{ foo: string }>("/thing");

    expect(result).toEqual({ foo: "bar" });
    const [, init] = fetchMock.mock.calls[0];
    expect((init.headers as Record<string, string>).Authorization).toBe("Bearer token-1");
  });

  it("refreshes an expired token and retries the request once", async () => {
    accessToken = "expired-token";
    refreshToken = "refresh-1";
    fetchMock
      .mockResolvedValueOnce(mockResponse({ ok: false, status: 401, statusText: "Unauthorized" }))
      .mockResolvedValueOnce(
        mockResponse({ body: { access_token: "new-token", refresh_token: "new-refresh" } }),
      )
      .mockResolvedValueOnce(mockResponse({ body: { foo: "bar" } }));

    const result = await apiRequest<{ foo: string }>("/thing");

    expect(result).toEqual({ foo: "bar" });
    expect(fetchMock).toHaveBeenCalledTimes(3);

    const [refreshUrl] = fetchMock.mock.calls[1];
    expect(refreshUrl).toContain("/auth/refresh");

    const [, retryInit] = fetchMock.mock.calls[2];
    expect((retryInit.headers as Record<string, string>).Authorization).toBe("Bearer new-token");

    expect(accessToken).toBe("new-token");
    expect(refreshToken).toBe("new-refresh");
  });

  it("clears the session and throws when the refresh itself fails", async () => {
    accessToken = "expired-token";
    refreshToken = "refresh-1";
    fetchMock
      .mockResolvedValueOnce(
        mockResponse({ ok: false, status: 401, statusText: "Unauthorized", body: { detail: "Unauthorized" } }),
      )
      .mockResolvedValueOnce(mockResponse({ ok: false, status: 400, statusText: "Bad Request" }));

    await expect(apiRequest("/thing")).rejects.toMatchObject({ status: 401, message: "Unauthorized" });

    expect(accessToken).toBeNull();
    expect(refreshToken).toBeNull();
  });

  it("throws an ApiError with the parsed detail message on failure", async () => {
    fetchMock.mockResolvedValueOnce(
      mockResponse({ ok: false, status: 400, statusText: "Bad Request", body: { detail: "Invalid credentials" } }),
    );

    await expect(
      apiRequest("/auth/login", { method: "POST", body: { email: "a@b.com" }, auth: false }),
    ).rejects.toThrow("Invalid credentials");
  });

  it("returns undefined for a 204 response without parsing a body", async () => {
    accessToken = "token-1";
    refreshToken = "refresh-1";
    const json = vi.fn();
    fetchMock.mockResolvedValueOnce({ ok: true, status: 204, statusText: "No Content", json });

    const result = await apiRequest("/auth/logout", { method: "POST" });

    expect(result).toBeUndefined();
    expect(json).not.toHaveBeenCalled();
  });
});

describe("ApiError", () => {
  it("carries the HTTP status and message", () => {
    const error = new ApiError(404, "Not found");
    expect(error.status).toBe(404);
    expect(error.message).toBe("Not found");
    expect(error.name).toBe("ApiError");
  });
});
