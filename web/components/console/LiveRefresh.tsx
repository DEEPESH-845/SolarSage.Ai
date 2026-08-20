"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

/**
 * Keeps an open console page current.
 *
 * Rather than patching values into the DOM, this re-runs the server render on a
 * timer: the page reads the database again and React swaps in what changed. One
 * code path draws the page whether it is the first paint or the twentieth
 * refresh, so a live value can never disagree with the markup around it.
 *
 * A hidden tab polls nothing — an operator with the console in a background
 * window should not be running the pipeline's queries every 30 seconds.
 */
export function LiveRefresh({ seconds }: { seconds: number }) {
  const router = useRouter();

  useEffect(() => {
    if (!seconds) return;
    const interval = setInterval(
      () => {
        if (!document.hidden) router.refresh();
      },
      Math.max(5, seconds) * 1000,
    );
    return () => clearInterval(interval);
  }, [seconds, router]);

  return null;
}
