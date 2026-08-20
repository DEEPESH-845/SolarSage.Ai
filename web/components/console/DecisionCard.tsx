import { ActionButton } from "./ActionButton";
import { analyzeAllAction } from "@/app/actions";
import { Counter } from "@/components/ui/Counter";
import { Empty, Note } from "@/components/ui/Empty";
import { Pill } from "@/components/ui/Pill";
import { decisionPill, hasDecision } from "@/lib/status";
import { stamp, titleCase } from "@/lib/format";
import type { LatestDecision } from "@/lib/types";

/**
 * The last thing the pipeline decided, and what it cost to reach that decision:
 * coverage, confidence, the energy the dust is holding back and whether washing
 * pays for itself. Empty until something has been analysed — the panel says so
 * rather than showing zeroes that look like measurements.
 */
export function DecisionCard({ decision }: { decision: LatestDecision | null }) {
  if (!hasDecision(decision)) {
    return (
      <article className="panel dash__decision">
        <div className="panel__head">
          <h2 className="panel__title">Last decision</h2>
        </div>
        <Empty icon="scan" tall>
          <p>
            Nothing has been analysed yet. Run the analyser and the decision it makes will show up
            here.
          </p>
          <ActionButton perform={analyzeAllAction} label="Analyse all panels" busyLabel="Analysing…" variant="sun" />
        </Empty>
      </article>
    );
  }

  const analysis = decision.analysis;
  const autoClean = decision.auto_clean;

  return (
    <article className="panel dash__decision">
      <div className="panel__head">
        <h2 className="panel__title">Last decision</h2>
        <Pill tone={decisionPill(decision.decision)}>{titleCase(decision.decision)}</Pill>
      </div>

      <p className="decision__action">{decision.action}</p>

      <div className="decision__grid">
        <div>
          <p className="label">Panel</p>
          <p className="mono decision__value">{decision.panel_id}</p>
        </div>
        <div>
          <p className="label">Dust coverage</p>
          <Counter
            className="numeral numeral--sm decision__value text-dust"
            value={Number((decision.dust_level * 100).toFixed(1))}
            decimals={1}
            suffix="%"
          />
        </div>
        <div>
          <p className="label">Confidence</p>
          <Counter
            className="numeral numeral--sm decision__value"
            value={Number((decision.confidence * 100).toFixed(1))}
            decimals={1}
            suffix="%"
          />
        </div>
        <div>
          <p className="label">Water planned</p>
          <p className="numeral numeral--sm decision__value">
            {decision.water_volume}
            <span className="decision__unit">ml</span>
          </p>
        </div>
      </div>

      {analysis && (
        <div className="econ">
          <div>
            <p className="label">Lost per day</p>
            <p className="mono">
              {analysis.daily_power_loss_kwh} kWh ({analysis.power_loss_percentage}%)
            </p>
          </div>
          <div>
            <p className="label">Saved per week</p>
            <p className="mono text-water">${analysis.estimated_savings_weekly}</p>
          </div>
          <div>
            <p className="label">Payback</p>
            <p className="mono">
              {analysis.payback_period_days} days{" "}
              {analysis.roi_percentage != null && (
                <span className={analysis.roi_percentage < 0 ? "text-alarm" : "text-water"}>
                  ({analysis.roi_percentage}% ROI)
                </span>
              )}
            </p>
          </div>
          <div>
            <p className="label">Best window</p>
            <p className="mono">{titleCase(analysis.optimal_cleaning_window)}</p>
          </div>
        </div>
      )}

      {autoClean &&
        ("error" in autoClean ? (
          <Note tone="error" icon="alert">
            Auto-wash refused: {autoClean.error}
          </Note>
        ) : (
          <Note tone="ok" icon="check">
            Auto-washed with {autoClean.water_used_ml}ml over {autoClean.duration_seconds}s.
          </Note>
        ))}

      {analysis?.insights?.length ? (
        <ul className="insights">
          {analysis.insights.slice(0, 3).map((line) => (
            <li key={line}>{line}</li>
          ))}
        </ul>
      ) : null}

      <p className="mono text-faint decision__stamp">{stamp(decision.timestamp)} UTC</p>
    </article>
  );
}
