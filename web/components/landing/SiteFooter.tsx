import Link from "next/link";

const CONSOLE_LINKS = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/panels", label: "Panels" },
  { href: "/reports", label: "Reports" },
  { href: "/settings", label: "Settings" },
];

export function SiteFooter() {
  return (
    <footer className="footer">
      <div className="shell">
        <div className="busbars" />
        <div className="footer__inner">
          <div>
            <Link className="wordmark" href="/">
              <span className="wordmark__mark" aria-hidden="true" />
              <span>
                SolarSage<span className="text-sun">.</span>
              </span>
            </Link>
            <p className="mono text-faint footer__tag">
              Autonomous soiling control for photovoltaic arrays.
            </p>
          </div>

          <nav className="footer__links" aria-label="Console">
            {CONSOLE_LINKS.map((link) => (
              <Link key={link.href} href={link.href}>
                {link.label}
              </Link>
            ))}
          </nav>

          <p className="mono text-faint footer__meta">
            ESP32 · OpenCV · FastAPI · Next.js
            <br />© {new Date().getFullYear()} SolarSage
          </p>
        </div>
      </div>
    </footer>
  );
}
