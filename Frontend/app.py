#!/usr/bin/env python3
"""Solar Panel Cleaning System — Flask frontend.

By default the frontend calls Backend.services in-process, so it runs as a
single deployable unit (this is what makes the Vercel deployment work). Set
BACKEND_URL to make it talk to a remote FastAPI backend over HTTP instead.
"""

import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Allow `python Frontend/app.py` as well as an import from the repo root.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from flask import Flask, flash, g, jsonify, redirect, render_template, request, url_for  # noqa: E402

from Backend import services  # noqa: E402
from Backend.config.settings import settings  # noqa: E402
from Backend.database.connection import SessionLocal, init_database  # noqa: E402

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "solar_panel_cleaning_system_2025")

BACKEND_URL = settings.backend_url  # None → in-process service layer
API_TIMEOUT = 10

init_database()


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

        url = f"{BACKEND_URL}{endpoint}"
        response = requests.request(method, url, json=data, timeout=API_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        flash(f"API Error: {e}", "error")
        return None


def as_list(value):
    """The logs endpoint returns a list on success and a dict on failure."""
    return value if isinstance(value, list) else []


@app.context_processor
def inject_globals():
    """Values every template can use, without each view passing them through."""
    config = make_api_request("/settings") or services.DEFAULT_SETTINGS
    return {
        "config": config,
        "refresh_interval": config.get("refresh_interval", 30),
        "now": datetime.now(timezone.utc),
    }


@app.route("/")
def dashboard():
    return render_template(
        "dashboard.html",
        health=make_api_request("/health"),
        panels=make_api_request("/panels"),
        latest_decision=make_api_request("/latest-decision"),
    )


@app.route("/analyze/<panel_id>")
def analyze_panel(panel_id):
    result = make_api_request("/analyze", method="POST", data={"panel_id": panel_id})
    if result and "error" in result:
        flash(result["error"], "error")
    elif result:
        flash(f"Analysis completed for {panel_id}: {result.get('action', 'No action needed')}", "success")
    return redirect(request.referrer or url_for("dashboard"))


@app.route("/spray/<panel_id>")
def spray_panel(panel_id):
    result = make_api_request("/spray", method="POST", data={"panel_id": panel_id})
    if result and "error" in result:
        flash(result["error"], "error")
    elif result:
        flash(f"Cleaning initiated for {panel_id}: {result.get('action', 'Spray completed')}", "success")
    return redirect(request.referrer or url_for("dashboard"))


@app.route("/panels")
def panels_page():
    return render_template(
        "panels.html",
        panels=make_api_request("/panels"),
        telemetry=make_api_request("/hardware/telemetry"),
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
    return render_template(
        "reports.html",
        stats=make_api_request("/system/stats"),
        logs=as_list(make_api_request("/system/logs")),
        panels=make_api_request("/panels"),
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


@app.route("/api/quick-analyze")
def quick_analyze():
    panels_data = make_api_request("/panels")
    if not panels_data:
        return jsonify({"error": "Could not get panels data"}), 503

    results, failures = [], []
    for panel in panels_data.get("panels", []):
        result = make_api_request("/analyze", method="POST", data={"panel_id": panel["id"]})
        if result and "error" not in result:
            results.append(result)
        else:
            failures.append(panel["id"])

    return jsonify({"results": results, "total": len(results), "failed": failures})


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


@app.route("/api/emergency-clean-all")
def emergency_clean_all():
    panels_data = make_api_request("/panels")
    if not panels_data:
        return jsonify({"error": "Could not get panels data"}), 503

    panel_ids = [p["id"] for p in panels_data.get("panels", [])]
    results, failures, water = _spray_panels(panel_ids)
    return jsonify({
        "results": results,
        "failures": failures,
        "total_panels": len(panel_ids),
        "successful_cleanings": len(results),
        "total_water_used": water,
        "message": f"Emergency cleaning completed for {len(results)}/{len(panel_ids)} panels. "
                   f"Total water used: {water:.0f}ml",
    })


@app.route("/api/clean-dirty-panels")
def clean_dirty_panels():
    panels_data = make_api_request("/panels")
    if not panels_data:
        return jsonify({"error": "Could not get panels data"}), 503

    all_panels = panels_data.get("panels", [])
    dirty = [p["id"] for p in all_panels if p["status"] in ("moderate_dust", "needs_cleaning")]
    if not dirty:
        return jsonify({
            "message": "No panels need cleaning at this time",
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
        "message": f"Cleaned {len(results)}/{len(dirty)} dirty panels. Water used: {water:.0f}ml",
    })


@app.route("/api/system-reports")
def api_system_reports():
    stats_data = make_api_request("/system/stats")
    logs_data = as_list(make_api_request("/system/logs"))
    panels_data = make_api_request("/panels")

    panels = (panels_data or {}).get("panels", [])
    counts = {"clean": 0, "moderate_dust": 0, "needs_cleaning": 0, "unknown": 0}
    for panel in panels:
        counts[panel["status"]] = counts.get(panel["status"], 0) + 1

    panel_health = {
        **{k: counts[k] for k in ("clean", "moderate_dust", "needs_cleaning")},
        "unknown": counts["unknown"],
        "health_percentage": round(counts["clean"] / len(panels) * 100, 1) if panels else 0,
    }

    return jsonify({
        "stats": stats_data,
        "logs": logs_data[:10],
        "panels": panels,
        "panel_health": panel_health,
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


@app.route("/api/settings/reset", methods=["POST"])
def api_settings_reset():
    result = make_api_request("/settings/reset", method="POST")
    if result is None:
        return jsonify({"error": "Could not reset settings"}), 503
    return jsonify({"message": "Settings reset to defaults", "settings": result})


@app.route("/api/refill-tank", methods=["POST"])
def api_refill_tank():
    result = make_api_request("/system/refill-tank", method="POST")
    if result is None:
        return jsonify({"error": "Could not refill tank"}), 503
    return jsonify({"message": "Water tank refilled", "water": result})


@app.route("/api/system-mode", methods=["POST"])
def api_system_mode():
    mode = (request.get_json(silent=True) or {}).get("mode")
    if mode not in ("active", "paused"):
        return jsonify({"error": "mode must be 'active' or 'paused'"}), 400

    updated = make_api_request("/settings", method="PUT", data={"values": {"system_mode": mode}})
    if updated is None:
        return jsonify({"error": "Could not change system mode"}), 503
    return jsonify({"message": f"System {mode}", "settings": updated})


@app.route("/api/panel/<panel_id>")
def api_panel_detail(panel_id):
    """Real panel detail for the panels-page modal: history plus its ESP32 reading."""
    if panel_id not in settings.panel_ids:
        return jsonify({"error": f"Unknown panel: {panel_id}"}), 404

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


if __name__ == "__main__":
    print("🌞 Starting Solar Panel Flask Frontend...")
    print(f"🌐 Frontend Server: http://localhost:{settings.frontend_port}")
    print(f"🔗 Backend: {BACKEND_URL or 'in-process service layer'}")
    app.run(debug=True, host="0.0.0.0", port=settings.frontend_port)
