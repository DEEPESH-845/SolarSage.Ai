import { describe, expect, it, vi, afterEach } from "vitest";
import { demoLogs, demoOverview, demoTelemetry } from "../demo";
import type { Counts, Panel } from "../types";

/**
 * The demo dataset is what a visitor sees whenever the backend is unreachable,
 * so it has to survive being read closely: a recruiter who adds up the tallies
 * or divides the water by the wash count should not find a contradiction.
 */

const SCHEDULE_THRESHOLD = 30;
const DUST_THRESHOLD = 60;

function expectedState(dust: number): Panel["status"] {
  const percent = dust * 100;
  if (percent >= DUST_THRESHOLD) return "needs_cleaning";
  if (percent >= SCHEDULE_THRESHOLD) return "moderate_dust";
  return "clean";
}

describe("demo dataset", () => {
  const overview = demoOverview();

  it("gives every panel a reading its state actually earns", () => {
    for (const panel of overview.panels) {
      expect(panel.dust_level).not.toBeNull();
      expect(panel.status).toBe(expectedState(panel.dust_level as number));
      expect(panel.dust_level as number).toBeGreaterThanOrEqual(0);
      expect(panel.dust_level as number).toBeLessThanOrEqual(1);
    }
  });

  it("tallies that add up to the number of panels", () => {
    const c: Counts = overview.counts;
    expect(c.clean + c.moderate_dust + c.needs_cleaning + c.unknown).toBe(c.total);
    expect(c.total).toBe(overview.panels.length);
    expect(c.attention).toBe(c.moderate_dust + c.needs_cleaning);
    expect(c.health_percentage).toBeCloseTo((c.clean / c.total) * 100, 1);
  });

  it("spends exactly as much water as the wash count implies", () => {
    const { stats, health, settings } = overview;
    const perWash = settings.spray_duration * 20; // ML_PER_SECOND_OF_SPRAY
    expect(stats.water_used_total).toBe(stats.total_cleanings * perWash);
    expect(health.water.used_ml).toBe(stats.water_used_total);
    expect(health.water.remaining_ml).toBe(health.water.capacity_ml - health.water.used_ml);
    expect(health.water.level_percent).toBeCloseTo(
      (health.water.remaining_ml / health.water.capacity_ml) * 100,
      1,
    );
    expect(health.water_level).toBe(health.water.level_percent);
  });

  it("never carries a value the dashboard would render as NaN", () => {
    const walk = (value: unknown, path: string): void => {
      if (typeof value === "number") {
        expect(Number.isFinite(value), `${path} is not finite`).toBe(true);
        return;
      }
      if (value && typeof value === "object") {
        for (const [key, inner] of Object.entries(value)) walk(inner, `${path}.${key}`);
      }
    };
    walk(overview, "overview");
    walk(demoTelemetry(), "telemetry");
    walk(demoLogs(), "logs");
  });

  it("does not claim to be a seeded live database", () => {
    // `demo_seeded_at` means "the backend answered, and its database was seeded".
    // The fallback is a different statement and must not borrow that banner.
    expect(overview.settings.demo_seeded_at).toBeNull();
  });

  it("reports timestamps in the past, newest log first", () => {
    const logs = demoLogs();
    const times = logs.map((log) => Date.parse(log.timestamp as string));
    expect(times.every((t) => Number.isFinite(t) && t <= Date.now() + 1000)).toBe(true);
    expect([...times].sort((a, b) => b - a)).toEqual(times);
    expect(new Set(logs.map((l) => l.id)).size).toBe(logs.length);
  });

  it("averages telemetry over the rows it actually ships", () => {
    const t = demoTelemetry();
    const mean = (nums: number[]) => nums.reduce((a, b) => a + b, 0) / nums.length;
    expect(t.readings.length).toBeGreaterThan(0);
    expect(t.avg_temperature).toBeCloseTo(mean(t.readings.map((r) => r.temperature)), 1);
    expect(t.avg_efficiency).toBeCloseTo(mean(t.readings.map((r) => r.efficiency)), 1);
  });
});

describe("feed", () => {
  afterEach(() => {
    vi.restoreAllMocks();
    vi.resetModules();
  });

  it("reports live when the backend answers", async () => {
    vi.resetModules();
    vi.doMock("../api", async () => {
      const actual = await vi.importActual<typeof import("../api")>("../api");
      return { ...actual, getOverview: async () => ({ ...demoOverview(), timestamp: "live" }) };
    });
    const { overviewFeed } = await import("../feed");
    const result = await overviewFeed();
    expect(result.source).toBe("live");
    expect(result.reason).toBeNull();
  });

  it("falls back to demo data — and says why — when the backend does not answer", async () => {
    vi.resetModules();
    vi.spyOn(console, "error").mockImplementation(() => {});
    vi.doMock("../api", async () => {
      const actual = await vi.importActual<typeof import("../api")>("../api");
      return {
        ...actual,
        getOverview: async () => {
          throw new actual.ApiError(0, "/overview", "The backend did not answer in time.");
        },
      };
    });
    const { overviewFeed } = await import("../feed");
    const result = await overviewFeed();
    expect(result.source).toBe("demo");
    expect(result.reason).toContain("did not answer in time");
    // The point of the fallback: a populated console, not an empty one.
    expect(result.data.panels.length).toBeGreaterThan(0);
    expect(result.data.counts.total).toBe(result.data.panels.length);
  });

  it("names a backend that answered with an error, rather than blaming the network", async () => {
    vi.resetModules();
    vi.spyOn(console, "error").mockImplementation(() => {});
    vi.doMock("../api", async () => {
      const actual = await vi.importActual<typeof import("../api")>("../api");
      return {
        ...actual,
        getOverview: async () => {
          throw new actual.ApiError(500, "/overview", "database is locked");
        },
      };
    });
    const { overviewFeed } = await import("../feed");
    const result = await overviewFeed();
    expect(result.source).toBe("demo");
    expect(result.reason).toContain("500");
  });

  it.each([
    ["every field null", { health: null, panels: null, counts: null, stats: null, latest_decision: null, settings: null }],
    ["an empty object", {}],
    ["fields of the wrong type", { health: "nope", panels: 42, counts: [], stats: "x", latest_decision: 7, settings: null }],
    ["a missing water block", { health: {}, panels: [], counts: { clean: 0, moderate_dust: 0, needs_cleaning: 0, unknown: 0, total: 0 }, stats: {}, latest_decision: {}, settings: {} }],
    ["counts that are not numbers", { health: { water: {} }, panels: [], counts: { clean: "1", moderate_dust: 0, needs_cleaning: 0, unknown: 0, total: 1 }, stats: {}, latest_decision: {}, settings: {} }],
    ["a panel with no id", { health: { water: {} }, panels: [{ status: "clean" }], counts: { clean: 1, moderate_dust: 0, needs_cleaning: 0, unknown: 0, total: 1 }, stats: {}, latest_decision: {}, settings: {} }],
    ["a string instead of an object", "<html>not json</html>"],
  ])("treats a 200 carrying %s as a failed read", async (_label, body) => {
    vi.resetModules();
    vi.spyOn(console, "error").mockImplementation(() => {});
    vi.doMock("../api", async () => {
      const actual = await vi.importActual<typeof import("../api")>("../api");
      return { ...actual, getOverview: async () => body };
    });
    const { overviewFeed } = await import("../feed");
    const result = await overviewFeed();
    expect(result.source).toBe("demo");
    expect(result.data.panels.length).toBeGreaterThan(0);
    expect(result.data.counts.total).toBe(result.data.panels.length);
  });

  it("keeps telemetry and logs on the same source as the overview", async () => {
    const { telemetryFeed, logsFeed } = await import("../feed");
    // A demo dashboard must not splice in a live sensor row.
    expect((await telemetryFeed("demo")).source).toBe(demoTelemetry().source);
    expect((await logsFeed("demo")).length).toBe(demoLogs().length);
  });

  it("renders an empty table rather than crashing when a live list is not a list", async () => {
    vi.resetModules();
    vi.doMock("../api", async () => {
      const actual = await vi.importActual<typeof import("../api")>("../api");
      return {
        ...actual,
        getTelemetry: async () => ({ available: true, readings: null }),
        getLogs: async () => ({ oops: true }),
      };
    });
    const { telemetryFeed, logsFeed } = await import("../feed");
    expect((await telemetryFeed("live")).readings).toEqual([]);
    expect(await logsFeed("live")).toEqual([]);
  });
});

describe("ApiError classification", () => {
  it("sorts failures into the kinds the UI branches on", async () => {
    const { ApiError } = await import("../api");
    expect(new ApiError(0, "/x", "The backend did not answer in time.").kind).toBe("TIMEOUT");
    expect(new ApiError(0, "/x", "The backend did not answer. Is it running?").kind).toBe("NETWORK_ERROR");
    expect(new ApiError(401, "/x", "nope").kind).toBe("AUTH_ERROR");
    expect(new ApiError(404, "/x", "nope").kind).toBe("NOT_FOUND");
    expect(new ApiError(422, "/x", "nope").kind).toBe("VALIDATION_ERROR");
    expect(new ApiError(503, "/x", "nope").kind).toBe("SERVER_ERROR");
    expect(new ApiError(418, "/x", "nope").kind).toBe("UNKNOWN_ERROR");
  });
});
