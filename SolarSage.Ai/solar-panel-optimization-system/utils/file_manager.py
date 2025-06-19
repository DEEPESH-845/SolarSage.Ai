# utils/file_manager.py
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class FileManager:
    """Handles JSON file operations for agent communication"""
    
    @staticmethod
    def ensure_directory(file_path: Path):
        """Ensure directory exists for file path"""
        file_path.parent.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def save_json(data: Dict, file_path: Path, create_backup: bool = True) -> bool:
        """Save data to JSON file"""
        try:
            FileManager.ensure_directory(file_path)
            
            # Create backup if file exists
            if create_backup and file_path.exists():
                backup_path = file_path.with_suffix(f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
                file_path.rename(backup_path)
            
            # Add metadata
            data['metadata'] = {
                'timestamp': datetime.now().isoformat(),
                'file_path': str(file_path),
                'version': '1.0'
            }
            
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            logger.info(f"Successfully saved data to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving data to {file_path}: {e}")
            return False
    
    @staticmethod
    def load_json(file_path: Path) -> Dict:
        """Load data from JSON file"""
        try:
            if not file_path.exists():
                logger.warning(f"File {file_path} does not exist")
                return {}
            
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            logger.info(f"Successfully loaded data from {file_path}")
            return data
            
        except Exception as e:
            logger.error(f"Error loading data from {file_path}: {e}")
            return {}
    
    @staticmethod
    def wait_for_file(file_path: Path, timeout: int = 60) -> bool:
        """Wait for file to be created (for agent synchronization)"""
        import time
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            if file_path.exists():
                # Wait a bit more to ensure file is fully written
                time.sleep(1)
                return True
            time.sleep(0.5)
        
        logger.warning(f"Timeout waiting for file {file_path}")
        return False
    
    @staticmethod
    def cleanup_old_files(directory: Path, max_age_hours: int = 24):
        """Clean up old files in directory"""
        try:
            current_time = datetime.now()
            for file_path in directory.glob("*.json"):
                file_age = current_time - datetime.fromtimestamp(file_path.stat().st_mtime)
                if file_age.total_seconds() > max_age_hours * 3600:
                    file_path.unlink()
                    logger.info(f"Cleaned up old file: {file_path}")
        except Exception as e:
            logger.error(f"Error cleaning up files in {directory}: {e}")