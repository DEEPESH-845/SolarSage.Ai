"""FastAPI backend.

Every route is a thin wrapper over Backend.services — the same functions the
Flask frontend calls in-process. Routes that touch the CV pipeline are declared
`def` (not `async def`) so FastAPI runs them in a worker thread instead of
blocking the event loop.
"""

import os

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from Backend import demo, services
from Backend.config.settings import settings
from Backend.database.connection import SessionLocal, get_db, init_database

app = FastAPI(title="Solar Panel Cleaning System", version="1.0.0")

_default_origins = "http://localhost:3000,http://127.0.0.1:3000"
allowed_origins = [o.strip() for o in os.getenv("CORS_ORIGINS", _default_origins).split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Writes here open a valve and spend water. When this API is reachable from
# anywhere — which it is once deployed — a shared secret is the difference
# between an operator and a stranger. Set API_TOKEN on both this deployment and
# the console (web/), and every mutating route starts demanding it. Left unset,
# the API is open, which is fine on a laptop and not fine in front of a pump.
API_TOKEN = os.getenv("API_TOKEN")


def require_token(x_api_key: str = Header(default="")):
    """Guards every route that changes something. A read stays open."""
    if API_TOKEN and x_api_key != API_TOKEN:
        raise HTTPException(status_code=401, detail="A valid X-API-Key header is required.")


init_database()

# See Backend/demo.py — no-op once the database holds a real analysis.
with SessionLocal() as _boot_session:
    demo.seed_if_empty(_boot_session)


class PanelRequest(BaseModel):
    panel_id: str = "panel_01"


class SettingsRequest(BaseModel):
    values: dict


class SprayScopeRequest(BaseModel):
    scope: str = "dirty"  # dirty | all


def _found(result: dict) -> dict:
    """An unknown panel is a missing resource, not a 200 with an error in it."""
    if isinstance(result, dict) and str(result.get("error", "")).startswith("Unknown panel"):
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@app.get("/")
async def root():
    return {
        "message": "🌞 Solar Panel Cleaning System Running!",
        "status": "online",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
def health(db: Session = Depends(get_db)):
    return services.health(db)


@app.post("/analyze", dependencies=[Depends(require_token)])
def analyze_panel(request: PanelRequest, db: Session = Depends(get_db)):
    """Analyze a solar panel for dust levels and record the resulting decision."""
    return _found(services.analyze_panel(db, request.panel_id))


@app.get("/latest-decision")
def get_latest_decision(db: Session = Depends(get_db)):
    return services.latest_decision(db)


@app.post("/spray", dependencies=[Depends(require_token)])
def spray_panel(request: PanelRequest, db: Session = Depends(get_db)):
    return _found(services.spray_panel(db, request.panel_id))


@app.get("/panels")
def list_panels(db: Session = Depends(get_db)):
    return services.list_panels(db)


@app.get("/panels/{panel_id}/history")
def get_panel_history(panel_id: str, db: Session = Depends(get_db)):
    return _found(services.panel_history(db, panel_id))


@app.get("/panels/{panel_id}/detail")
def get_panel_detail(panel_id: str, db: Session = Depends(get_db)):
    """Current state, history and sensor node for one panel — the detail drawer."""
    return _found(services.panel_detail(db, panel_id))


@app.get("/overview")
def get_overview(db: Session = Depends(get_db)):
    """Health, panels, tallies, stats and the newest decision in one response.

    Console pages render from this, and the open page polls it to stay current.
    """
    return services.overview(db)


@app.post("/panels/analyze-all", dependencies=[Depends(require_token)])
def post_analyze_all(db: Session = Depends(get_db)):
    return services.analyze_all(db)


@app.post("/panels/spray", dependencies=[Depends(require_token)])
def post_spray_many(request: SprayScopeRequest, db: Session = Depends(get_db)):
    """Bulk wash. `scope` is 'dirty' (past the schedule threshold) or 'all'."""
    try:
        return services.spray_many(db, request.scope)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/system/logs")
def get_system_logs(limit: int = 50, db: Session = Depends(get_db)):
    return services.system_logs(db, limit)


@app.get("/system/stats")
def get_system_stats(db: Session = Depends(get_db)):
    return services.system_stats(db)


@app.get("/settings")
def get_settings(db: Session = Depends(get_db)):
    return services.get_settings(db)


@app.put("/settings", dependencies=[Depends(require_token)])
def put_settings(request: SettingsRequest, db: Session = Depends(get_db)):
    return services.update_settings(db, request.values)


@app.post("/settings/reset", dependencies=[Depends(require_token)])
def post_settings_reset(db: Session = Depends(get_db)):
    return services.reset_settings(db)


@app.post("/system/refill-tank", dependencies=[Depends(require_token)])
def post_refill_tank(db: Session = Depends(get_db)):
    return services.refill_tank(db)


@app.get("/hardware/telemetry")
def get_telemetry():
    return services.latest_telemetry()
