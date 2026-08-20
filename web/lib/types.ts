/**
 * The shapes Backend/services.py returns.
 *
 * These are hand-written rather than generated: the service layer is small and
 * stable, and a hand-written type is the one place to read what a field means.
 * Anything nullable here is nullable there — a panel that has never been
 * analysed genuinely has no dust level, and the UI has to say so.
 */

export type PanelState = "clean" | "moderate_dust" | "needs_cleaning" | "unknown";
export type SystemMode = "active" | "paused";
export type HealthState = "healthy" | "degraded" | "paused";
export type WaterPressure = "low" | "medium" | "high";
export type CleaningFrequency = "daily" | "weekly" | "biweekly" | "monthly";
export type LogLevel = "INFO" | "WARNING" | "ERROR";

export interface Panel {
  id: string;
  status: PanelState;
  /** A formatted date, or the literal string "Never". */
  last_cleaned: string;
  /** Fraction 0–1, or null when the panel has never been analysed. */
  dust_level: number | null;
  confidence: number | null;
  last_analysed: string | null;
  image_available: boolean;
}

export interface Water {
  capacity_ml: number;
  used_ml: number;
  remaining_ml: number;
  level_percent: number;
}

export interface Health {
  status: HealthState;
  timestamp: string;
  water_level: number;
  water: Water;
  camera_status: "online" | "degraded" | "offline";
  system_temperature: string;
  system_mode: SystemMode;
  telemetry_available: boolean;
}

export interface Stats {
  total_panels: number;
  total_cleanings: number;
  total_analyses: number;
  system_uptime: string;
  water_used_total: number;
  avg_dust_level: number;
  last_analysis: string | null;
}

export interface Counts {
  clean: number;
  moderate_dust: number;
  needs_cleaning: number;
  unknown: number;
  total: number;
  attention: number;
  health_percentage: number;
}

/** The forecasting and economic stages, carried through the decision. */
export interface DecisionAnalysis {
  visual_score: number;
  image_quality: string;
  insights: string[];
  processing_time_ms: number;
  daily_power_loss_kwh: number | null;
  power_loss_percentage: number | null;
  optimal_cleaning_window: string;
  cleaning_cost_usd: number | null;
  estimated_savings_weekly: number | null;
  roi_percentage: number | null;
  payback_period_days: number | null;
  recommendation: string;
  reasoning: string;
}

export interface SprayResult {
  panel_id: string;
  action: string;
  duration_seconds: number;
  water_used_ml: number;
  pressure: WaterPressure;
  timestamp: string;
  water_remaining_ml: number;
  next_check: string;
}

export interface Decision {
  decision_id: string;
  panel_id: string;
  dust_level: number;
  status: string;
  confidence: number;
  decision: "spray_now" | "schedule_cleaning" | "no_action";
  action: string;
  spray_duration: number;
  water_volume: number;
  timestamp: string;
  analysis: DecisionAnalysis;
  /** Present only when auto-cleaning acted on this decision. */
  auto_clean?: SprayResult | { error: string };
}

/** `latest_decision` before anything has been analysed. */
export interface NoDecision {
  message: string;
}

export type LatestDecision = Decision | NoDecision;

export interface SystemSettings {
  dust_threshold: number;
  schedule_threshold: number;
  spray_duration: number;
  water_pressure: WaterPressure;
  auto_clean: boolean;
  notifications: boolean;
  refresh_interval: number;
  system_mode: SystemMode;
  alert_email: string;
  cleaning_frequency: CleaningFrequency;
  preferred_time: string;
  tank_refilled_at: string | null;
  /** Set when this database was filled by Backend/demo.py. */
  demo_seeded_at: string | null;
}

export interface LogEntry {
  id: number;
  timestamp: string | null;
  level: LogLevel;
  component: string;
  message: string;
  details: Record<string, unknown>;
}

export interface TelemetryReading {
  panel_id: string;
  timestamp?: string;
  efficiency: number;
  temperature: number;
  humidity: number;
  spray_interval: number;
  power: number;
  light: number;
}

export interface Telemetry {
  available: boolean;
  readings: TelemetryReading[];
  source?: string;
  captured_at?: string;
  avg_temperature?: number | null;
  avg_humidity?: number | null;
  avg_efficiency?: number | null;
}

/** Everything a console page renders — one call, and the poll target. */
export interface Overview {
  health: Health;
  panels: Panel[];
  counts: Counts;
  stats: Stats;
  latest_decision: LatestDecision;
  settings: SystemSettings;
  timestamp: string;
}

export interface StatusHistoryEntry {
  id: number;
  panel_id: string;
  timestamp: string | null;
  dust_level: number | null;
  classification_confidence: number | null;
  is_dirty: boolean;
  needs_cleaning: boolean;
  image_path: string | null;
}

export interface CleaningHistoryEntry {
  id: number;
  panel_id: string;
  timestamp: string | null;
  action_type: string;
  water_volume: number | null;
  duration: number | null;
  success: boolean;
  error_message: string | null;
}

export interface PanelDetail {
  panel_id: string;
  panel: Panel | null;
  telemetry: TelemetryReading | null;
  status_history: StatusHistoryEntry[];
  cleaning_history: CleaningHistoryEntry[];
}

export interface BulkFailure {
  panel_id: string;
  error: string;
}

export interface AnalyzeAllResult {
  results: Decision[];
  failures: BulkFailure[];
  analysed: number;
  message: string;
}

export interface SprayManyResult {
  results: SprayResult[];
  failures: BulkFailure[];
  total_panels: number;
  targeted: number;
  cleaned: number;
  water_used_ml: number;
  message: string;
}

/** What every server action hands back to the component that called it. */
export interface ActionResult {
  ok: boolean;
  message: string;
  failures?: BulkFailure[];
}
