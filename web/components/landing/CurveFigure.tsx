"use client";

import { useEffect, useRef } from "react";
import { gsap } from "gsap";
import { DrawSVGPlugin } from "gsap/DrawSVGPlugin";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { prefersReducedMotion } from "@/lib/motion";

/**
 * Output across a day, clean against soiled, with the lost energy shaded
 * between them. The two curves draw themselves and then the loss fills in —
 * the order matters, because the shaded area only means something once the
 * reader has seen the two lines it sits between.
 */
export function CurveFigure() {
  const ref = useRef<HTMLElement>(null);

  useEffect(() => {
    const figure = ref.current;
    if (!figure || prefersReducedMotion()) return;
    gsap.registerPlugin(ScrollTrigger, DrawSVGPlugin);

    const context = gsap.context(() => {
      const timeline = gsap.timeline({
        scrollTrigger: { trigger: figure, start: "top 78%", once: true },
      });
      timeline
        .from(".curve__clean", { drawSVG: "0%", duration: 1.5, ease: "power2.inOut" })
        .from(".curve__soiled", { drawSVG: "0%", duration: 1.5, ease: "power2.inOut" }, 0.35)
        .to(".curve__loss", { opacity: 1, duration: 0.9 }, 1.1);
    }, figure);

    return () => context.revert();
  }, []);

  return (
    <figure className="curve" ref={ref} data-reveal="scale">
      <svg
        viewBox="0 0 600 240"
        className="curve__svg"
        role="img"
        aria-label="Output across a day: the clean curve against the soiled curve, with the lost energy shaded between them."
      >
        <defs>
          <linearGradient id="lossFill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#c4813c" stopOpacity="0.6" />
            <stop offset="100%" stopColor="#c4813c" stopOpacity="0.06" />
          </linearGradient>
        </defs>

        <g className="curve__grid">
          <line x1="0" y1="200" x2="600" y2="200" />
          <line x1="0" y1="140" x2="600" y2="140" />
          <line x1="0" y1="80" x2="600" y2="80" />
          <line x1="0" y1="20" x2="600" y2="20" />
        </g>

        <path
          className="curve__loss"
          d="M0,200 C90,200 120,60 300,40 C480,60 510,200 600,200 C510,200 470,105 300,88 C130,105 90,200 0,200 Z"
        />
        <path className="curve__clean" d="M0,200 C90,200 120,60 300,40 C480,60 510,200 600,200" />
        <path className="curve__soiled" d="M0,200 C90,200 130,105 300,88 C470,105 510,200 600,200" />

        <g className="curve__marks">
          <text x="2" y="228">
            06:00
          </text>
          <text x="285" y="228">
            12:00
          </text>
          <text x="562" y="228">
            18:00
          </text>
        </g>
      </svg>

      <figcaption className="curve__key">
        <span className="key key--clean">Clean output</span>
        <span className="key key--soiled">Measured output</span>
        <span className="key key--loss">Energy lost to dust</span>
      </figcaption>
    </figure>
  );
}
