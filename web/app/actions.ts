"use server";

import { revalidatePath } from "next/cache";
import * as api from "@/lib/api";
import { ApiError } from "@/lib/api";
import type { ActionResult, PanelDetail, SystemMode, SystemSettings } from "@/lib/types";

/**
 * Everything the console can *do*.
 *
 * Each action runs on the server, calls the backend, and returns a plain
 * `{ok, message}` the calling component turns into a toast — a failure is a
 * result to show the operator, never an exception thrown at the browser. After
 * a successful write the console pages are revalidated, so the numbers on
 * screen come from the database rather than from optimistic guesswork.
 */

/** Console routes all read the same state, so one write refreshes all of them. */
function refreshConsole() {
  revalidatePath("/", "layout");
}

async function run(work: () => Promise<ActionResult>): Promise<ActionResult> {
  try {
    const result = await work();
    if (result.ok) refreshConsole();
    return result;
  } catch (error) {
    const message =
      error instanceof ApiError ? error.message : "The system did not answer. Try again.";
    return { ok: false, message };
  }
}

export async function analyzePanelAction(panelId: string): Promise<ActionResult> {
  return run(async () => {
    const decision = await api.analyzePanel(panelId);
    return { ok: true, message: `${panelId}: ${decision.action}` };
  });
}

export async function sprayPanelAction(panelId: string): Promise<ActionResult> {
  return run(async () => {
    const spray = await api.sprayPanel(panelId);
    return {
      ok: true,
      message: `${panelId} cleaned — ${spray.water_used_ml.toFixed(0)}ml over ${spray.duration_seconds.toFixed(0)}s.`,
    };
  });
}

export async function analyzeAllAction(): Promise<ActionResult> {
  return run(async () => {
    const result = await api.analyzeAll();
    return { ok: true, message: result.message, failures: result.failures };
  });
}

export async function sprayManyAction(scope: "dirty" | "all"): Promise<ActionResult> {
  return run(async () => {
    const result = await api.sprayMany(scope);
    return { ok: true, message: result.message, failures: result.failures };
  });
}

export async function refillTankAction(): Promise<ActionResult> {
  return run(async () => {
    await api.refillTank();
    return { ok: true, message: "Water tank refilled" };
  });
}

export async function saveSettingsAction(values: Partial<SystemSettings>): Promise<ActionResult> {
  return run(async () => {
    await api.updateSettings(values);
    return { ok: true, message: "Settings saved" };
  });
}

export async function resetSettingsAction(): Promise<ActionResult> {
  return run(async () => {
    await api.resetSettings();
    return { ok: true, message: "Settings back to defaults" };
  });
}

export async function setSystemModeAction(mode: SystemMode): Promise<ActionResult> {
  return run(async () => {
    await api.updateSettings({ system_mode: mode });
    return { ok: true, message: mode === "paused" ? "Cleaning paused" : "Cleaning resumed" };
  });
}

/**
 * A read, not a write — the detail drawer opens on demand, so its data cannot
 * come from the page's own render. It still runs on the server, which keeps the
 * backend URL out of the browser like every other call here.
 */
export async function loadPanelDetailAction(
  panelId: string,
): Promise<{ ok: true; detail: PanelDetail } | { ok: false; message: string }> {
  try {
    return { ok: true, detail: await api.getPanelDetail(panelId) };
  } catch (error) {
    const message =
      error instanceof ApiError ? error.message : "Could not load this panel.";
    return { ok: false, message };
  }
}
