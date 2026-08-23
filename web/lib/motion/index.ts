"use client";

import { useEffect, useRef, type RefObject } from "react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { animate } from "motion";
import { decimal } from "@/lib/format";

/**
 * The animation vocabulary of the site, as hooks.
 *
 * GSAP + ScrollTrigger choreograph anything tied to scroll position; Motion
 * drives the pointer-following micro-interactions, because a cursor wants a
 * spring and not a tween. Each hook returns a ref you attach to the element it
 * animates, and each one is a no-op when the visitor asked for reduced motion —
 * the page then renders exactly as it does without JavaScript.
 */

let registered = false;

function setup() {
  if (registered || typeof window === "undefined") return;
  gsap.registerPlugin(ScrollTrigger);
  gsap.defaults({ ease: "power3.out", duration: 0.9 });
  // boot.js hides reveal targets under .js and un-hides them if nothing claims
  // them within four seconds; this is what claims them.
  (window as unknown as { __solarsageMotionReady?: boolean }).__solarsageMotionReady = true;
  registered = true;
}

function prefersReducedMotion(): boolean {
  return (
    typeof window !== "undefined" &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches
  );
}

function isTouch(): boolean {
  return typeof window !== "undefined" && window.matchMedia("(hover: none)").matches;
}

export type RevealMode = "up" | "left" | "right" | "scale";

/**
 * Every hook here takes the ref of the element it animates rather than making
 * one, so a single element can carry more than one behaviour — the console
 * preview both reveals and tilts, and that is one element, not two wrappers.
 */

/** A section arrives as the scroll reaches it: a short rise, never a bounce. */
export function useReveal(
  ref: RefObject<HTMLElement | null>,
  mode: RevealMode | null = "up",
  delay = 0,
) {
  useEffect(() => {
    if (!mode) return;
    const element = ref.current;
    if (!element) return;
    if (prefersReducedMotion()) {
      element.style.opacity = "1";
      return;
    }
    setup();

    const from: gsap.TweenVars = { opacity: 0 };
    if (mode === "up") from.y = 28;
    if (mode === "left") from.x = -28;
    if (mode === "right") from.x = 28;
    if (mode === "scale") from.scale = 0.96;

    const context = gsap.context(() => {
      gsap.set(element, from);
      gsap.to(element, {
        opacity: 1,
        x: 0,
        y: 0,
        scale: 1,
        duration: 1,
        delay,
        // "top bottom" and not a percentage band: anything with a pixel inside
        // the viewport at load animates immediately. A band leaves content that
        // is *almost* on screen sitting at opacity 0 until someone scrolls,
        // which on the console means the dashboard's own grid can paint empty.
        scrollTrigger: { trigger: element, start: "top bottom", once: true },
      });
    }, element);

    return () => context.revert();
  }, [mode, delay, ref]);
}

/** Children of the element land as one gesture rather than all at once. */
export function useStagger(ref: RefObject<HTMLElement | null>, step = 0.07) {
  useEffect(() => {
    const element = ref.current;
    if (!element || !element.children.length || prefersReducedMotion()) return;
    setup();

    const context = gsap.context(() => {
      gsap.from(Array.from(element.children), {
        opacity: 0,
        y: 22,
        duration: 0.85,
        stagger: step,
        scrollTrigger: { trigger: element, start: "top bottom", once: true },
      });
    }, element);

    return () => context.revert();
  }, [step, ref]);
}

interface CountOptions {
  decimals?: number;
  prefix?: string;
  suffix?: string;
}

/**
 * A number counts to its real value once, when it scrolls into view.
 *
 * The element keeps its server-rendered value until the tween starts, so a
 * counter below the fold never sits at zero waiting to be scrolled to — and a
 * value that changes while the page is open is written straight in.
 */
export function useCountUp(
  ref: RefObject<HTMLElement | null>,
  value: number,
  options: CountOptions = {},
) {
  const { decimals = 0, prefix = "", suffix = "" } = options;
  const started = useRef(false);

  useEffect(() => {
    const element = ref.current;
    if (!element || !Number.isFinite(value)) return;

    const write = (current: number) => {
      element.textContent = `${prefix}${decimal(current, decimals)}${suffix}`;
    };

    if (prefersReducedMotion() || started.current) {
      write(value);
      return;
    }
    setup();
    started.current = true;

    const state = { value: 0 };
    const context = gsap.context(() => {
      gsap.to(state, {
        value,
        duration: 1.4,
        ease: "power2.out",
        scrollTrigger: { trigger: element, start: "top 96%", once: true },
        onStart: () => write(0),
        onUpdate: () => write(state.value),
      });
    }, element);

    return () => context.revert();
  }, [value, decimals, prefix, suffix, ref]);
}

/** Cards tip a couple of degrees under the pointer, like glass catching light. */
export function useTilt(ref: RefObject<HTMLElement | null>, max = 6) {
  useEffect(() => {
    const element = ref.current;
    if (!element || prefersReducedMotion() || isTouch()) return;

    const spring = { type: "spring" as const, stiffness: 200, damping: 20 };
    element.style.transformStyle = "preserve-3d";

    const move = (event: PointerEvent) => {
      const box = element.getBoundingClientRect();
      const x = (event.clientX - box.left) / box.width - 0.5;
      const y = (event.clientY - box.top) / box.height - 0.5;
      element.style.setProperty("--spot-x", `${((x + 0.5) * 100).toFixed(1)}%`);
      element.style.setProperty("--spot-y", `${((y + 0.5) * 100).toFixed(1)}%`);
      animate(element, { rotateY: x * max, rotateX: -y * max }, spring);
    };
    const leave = () => animate(element, { rotateY: 0, rotateX: 0 }, spring);

    element.addEventListener("pointermove", move);
    element.addEventListener("pointerleave", leave);
    return () => {
      element.removeEventListener("pointermove", move);
      element.removeEventListener("pointerleave", leave);
    };
  }, [max, ref]);
}

/** Primary actions lean toward the cursor — a spring, so it settles honestly. */
export function useMagnetic(ref: RefObject<HTMLElement | null>, strength = 0.35) {
  useEffect(() => {
    const element = ref.current;
    if (!element || prefersReducedMotion() || isTouch()) return;

    const spring = { type: "spring" as const, stiffness: 260, damping: 18, mass: 0.4 };
    const move = (event: PointerEvent) => {
      const box = element.getBoundingClientRect();
      animate(
        element,
        {
          x: (event.clientX - (box.left + box.width / 2)) * strength,
          y: (event.clientY - (box.top + box.height / 2)) * strength,
        },
        spring,
      );
    };
    const leave = () => animate(element, { x: 0, y: 0 }, spring);

    element.addEventListener("pointermove", move);
    element.addEventListener("pointerleave", leave);
    return () => {
      element.removeEventListener("pointermove", move);
      element.removeEventListener("pointerleave", leave);
    };
  }, [strength, ref]);
}

/** The hairline at the top of the page that tracks how far down it you are. */
export function useScrollProgress(ref: RefObject<HTMLElement | null>) {
  useEffect(() => {
    const element = ref.current;
    if (!element || prefersReducedMotion()) return;
    setup();

    const context = gsap.context(() => {
      gsap.to(element, {
        scaleX: 1,
        ease: "none",
        scrollTrigger: { start: 0, end: "max", scrub: 0.3 },
      });
    }, element);

    return () => context.revert();
  }, [ref]);
}

export { animate, gsap, prefersReducedMotion, useRef };
