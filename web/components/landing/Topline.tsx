"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Icon } from "@/components/ui/Icon";
import { MagneticLink } from "@/components/ui/Motion";
import { clsx } from "@/lib/clsx";

const SECTIONS = [
  { href: "#cost", label: "The cost" },
  { href: "#loop", label: "The loop" },
  { href: "#field", label: "In the field" },
  { href: "#console", label: "Console" },
];

/** The header thickens once the page has scrolled past the hero's first band,
 *  so the transparent version never sits over moving artwork. */
export function Topline() {
  const [stuck, setStuck] = useState(false);

  useEffect(() => {
    const apply = () => setStuck(window.scrollY > 40);
    apply();
    window.addEventListener("scroll", apply, { passive: true });
    return () => window.removeEventListener("scroll", apply);
  }, []);

  return (
    <header className={clsx("topline", stuck && "topline--stuck")}>
      <div className="shell topline__inner">
        <Link className="wordmark" href="/">
          <span className="wordmark__mark" aria-hidden="true" />
          <span>
            SolarSage<span className="text-sun">.</span>
          </span>
        </Link>

        <nav className="topline__nav" aria-label="Sections">
          {SECTIONS.map((section) => (
            <a key={section.href} href={section.href}>
              {section.label}
            </a>
          ))}
        </nav>

        <MagneticLink className="btn btn--sun btn--sm" href="/dashboard" strength={0.2}>
          Open the console <Icon name="arrow" size={14} />
        </MagneticLink>
      </div>
    </header>
  );
}
