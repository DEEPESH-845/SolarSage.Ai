from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    database_type: str = "sqlite"
    sqlite_database_path: str = "./data/solar_panel_system.db"
    
    # ESP32 Communication
    esp32_serial_port: str = "/dev/ttyUSB0"  # Linux
    esp32_baudrate: int = 115200
    
    # MQTT Configuration
    mqtt_enabled: bool = True
    mqtt_broker_host: str = "192.168.1.100"
    mqtt_broker_port: int = 1883
    mqtt_username: Optional[str] = None
    mqtt_password: Optional[str] = None
    
    # Camera Settings
    image_save_path: str = "./data/images"
    image_format: str = "jpg"
    
    # AI Model
    model_confidence_threshold: float = 0.8
    
    # Panel Configuration
    panel_positions: dict = {
        "panel_001": {"x": 45, "y": 90},
        "panel_002": {"x": 90, "y": 90},
        "panel_003": {"x": 135, "y": 90},
    }
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    class Config:
        env_file = ".env"

settings = Settings()