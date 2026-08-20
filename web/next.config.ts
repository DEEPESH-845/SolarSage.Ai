import type { NextConfig } from "next";

/**
 * The Python API is a separate deployment (see README). Nothing here proxies to
 * it: pages fetch it server-side, so the browser only ever talks to this app.
 */
const nextConfig: NextConfig = {
  reactStrictMode: true,
  // The console shows live hardware state; a cached HTML page would lie.
  async headers() {
    return [
      {
        source: "/(dashboard|panels|reports|settings)",
        headers: [{ key: "Cache-Control", value: "no-store" }],
      },
    ];
  },
};

export default nextConfig;
