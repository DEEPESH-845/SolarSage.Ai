import { ApiError, getLogs, getOverview, getTelemetry } from "./api";
import { demoLogs, demoOverview, demoTelemetry } from "./demo";
import type { LogEntry, Overview, Panel, Telemetry } from "./types";

/**
 * The console's read path, and the one place that decides whether a page is
 * looking at the real system or at the recorded fixture run.
 *
 * A backend that does not answer is a state to render, not an exception to throw
 * at the operator: the pages below all draw from `demo.ts` instead and say so at
 * the top of the screen. Which of the two happened is carried in `source` rather
 * than inferred from the data, so nothing downstream has to guess, and demo data
 * can never be presented as live.
 */

export type DataSource = "live" | "demo";

export interface Feed<T> {
  data: T;
  source: DataSource;
  /** Why the backend was passed over. Null when it answered. */
  reason: string | null;
}

/** Errors worth naming on screen; anything else is reported as unreachable. */
function describe(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.status === 0) return error.message;
    return `The backend answered ${error.status}: ${error.message}`;
  }
  if (error instanceof Error && error.name === "TimeoutError") {
    return "The backend did not answer in time.";
  }
  return "The backend could not be reached.";
}

/**
 * A backend can fail by not answering, and it can fail by answering with
 * something else — a proxy's HTML error page under a 200, a half-migrated
 * deployment, a version skew that drops a field. The pages below destructure
 * this object and index into it, so a shape that is merely *wrong* crashes them
 * exactly as hard as a connection that was refused, and has to be caught in the
 * same place. This checks only what the console actually reads; it is a guard,
 * not a schema.
 */
function isOverview(value: unknown): value is Overview {
  if (!value || typeof value !== "object") return false;
  const v = value as Record<string, unknown>;

  const isRecord = (x: unknown) => Boolean(x) && typeof x === "object" && !Array.isArray(x);
  if (!isRecord(v.health) || !isRecord(v.counts) || !isRecord(v.stats)) return false;
  if (!isRecord(v.settings) || !isRecord(v.latest_decision)) return false;
  if (!Array.isArray(v.panels)) return false;

  // The water block is read two levels deep on every console page.
  if (!isRecord((v.health as Record<string, unknown>).water)) return false;

  // Counts drive a donut and four stat cards; a non-number there is a NaN on screen.
  const counts = v.counts as Record<string, unknown>;
  const required = ["clean", "moderate_dust", "needs_cleaning", "unknown", "total"];
  if (!required.every((key) => Number.isFinite(counts[key]))) return false;

  return v.panels.every((panel) => isRecord(panel) && typeof (panel as Panel).id === "string");
}

async function feed<T>(
  load: () => Promise<T>,
  fallback: () => T,
  valid: (value: unknown) => boolean = () => true,
): Promise<Feed<T>> {
  try {
    const data = await load();
    if (!valid(data)) {
      throw new ApiError(
        502,
        "/overview",
        "The backend answered with data the console could not read.",
      );
    }
    return { data, source: "live", reason: null };
  } catch (error) {
    // Loud in the server log, quiet on screen: an operator gets the banner, a
    // developer gets the cause.
    console.error("[solarsage] falling back to demo data —", error);
    return { data: fallback(), source: "demo", reason: describe(error) };
  }
}

export const overviewFeed = () => feed<Overview>(getOverview, demoOverview, isOverview);

/**
 * Telemetry and logs follow whichever source the overview settled on, so one
 * page can never mix a live reading into a demo dashboard. When the backend is
 * up but only these fail, the pages already have an empty state for it.
 */
export async function telemetryFeed(source: DataSource): Promise<Telemetry> {
  if (source === "demo") return demoTelemetry();
  return getTelemetry()
    .then((t) => (t && Array.isArray(t.readings) ? t : { available: false, readings: [] }))
    .catch(() => ({ available: false, readings: [] }));
}

export async function logsFeed(source: DataSource, limit = 50): Promise<LogEntry[]> {
  if (source === "demo") return demoLogs();
  return getLogs(limit)
    .then((rows) => (Array.isArray(rows) ? rows : []))
    .catch(() => []);
}
