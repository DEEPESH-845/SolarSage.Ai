import type { Metadata, Viewport } from "next";
import Script from "next/script";
import { ConfirmProvider } from "@/components/ui/Confirm";
import { ToastProvider } from "@/components/ui/Toast";
import { ScrollProgress } from "@/components/ui/Motion";
import "@/styles/core.css";

export const metadata: Metadata = {
  title: {
    default: "SolarSage — autonomous soiling control",
    template: "%s — SolarSage",
  },
  description:
    "SolarSage watches every panel in the array for dust, prices the energy it costs, and opens the valve only when cleaning pays for itself.",
  icons: { icon: "/img/mark.svg" },
};

export const viewport: Viewport = {
  colorScheme: "dark",
  themeColor: "#05091a",
};

/**
 * The document every page is drawn into: fonts, the global stylesheet, and the
 * two providers that anything below can reach for — toasts to report what an
 * action did, and a confirm dialog for anything that opens a valve.
 */
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="no-js">
      <head>
        {/* Unversioned on purpose: core.css asks for these exact URLs, and a
            preload that differs by a query string is a second download. */}
        <link rel="preload" href="/fonts/archivo-var-latin.woff2" as="font" type="font/woff2" crossOrigin="" />
        <link rel="preload" href="/fonts/plex-sans-var-latin.woff2" as="font" type="font/woff2" crossOrigin="" />
        <Script src="/boot.js" strategy="beforeInteractive" />
      </head>
      <body>
        <a className="skip-link" href="#main">
          Skip to content
        </a>
        <ScrollProgress />
        <ToastProvider>
          <ConfirmProvider>
            <main id="main">{children}</main>
          </ConfirmProvider>
        </ToastProvider>
      </body>
    </html>
  );
}
