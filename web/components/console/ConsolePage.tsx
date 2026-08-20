import { Note } from "@/components/ui/Empty";
import { LiveRefresh } from "./LiveRefresh";

/**
 * The frame every console screen sits in: the bar that names the page and
 * carries its actions, the banner when the data underneath is synthetic, and
 * the timer that keeps the page current while an operator watches it.
 */
export function ConsolePage({
  eyebrow,
  title,
  actions,
  demo,
  refreshInterval,
  children,
}: {
  eyebrow: string;
  title: string;
  actions?: React.ReactNode;
  /** Set when this database was filled by Backend/demo.py. */
  demo: boolean;
  refreshInterval: number;
  children: React.ReactNode;
}) {
  return (
    <>
      <header className="topbar">
        <div className="topbar__titles">
          <p className="eyebrow eyebrow--plain">{eyebrow}</p>
          <h1 className="display topbar__title">{title}</h1>
        </div>
        <div className="topbar__actions">{actions}</div>
      </header>

      <div className="console-page">
        {demo && (
          <Note tone="demo" icon="alert">
            <strong>Synthetic data.</strong> No controller is reporting in, so this console was
            seeded from the panel image fixtures — the readings are a real classifier run on
            rendered frames, not a real array. Analyses and washes you trigger here are just as
            real, and just as synthetic.
          </Note>
        )}
        {children}
      </div>

      <LiveRefresh seconds={refreshInterval} />
    </>
  );
}
