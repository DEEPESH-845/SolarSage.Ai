#!/usr/bin/env python3
"""Solar Panel Cleaning System — Flask frontend.

By default the frontend calls Backend.services in-process, so it runs as a
single deployable unit (this is what makes the Vercel deployment work). Set
BACKEND_URL to make it talk to a remote FastAPI backend over HTTP instead.

Routes come in three shapes:
  * pages          — server-rendered HTML (`/`, `/dashboard`, `/panels`, …)
  * actions        — POST-only, because they spray water and write rows
  * /api/*         — JSON for the page scripts
"""

import logging
import os
import secrets
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

# Allow `python Frontend/app.py` as well as an import from the repo root.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from flask import (  # noqa: E402
    Flask, flash, g, has_request_context, jsonify, redirect, render_template, request, url_for,
)

from Backend import services  # noqa: E402
from Backend.config.settings import settings  # noqa: E402
from Backend.database.connection import SessionLocal, init_database  # noqa: E402

app = Flask(__name__)

# A fixed fallback secret would let anyone forge a session cookie, so an unset
# SECRET_KEY gets a random one: sessions only carry flash messages, and losing
# them on restart is cheaper than shipping a known key.
app.secret_key = os.getenv("SECRET_KEY") or secrets.token_hex(32)
if not os.getenv("SECRET_KEY"):
    app.logger.warning("SECRET_KEY is not set — using a random key for this process only.")

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=bool(os.getenv("VERCEL") or os.getenv("HTTPS")),
    JSON_SORT_KEYS=False,
    SEND_FILE_MAX_AGE_DEFAULT=31536000,  # assets are fingerprinted by asset_url()
)

BACKEND_URL = settings.backend_url  # None → in-process service layer
API_TIMEOUT = 10

# Scripts and fonts are served from this origin only — no CDN, no inline script.
CONTENT_SECURITY_POLICY = "; ".join([
    "default-src 'self'",
    "img-src 'self' data:",
    "style-src 'self' 'unsafe-inline'",  # progress widths and animation set style attrs
    "script-src 'self'",
    "font-src 'self'",
    "connect-src 'self'",
    "frame-ancestors 'none'",
    "base-uri 'self'",
    "form-action 'self'",
])

init_database()


# --------------------------------------------------------------------------
# request plumbing
# --------------------------------------------------------------------------

def get_session():
    """One database session per request, closed by teardown_appcontext."""
    if "db" not in g:
        g.db = SessionLocal()
    return g.db


@app.teardown_appcontext
def close_session(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


@app.before_request
def block_cross_origin_writes():
    """Refuse writes that a different site asked for.

    Nothing here is behind a login, so a page on another origin could otherwise
    post to /spray and open a valve. Browsers attach Origin to cross-site
    requests; when it is present and not ours, the request is not from our UI.
    """
    if request.method in ("GET", "HEAD", "OPTIONS"):
        return None

    origin = request.headers.get("Origin")
    if origin and urlparse(origin).netloc != request.host:
        app.logger.warning("Refused cross-origin %s %s from %s", request.method, request.path, origin)
        return jsonify({"error": "Cross-origin requests are not accepted."}), 403
    return None


@app.after_request
def set_security_headers(response):
    response.headers.setdefault("Content-Security-Policy", CONTENT_SECURITY_POLICY)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("Referrer-Policy", "same-origin")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Permissions-Policy", "geolocation=(), microphone=(), camera=()")
    return response


def wants_json():
    """Actions answer fetch() with JSON and a plain form post with a redirect."""
    if request.headers.get("X-Requested-With") == "fetch":
        return True
    accept = request.accept_mimetypes
    return accept["application/json"] > accept["text/html"]


def redirect_back(default="dashboard"):
    """Return to the page that triggered the action — but only ever to this app.

    request.referrer is attacker-controlled, so only its path and query survive.
    """
    if request.referrer:
        parsed = urlparse(request.referrer)
        if not parsed.netloc or parsed.netloc == request.host:
            target = parsed.path or url_for(default)
            return redirect(f"{target}?{parsed.query}" if parsed.query else target)
    return redirect(url_for(default))


def respond(payload, message, ok, status=200):
    """One reply shape for actions, JSON or redirect depending on the caller."""
    if wants_json():
        return jsonify({**payload, "ok": ok, "message": message}), status
    flash(message, "success" if ok else "error")
    return redirect_back()


# --------------------------------------------------------------------------
# service access
# --------------------------------------------------------------------------

def _dispatch_local(endpoint, method, data):
    """Map an API path onto the service layer. Mirrors Backend/api/main.py."""
    db = get_session()
    data = data or {}
    panel_id = data.get("panel_id", "panel_01")

    routes = {
        ("GET", "/health"): lambda: services.health(db),
        ("GET", "/panels"): lambda: services.list_panels(db),
        ("GET", "/latest-decision"): lambda: services.latest_decision(db),
        ("GET", "/system/stats"): lambda: services.system_stats(db),
        ("GET", "/system/logs"): lambda: services.system_logs(db),
        ("GET", "/settings"): lambda: services.get_settings(db),
        ("GET", "/hardware/telemetry"): lambda: services.latest_telemetry(),
        ("POST", "/analyze"): lambda: services.analyze_panel(db, panel_id),
        ("POST", "/spray"): lambda: services.spray_panel(db, panel_id),
        ("POST", "/settings/reset"): lambda: services.reset_settings(db),
        ("POST", "/system/refill-tank"): lambda: services.refill_tank(db),
        ("PUT", "/settings"): lambda: services.update_settings(db, data.get("values", {})),
    }

    if method == "GET" and endpoint.startswith("/panels/") and endpoint.endswith("/history"):
        return services.panel_history(db, endpoint.split("/")[2])

    handler = routes.get((method, endpoint))
    if handler is None:
        raise ValueError(f"Unknown endpoint: {method} {endpoint}")
    return handler()


def make_api_request(endpoint, method="GET", data=None):
    """Call the backend. In-process by default, over HTTP when BACKEND_URL is set."""
    try:
        if not BACKEND_URL:
            return _dispatch_local(endpoint, method, data)

        import requests

        response = requests.request(method, f"{BACKEND_URL}{endpoint}", json=data, timeout=API_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except Exception:
        # The detail goes to the log; the page gets a message that says what to
        # do about it, and JSON callers get their own error from the caller.
        app.logger.exception("Backend call failed: %s %s", method, endpoint)
        if has_request_context() and not request.path.startswith("/api/"):
            flash("The system did not answer. Refresh, or check that the backend is running.", "error")
        return None


def as_list(value):
    """The logs endpoint returns a list on success and a dict on failure."""
    return value if isinstance(value, list) else []


def panel_counts(panels):
    """Status tallies used by the dashboard, the panels page and the reports."""
    rows = (panels or {}).get("panels", [])
    counts = {"clean": 0, "moderate_dust": 0, "needs_cleaning": 0, "unknown": 0}
    for panel in rows:
        counts[panel["status"]] = counts.get(panel["status"], 0) + 1
    counts["total"] = len(rows)
    counts["attention"] = counts["moderate_dust"] + counts["needs_cleaning"]
    counts["health_percentage"] = round(counts["clean"] / len(rows) * 100, 1) if rows else 0.0
    return counts


# --------------------------------------------------------------------------
# template globals
# --------------------------------------------------------------------------

@app.context_processor
def inject_globals():
    """Values every template can use, without each view passing them through."""
    config = make_api_request("/settings") or services.DEFAULT_SETTINGS

    def asset_url(filename):
        """Fingerprint static files so they can be cached for a year."""
        path = Path(app.static_folder) / filename
        version = int(path.stat().st_mtime) if path.is_file() else 0
        return url_for("static", filename=filename, v=version)

    return {
        "config": config,
        "refresh_interval": config.get("refresh_interval", 30),
        "now": datetime.now(timezone.utc),
        "asset_url": asset_url,
        "panel_ids": settings.panel_ids,
    }


@app.errorhandler(404)
def not_found(error):
    return render_template("error.html", code=404,
                           title="No such page",
                           detail="The address you followed is not part of the console."), 404


@app.errorhandler(500)
def server_error(error):
    app.logger.exception("Unhandled error")
    return render_template("error.html", code=500,
                           title="The console hit an error",
                           detail="The request was logged. Try again, or reload the page."), 500


# --------------------------------------------------------------------------
# pages
# --------------------------------------------------------------------------

@app.route("/")
def landing():
    panels = make_api_request("/panels")
    telemetry = make_api_request("/hardware/telemetry") or {}
    return render_template(
        "landing.html",
        panels=panels,
        counts=panel_counts(panels),
        telemetry=telemetry,
        stats=make_api_request("/system/stats"),
        health=make_api_request("/health"),
        latest_decision=make_api_request("/latest-decision"),
    )


@app.route("/dashboard")
def dashboard():
    panels = make_api_request("/panels")
    return render_template(
        "dashboard.html",
        health=make_api_request("/health"),
        panels=panels,
        counts=panel_counts(panels),
        stats=make_api_request("/system/stats"),
        telemetry=make_api_request("/hardware/telemetry") or {},
        latest_decision=make_api_request("/latest-decision"),
    )


@app.route("/panels")
def panels_page():
    panels = make_api_request("/panels")
    return render_template(
        "panels.html",
        panels=panels,
        counts=panel_counts(panels),
        telemetry=make_api_request("/hardware/telemetry") or {},
    )


@app.route("/settings")
def settings_page():
    return render_template(
        "settings.html",
        health=make_api_request("/health"),
        stats=make_api_request("/system/stats"),
    )


@app.route("/system-reports")
def system_reports():
    panels = make_api_request("/panels")
    return render_template(
        "reports.html",
        stats=make_api_request("/system/stats"),
        logs=as_list(make_api_request("/system/logs")),
        panels=panels,
        counts=panel_counts(panels),
        health=make_api_request("/health"),
    )


# --------------------------------------------------------------------------
# actions — POST only: each one writes rows, and one of them opens a valve
# --------------------------------------------------------------------------

@app.post("/analyze/<panel_id>")
def analyze_panel(panel_id):
    result = make_api_request("/analyze", method="POST", data={"panel_id": panel_id})
    if result is None:
        return respond({}, "The analyser did not answer.", False, 503)
    if "error" in result:
        return respond(result, result["error"], False, 400)
    return respond(result, f"{panel_id}: {result.get('action', 'analysis complete')}", True)


@app.post("/spray/<panel_id>")
def spray_panel(panel_id):
    result = make_api_request("/spray", method="POST", data={"panel_id": panel_id})
    if result is None:
        return respond({}, "The spray controller did not answer.", False, 503)
    if "error" in result:
        return respond(result, result["error"], False, 400)
    return respond(
        result,
        f"{panel_id} cleaned — {result.get('water_used_ml', 0):.0f}ml over "
        f"{result.get('duration_seconds', 0):.0f}s.",
        True,
    )


# --------------------------------------------------------------------------
# JSON endpoints used by the page scripts
# --------------------------------------------------------------------------

@app.route("/api/status")
def api_status():
    health_data = make_api_request("/health")
    if health_data:
        return jsonify({"status": "connected", "data": health_data})
    return jsonify({"status": "disconnected", "error": "No response from backend"}), 503


@app.post("/api/quick-analyze")
def quick_analyze():
    panels_data = make_api_request("/panels")
    if not panels_data:
        return jsonify({"error": "Could not read the panel list"}), 503

    results, failures = [], []
    for panel in panels_data.get("panels", []):
        result = make_api_request("/analyze", method="POST", data={"panel_id": panel["id"]})
        if result and "error" not in result:
            results.append(result)
        else:
            failures.append(panel["id"])

    return jsonify({
        "results": results,
        "total": len(results),
        "failed": failures,
        "message": f"Analysed {len(results)} panel(s)"
                   + (f", {len(failures)} failed" if failures else "") + ".",
    })


def _spray_panels(panel_ids):
    """Spray a set of panels, reporting per-panel failures instead of hiding them."""
    results, failures, water = [], [], 0
    for panel_id in panel_ids:
        result = make_api_request("/spray", method="POST", data={"panel_id": panel_id})
        if result and "error" not in result:
            results.append(result)
            water += result.get("water_used_ml", 0)
        else:
            failures.append({"panel_id": panel_id, "error": (result or {}).get("error", "no response")})
    return results, failures, water


@app.post("/api/emergency-clean-all")
def emergency_clean_all():
    panels_data = make_api_request("/panels")
    if not panels_data:
        return jsonify({"error": "Could not read the panel list"}), 503

    panel_ids = [p["id"] for p in panels_data.get("panels", [])]
    results, failures, water = _spray_panels(panel_ids)
    return jsonify({
        "results": results,
        "failures": failures,
        "total_panels": len(panel_ids),
        "successful_cleanings": len(results),
        "total_water_used": water,
        "message": f"Cleaned {len(results)} of {len(panel_ids)} panels using {water:.0f}ml.",
    })


@app.post("/api/clean-dirty-panels")
def clean_dirty_panels():
    panels_data = make_api_request("/panels")
    if not panels_data:
        return jsonify({"error": "Could not read the panel list"}), 503

    all_panels = panels_data.get("panels", [])
    dirty = [p["id"] for p in all_panels if p["status"] in ("moderate_dust", "needs_cleaning")]
    if not dirty:
        return jsonify({
            "message": "Every panel is clean. Nothing to do.",
            "total_panels": len(all_panels),
            "panels_cleaned": 0,
            "total_water_used": 0,
        })

    results, failures, water = _spray_panels(dirty)
    return jsonify({
        "results": results,
        "failures": failures,
        "total_panels": len(all_panels),
        "dirty_panels_found": len(dirty),
        "panels_cleaned": len(results),
        "total_water_used": water,
        "message": f"Cleaned {len(results)} of {len(dirty)} dusty panels using {water:.0f}ml.",
    })


@app.route("/api/system-reports")
def api_system_reports():
    stats_data = make_api_request("/system/stats")
    logs_data = as_list(make_api_request("/system/logs"))
    panels_data = make_api_request("/panels")
    counts = panel_counts(panels_data)

    return jsonify({
        "stats": stats_data,
        "logs": logs_data[:10],
        "panels": (panels_data or {}).get("panels", []),
        "panel_health": {
            "clean": counts["clean"],
            "moderate_dust": counts["moderate_dust"],
            "needs_cleaning": counts["needs_cleaning"],
            "unknown": counts["unknown"],
            "health_percentage": counts["health_percentage"],
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


@app.route("/api/settings", methods=["GET", "POST"])
def api_settings():
    if request.method == "GET":
        return jsonify(make_api_request("/settings") or {})

    values = request.get_json(silent=True) or {}
    updated = make_api_request("/settings", method="PUT", data={"values": values})
    if updated is None:
        return jsonify({"error": "Could not save settings"}), 503
    return jsonify({"message": "Settings saved", "settings": updated})


@app.post("/api/settings/reset")
def api_settings_reset():
    result = make_api_request("/settings/reset", method="POST")
    if result is None:
        return jsonify({"error": "Could not reset settings"}), 503
    return jsonify({"message": "Settings back to defaults", "settings": result})


@app.post("/api/refill-tank")
def api_refill_tank():
    result = make_api_request("/system/refill-tank", method="POST")
    if result is None:
        return jsonify({"error": "Could not refill the tank"}), 503
    return jsonify({"message": "Water tank refilled", "water": result})


@app.post("/api/system-mode")
def api_system_mode():
    mode = (request.get_json(silent=True) or {}).get("mode")
    if mode not in ("active", "paused"):
        return jsonify({"error": "mode must be 'active' or 'paused'"}), 400

    updated = make_api_request("/settings", method="PUT", data={"values": {"system_mode": mode}})
    if updated is None:
        return jsonify({"error": "Could not change the system mode"}), 503
    return jsonify({
        "message": "Cleaning paused" if mode == "paused" else "Cleaning resumed",
        "settings": updated,
    })


@app.route("/api/panel/<panel_id>")
def api_panel_detail(panel_id):
    """Real panel detail for the panels-page drawer: history plus its ESP32 reading."""
    invalid = services.unknown_panel(panel_id)
    if invalid:
        return jsonify(invalid), 404

    history = make_api_request(f"/panels/{panel_id}/history")
    if history is None:
        return jsonify({"error": "Could not load panel history"}), 503

    panels = (make_api_request("/panels") or {}).get("panels", [])
    summary = next((p for p in panels if p["id"] == panel_id), None)

    # Hardware logs index panels as PANNEL_0..N, in the same order as panel_ids.
    telemetry = make_api_request("/hardware/telemetry") or {}
    hardware_id = f"PANNEL_{settings.panel_ids.index(panel_id)}"
    reading = next((r for r in telemetry.get("readings", []) if r.get("panel_id") == hardware_id), None)

    return jsonify({"panel": summary, "telemetry": reading, **history})


@app.route("/api/telemetry")
def api_telemetry():
    return jsonify(make_api_request("/hardware/telemetry") or {"available": False, "readings": []})


@app.route("/api/live")
def api_live():
    """One poll for everything the console keeps up to date."""
    panels = make_api_request("/panels")
    return jsonify({
        "health": make_api_request("/health"),
        "panels": (panels or {}).get("panels", []),
        "counts": panel_counts(panels),
        "stats": make_api_request("/system/stats"),
        "latest_decision": make_api_request("/latest-decision"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    debug = os.getenv("FLASK_DEBUG", "").lower() in ("1", "true", "yes")
    print("🌞 Solar Panel Cleaning System — frontend")
    print(f"🌐 http://localhost:{settings.frontend_port}")
    print(f"🔗 Backend: {BACKEND_URL or 'in-process service layer'}")
    if debug:
        print("⚠️  Debug mode is on — never expose this port to a network.")
    # The Werkzeug debugger executes arbitrary code, so it stays opt-in.
    app.run(debug=debug, host="127.0.0.1" if debug else "0.0.0.0", port=settings.frontend_port)
