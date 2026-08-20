import { describe, expect, it } from "vitest";
import { decisionPill, hasDecision, panelState } from "../status";
import type { Decision } from "../types";

/**
 * One table decides what a state looks like. If a pill and the meter beside it
 * ever disagree, it is because something bypassed this — so the mapping is
 * pinned here, including the one state whose CSS class is not its name.
 */
describe("panel state", () => {
  it("maps every state to a label, a colour and a next step", () => {
    expect(panelState("clean").label).toBe("Clean");
    expect(panelState("needs_cleaning").nextStep).toBe("Wash now");
    expect(panelState("moderate_dust").colour).toBe("var(--dust)");
  });

  it("keeps the CSS modifier for moderate dust, which is not its name", () => {
    expect(panelState("moderate_dust").pill).toBe("moderate");
    expect(panelState("needs_cleaning").pill).toBe("needs_cleaning");
  });

  it("falls back to unknown for a state it has never seen", () => {
    expect(panelState("on_fire").label).toBe("Unknown");
  });
});

describe("decision", () => {
  it("colours a decision the way the panel it acted on is coloured", () => {
    expect(decisionPill("spray_now")).toBe("needs_cleaning");
    expect(decisionPill("schedule_cleaning")).toBe("moderate");
    expect(decisionPill("no_action")).toBe("clean");
  });

  it("tells a real decision from the note that stands in for one", () => {
    expect(hasDecision({ message: "No decisions made yet. Try /analyze first!" })).toBe(false);
    expect(hasDecision(null)).toBe(false);
    expect(hasDecision({ decision_id: "decision_1" } as Decision)).toBe(true);
  });
});
