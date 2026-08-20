"use client";

import { Icon } from "@/components/ui/Icon";
import { useToast } from "@/components/ui/Toast";
import type { Counts, LogEntry, Panel, Stats, SystemSettings } from "@/lib/types";

/**
 * Takes what is already on the page and hands it to the operator as a file.
 *
 * Nothing is fetched to export: the report, the panel list and the log are the
 * same rows the page rendered, so a download can never disagree with the screen
 * it came from.
 */

function today(): string {
  return new Date().toISOString().slice(0, 10);
}

function csvCell(value: unknown): string {
  const text = value == null ? "" : String(value);
  return /[",\n]/.test(text) ? `"${text.replace(/"/g, '""')}"` : text;
}

function save(filename: string, content: string, mime: string) {
  const url = URL.createObjectURL(new Blob([content], { type: mime }));
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

export function ExportButtons({
  stats,
  counts,
  panels,
  logs,
}: {
  stats: Stats;
  counts: Counts;
  panels: Panel[];
  logs: LogEntry[];
}) {
  const toast = useToast();

  function saved(filename: string) {
    toast({ message: `Saved ${filename}`, kind: "info", title: "Export" });
  }

  function exportReport() {
    const filename = `solarsage-report-${today()}.json`;
    save(
      filename,
      JSON.stringify(
        {
          generated_at: new Date().toISOString(),
          statistics: stats,
          panel_health: counts,
          recent_logs: logs.slice(0, 10),
        },
        null,
        2,
      ),
      "application/json",
    );
    saved(filename);
  }

  function exportPanels() {
    const filename = `solarsage-panels-${today()}.csv`;
    const lines = [
      "panel_id,status,dust_percent,confidence_percent,last_analysed,last_cleaned",
      ...panels.map((panel) =>
        [
          panel.id,
          panel.status,
          panel.dust_level == null ? "" : (panel.dust_level * 100).toFixed(1),
          panel.confidence == null ? "" : (panel.confidence * 100).toFixed(1),
          panel.last_analysed ?? "",
          panel.last_cleaned,
        ]
          .map(csvCell)
          .join(","),
      ),
    ];
    save(filename, lines.join("\n"), "text/csv");
    saved(filename);
  }

  function exportLogs() {
    const filename = `solarsage-logs-${today()}.txt`;
    const text = logs
      .map((log) => `[${log.timestamp}] ${log.level} ${log.component}: ${log.message}`)
      .join("\n");
    save(filename, text || "No log entries.", "text/plain");
    saved(filename);
  }

  return (
    <>
      <button className="btn btn--sm" type="button" onClick={exportReport}>
        <Icon name="download" size={14} /> Report (JSON)
      </button>
      <button className="btn btn--sm" type="button" onClick={exportPanels}>
        <Icon name="download" size={14} /> Panels (CSV)
      </button>
      <button className="btn btn--sm" type="button" onClick={exportLogs}>
        <Icon name="download" size={14} /> Logs (TXT)
      </button>
    </>
  );
}

/** The settings page exports the live configuration, which is not on this page. */
export function ExportSettingsButton({ settings }: { settings: SystemSettings }) {
  const toast = useToast();

  return (
    <button
      className="btn"
      type="button"
      onClick={() => {
        const filename = `solarsage-settings-${today()}.json`;
        save(filename, JSON.stringify(settings, null, 2), "application/json");
        toast({ message: `Saved ${filename}`, kind: "info", title: "Export" });
      }}
    >
      <Icon name="download" size={14} /> Export settings
    </button>
  );
}
