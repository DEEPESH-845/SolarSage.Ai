import type { Metadata } from "next";
import { ConsolePreview } from "@/components/landing/ConsolePreview";
import { CostSection } from "@/components/landing/CostSection";
import { FieldSection } from "@/components/landing/FieldSection";
import { Hero } from "@/components/landing/Hero";
import { Ledger } from "@/components/landing/Ledger";
import { LoopSection } from "@/components/landing/LoopSection";
import { SiteFooter } from "@/components/landing/SiteFooter";
import { Topline } from "@/components/landing/Topline";
import { overviewFeed, telemetryFeed } from "@/lib/feed";
import { hasDecision } from "@/lib/status";
import "@/styles/landing.css";

/**
 * Live hardware state: rendered per request, never prerendered. This also keeps
 * the build independent of the backend — the API is a separate deployment, and
 * `next build` must not need it to be up.
 */
export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "SolarSage — the array that washes itself",
};

/**
 * The landing page is the same data as the console, told as an argument: what
 * soiling costs, how the loop closes it, what the hardware actually reported,
 * and what the system has done so far. Every figure on it comes from the
 * database — there is no marketing copy standing in for a measurement.
 */
export default async function LandingPage() {
  const { data: overview, source } = await overviewFeed();
  const telemetry = await telemetryFeed(source);
  const { health, panels, counts, stats, latest_decision, settings } = overview;
  const analysis = hasDecision(latest_decision) ? latest_decision.analysis : null;

  return (
    <div className="landing">
      <Topline />
      <Hero panels={panels} health={health} counts={counts} />
      <CostSection decision={latest_decision} />
      <LoopSection
        settings={settings}
        health={health}
        analysis={analysis}
        panelCount={panels.length}
      />
      <FieldSection telemetry={telemetry} panelCount={panels.length} />
      <ConsolePreview panels={panels} counts={counts} health={health} />
      <Ledger stats={stats} />
      <SiteFooter />
    </div>
  );
}
