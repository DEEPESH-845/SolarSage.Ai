import type { Metadata } from "next";
import { ConsolePage } from "@/components/console/ConsolePage";
import { HealthCard } from "@/components/console/HealthCard";
import { SETTINGS_FORM_ID, SettingsForm } from "@/components/console/SettingsForm";
import { Icon } from "@/components/ui/Icon";
import { getOverview } from "@/lib/api";

/**
 * Live hardware state: rendered per request, never prerendered. This also keeps
 * the build independent of the backend — the API is a separate deployment, and
 * `next build` must not need it to be up.
 */
export const dynamic = "force-dynamic";

export const metadata: Metadata = { title: "Settings" };

export default async function SettingsPage() {
  const { health, stats, settings } = await getOverview();

  return (
    <ConsolePage
      eyebrow="What the system does on its own"
      title="Settings"
      demo={Boolean(settings.demo_seeded_at)}
      refreshInterval={settings.refresh_interval}
      actions={
        // Submits the form below through the HTML `form` attribute, so the bar
        // button and the one inside the form are the same action.
        <button className="btn btn--sm btn--sun" type="submit" form={SETTINGS_FORM_ID}>
          <Icon name="check" size={14} /> Save changes
        </button>
      }
    >
      <SettingsForm settings={settings}>
        <HealthCard health={health} stats={stats} showReading />
      </SettingsForm>
    </ConsolePage>
  );
}
