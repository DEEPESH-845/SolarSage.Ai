"""Business logic behind the API.

Every route in Backend/api/main.py is a thin wrapper over one of these
functions, and no behaviour lives anywhere else: the console (web/) renders what
they return and the hardware clients call the same routes. A rule that decides
something — a threshold, a tally, which panels a bulk wash touches — belongs
here, where it has tests, and not in the layer that displays it.
"""

import json
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from Backend.agents.image_classifier import ImageClassifierAgent
from Backend.config.settings import settings
from Backend.database.models import (
    CleaningAction,
    PanelStatus,
    SystemDecision,
    SystemLog,
    SystemSetting,
    utcnow,
)

PROCESS_STARTED_AT = time.time()
ML_PER_SECOND_OF_SPRAY = 20

classifier = ImageClassifierAgent()

# Runtime-tunable configuration. Anything a user can change from the settings
# page lives here, not in Backend/config/settings.py.
DEFAULT_SETTINGS = {
    "dust_threshold": 60,          # % dust above which cleaning runs immediately
    "schedule_threshold": 30,      # % dust above which cleaning is scheduled
    "spray_duration": 5,           # seconds per cleaning cycle
    "water_pressure": "medium",    # low | medium | high
    "auto_clean": True,
    "notifications": True,
    "refresh_interval": 30,        # dashboard auto-refresh, seconds
    "system_mode": "active",       # active | paused — paused blocks all spraying
    "alert_email": "",
    "cleaning_frequency": "weekly",
    "preferred_time": "06:00",
    "tank_refilled_at": None,      # ISO timestamp of the last tank refill
    "demo_seeded_at": None,        # set by Backend/demo.py — the console labels itself with it
}


def _bounded_int(low: int, high: int):
    def coerce(value):
        return max(low, min(high, int(float(value))))
    return coerce


def _one_of(*allowed):
    def coerce(value):
        if value not in allowed:
            raise ValueError(f"expected one of: {', '.join(map(str, allowed))}")
        return value
    return coerce


def _boolean(value):
    if isinstance(value, str):
        return value.strip().lower() in ("1", "true", "yes", "on")
    return bool(value)


def _clock(value):
    datetime.strptime(str(value), "%H:%M")  # raises on anything else
    return str(value)


def _iso_or_none(value):
    """Normalise a timestamp to naive UTC.

    Every timestamp in the database is naive UTC (see models.utcnow), and this one
    is compared against them to decide how much water is left. An offset-carrying
    value used to be stored verbatim, so a refill recorded in +05:30 compared as a
    time 5.5 hours later than it was and hid real usage from the tank guard.
    """
    if value in (None, ""):
        return None
    parsed = datetime.fromisoformat(str(value))  # raises on anything else
    if parsed.tzinfo is not None:
        parsed = parsed.astimezone(timezone.utc).replace(tzinfo=None)
    return parsed.isoformat()


# Every writable setting declares what it accepts, because these values leave
# the database and act: refresh_interval becomes a browser timer, spray_duration
# becomes pump seconds. Values that fail are rejected rather than stored.
SETTING_VALIDATORS = {
    "dust_threshold": _bounded_int(0, 100),
    "schedule_threshold": _bounded_int(0, 100),
    "spray_duration": _bounded_int(0, 3600),  # the tank is the real limit
    "refresh_interval": _bounded_int(5, 3600),
    "water_pressure": _one_of("low", "medium", "high"),
    "cleaning_frequency": _one_of("daily", "weekly", "biweekly", "monthly"),
    "system_mode": _one_of("active", "paused"),
    "auto_clean": _boolean,
    "notifications": _boolean,
    "alert_email": lambda value: str(value).strip()[:254],
    "preferred_time": _clock,
    "tank_refilled_at": _iso_or_none,
}


def unknown_panel(panel_id: str) -> Optional[dict]:
    """Panel ids reach the filesystem (image fixtures) and the database, so every
    entry point that takes one validates it here rather than trusting its caller."""
    if panel_id not in settings.panel_ids:
        return {"error": f"Unknown panel: {panel_id}", "panel_id": panel_id}
    return None


# --------------------------------------------------------------------------
# logging
# --------------------------------------------------------------------------

def log_event(db: Session, level: str, component: str, message: str, details: Optional[dict] = None):
    """Record a system log row. Never raises — logging must not break a request."""
    try:
        db.add(
            SystemLog(
                level=level,
                component=component,
                message=message,
                details=json.dumps(details) if details else None,
            )
        )
    except Exception:
        pass


# --------------------------------------------------------------------------
# settings
# --------------------------------------------------------------------------

def get_settings(db: Session) -> dict:
    stored = {}
    for row in db.query(SystemSetting).all():
        try:
            stored[row.key] = json.loads(row.value)
        except (TypeError, ValueError):
            continue  # a corrupt row falls back to its default rather than 500ing
    return {**DEFAULT_SETTINGS, **stored}


def update_settings(db: Session, values: dict) -> dict:
    """Persist only known keys; unknown keys are ignored rather than stored."""
    applied, rejected = {}, {}
    for key, value in values.items():
        validator = SETTING_VALIDATORS.get(key)
        if validator is None:
            continue
        try:
            value = validator(value)
        except (TypeError, ValueError) as e:
            rejected[key] = str(e)
            continue
        row = db.get(SystemSetting, key)
        if row:
            row.value = json.dumps(value)
        else:
            db.add(SystemSetting(key=key, value=json.dumps(value)))
        applied[key] = value

    log_event(db, "INFO", "settings", f"Updated {len(applied)} setting(s)", applied)
    if rejected:
        log_event(db, "WARNING", "settings", f"Rejected {len(rejected)} invalid setting(s)", rejected)
    db.commit()
    return get_settings(db)


def reset_settings(db: Session) -> dict:
    # demo_seeded_at is not a preference, it is a fact about the rows in this
    # database: clearing it would drop the "synthetic data" label off data that
    # is still synthetic.
    db.query(SystemSetting).filter(SystemSetting.key != "demo_seeded_at").delete()
    log_event(db, "WARNING", "settings", "Settings reset to defaults")
    db.commit()
    return get_settings(db)


# --------------------------------------------------------------------------
# water tank
# --------------------------------------------------------------------------

def _water_used_ml(db: Session, since: Optional[datetime]) -> float:
    q = db.query(func.coalesce(func.sum(CleaningAction.water_volume), 0.0)).filter(
        CleaningAction.success.is_(True)
    )
    if since:
        q = q.filter(CleaningAction.timestamp >= since)
    return float(q.scalar() or 0.0)


def water_status(db: Session, config: Optional[dict] = None) -> dict:
    config = config or get_settings(db)
    refilled_at = config.get("tank_refilled_at")
    since = datetime.fromisoformat(refilled_at) if refilled_at else None
    used = _water_used_ml(db, since)
    capacity = settings.water_tank_capacity_ml
    remaining = max(0.0, capacity - used)
    return {
        "capacity_ml": capacity,
        "used_ml": round(used, 1),
        "remaining_ml": round(remaining, 1),
        "level_percent": round(remaining / capacity * 100, 1) if capacity else 0.0,
    }


def refill_tank(db: Session) -> dict:
    update_settings(db, {"tank_refilled_at": utcnow().isoformat()})
    log_event(db, "INFO", "hardware", "Water tank refilled")
    db.commit()
    return water_status(db)


# --------------------------------------------------------------------------
# hardware telemetry
# --------------------------------------------------------------------------

def latest_telemetry() -> dict:
    """Most recent capture from the ESP32 logs in Hardware/."""
    captures = sorted(Path(settings.hardware_dir).glob("panel_data_*.json"))
    if not captures:
        return {"available": False, "readings": []}
    try:
        readings = json.loads(captures[-1].read_text())
    except (OSError, json.JSONDecodeError) as e:
        return {"available": False, "readings": [], "error": str(e)}

    if not isinstance(readings, list) or not readings:
        return {"available": False, "readings": []}

    # One capture file holds several sweeps; keep the newest row per panel.
    latest: dict = {}
    for row in readings:
        panel = row.get("panel_id")
        if panel and row.get("timestamp", "") >= latest.get(panel, {}).get("timestamp", ""):
            latest[panel] = row

    # Node order, not file order: PANNEL_10 must not sort before PANNEL_2, and both
    # the console table and the panel lookup read this list positionally.
    def node_index(row):
        digits = "".join(c for c in str(row.get("panel_id", "")) if c.isdigit())
        return int(digits) if digits else 0

    rows = sorted(latest.values(), key=node_index)
    numeric = lambda key: [r[key] for r in rows if isinstance(r.get(key), (int, float))]
    temps, humidity, efficiency = numeric("temperature"), numeric("humidity"), numeric("efficiency")
    return {
        "available": True,
        "source": captures[-1].name,
        "captured_at": max(r.get("timestamp", "") for r in rows),
        "readings": rows,
        "avg_temperature": round(sum(temps) / len(temps), 1) if temps else None,
        "avg_humidity": round(sum(humidity) / len(humidity), 1) if humidity else None,
        "avg_efficiency": round(sum(efficiency) / len(efficiency), 1) if efficiency else None,
    }


# --------------------------------------------------------------------------
# health & stats
# --------------------------------------------------------------------------

def _camera_status() -> str:
    images = [Path(settings.image_dir) / f"{p}_test.jpg" for p in settings.panel_ids]
    found = sum(1 for p in images if p.is_file())
    if found == len(images):
        return "online"
    return "degraded" if found else "offline"


def _format_uptime(seconds: float) -> str:
    delta = timedelta(seconds=int(seconds))
    days, rem = divmod(int(delta.total_seconds()), 86400)
    hours, rem = divmod(rem, 3600)
    minutes = rem // 60
    if days:
        return f"{days}d {hours}h"
    return f"{hours}h {minutes}m" if hours else f"{minutes}m"


def health(db: Session) -> dict:
    config = get_settings(db)
    water = water_status(db, config)
    telemetry = latest_telemetry()
    camera = _camera_status()

    degraded = camera != "online" or water["level_percent"] < 10
    return {
        "status": "paused" if config["system_mode"] == "paused" else ("degraded" if degraded else "healthy"),
        "timestamp": utcnow().isoformat(),
        "water_level": water["level_percent"],
        "water": water,
        "camera_status": camera,
        "system_temperature": (
            f"{telemetry['avg_temperature']}°C" if telemetry.get("avg_temperature") is not None else "n/a"
        ),
        "system_mode": config["system_mode"],
        "telemetry_available": telemetry["available"],
    }


def system_stats(db: Session) -> dict:
    total_cleanings = db.query(CleaningAction).filter(CleaningAction.success.is_(True)).count()
    total_analyses = db.query(PanelStatus).count()
    avg_dust = db.query(func.avg(PanelStatus.dust_level)).scalar()
    water_used = _water_used_ml(db, None)
    last_analysis = db.query(func.max(PanelStatus.timestamp)).scalar()

    return {
        "total_panels": len(settings.panel_ids),
        "total_cleanings": total_cleanings,
        "total_analyses": total_analyses,
        "system_uptime": _format_uptime(time.time() - PROCESS_STARTED_AT),
        "water_used_total": round(water_used, 1),
        "avg_dust_level": round(float(avg_dust), 4) if avg_dust is not None else 0.0,
        "last_analysis": last_analysis.isoformat() if last_analysis else None,
    }


def system_logs(db: Session, limit: int = 50) -> list:
    # The API takes this from a query string, so it is bounded here rather than
    # trusting a caller to ask for a sane number of rows.
    limit = max(1, min(int(limit), 500))
    rows = db.query(SystemLog).order_by(SystemLog.timestamp.desc()).limit(limit).all()
    return [row.to_dict() for row in rows]


# --------------------------------------------------------------------------
# panels
# --------------------------------------------------------------------------

def _panel_image(panel_id: str) -> Path:
    return Path(settings.image_dir) / f"{panel_id}_test.jpg"


def analyze_panel(db: Session, panel_id: str) -> dict:
    """Run the CV + forecasting pipeline for one panel and record the decision."""
    invalid = unknown_panel(panel_id)
    if invalid:
        return invalid

    config = get_settings(db)
    image_path = _panel_image(panel_id)

    result = classifier.classify_dust_level(image_path)
    if "error" in result:
        log_event(db, "ERROR", "image_classifier", f"Analysis failed for {panel_id}", result)
        db.commit()
        return {"error": f"Image classification failed: {result['error']}", "panel_id": panel_id}

    dust_percent = result["dust_level"] * 100
    if dust_percent > config["dust_threshold"]:
        decision, action = "spray_now", "🚿 Cleaning initiated - High dust detected"
        spray_duration = config["spray_duration"]
    elif dust_percent > config["schedule_threshold"]:
        decision, action = "schedule_cleaning", "⏰ Cleaning scheduled - Moderate dust detected"
        spray_duration = config["spray_duration"]
    else:
        decision, action = "no_action", "✅ Panel is clean - No action needed"
        spray_duration = 0

    db.add(
        PanelStatus(
            panel_id=panel_id,
            dust_level=result["dust_level"],
            classification_confidence=result["confidence"],
            is_dirty=dust_percent > config["schedule_threshold"],
            needs_cleaning=dust_percent > config["dust_threshold"],
            image_path=str(image_path),
        )
    )

    decision_data = {
        "decision_id": f"decision_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
        "panel_id": panel_id,
        "dust_level": result["dust_level"],
        "status": result["status"],
        "confidence": result["confidence"],
        "decision": decision,
        "action": action,
        "spray_duration": spray_duration,
        "water_volume": spray_duration * ML_PER_SECOND_OF_SPRAY,
        "timestamp": utcnow().isoformat(),
        "analysis": {
            key: result[key]
            for key in (
                "visual_score", "image_quality", "insights", "processing_time_ms",
                "daily_power_loss_kwh", "power_loss_percentage", "optimal_cleaning_window",
                "cleaning_cost_usd", "estimated_savings_weekly", "roi_percentage",
                "payback_period_days", "recommendation", "reasoning",
            )
        },
    }

    db.add(
        SystemDecision(
            decision_id=decision_data["decision_id"],
            decision_data=json.dumps(decision_data),
            panels_involved=panel_id,
            action_taken=decision,
            execution_status="completed",
        )
    )
    log_event(
        db, "INFO", "analyzer",
        f"{panel_id}: {dust_percent:.1f}% dust ({result['status']}) → {decision}",
        {"dust_level": result["dust_level"], "confidence": result["confidence"]},
    )
    _write_latest_decision(decision_data)
    db.commit()

    # Automated execution: the auto_clean setting is what makes the decision act.
    if decision == "spray_now" and config["auto_clean"] and config["system_mode"] == "active":
        decision_data["auto_clean"] = spray_panel(db, panel_id)
        row = db.query(SystemDecision).filter_by(decision_id=decision_data["decision_id"]).first()
        if row:
            row.execution_status = "failed" if "error" in decision_data["auto_clean"] else "executed"
            row.decision_data = json.dumps(decision_data)
            db.commit()
        _write_latest_decision(decision_data)

    return decision_data


def _write_latest_decision(decision_data: dict):
    """Mirror the newest decision to disk. Best effort — read-only filesystems
    (serverless) are expected and must not fail the request."""
    try:
        settings.decisions_dir.mkdir(parents=True, exist_ok=True)
        (settings.decisions_dir / "latest_decision.json").write_text(
            json.dumps(decision_data, indent=2)
        )
    except OSError:
        pass


def latest_decision(db: Session) -> dict:
    row = db.query(SystemDecision).order_by(SystemDecision.timestamp.desc()).first()
    if row:
        return json.loads(row.decision_data)

    fallback = settings.decisions_dir / "latest_decision.json"
    if fallback.is_file():
        try:
            return json.loads(fallback.read_text())
        except (OSError, json.JSONDecodeError):
            pass
    return {"message": "No decisions made yet. Try /analyze first!"}


def spray_panel(db: Session, panel_id: str) -> dict:
    invalid = unknown_panel(panel_id)
    if invalid:
        return invalid

    config = get_settings(db)

    if config["system_mode"] == "paused":
        log_event(db, "WARNING", "spray_controller", f"Spray refused for {panel_id}: system paused")
        db.commit()
        return {"error": "System is paused — resume it from Settings before cleaning.", "panel_id": panel_id}

    duration = float(config["spray_duration"])
    volume = duration * ML_PER_SECOND_OF_SPRAY
    water = water_status(db, config)

    if water["remaining_ml"] < volume:
        db.add(
            CleaningAction(
                panel_id=panel_id, action_type="spray", water_volume=0, duration=0,
                success=False, error_message="Insufficient water in tank",
            )
        )
        log_event(db, "ERROR", "spray_controller", f"Spray aborted for {panel_id}: tank empty", water)
        db.commit()
        return {
            "error": f"Insufficient water: {water['remaining_ml']:.0f}ml left, {volume:.0f}ml required.",
            "panel_id": panel_id,
        }

    db.add(
        CleaningAction(
            panel_id=panel_id, action_type="spray", water_volume=volume,
            duration=duration, success=True,
        )
    )
    log_event(
        db, "INFO", "spray_controller",
        f"{panel_id}: sprayed {volume:.0f}ml over {duration:.0f}s", {"pressure": config["water_pressure"]},
    )
    db.commit()

    return {
        "panel_id": panel_id,
        "action": "🚿 spray_completed",
        "duration_seconds": duration,
        "water_used_ml": volume,
        "pressure": config["water_pressure"],
        "timestamp": utcnow().isoformat(),
        "water_remaining_ml": round(water["remaining_ml"] - volume, 1),
        "next_check": "in 24 hours",
    }


def list_panels(db: Session) -> dict:
    panels = []
    for panel_id in settings.panel_ids:
        status_row = (
            db.query(PanelStatus)
            .filter(PanelStatus.panel_id == panel_id)
            .order_by(PanelStatus.timestamp.desc())
            .first()
        )
        cleaned_at = (
            db.query(func.max(CleaningAction.timestamp))
            .filter(CleaningAction.panel_id == panel_id, CleaningAction.success.is_(True))
            .scalar()
        )

        if status_row is None:
            status = "unknown"
        elif status_row.needs_cleaning:
            status = "needs_cleaning"
        elif status_row.is_dirty:
            status = "moderate_dust"
        else:
            status = "clean"

        panels.append(
            {
                "id": panel_id,
                "status": status,
                "last_cleaned": cleaned_at.strftime("%Y-%m-%d") if cleaned_at else "Never",
                "dust_level": status_row.dust_level if status_row else None,
                "confidence": status_row.classification_confidence if status_row else None,
                "last_analysed": status_row.timestamp.isoformat() if status_row else None,
                "image_available": _panel_image(panel_id).is_file(),
            }
        )

    return {"total_panels": len(panels), "panels": panels}


def panel_history(db: Session, panel_id: str, limit: int = 10) -> dict:
    invalid = unknown_panel(panel_id)
    if invalid:
        return invalid

    status_history = (
        db.query(PanelStatus)
        .filter(PanelStatus.panel_id == panel_id)
        .order_by(PanelStatus.timestamp.desc())
        .limit(limit)
        .all()
    )
    cleaning_history = (
        db.query(CleaningAction)
        .filter(CleaningAction.panel_id == panel_id)
        .order_by(CleaningAction.timestamp.desc())
        .limit(limit)
        .all()
    )
    return {
        "panel_id": panel_id,
        "status_history": [row.to_dict() for row in status_history],
        "cleaning_history": [row.to_dict() for row in cleaning_history],
    }


# --------------------------------------------------------------------------
# aggregates and bulk operations
#
# These used to live in the Flask frontend, which meant the rules for "how many
# panels need attention" and "which panels does a bulk wash touch" were written
# in the presentation layer. They are business rules, so they live here and the
# console only renders what they return.
# --------------------------------------------------------------------------

DIRTY_STATUSES = ("moderate_dust", "needs_cleaning")


def panel_counts(panels: Optional[dict]) -> dict:
    """Status tallies for the dashboard, the panels page and the reports."""
    rows = (panels or {}).get("panels", [])
    counts = {"clean": 0, "moderate_dust": 0, "needs_cleaning": 0, "unknown": 0}
    for panel in rows:
        counts[panel["status"]] = counts.get(panel["status"], 0) + 1
    counts["total"] = len(rows)
    counts["attention"] = counts["moderate_dust"] + counts["needs_cleaning"]
    counts["health_percentage"] = round(counts["clean"] / len(rows) * 100, 1) if rows else 0.0
    return counts


def overview(db: Session) -> dict:
    """Everything a console page shows at once — one call instead of five.

    The frontend polls this on a timer, so it is also the shape that keeps the
    open page current.
    """
    panels = list_panels(db)
    return {
        "health": health(db),
        "panels": panels["panels"],
        "counts": panel_counts(panels),
        "stats": system_stats(db),
        "latest_decision": latest_decision(db),
        "settings": get_settings(db),
        "timestamp": utcnow().isoformat(),
    }


def panel_detail(db: Session, panel_id: str) -> dict:
    """One panel in full: its current state, its history and its sensor node."""
    invalid = unknown_panel(panel_id)
    if invalid:
        return invalid

    summary = next((p for p in list_panels(db)["panels"] if p["id"] == panel_id), None)

    # Hardware logs index panels as PANNEL_0..N, in the same order as panel_ids.
    hardware_id = f"PANNEL_{settings.panel_ids.index(panel_id)}"
    readings = latest_telemetry().get("readings", [])
    reading = next((r for r in readings if r.get("panel_id") == hardware_id), None)

    return {"panel": summary, "telemetry": reading, **panel_history(db, panel_id)}


def analyze_all(db: Session) -> dict:
    """Analyse every configured panel, reporting failures rather than hiding them."""
    results, failures = [], []
    for panel in list_panels(db)["panels"]:
        result = analyze_panel(db, panel["id"])
        if "error" in result:
            failures.append({"panel_id": panel["id"], "error": result["error"]})
        else:
            results.append(result)

    return {
        "results": results,
        "failures": failures,
        "analysed": len(results),
        "message": f"Analysed {len(results)} panel(s)"
                   + (f", {len(failures)} failed" if failures else "") + ".",
    }


def resolve_spray_scope(db: Session, scope: str) -> list:
    """Which panels a bulk wash touches. 'dirty' is the only one that filters."""
    rows = list_panels(db)["panels"]
    if scope == "all":
        return [panel["id"] for panel in rows]
    if scope == "dirty":
        return [panel["id"] for panel in rows if panel["status"] in DIRTY_STATUSES]
    raise ValueError("scope must be 'dirty' or 'all'")


def spray_many(db: Session, scope: str = "dirty") -> dict:
    """Wash a set of panels. Every panel is sprayed through the same guarded path
    as a single wash, so a paused system or an empty tank still refuses each one."""
    total_panels = len(list_panels(db)["panels"])
    targets = resolve_spray_scope(db, scope)

    if not targets:
        return {
            "results": [], "failures": [], "total_panels": total_panels,
            "targeted": 0, "cleaned": 0, "water_used_ml": 0,
            "message": "Every panel is clean. Nothing to do.",
        }

    results, failures, water = [], [], 0.0
    for panel_id in targets:
        result = spray_panel(db, panel_id)
        if "error" in result:
            failures.append({"panel_id": panel_id, "error": result["error"]})
        else:
            results.append(result)
            water += result.get("water_used_ml", 0)

    return {
        "results": results,
        "failures": failures,
        "total_panels": total_panels,
        "targeted": len(targets),
        "cleaned": len(results),
        "water_used_ml": round(water, 1),
        "message": f"Cleaned {len(results)} of {len(targets)} panel(s) using {water:.0f}ml.",
    }
