"use client";

import { useRef, type ElementType } from "react";
import Link from "next/link";
import {
  useMagnetic,
  useReveal,
  useScrollProgress,
  useStagger,
  useTilt,
  type RevealMode,
} from "@/lib/motion";

/**
 * Thin wrappers that put the motion hooks on an element without every caller
 * holding a ref. Each renders one plain element and nothing else — and because
 * the hooks take a ref, one element can both reveal and tilt.
 */

export function Reveal({
  mode = "up",
  delay = 0,
  as: Tag = "div",
  className,
  children,
}: {
  mode?: RevealMode;
  delay?: number;
  as?: ElementType;
  className?: string;
  children: React.ReactNode;
}) {
  const ref = useRef<HTMLDivElement>(null);
  useReveal(ref, mode, delay);
  return (
    <Tag ref={ref} className={className} data-reveal={mode}>
      {children}
    </Tag>
  );
}

export function Stagger({
  step = 0.07,
  as: Tag = "div",
  className,
  children,
}: {
  step?: number;
  as?: ElementType;
  className?: string;
  children: React.ReactNode;
}) {
  const ref = useRef<HTMLDivElement>(null);
  useStagger(ref, step);
  return (
    <Tag ref={ref} className={className}>
      {children}
    </Tag>
  );
}

export function Tilt({
  max = 6,
  reveal,
  as: Tag = "article",
  className,
  children,
}: {
  max?: number;
  /** Tilt and reveal on the same element, rather than one wrapping the other. */
  reveal?: RevealMode;
  as?: ElementType;
  className?: string;
  children: React.ReactNode;
}) {
  const ref = useRef<HTMLElement>(null);
  useTilt(ref, max);
  useReveal(ref, reveal ?? null);
  return (
    <Tag ref={ref} className={className} data-reveal={reveal}>
      {children}
    </Tag>
  );
}

/** A primary link that leans toward the cursor. */
export function MagneticLink({
  href,
  strength = 0.25,
  className,
  children,
}: {
  href: string;
  strength?: number;
  className?: string;
  children: React.ReactNode;
}) {
  const ref = useRef<HTMLAnchorElement>(null);
  useMagnetic(ref, strength);
  return (
    <Link ref={ref} href={href} className={className}>
      {children}
    </Link>
  );
}

export function ScrollProgress() {
  const ref = useRef<HTMLDivElement>(null);
  useScrollProgress(ref);
  return <div ref={ref} className="scroll-progress" aria-hidden="true" />;
}
