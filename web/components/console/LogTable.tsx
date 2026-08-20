"use client";

import { useMemo, useState } from "react";
import { Empty } from "@/components/ui/Empty";
import { stamp } from "@/lib/format";
import type { LogEntry } from "@/lib/types";

/**
 * The activity log, filtered as you type. The filter is client-side on purpose:
 * the page already holds every row it will show, and a round trip per keystroke
 * would be slower than the filter is worth.
 */
export function LogTable({ logs }: { logs: LogEntry[] }) {
  const [needle, setNeedle] = useState("");

  const shown = useMemo(() => {
    const query = needle.trim().toLowerCase();
    if (!query) return logs;
    return logs.filter((log) =>
      `${log.component} ${log.message} ${log.level}`.toLowerCase().includes(query),
    );
  }, [logs, needle]);

  return (
    <section className="panel">
      <div className="panel__head">
        <h2 className="panel__title">Activity log</h2>
        <div className="row">
          <span className="mono text-faint">
            {needle ? `${shown.length} of ${logs.length}` : `${logs.length} entries`}
          </span>
          <label className="visually-hidden" htmlFor="log-filter">
            Filter the log
          </label>
          <input
            className="input"
            id="log-filter"
            type="search"
            placeholder="Filter by panel, component or message"
            style={{ width: "min(22rem, 60vw)" }}
            value={needle}
            onChange={(event) => setNeedle(event.target.value)}
          />
        </div>
      </div>

      {logs.length ? (
        <div className="table-wrap">
          <table className="data">
            <thead>
              <tr>
                <th>Time (UTC)</th>
                <th>Component</th>
                <th>Message</th>
                <th>Level</th>
              </tr>
            </thead>
            <tbody>
              {shown.map((log) => (
                <tr key={log.id}>
                  <td className="mono text-faint">{stamp(log.timestamp, "")}</td>
                  <td className="mono">{log.component}</td>
                  <td>{log.message}</td>
                  <td>
                    <span className={`loglevel loglevel--${log.level}`}>{log.level}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <Empty icon="log">
          Nothing has been logged yet. Run an analysis and entries will appear here.
        </Empty>
      )}
    </section>
  );
}
