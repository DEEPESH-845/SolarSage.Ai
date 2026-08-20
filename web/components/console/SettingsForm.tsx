"use client";

import { useState, useTransition, type CSSProperties } from "react";
import { resetSettingsAction, saveSettingsAction, setSystemModeAction } from "@/app/actions";
import { ExportSettingsButton } from "./ExportButtons";
import { Icon } from "@/components/ui/Icon";
import { useConfirm } from "@/components/ui/Confirm";
import { useToast } from "@/components/ui/Toast";
import type { CleaningFrequency, SystemSettings, WaterPressure } from "@/lib/types";

/**
 * Everything the system does on its own, as one form.
 *
 * The form owns a draft of the settings and writes it in one call — these
 * values act (a threshold opens a valve, an interval becomes a browser timer),
 * so they are saved deliberately rather than on every keystroke. The backend
 * validates each one again; the only check here is the one the operator needs
 * to see immediately, that the two thresholds cannot cross.
 */

/** The id the title-bar Save button targets through its `form` attribute. */
export const SETTINGS_FORM_ID = "settings-form";

const PRESSURES: WaterPressure[] = ["low", "medium", "high"];
const FREQUENCIES: CleaningFrequency[] = ["daily", "weekly", "biweekly", "monthly"];

export function SettingsForm({
  settings,
  children,
}: {
  settings: SystemSettings;
  /** The system-state panel, rendered on the server and placed first in the
   *  grid — it belongs beside these panels, not above them. */
  children?: React.ReactNode;
}) {
  const [draft, setDraft] = useState(settings);
  const [pending, startTransition] = useTransition();
  const confirm = useConfirm();
  const toast = useToast();

  function set<K extends keyof SystemSettings>(key: K, value: SystemSettings[K]) {
    setDraft((current) => ({ ...current, [key]: value }));
  }

  function save() {
    if (draft.schedule_threshold >= draft.dust_threshold) {
      toast({
        message: "The schedule threshold has to stay below the immediate threshold.",
        kind: "error",
      });
      return;
    }

    startTransition(async () => {
      const result = await saveSettingsAction({
        dust_threshold: draft.dust_threshold,
        schedule_threshold: draft.schedule_threshold,
        spray_duration: draft.spray_duration,
        water_pressure: draft.water_pressure,
        auto_clean: draft.auto_clean,
        notifications: draft.notifications,
        refresh_interval: draft.refresh_interval,
        alert_email: draft.alert_email,
        cleaning_frequency: draft.cleaning_frequency,
        preferred_time: draft.preferred_time,
      });
      toast({ message: result.message, kind: result.ok ? "success" : "error" });
    });
  }

  function reset() {
    startTransition(async () => {
      const confirmed = await confirm({
        title: "Reset every setting?",
        message: "Thresholds, schedule and notification settings all go back to their defaults.",
        confirmLabel: "Reset",
        danger: true,
      });
      if (!confirmed) return;
      const result = await resetSettingsAction();
      toast({ message: result.message, kind: result.ok ? "success" : "error" });
    });
  }

  function toggleMode() {
    const next = draft.system_mode === "paused" ? "active" : "paused";
    startTransition(async () => {
      const confirmed = await confirm({
        title: next === "paused" ? "Pause cleaning?" : "Resume cleaning?",
        message:
          next === "paused"
            ? "Analysis keeps running, but no valve opens until the system is resumed."
            : "Washing becomes possible again, by hand and automatically.",
        confirmLabel: next === "paused" ? "Pause" : "Resume",
        danger: next === "paused",
      });
      if (!confirmed) return;
      const result = await setSystemModeAction(next);
      toast({ message: result.message, kind: result.ok ? "success" : "error" });
      if (result.ok) set("system_mode", next);
    });
  }

  return (
    <form
      id={SETTINGS_FORM_ID}
      onSubmit={(event) => {
        event.preventDefault();
        save();
      }}
      className="settings__form"
    >
      <div className="settings__grid">
        {children}

        <section className="panel">
          <div className="panel__head">
            <h2 className="panel__title">Dust thresholds</h2>
          </div>

          <Slider
            id="dust_threshold"
            label="Wash immediately above"
            value={draft.dust_threshold}
            hint="Coverage past this point opens the valve on the next analysis."
            onChange={(value) => set("dust_threshold", value)}
          />
          <Slider
            id="schedule_threshold"
            label="Schedule a wash above"
            value={draft.schedule_threshold}
            hint="Between the two thresholds a panel is flagged but not sprayed."
            onChange={(value) => set("schedule_threshold", value)}
          />

          <div
            className="threshold-map"
            aria-hidden="true"
            style={
              {
                "--schedule": `${draft.schedule_threshold}%`,
                "--immediate": `${draft.dust_threshold}%`,
              } as CSSProperties
            }
          >
            <span>Leave alone</span>
            <span>Schedule</span>
            <span>Wash now</span>
          </div>
        </section>

        <section className="panel">
          <div className="panel__head">
            <h2 className="panel__title">Spray</h2>
          </div>

          <label className="field" htmlFor="spray_duration">
            <span className="field__label">
              <span>Cycle length</span>
              <span className="mono text-faint">seconds</span>
            </span>
            <input
              className="input"
              type="number"
              id="spray_duration"
              min={1}
              max={60}
              value={draft.spray_duration}
              onChange={(event) => set("spray_duration", Number(event.target.value))}
            />
            <span className="field__hint">
              The pump moves 20 ml per second, so this cycle uses {draft.spray_duration * 20} ml of
              the {draft.water_pressure}-pressure line.
            </span>
          </label>

          <label className="field" htmlFor="water_pressure">
            <span className="field__label">
              <span>Line pressure</span>
            </span>
            <select
              className="select"
              id="water_pressure"
              value={draft.water_pressure}
              onChange={(event) => set("water_pressure", event.target.value as WaterPressure)}
            >
              {PRESSURES.map((level) => (
                <option key={level} value={level}>
                  {level[0].toUpperCase() + level.slice(1)}
                </option>
              ))}
            </select>
          </label>

          <label className="switch field">
            <input
              type="checkbox"
              id="auto_clean"
              checked={draft.auto_clean}
              onChange={(event) => set("auto_clean", event.target.checked)}
            />
            <span className="switch__text">
              Wash without asking{" "}
              <span className="field__hint">
                When an analysis crosses the immediate threshold, the valve opens straight away.
              </span>
            </span>
          </label>
        </section>

        <section className="panel">
          <div className="panel__head">
            <h2 className="panel__title">Schedule &amp; alerts</h2>
          </div>

          <label className="field" htmlFor="cleaning_frequency">
            <span className="field__label">
              <span>Preferred cadence</span>
            </span>
            <select
              className="select"
              id="cleaning_frequency"
              value={draft.cleaning_frequency}
              onChange={(event) => set("cleaning_frequency", event.target.value as CleaningFrequency)}
            >
              {FREQUENCIES.map((frequency) => (
                <option key={frequency} value={frequency}>
                  {frequency[0].toUpperCase() + frequency.slice(1)}
                </option>
              ))}
            </select>
            <span className="field__hint">Advisory only — a threshold crossing still wins.</span>
          </label>

          <label className="field" htmlFor="preferred_time">
            <span className="field__label">
              <span>Preferred time of day</span>
            </span>
            <input
              className="input"
              type="time"
              id="preferred_time"
              value={draft.preferred_time}
              onChange={(event) => set("preferred_time", event.target.value)}
            />
          </label>

          <label className="field" htmlFor="alert_email">
            <span className="field__label">
              <span>Alert address</span>
            </span>
            <input
              className="input"
              type="email"
              id="alert_email"
              value={draft.alert_email}
              placeholder="operator@example.com"
              onChange={(event) => set("alert_email", event.target.value)}
            />
          </label>

          <label className="field" htmlFor="refresh_interval">
            <span className="field__label">
              <span>Console refresh</span>
              <span className="mono text-faint">seconds</span>
            </span>
            <input
              className="input"
              type="number"
              id="refresh_interval"
              min={5}
              max={600}
              value={draft.refresh_interval}
              onChange={(event) => set("refresh_interval", Number(event.target.value))}
            />
          </label>

          <label className="switch field">
            <input
              type="checkbox"
              id="notifications"
              checked={draft.notifications}
              onChange={(event) => set("notifications", event.target.checked)}
            />
            <span className="switch__text">Send notifications for washes and faults</span>
          </label>
        </section>
      </div>

      <section className="panel">
        <div className="panel__head">
          <h2 className="panel__title">Actions</h2>
          <span className="mono text-faint">
            Pausing blocks every valve; analysis keeps running
          </span>
        </div>

        <div className="settings__actions">
          <button className="btn btn--sun" type="submit" disabled={pending} aria-busy={pending || undefined}>
            {pending ? <span className="spinner" aria-hidden="true" /> : <Icon name="check" size={14} />}
            {pending ? "Saving…" : "Save changes"}
          </button>
          <ExportSettingsButton settings={draft} />
          <button className="btn" type="button" onClick={reset} disabled={pending}>
            <Icon name="refresh" size={14} /> Reset to defaults
          </button>
          {draft.system_mode === "paused" ? (
            <button className="btn btn--water" type="button" onClick={toggleMode} disabled={pending}>
              <Icon name="play" size={14} /> Resume cleaning
            </button>
          ) : (
            <button className="btn btn--danger" type="button" onClick={toggleMode} disabled={pending}>
              <Icon name="pause" size={14} /> Pause cleaning
            </button>
          )}
        </div>
      </section>
    </form>
  );
}

/** A range input that paints its own track, and the value beside its label. */
function Slider({
  id,
  label,
  value,
  hint,
  onChange,
}: {
  id: string;
  label: string;
  value: number;
  hint: string;
  onChange: (value: number) => void;
}) {
  return (
    <label className="field" htmlFor={id}>
      <span className="field__label">
        <span>{label}</span>
        <span className="mono text-sun">{value}%</span>
      </span>
      <input
        type="range"
        id={id}
        min={0}
        max={100}
        value={value}
        style={{ "--fill": `${value}%` } as CSSProperties}
        onChange={(event) => onChange(Number(event.target.value))}
      />
      <span className="field__hint">{hint}</span>
    </label>
  );
}
