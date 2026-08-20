"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Icon } from "@/components/ui/Icon";
import { Pill } from "@/components/ui/Pill";
import { clsx } from "@/lib/clsx";
import type { SystemMode } from "@/lib/types";

const LINKS = [
  { href: "/dashboard", label: "Dashboard", icon: "gauge" },
  { href: "/panels", label: "Panels", icon: "grid" },
  { href: "/reports", label: "Reports", icon: "chart" },
  { href: "/settings", label: "Settings", icon: "sliders" },
] as const;

/** The fixed rail of destinations, and the one fact that belongs beside them:
 *  whether the system is allowed to open a valve at all. */
export function Rail({ mode }: { mode: SystemMode }) {
  const pathname = usePathname();

  return (
    <aside className="rail">
      <Link className="wordmark rail__brand" href="/">
        <span className="wordmark__mark" aria-hidden="true" />
        <span className="rail__brandtext">
          SolarSage<span className="text-sun">.</span>
        </span>
      </Link>

      <nav className="rail__nav" aria-label="Console">
        {LINKS.map((link) => {
          const current = pathname === link.href;
          return (
            <Link
              key={link.href}
              className={clsx("rail__link", current && "is-current")}
              href={link.href}
              aria-current={current ? "page" : undefined}
            >
              <Icon name={link.icon} size={17} />
              <span>{link.label}</span>
            </Link>
          );
        })}
      </nav>

      <div className="rail__foot">
        <Pill tone={mode}>{mode === "active" ? "Cleaning live" : "Paused"}</Pill>
      </div>
    </aside>
  );
}
