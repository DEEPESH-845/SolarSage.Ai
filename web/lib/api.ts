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

const API_URL = process.env.API_URL ?? "http://127.0.0.1:8000";

// Mutating routes demand this when the backend has API_TOKEN set. It stays on
// the server: the browser never calls the API, so it never needs the secret.
const API_TOKEN = process.env.API_TOKEN;

/** A backend that answered with a failure, carrying enough to show the operator. */
export class ApiError extends Error {
  constructor(
    readonly status: number,
    readonly path: string,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function call<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_URL}${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...(API_TOKEN ? { "X-API-Key": API_TOKEN } : {}),
        ...init?.headers,
      },
      // The console reports live hardware state; a cached answer would be a lie.
      cache: "no-store",
    });
  } catch (cause) {
    throw new ApiError(0, path, "The backend did not answer. Is it running?");
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
