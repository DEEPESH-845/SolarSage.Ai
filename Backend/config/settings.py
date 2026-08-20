import os
from pathlib import Path
from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[2]

# Serverless hosts ship a read-only filesystem with only /tmp writable. Default
# the writable directory there so a deployment works without extra configuration;
# DATA_DIR still overrides it.
SERVERLESS = bool(os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"))
DEFAULT_DATA_DIR = Path("/tmp/solarsage") if SERVERLESS else REPO_ROOT / "Backend" / "data"


class Settings(BaseSettings):
    """Deployment-level configuration. Runtime-tunable values live in the
    system_settings table instead — see Backend/services.py."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Writable storage. Serverless hosts only allow /tmp, so set DATA_DIR there.
    data_dir: Path = DEFAULT_DATA_DIR
    # Read-only fixtures shipped with the repo — never written to.
    image_dir: Path = REPO_ROOT / "Backend" / "data" / "images"
    hardware_dir: Path = REPO_ROOT / "Hardware"

    # Defaults to <data_dir>/solar_panel_system.db; override with SQLITE_DATABASE_PATH.
    sqlite_database_path: Optional[Path] = None

    panel_ids: List[str] = ["panel_01", "panel_02", "panel_03", "panel_04"]

    # Seed an empty database with synthetic panel history, so a console deployed
    # without hardware behind it shows a working system rather than four unknown
    # panels. Set DEMO_DATA=false to leave an empty database empty.
    demo_data: bool = True
    water_tank_capacity_ml: int = 5000

    api_host: str = "0.0.0.0"
    api_port: int = 8000

    @property
    def db_path(self) -> Path:
        return self.sqlite_database_path or self.data_dir / "solar_panel_system.db"

    @property
    def decisions_dir(self) -> Path:
        return self.data_dir / "decisions"


settings = Settings()
