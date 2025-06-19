# config/logging_config.py
import logging
import os
from pathlib import Path

def setup_logging(log_level=logging.INFO):
    """Setup logging configuration"""
    
    # Create logs directory if it doesn't exist
    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "system.log"),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)
