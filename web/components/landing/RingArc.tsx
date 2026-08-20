"use client";

import { useEffect, useRef, useState } from "react";
import { prefersReducedMotion } from "@/lib/motion";

/** Dash length of the r=42 ring the efficiency dial is drawn on. */
const RING = 264;

/**
 * The efficiency dial fills from empty when it scrolls into view. The fill is a
 * CSS transition on the dash offset, so this only has to decide when to hand
 * over the real value.
 */
export function RingArc({ efficiency }: { efficiency: number }) {
  const target = Number((RING * (1 - efficiency / 100)).toFixed(1));
  const [offset, setOffset] = useState(prefersReducedMotion() ? target : RING);
  const ref = useRef<SVGCircleElement>(null);

  useEffect(() => {
    const arc = ref.current;
    if (!arc || prefersReducedMotion()) {
      setOffset(target);
      return;
    }
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) {
          setOffset(target);
          observer.disconnect();
        }
      },
      { rootMargin: "0px 0px -8% 0px" },
    );
    observer.observe(arc);
    return () => observer.disconnect();
  }, [target]);

  return (
    <circle
      ref={ref}
      className="reading__arc"
      cx="50"
      cy="50"
      r="42"
      style={{ strokeDashoffset: offset }}
    />
  );
}
