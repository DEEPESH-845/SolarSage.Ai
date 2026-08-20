import { Icon } from "@/components/ui/Icon";
import { Reveal, Stagger } from "@/components/ui/Motion";
import type { DecisionAnalysis, Health, SystemSettings } from "@/lib/types";

/**
 * The four stages, in the order they run. Each card's footer carries a real
 * number from the last run rather than a claim — the loop is only interesting
 * because it is measured end to end.
 */
export function LoopSection({
  settings,
  health,
  analysis,
  panelCount,
}: {
  settings: SystemSettings;
  health: Health | null;
  analysis: DecisionAnalysis | null;
  panelCount: number;
}) {
  const cameraStatus = health?.camera_status ?? "offline";

  return (
    <section className="section section--loop" id="loop">
      <div className="shell">
        <div className="section__head">
          <Reveal as="p" className="eyebrow">
            How the loop closes
          </Reveal>
          <Reveal as="h2" className="display" delay={0.08}>
            Four steps, then it starts again.
          </Reveal>
          <Reveal as="p" className="lede" delay={0.14}>
            These stages run in order, and each one hands the next a number rather than an opinion.
            Nothing sprays until the last step has a reason to.
          </Reveal>
        </div>
      </div>

      <div className="loop" id="loop-track">
        <Stagger className="loop__rail" step={0.12}>
          <article className="stage">
            <p className="stage__index mono">01</p>
            <h3 className="display stage__title">Capture</h3>
            <p className="stage__body">
              An ESP32 at the array pushes one frame per panel with a sensor sweep beside it —
              temperature, humidity, irradiance, output.
            </p>
            <p className="stage__meta mono">
              <Icon name="camera" size={14} /> {panelCount} cameras ·{" "}
              {cameraStatus[0].toUpperCase() + cameraStatus.slice(1)}
            </p>
          </article>

          <article className="stage">
            <p className="stage__index mono">02</p>
            <h3 className="display stage__title">Classify</h3>
            <p className="stage__body">
              OpenCV scores dust coverage on the frame and returns a confidence next to it, so a bad
              photo cannot pass itself off as a clean panel.
            </p>
            <p className="stage__meta mono">
              <Icon name="scan" size={14} /> coverage + confidence, ~
              {analysis?.processing_time_ms ?? "—"} ms
            </p>
          </article>

          <article className="stage">
            <p className="stage__index mono">03</p>
            <h3 className="display stage__title">Price</h3>
            <p className="stage__body">
              Coverage becomes kilowatt-hours: what the dust costs per day, what a wash costs, and
              how many days it takes to pay that back.
            </p>
            <p className="stage__meta mono">
              <Icon name="money" size={14} /> last run: pays back in{" "}
              {analysis?.payback_period_days ?? "—"} days
            </p>
          </article>

          <article className="stage stage--act">
            <p className="stage__index mono">04</p>
            <h3 className="display stage__title">Act</h3>
            <p className="stage__body">
              Above {settings.dust_threshold}% coverage the valve opens for {settings.spray_duration}{" "}
              seconds at {settings.water_pressure} pressure. Between {settings.schedule_threshold}%
              and {settings.dust_threshold}% it only schedules. Below that, nothing happens.
            </p>
            <p className="stage__meta mono">
              <Icon name="droplet" size={14} /> {settings.spray_duration * 20} ml per cycle
            </p>
          </article>
        </Stagger>
      </div>
    </section>
  );
}
