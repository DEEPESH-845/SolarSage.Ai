import type { HealthState, PanelState } from "./types";

/**
 * One table for what a panel state looks like, so a pill, a meter and a table
 * cell can never disagree about what "moderate dust" means.
 */

interface StateStyle {
  label: string;
  /** CSS modifier suffix — `moderate_dust` is `pill--moderate` in the stylesheet. */
  pill: string;
  colour: string;
  /** What the operator should do about it, in the panels table. */
  nextStep: string;
  nextStepClass: string;
}

export const PANEL_STATE: Record<PanelState, StateStyle> = {
  clean: {
    label: "Clean",
    pill: "clean",
    colour: "var(--water)",
    nextStep: "Nothing to do",
    nextStepClass: "text-water",
  },
  moderate_dust: {
    label: "Moderate Dust",
    pill: "moderate",
    colour: "var(--dust)",
    nextStep: "Wash when convenient",
    nextStepClass: "text-dust",
  },
  needs_cleaning: {
    label: "Needs Cleaning",
    pill: "needs_cleaning",
    colour: "var(--alarm)",
    nextStep: "Wash now",
    nextStepClass: "text-alarm",
  },
  unknown: {
    label: "Unknown",
    pill: "unknown",
    colour: "var(--ink-faint)",
    nextStep: "Run an analysis",
    nextStepClass: "text-faint",
  },
};

export function panelState(state: PanelState | string): StateStyle {
  return PANEL_STATE[state as PanelState] ?? PANEL_STATE.unknown;
}

/** The decision a run produced, coloured the way the panel states are. */
export function decisionPill(decision: string): string {
  if (decision === "spray_now") return "needs_cleaning";
  if (decision === "schedule_cleaning") return "moderate";
  return "clean";
}

export function healthLabel(status: HealthState | undefined): string {
  if (!status) return "Offline";
  return status.charAt(0).toUpperCase() + status.slice(1);
}

/** `latest_decision` is either a decision or a note saying there isn't one. */
export function hasDecision(
  value: import("./types").LatestDecision | null | undefined,
): value is import("./types").Decision {
  return Boolean(value && "decision_id" in value);
}
