# SolarSage — Next.js frontend

**Date:** 2026-08-20
**Status:** approved, in implementation

## Why

The console is a Flask app rendering Jinja templates, with behaviour bolted on
through two hand-written scripts (`kit.js`, `console.js`) that patch the DOM by
`data-live` attribute. It works, but every screen's behaviour is spread across a
template, a delegated click handler and a DOM-patching routine, and there is no
component boundary anywhere. The UI moves to Next.js + React so a screen is one
tree of named components with typed data flowing into it.

The computer-vision pipeline (OpenCV, `Agents/crew.py`) stays in Python. The
question this design answers is where everything *else* lives.

## Decisions

| Decision | Choice |
|---|---|
| API | FastAPI only. Flask (`Frontend/app.py`) is deleted. |
| Styling | `core.css` / `console.css` / `landing.css` move verbatim. The refactor is behaviour-only; the pages stay pixel-identical. |
| Scope | Every page: landing, dashboard, panels, reports, settings. |
| Layout | Next.js app in `web/`; `Frontend/` deleted in the final step. |
| Deployment | Two Vercel projects from one repo: `web/` (Next.js) and the repo root (`api/index.py` → FastAPI). |

## Architecture

```
browser ──► Next.js (web/)  ──server-side──►  FastAPI (api/index.py)  ──►  Backend/services.py
                                                                             │
                                                    SQLite · image fixtures · Agents/crew.py
```

The browser never calls FastAPI directly: server components fetch during render
and server actions call it for mutations, so there is no CORS surface and no API
credentials in the client bundle.

### Python: logic moves down a layer

`Frontend/app.py` had accumulated business logic that React must not inherit.
It moves into `Backend/services.py` and is exposed by FastAPI:

| New service function | New route | Replaces |
|---|---|---|
| `panel_counts(panels)` | — | `Frontend/app.py:panel_counts` |
| `overview(db)` | `GET /overview` | `/api/live`, and the four fetches every console page made |
| `panel_detail(db, panel_id)` | `GET /panels/{id}/detail` | `/api/panel/<id>` |
| `analyze_all(db)` | `POST /panels/analyze-all` | `/api/quick-analyze` |
| `spray_many(db, scope)` | `POST /panels/spray` | `/api/clean-dirty-panels`, `/api/emergency-clean-all` |

The React app renders; it never computes a threshold, a tally or a status.

### Next.js structure

```
web/
  app/
    layout.tsx                fonts, global CSS, ToastProvider
    page.tsx                  landing
    (console)/layout.tsx      rail + topbar + demo banner
    (console)/dashboard/page.tsx  panels/page.tsx  reports/page.tsx  settings/page.tsx
    actions.ts                server actions: analyze, spray, bulk, settings, refill, mode
    api/live/route.ts         polling endpoint the console client hits
    not-found.tsx  error.tsx
  components/ui/              Icon Pill Card Meter Numeral Button Field Empty Note
                              Dialog ConfirmDialog Toast Tank Spinner
  components/console/         Rail Topbar DemoBanner HealthCard DecisionCard PanelCard
                              PanelTable TelemetryTable StatCard Donut LogTable
                              SettingsForm PanelDetailDialog ActionButton LiveProvider
  components/landing/         Hero Loop CostStats FieldReadings ConsolePreview Ledger
  lib/                        api.ts types.ts format.ts status.ts
  lib/motion/                 useReveal useStagger useCountUp useTilt useMagnetic
  styles/                     core.css console.css landing.css
  public/fonts  public/img
```

### Data flow

1. A console page is an async server component. It calls `getOverview()` in
   `lib/api.ts` with `cache: 'no-store'` and renders the first paint.
2. `LiveRefresh` (client) calls `router.refresh()` on `refresh_interval` while
   the tab is visible, so the server re-renders and React swaps in what changed.
3. Mutations are server actions in `app/actions.ts`. Each calls FastAPI,
   `revalidatePath`s the affected route and returns `{ok, message}`, which the
   calling component turns into a toast.

**Deviation from the original plan, taken during implementation.** The plan had
a `LiveProvider` holding polled state from a `/api/live` route handler, with
components reading it through `useLive()`. Re-rendering on the server is
strictly less code and removes a whole class of bug: there is no second mapping
from JSON to markup that can disagree with the first. The route handler and the
provider were not built.

### Ported behaviour

| Was | Becomes |
|---|---|
| `kit.js` reveal / stagger / counters / tilt / magnetic | hooks in `lib/motion/`, `gsap` + `motion` from npm |
| `SS.toast` building DOM | `ToastProvider` context + `<Toast>` |
| `SS.confirm` building a `<dialog>` | `useConfirm()` + `<ConfirmDialog>` |
| `console.js` action table | `<ActionButton action=… />` calling a server action |
| `console.js` settings/sliders/log filter/exports | `SettingsForm`, `LogTable`, `ExportButtons` client components. The exports build from the data the page already holds, so a download cannot disagree with the screen it came from |
| `_icons.html` macro | `<Icon name=… />` with the same path data |

### Deployment guard

Making the API its own deployment makes it publicly reachable, and its POST
routes open a valve. `API_TOKEN`, when set, is required as `X-API-Key` on every
mutating route; reads stay open, and the console's server holds the secret. This
was not in the original plan and was added once the topology made it necessary.

## Error handling

- `lib/api.ts` throws a typed `ApiError` on a non-OK response; pages catch it and
  render the same "the service layer did not answer" empty state as today.
- Server actions never throw to the client: they return `{ok: false, message}`.
- `app/error.tsx` and `app/not-found.tsx` replace `error.html`.

## Testing

- Python: the existing suite keeps proving the logic, extended to cover the new
  service functions and routes. The Flask page test is replaced.
- Frontend: vitest over `lib/` only — counts, formatting, status mapping. No
  component snapshots; the CSS is unchanged, so visual review is a diff of markup.

## What the CSS needed after all

Three additions, each because React rendered a legal element the stylesheet had
not been asked to cope with:

* `.meter { display: block }` — the meter used to be a `<div>` on the dashboard
  and a `<span>` inside the console preview. As a component it is always a
  `<span>`, which collapsed to nothing outside a flex row.
* `.settings__form { display: grid; gap }` — the settings page is one `<form>`
  now, and its sections needed the page's own rhythm rather than collapsing.
* A `reading()` formatter in `lib/format.ts`, because Python prints `81.0` and
  JSON delivers `81`; the telemetry columns had always shown the decimal.

## Out of scope

Auth, a database other than SQLite, and any redesign. The look does not change.
