"use client";

import { createElement, useRef } from "react";
import { decimal } from "@/lib/format";
import { useCountUp } from "@/lib/motion";

/**
 * A number that counts up to its value when it scrolls into view.
 *
 * It renders the true value first and the animation overwrites it, so the
 * server-rendered page and a page without JavaScript both show the real figure.
 */
export function Counter({
  value,
  decimals = 0,
  prefix = "",
  suffix = "",
  as = "p",
  className,
}: {
  value: number;
  decimals?: number;
  prefix?: string;
  suffix?: string;
  as?: "p" | "span" | "dd" | "div";
  className?: string;
}) {
  const ref = useRef<HTMLElement>(null);
  useCountUp(ref, value, { decimals, prefix, suffix });
  return createElement(as, { ref, className }, `${prefix}${decimal(value, decimals)}${suffix}`);
}
