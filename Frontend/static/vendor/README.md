Third-party animation runtimes, vendored so the app makes no third-party
requests at runtime (keeps the CSP tight and the page fast offline).

| File | Package | Version | Licence |
|------|---------|---------|---------|
| `gsap.min.js`, `ScrollTrigger.min.js`, `SplitText.min.js`, `DrawSVGPlugin.min.js` | [gsap](https://gsap.com) | 3.15.0 | GSAP Standard "No Charge" licence |
| `motion.min.js` | [motion](https://motion.dev) (Framer Motion's vanilla build) | 13.1.0 | MIT |

Refresh with `npm pack gsap motion` and copy `dist/` out of the tarballs.
