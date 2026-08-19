"""FastAPI backend.

Every route is a thin wrapper over Backend.services — the same functions the
Flask frontend calls in-process. Routes that touch the CV pipeline are declared
`def` (not `async def`) so FastAPI runs them in a worker thread instead of
blocking the event loop.
"""

import os

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from Backend import services
from Backend.config.settings import settings
from Backend.database.connection import get_db, init_database

app = FastAPI(title="Solar Panel Cleaning System", version="1.0.0")

_default_origins = f"http://localhost:{settings.frontend_port},http://127.0.0.1:{settings.frontend_port}"
allowed_origins = [o.strip() for o in os.getenv("CORS_ORIGINS", _default_origins).split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_database()


class PanelRequest(BaseModel):
    panel_id: str = "panel_01"


class SettingsRequest(BaseModel):
    values: dict


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


@app.post("/analyze")
def analyze_panel(request: PanelRequest, db: Session = Depends(get_db)):
    """Analyze a solar panel for dust levels and record the resulting decision."""
    return services.analyze_panel(db, request.panel_id)


@app.get("/latest-decision")
def get_latest_decision(db: Session = Depends(get_db)):
    return services.latest_decision(db)


@app.post("/spray")
def spray_panel(request: PanelRequest, db: Session = Depends(get_db)):
    return services.spray_panel(db, request.panel_id)


@app.get("/panels")
def list_panels(db: Session = Depends(get_db)):
    return services.list_panels(db)


@app.get("/panels/{panel_id}/history")
def get_panel_history(panel_id: str, db: Session = Depends(get_db)):
    return services.panel_history(db, panel_id)


@app.get("/system/logs")
def get_system_logs(limit: int = 50, db: Session = Depends(get_db)):
    return services.system_logs(db, limit)


@app.get("/system/stats")
def get_system_stats(db: Session = Depends(get_db)):
    return services.system_stats(db)


@app.get("/settings")
def get_settings(db: Session = Depends(get_db)):
    return services.get_settings(db)


@app.put("/settings")
def put_settings(request: SettingsRequest, db: Session = Depends(get_db)):
    return services.update_settings(db, request.values)


@app.post("/settings/reset")
def post_settings_reset(db: Session = Depends(get_db)):
    return services.reset_settings(db)


@app.post("/system/refill-tank")
def post_refill_tank(db: Session = Depends(get_db)):
    return services.refill_tank(db)


@app.get("/hardware/telemetry")
def get_telemetry():
    return services.latest_telemetry()
