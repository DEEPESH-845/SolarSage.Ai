import { Rail } from "@/components/console/Rail";
import { getSettings } from "@/lib/api";
import "@/styles/console.css";

/**
 * The console shell. Only the rail lives here — each page draws its own title
 * bar, because the title, the eyebrow and the actions are the page's own.
 */
/**
 * Live hardware state: rendered per request, never prerendered. This also keeps
 * the build independent of the backend — the API is a separate deployment, and
 * `next build` must not need it to be up.
 */
export const dynamic = "force-dynamic";

export default async function ConsoleLayout({ children }: { children: React.ReactNode }) {
  // The rail shows whether cleaning is allowed at all, which every page needs
  // and none of them own.
  const settings = await getSettings().catch(() => null);

  return (
    <div className="console-body">
      <Rail mode={settings?.system_mode ?? "active"} />
      {children}
    </div>
  );
}
