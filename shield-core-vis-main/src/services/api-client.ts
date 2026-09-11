/**
 * Centralized API Client & Configuration
 * Provides base URL resolution, typed error classes, and resilient fetch with AbortSignal timeout.
 */

export interface ApiConfig {
  baseUrl: string;
  timeoutMs: number;
}

export const apiConfig: ApiConfig = {
  baseUrl: (import.meta.env.VITE_API_URL as string | undefined)?.replace(/\/$/, "") ?? "/api/v1",
  timeoutMs: Number(import.meta.env.VITE_API_TIMEOUT_MS ?? 8000),
};

export type ApiErrorKind =
  | "NETWORK_ERROR"
  | "TIMEOUT"
  | "HTTP_4XX"
  | "HTTP_5XX"
  | "INVALID_RESPONSE"
  | "SERVICE_UNAVAILABLE";

export class ApiError extends Error {
  readonly kind: ApiErrorKind;
  readonly status?: number;
  readonly endpoint: string;

  constructor(kind: ApiErrorKind, message: string, endpoint: string, status?: number) {
    super(message);
    this.name = "ApiError";
    this.kind = kind;
    this.endpoint = endpoint;
    if (status !== undefined) {
      this.status = status;
    }
  }
}

/**
 * Resilient typed fetch with timeout and standard error classification.
 */
export async function apiFetch<T>(
  endpoint: string,
  options: RequestInit = {},
  customTimeoutMs?: number,
): Promise<T> {
  const timeoutMs = customTimeoutMs ?? apiConfig.timeoutMs;
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  const cleanEndpoint = endpoint.startsWith("/") ? endpoint : `/${endpoint}`;
  const url = `${apiConfig.baseUrl}${cleanEndpoint}`;

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
        ...options.headers,
      },
    });

    if (!response.ok) {
      const status = response.status;
      const kind: ApiErrorKind =
        status === 503 ? "SERVICE_UNAVAILABLE" : status >= 500 ? "HTTP_5XX" : "HTTP_4XX";
      throw new ApiError(kind, `HTTP ${status}: ${response.statusText}`, cleanEndpoint, status);
    }

    const json = (await response.json()) as T;
    return json;
  } catch (err: unknown) {
    if (err instanceof ApiError) {
      throw err;
    }

    if (err instanceof DOMException && err.name === "AbortError") {
      throw new ApiError(
        "TIMEOUT",
        `Request to ${cleanEndpoint} timed out after ${timeoutMs}ms`,
        cleanEndpoint,
      );
    }

    const message = err instanceof Error ? err.message : "Network communication failure";
    throw new ApiError("NETWORK_ERROR", message, cleanEndpoint);
  } finally {
    clearTimeout(timer);
  }
}
