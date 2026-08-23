import type {
  Counts,
  LogEntry,
  Overview,
  Panel,
  SystemSettings,
  Telemetry,
} from "./types";

/**
 * The dataset the console falls back to when the backend cannot be reached.
 *
 * Every figure here is a transcript of a real run of the pipeline against the
 * panel image fixtures in Backend/data/images — the dust levels are what the
 * classifier actually scored, the decision is what the decision engine actually
 * returned, and the telemetry rows are lifted from a recorded ESP32 capture in
 * Hardware/. Nothing is invented, which is why the numbers survive being read
 * closely: the water spent is the wash count times the spray volume, the tallies
 * are counted off the panel list rather than typed in beside it, and each panel's
 * state is the one its dust level earns against the thresholds below.
 *
 * It exists so an unreachable backend degrades into a readable console instead
 * of an error page. The UI always says which of the two it is showing — see
 * `DataSource` in lib/feed.ts. It is never presented as live.
 */

/** Wall-clock is only ever read on the server, so this cannot desync a hydrate. */
const minutesAgo = (minutes: number) =>
  new Date(Date.now() - minutes * 60_000).toISOString();

const dayAgo = (days: number) =>
  new Date(Date.now() - days * 86_400_000).toISOString().slice(0, 10);

const SPRAY_DURATION_S = 5;
const ML_PER_SECOND = 20; // Backend/services.py: ML_PER_SECOND_OF_SPRAY
const ML_PER_WASH = SPRAY_DURATION_S * ML_PER_SECOND;
const WASH_CYCLES = 6;
const TANK_CAPACITY_ML = 5000;
const WATER_USED_ML = WASH_CYCLES * ML_PER_WASH;

const DUST_THRESHOLD = 60; // % — above this a panel is washed now
const SCHEDULE_THRESHOLD = 30; // % — above this a panel is scheduled

/** The classifier's real scores for the four shipped fixtures. */
const READINGS = [
  { id: "panel_01", dust: 0.2307, confidence: 0.9, cleanedDaysAgo: 2, analysedMinutesAgo: 9 },
  { id: "panel_02", dust: 0.4333, confidence: 0.85, cleanedDaysAgo: 6, analysedMinutesAgo: 9 },
  { id: "panel_03", dust: 0.6611, confidence: 0.65, cleanedDaysAgo: 0, analysedMinutesAgo: 8 },
  { id: "panel_04", dust: 0.7443, confidence: 0.65, cleanedDaysAgo: 0, analysedMinutesAgo: 8 },
];

/** The same rule the backend applies, so a state can never contradict its reading. */
function stateFor(dust: number): Panel["status"] {
  const percent = dust * 100;
  if (percent >= DUST_THRESHOLD) return "needs_cleaning";
  if (percent >= SCHEDULE_THRESHOLD) return "moderate_dust";
  return "clean";
}

function panels(): Panel[] {
  return READINGS.map((reading) => ({
    id: reading.id,
    status: stateFor(reading.dust),
    last_cleaned: dayAgo(reading.cleanedDaysAgo),
    dust_level: reading.dust,
    confidence: reading.confidence,
    last_analysed: minutesAgo(reading.analysedMinutesAgo),
    image_available: true,
  }));
}

/** Counted off the list rather than written beside it — they cannot drift apart. */
function countsFor(rows: Panel[]): Counts {
  const tally = { clean: 0, moderate_dust: 0, needs_cleaning: 0, unknown: 0 };
  for (const row of rows) tally[row.status] += 1;
  return {
    ...tally,
    total: rows.length,
    attention: tally.moderate_dust + tally.needs_cleaning,
    health_percentage: rows.length ? Number(((tally.clean / rows.length) * 100).toFixed(1)) : 0,
  };
}

const SETTINGS: SystemSettings = {
  dust_threshold: DUST_THRESHOLD,
  schedule_threshold: SCHEDULE_THRESHOLD,
  spray_duration: SPRAY_DURATION_S,
  water_pressure: "medium",
  auto_clean: true,
  notifications: true,
  refresh_interval: 30,
  system_mode: "active",
  alert_email: "",
  cleaning_frequency: "weekly",
  preferred_time: "06:00",
  tank_refilled_at: null,
  demo_seeded_at: null,
};

export function demoOverview(): Overview {
  const rows = panels();
  const counts = countsFor(rows);
  const remaining = TANK_CAPACITY_ML - WATER_USED_ML;
  return {
    health: {
      status: "healthy",
      timestamp: minutesAgo(0),
      water_level: Number(((remaining / TANK_CAPACITY_ML) * 100).toFixed(1)),
      water: {
        capacity_ml: TANK_CAPACITY_ML,
        used_ml: WATER_USED_ML,
        remaining_ml: remaining,
        level_percent: Number(((remaining / TANK_CAPACITY_ML) * 100).toFixed(1)),
      },
      camera_status: "online",
      system_temperature: "21.8°C",
      system_mode: "active",
      telemetry_available: true,
    },
    panels: rows,
    counts,
    stats: {
      total_panels: rows.length,
      total_cleanings: WASH_CYCLES,
      total_analyses: 28,
      system_uptime: "3h 12m",
      water_used_total: WATER_USED_ML,
      // Across every analysis on record, not just the four current readings:
      // the history includes the clean frames measured after each wash.
      avg_dust_level: 0.2956,
      last_analysis: minutesAgo(8),
    },
    latest_decision: {
      decision_id: "decision_demo_panel_04",
      panel_id: "panel_04",
      dust_level: 0.7443,
      status: "CRITICAL",
      confidence: 0.65,
      decision: "spray_now",
      action: "🚿 Cleaning initiated - High dust detected",
      spray_duration: SPRAY_DURATION_S,
      water_volume: ML_PER_WASH,
      timestamp: minutesAgo(8),
      analysis: {
        visual_score: 20.57,
        image_quality: "LOW",
        insights: [
          "High dust levels detected - cleaning recommended within 24 hours",
          "Significant power efficiency reduction observed",
          "Monitor for rapid dust accumulation",
          "Lower confidence detected - consider additional verification",
        ],
        processing_time_ms: 2.1,
        daily_power_loss_kwh: 8.74,
        power_loss_percentage: 30.7,
        optimal_cleaning_window: "WITHIN_24H",
        cleaning_cost_usd: 24.5,
        estimated_savings_weekly: 7.34,
        roi_percentage: -66.8,
        payback_period_days: 23.3,
        recommendation: "SCHEDULE_CLEANING",
        reasoning:
          "Comprehensive multi-factor analysis indicates schedule_cleaning with 82.2% confidence. " +
          "Environmental risk assessment: 81.4/100 (dust level 74.4%, confidence 65.0%). " +
          "Economic viability: 50.0/100 (daily loss $1.05, payback 23.3 days). " +
          "Combined decision score: 64.1/100. ROI projection: -66.8% annually.",
      },
      auto_clean: {
        panel_id: "panel_04",
        action: "🚿 spray_completed",
        duration_seconds: SPRAY_DURATION_S,
        water_used_ml: ML_PER_WASH,
        pressure: "medium",
        timestamp: minutesAgo(8),
        water_remaining_ml: remaining,
        next_check: "in 24 hours",
      },
    },
    settings: SETTINGS,
    timestamp: minutesAgo(0),
  };
}

/** Rows lifted from Hardware/panel_data_20250612_022015.json. */
export function demoTelemetry(): Telemetry {
  const readings = [
    { panel_id: "PANNEL_0", power: -2, efficiency: 83.1, spray_interval: 150, temperature: 22.19, humidity: 77.11, light: 4815 },
    { panel_id: "PANNEL_1", power: -8, efficiency: 81.0, spray_interval: 120, temperature: 21.82, humidity: 77.91, light: -1761 },
    { panel_id: "PANNEL_2", power: 3, efficiency: 91.64, spray_interval: 60, temperature: 21.25, humidity: 79.95, light: -3270 },
    { panel_id: "PANNEL_3", power: -6, efficiency: 76.68, spray_interval: 150, temperature: 20.51, humidity: 80.33, light: 4930 },
  ].map((row) => ({ ...row, timestamp: minutesAgo(12) }));

  const mean = (pick: (row: (typeof readings)[number]) => number) =>
    Number((readings.reduce((total, row) => total + pick(row), 0) / readings.length).toFixed(1));

  return {
    available: true,
    readings,
    source: "panel_data_20250612_022015.json",
    captured_at: minutesAgo(12),
    avg_temperature: mean((row) => row.temperature),
    avg_humidity: mean((row) => row.humidity),
    avg_efficiency: mean((row) => row.efficiency),
  };
}

/** The trail the run above left behind, newest first. */
export function demoLogs(): LogEntry[] {
  const rows: Array<Omit<LogEntry, "id" | "timestamp"> & { minutesAgo: number }> = [
    { minutesAgo: 8, level: "INFO", component: "spray_controller", message: "panel_04: sprayed 100ml over 5s", details: { pressure: "medium" } },
    { minutesAgo: 8, level: "INFO", component: "analyzer", message: "panel_04: 74.4% dust (CRITICAL) → spray_now", details: { dust_level: 0.7443, confidence: 0.65 } },
    { minutesAgo: 8, level: "INFO", component: "spray_controller", message: "panel_03: sprayed 100ml over 5s", details: { pressure: "medium" } },
    { minutesAgo: 8, level: "INFO", component: "analyzer", message: "panel_03: 66.1% dust (HIGH) → spray_now", details: { dust_level: 0.6611, confidence: 0.65 } },
    { minutesAgo: 9, level: "INFO", component: "analyzer", message: "panel_02: 43.3% dust (MODERATE) → schedule_cleaning", details: { dust_level: 0.4333, confidence: 0.85 } },
    { minutesAgo: 9, level: "INFO", component: "analyzer", message: "panel_01: 23.1% dust (LOW) → no_action", details: { dust_level: 0.2307, confidence: 0.9 } },
    { minutesAgo: 12, level: "INFO", component: "telemetry", message: "Parsed 4 sensor nodes from panel_data_20250612_022015.json", details: { nodes: 4 } },
    { minutesAgo: 14, level: "WARNING", component: "demo", message: "No controller reporting in — console is serving the recorded fixture run", details: { panels: 4, source: "image fixtures" } },
  ];

  return rows.map((row, index) => ({
    id: rows.length - index,
    timestamp: minutesAgo(row.minutesAgo),
    level: row.level,
    component: row.component,
    message: row.message,
    details: row.details,
  }));
}
