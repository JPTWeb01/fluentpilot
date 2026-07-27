export interface ApiClientConfig {
  baseUrl: string;
  getAccessToken: () => string | null;
  getRefreshToken: () => string | null;
  onSession: (accessToken: string, refreshToken: string) => void;
  onSessionCleared: () => void;
}

let config: ApiClientConfig | null = null;

export function configureApiClient(cfg: ApiClientConfig): void {
  config = cfg;
}

export function getApiClientConfig(): ApiClientConfig {
  if (!config) {
    throw new Error("apiRequest() called before configureApiClient() was run");
  }
  return config;
}

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function parseErrorMessage(response: Response): Promise<string> {
  try {
    const body = await response.json();
    return body.detail ?? response.statusText;
  } catch {
    return response.statusText;
  }
}

async function refreshAccessToken(): Promise<string | null> {
  const { baseUrl, getRefreshToken, onSession, onSessionCleared } = getApiClientConfig();
  const refreshToken = getRefreshToken();
  if (!refreshToken) return null;

  const response = await fetch(`${baseUrl}/auth/refresh`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });

  if (!response.ok) {
    onSessionCleared();
    return null;
  }

  const data: { access_token: string; refresh_token: string } = await response.json();
  onSession(data.access_token, data.refresh_token);
  return data.access_token;
}

interface RequestOptions {
  method?: string;
  body?: unknown;
  auth?: boolean;
}

export async function apiRequest<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = "GET", body, auth = true } = options;
  const { baseUrl, getAccessToken } = getApiClientConfig();

  const doFetch = async (token: string | null): Promise<Response> => {
    const headers: Record<string, string> = { "Content-Type": "application/json" };
    if (auth && token) headers.Authorization = `Bearer ${token}`;

    return fetch(`${baseUrl}${path}`, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
    });
  };

  let token = getAccessToken();
  let response = await doFetch(token);

  if (auth && response.status === 401) {
    token = await refreshAccessToken();
    if (token) {
      response = await doFetch(token);
    }
  }

  if (!response.ok) {
    throw new ApiError(response.status, await parseErrorMessage(response));
  }

  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}
