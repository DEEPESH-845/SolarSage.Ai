import os
from pathlib import Path

class Config:
    # Base paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    INPUT_DIR = DATA_DIR / "input"
    OUTPUT_DIR = DATA_DIR / "output"
    MODELS_DIR = DATA_DIR / "models"
    LOGS_DIR = BASE_DIR / "logs"
    
    # API Keys
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "your_api_key_here")
    
    # Model paths
    DIRT_CLASSIFIER_PATH = MODELS_DIR / "dirt_classifier.pth"
    IMAGE_CLASSIFIER_PATH = MODELS_DIR / "image_classifier.pth"
    
    # Agent communication files
    DUST_ANALYSIS_FILE = OUTPUT_DIR / "dust_analysis" / "dust_results.json"
    IMAGE_ANALYSIS_FILE = OUTPUT_DIR / "image_analysis" / "image_results.json"
    COORDINATION_FILE = OUTPUT_DIR / "coordination" / "coordination_results.json"
    SPRAYING_FILE = OUTPUT_DIR / "spraying_results" / "spraying_plan.json"
    
    # Processing parameters
    IMAGE_SIZE = (224, 224)
    BATCH_SIZE = 32
    CONFIDENCE_THRESHOLD = 0.7
    
    # Dirt classification levels
    DIRT_LEVELS = {
        0: "clean",
        1: "light",
        2: "moderate", 
        3: "heavy"
    }
    
    # Spraying parameters
    SPRAYING_PATTERNS = {
        "clean": {"duration": 0, "pressure": "none", "water_usage": 0},
        "light": {"duration": 30, "pressure": "low", "water_usage": 5},
        "moderate": {"duration": 60, "pressure": "medium", "water_usage": 10},
        "heavy": {"duration": 120, "pressure": "high", "water_usage": 20}
    }