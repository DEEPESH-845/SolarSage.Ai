import type {
  AnalyzeAllResult,
  Decision,
  LogEntry,
  Overview,
  PanelDetail,
  SprayManyResult,
  SprayResult,
  SystemSettings,
  Telemetry,
} from "./types";

/**
 * The only place this app talks to the FastAPI backend.
 *
 * Every call runs on the server — from a server component during render, or
 * from a server action during a mutation — so `API_URL` never reaches the
 * browser and there is no CORS surface to configure.
 */

const API_URL = (process.env.API_URL ?? "http://127.0.0.1:8000").replace(/\/+$/, "");

// Mutating routes demand this when the backend has API_TOKEN set. It stays on
// the server: the browser never calls the API, so it never needs the secret.
const API_TOKEN = process.env.API_TOKEN;

/**
 * How long a call waits before it counts as a failure.
 *
 * Without a deadline a backend that accepts the connection and then stalls holds
 * the render open until the platform kills the whole request — the page would
 * hang rather than fall back. Reads are the ones a visitor waits on, so they give
 * up early enough to still show the demo console; a write is a deliberate act and
 * is given room to finish, because a spray that timed out client-side may well
 * have opened the valve anyway.
 */
const READ_TIMEOUT_MS = Number(process.env.API_TIMEOUT_MS ?? 6000);
const WRITE_TIMEOUT_MS = Number(process.env.API_WRITE_TIMEOUT_MS ?? 25000);

/** A backend that answered with a failure, carrying enough to show the operator. */
export class ApiError extends Error {
  constructor(
    readonly status: number,
    readonly path: string,
    message: string,
    options?: ErrorOptions,
  ) {
    super(message, options);
    this.name = "ApiError";
  }

  /** What went wrong, in the terms the UI and the logs both sort by. */
  get kind():
    | "NETWORK_ERROR"
    | "TIMEOUT"
    | "AUTH_ERROR"
    | "VALIDATION_ERROR"
    | "NOT_FOUND"
    | "SERVER_ERROR"
    | "UNKNOWN_ERROR" {
    if (this.status === 0) {
      return this.message.includes("in time") ? "TIMEOUT" : "NETWORK_ERROR";
    }
    if (this.status === 401 || this.status === 403) return "AUTH_ERROR";
    if (this.status === 404) return "NOT_FOUND";
    if (this.status === 422 || this.status === 400) return "VALIDATION_ERROR";
    if (this.status >= 500) return "SERVER_ERROR";
    return "UNKNOWN_ERROR";
  }
}

async function call<T>(path: string, init?: RequestInit): Promise<T> {
  const write = init?.method !== undefined && init.method !== "GET";
  let response: Response;
  try {
    response = await fetch(`${API_URL}${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...(API_TOKEN ? { "X-API-Key": API_TOKEN } : {}),
        ...init?.headers,
      },
      signal: AbortSignal.timeout(write ? WRITE_TIMEOUT_MS : READ_TIMEOUT_MS),
      // The console reports live hardware state; a cached answer would be a lie.
      cache: "no-store",
    });
  } catch (cause) {
    // A deadline that ran out and a connection that was refused are different
    // facts, and the operator is told which one happened.
    const timedOut = cause instanceof Error && cause.name === "TimeoutError";
    throw new ApiError(
      0,
      path,
      timedOut
        ? "The backend did not answer in time."
        : "The backend did not answer. Is it running?",
      { cause },
    );
  }

  const body = await response.json().catch(() => null);

  if (!response.ok) {
    // FastAPI puts its message in `detail`; the service layer uses `error`.
    const detail = body?.detail ?? body?.error ?? `Request failed (${response.status})`;
    throw new ApiError(response.status, path, String(detail));
  }
  return body as T;
}

function post<T>(path: string, payload?: unknown): Promise<T> {
  return call<T>(path, {
    method: "POST",
    body: payload === undefined ? undefined : JSON.stringify(payload),
  });
}

/* ----------------------------------------------------------------- reads */

export const getOverview = () => call<Overview>("/overview");
export const getSettings = () => call<SystemSettings>("/settings");
export const getTelemetry = () => call<Telemetry>("/hardware/telemetry");
export const getLogs = (limit = 50) => call<LogEntry[]>(`/system/logs?limit=${limit}`);
export const getPanelDetail = (panelId: string) =>
  call<PanelDetail>(`/panels/${encodeURIComponent(panelId)}/detail`);

/* -------------------------------------------------------------- mutations */

export const analyzePanel = (panelId: string) => post<Decision>("/analyze", { panel_id: panelId });
export const sprayPanel = (panelId: string) => post<SprayResult>("/spray", { panel_id: panelId });
export const analyzeAll = () => post<AnalyzeAllResult>("/panels/analyze-all");
export const sprayMany = (scope: "dirty" | "all") =>
  post<SprayManyResult>("/panels/spray", { scope });
export const refillTank = () => post<Record<string, number>>("/system/refill-tank");
export const resetSettings = () => post<SystemSettings>("/settings/reset");
export const updateSettings = (values: Partial<SystemSettings>) =>
  call<SystemSettings>("/settings", { method: "PUT", body: JSON.stringify({ values }) });
