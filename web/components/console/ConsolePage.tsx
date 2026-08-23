import { Note } from "@/components/ui/Empty";
import { Pill } from "@/components/ui/Pill";
import { LiveRefresh } from "./LiveRefresh";
import type { DataSource } from "@/lib/feed";

/**
 * The frame every console screen sits in: the bar that names the page and
 * carries its actions, the banner that says where the numbers underneath came
 * from, and the timer that keeps the page current while an operator watches it.
 *
 * There are three things the banner can be saying, and they are not the same:
 * the backend is unreachable and this is the recorded fixture run; the backend
 * is live but its database was seeded rather than filled by hardware; or the
 * backend is live and reporting a real array, in which case it says nothing.
 */
export function ConsolePage({
  eyebrow,
  title,
  actions,
  source,
  reason,
  seeded,
  refreshInterval,
  children,
}: {
  eyebrow: string;
  title: string;
  actions?: React.ReactNode;
  /** Whether the backend answered, or the console fell back to lib/demo.ts. */
  source: DataSource;
  /** Why the backend was passed over — shown only when it was. */
  reason?: string | null;
  /** Set when the live database was filled by Backend/demo.py. */
  seeded: boolean;
  refreshInterval: number;
  children: React.ReactNode;
}) {
  const offline = source === "demo";

  return (
    <>
      <header className="topbar">
        <div className="topbar__titles">
          {/* Sits with the page title rather than in the rail so it survives the
              mobile layout, and so it is read from the same fetch as the banner
              below — two sources for one fact let them contradict each other. */}
          <p className="eyebrow eyebrow--plain topbar__eyebrow">
            {offline ? (
              <Pill tone="needs_cleaning">Demo data</Pill>
            ) : (
              <Pill tone="clean" live>
                Live data
              </Pill>
            )}
            <span>{eyebrow}</span>
          </p>
          <h1 className="display topbar__title">{title}</h1>
        </div>
        <div className="topbar__actions">{actions}</div>
      </header>

      <div className="console-page">
        {offline ? (
          <Note tone="offline" icon="wifi">
            <strong>Backend unavailable — showing demo data.</strong> {reason} Every figure below
            is a transcript of a recorded pipeline run against the panel image fixtures, not a
            live array. The controls still work — they will report the same failure — and this page
            returns to live data on its own once the API answers.
          </Note>
        ) : (
          seeded && (
            <Note tone="demo" icon="alert">
              <strong>Synthetic data.</strong> No controller is reporting in, so this console was
              seeded from the panel image fixtures — the readings are a real classifier run on
              rendered frames, not a real array. Analyses and washes you trigger here are just as
              real, and just as synthetic.
            </Note>
          )
        )}
        {children}
      </div>

      {/* Left running while degraded on purpose: each tick re-attempts the
          fetch, so a backend that was merely cold-starting brings the console
          back to live data without anyone reloading it. */}
      <LiveRefresh seconds={refreshInterval} />
    </>
  );
}
