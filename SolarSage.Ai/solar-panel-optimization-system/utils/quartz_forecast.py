
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

class SolarForecaster:
    """Solar power forecasting using simplified Quartz methodology"""
    
    def __init__(self):
        # Solar constants
        self.solar_constant = 1361  # W/m² - Solar constant outside atmosphere
        self.panel_efficiency = 0.20  # 20% typical efficiency
        self.system_losses = 0.15  # 15% system losses
        
    def calculate_solar_position(self, latitude: float, longitude: float, 
                               timestamp: datetime) -> Dict[str, float]:
        """Calculate solar position (elevation and azimuth)"""
        try:
            # Convert to Julian day
            julian_day = timestamp.timetuple().tm_yday
            
            # Solar declination angle
            declination = 23.45 * np.sin(np.radians(360 * (284 + julian_day) / 365))
            
            # Hour angle
            hour_angle = 15 * (timestamp.hour + timestamp.minute/60 - 12)
            
            # Solar elevation angle
            lat_rad = np.radians(latitude)
            dec_rad = np.radians(declination)
            hour_rad = np.radians(hour_angle)
            
            elevation = np.arcsin(
                np.sin(lat_rad) * np.sin(dec_rad) + 
                np.cos(lat_rad) * np.cos(dec_rad) * np.cos(hour_rad)
            )
            
            # Solar azimuth angle
            azimuth = np.arctan2(
                np.sin(hour_rad),
                np.cos(hour_rad) * np.sin(lat_rad) - np.tan(dec_rad) * np.cos(lat_rad)
            )
            
            return {
                "elevation": np.degrees(elevation),
                "azimuth": np.degrees(azimuth),
                "declination": declination
            }
            
        except Exception as e:
            logger.error(f"Error calculating solar position: {e}")
            return {"elevation": 0, "azimuth": 0, "declination": 0}
    
    def calculate_clear_sky_irradiance(self, elevation: float, altitude: float = 0) -> float:
        """Calculate clear sky solar irradiance"""
        if elevation <= 0:
            return 0
        
        # Air mass calculation
        air_mass = 1 / (np.sin(np.radians(elevation)) + 0.50572 * (elevation + 6.07995)**-1.6364)
        
        # Altitude correction
        altitude_factor = np.exp(-altitude / 8400)  # Scale height ~8.4 km
        
        # Clear sky irradiance (simplified model)
        clear_sky = self.solar_constant * np.sin(np.radians(elevation)) * (0.7**(air_mass**0.678)) * altitude_factor
        
        return max(0, clear_sky)
    
    def apply_weather_corrections(self, clear_sky_irradiance: float, 
                                weather_data: Dict) -> float:
        """Apply weather-based corrections to clear sky irradiance"""
        try:
            cloudiness = weather_data.get("cloudiness", 0) / 100  # Convert to fraction
            humidity = weather_data.get("humidity", 50) / 100
            visibility = weather_data.get("visibility", 10000) / 10000  # Normalize to 10km
            
            # Cloud factor (simplified)
            cloud_factor = 1 - 0.8 * cloudiness
            
            # Humidity factor (higher humidity slightly reduces irradiance)
            humidity_factor = 1 - 0.1 * humidity
            
            # Visibility factor (reduced visibility = more atmospheric scattering)
            visibility_factor = 0.8 + 0.2 * visibility
            
            # Combined weather factor
            weather_factor = cloud_factor * humidity_factor * visibility_factor
            
            return clear_sky_irradiance * max(0.1, weather_factor)
            
        except Exception as e:
            logger.error(f"Error applying weather corrections: {e}")
            return clear_sky_irradiance * 0.5  # Default to 50% if error
    
    def calculate_panel_power(self, irradiance: float, panel_area: float = 2.0,
                            cleanliness_factor: float = 1.0) -> float:
        """Calculate panel power output"""
        try:
            # Base power calculation
            base_power = (irradiance * panel_area * self.panel_efficiency * 
                         (1 - self.system_losses)) / 1000  # Convert to kW
            
            # Apply cleanliness factor
            actual_power = base_power * cleanliness_factor
            
            return max(0, actual_power)
            
        except Exception as e:
            logger.error(f"Error calculating panel power: {e}")
            return 0
    
    def generate_hourly_forecast(self, latitude: float, longitude: float,
                               weather_forecast: Dict, 
                               cleanliness_factor: float = 1.0) -> List[Dict]:
        """Generate hourly solar power forecast"""
        try:
            forecasts = weather_forecast.get("forecasts", [])
            hourly_forecast = []
            
            for forecast_item in forecasts:
                # Parse datetime
                try:
                    forecast_time = datetime.strptime(forecast_item["datetime"], "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    continue
                
                # Calculate solar position
                solar_pos = self.calculate_solar_position(latitude, longitude, forecast_time)
                
                # Calculate clear sky irradiance
                clear_sky = self.calculate_clear_sky_irradiance(solar_pos["elevation"])
                
                # Apply weather corrections
                actual_irradiance = self.apply_weather_corrections(clear_sky, forecast_item)
                
                # Calculate power output
                power_output = self.calculate_panel_power(actual_irradiance, 2.0, cleanliness_factor)
                
                hourly_forecast.append({
                    "datetime": forecast_item["datetime"],
                    "solar_elevation": round(solar_pos["elevation"], 2),
                    "clear_sky_irradiance": round(clear_sky, 2),
                    "actual_irradiance": round(actual_irradiance, 2),
                    "power_output_kw": round(power_output, 3),
                    "weather_conditions": {
                        "temperature": forecast_item.get("temperature"),
                        "cloudiness": forecast_item.get("cloudiness"),
                        "weather": forecast_item.get("weather_description")
                    }
                })
            
            return hourly_forecast
            
        except Exception as e:
            logger.error(f"Error generating hourly forecast: {e}")
            return []
    
    def calculate_daily_summary(self, hourly_forecast: List[Dict]) -> Dict:
        """Calculate daily summary from hourly forecast"""
        try:
            if not hourly_forecast:
                return {}
            
            # Extract power values
            power_values = [item["power_output_kw"] for item in hourly_forecast]
            irradiance_values = [item["actual_irradiance"] for item in hourly_forecast]
            
            # Calculate statistics
            total_energy = sum(power_values)  # kWh (assuming 1-hour intervals)
            peak_power = max(power_values)
            avg_power = np.mean(power_values)
            peak_irradiance = max(irradiance_values)
            avg_irradiance = np.mean(irradiance_values)
            
            # Find peak hours
            peak_hours = [item["datetime"] for item in hourly_forecast 
                         if item["power_output_kw"] >= peak_power * 0.8]
            
            summary = {
                "total_daily_energy_kwh": round(total_energy, 2),
                "peak_power_kw": round(peak_power, 3),
                "average_power_kw": round(avg_power, 3),
                "peak_irradiance_wm2": round(peak_irradiance, 2),
                "average_irradiance_wm2": round(avg_irradiance, 2),
                "peak_hours": peak_hours[:3],  # Top 3 peak hours
                "capacity_factor": round(avg_power / max(peak_power, 0.001), 3),
                "forecast_date": hourly_forecast[0]["datetime"][:10]
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error calculating daily summary: {e}")
            return {}

---

# utils/validation.py
"""
Data validation utilities for the solar panel optimization system
"""

import os
from pathlib import Path
from typing import Dict, List, Tuple, Any
import logging

logger = logging.getLogger(__name__)

class DataValidator:
    """Validates input data and system requirements"""
    
    @staticmethod
    def validate_panel_data(panel_data: Dict) -> Tuple[bool, List[str]]:
        """Validate panel data structure"""
        errors = []
        
        # Required fields
        required_fields = ["panel_id", "image_path", "latitude", "longitude"]
        
        for field in required_fields:
            if field not in panel_data:
                errors.append(f"Missing required field: {field}")
            elif panel_data[field] is None:
                errors.append(f"Field {field} cannot be None")
        
        # Validate data types and ranges
        if "latitude" in panel_data:
            try:
                lat = float(panel_data["latitude"])
                if not -90 <= lat <= 90:
                    errors.append("Latitude must be between -90 and 90 degrees")
            except (ValueError, TypeError):
                errors.append("Latitude must be a valid number")
        
        if "longitude" in panel_data:
            try:
                lon = float(panel_data["longitude"])
                if not -180 <= lon <= 180:
                    errors.append("Longitude must be between -180 and 180 degrees")
            except (ValueError, TypeError):
                errors.append("Longitude must be a valid number")
        
        # Validate image path
        if "image_path" in panel_data:
            image_path = Path(panel_data["image_path"])
            if not image_path.exists():
                errors.append(f"Image file does not exist: {image_path}")
            elif not image_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp']:
                errors.append(f"Unsupported image format: {image_path.suffix}")
        
        # Validate panel ID format
        if "panel_id" in panel_data:
            panel_id = str(panel_data["panel_id"])
            if len(panel_id) == 0:
                errors.append("Panel ID cannot be empty")
            elif len(panel_id) > 50:
                errors.append("Panel ID too long (max 50 characters)")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_system_requirements() -> Tuple[bool, List[str]]:
        """Validate system requirements and dependencies"""
        errors = []
        
        # Check Python packages
        required_packages = [
            "torch", "torchvision", "opencv-python", "PIL", "numpy", 
            "pandas", "requests", "sklearn"
        ]
        
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
            except ImportError:
                errors.append(f"Required package not installed: {package}")
        
        # Check directory structure
        from config.settings import Config
        config = Config()
        
        required_dirs = [
            config.DATA_DIR,
            config.INPUT_DIR,
            config.OUTPUT_DIR,
            config.LOGS_DIR
        ]
        
        for directory in required_dirs:
            if not directory.exists():
                try:
                    directory.mkdir(parents=True, exist_ok=True)
                    logger.info(f"Created directory: {directory}")
                except PermissionError:
                    errors.append(f"Cannot create required directory: {directory}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_image_file(image_path: str) -> Tuple[bool, List[str]]:
        """Validate image file for processing"""
        errors = []
        
        try:
            from PIL import Image
            import cv2
            
            # Check file existence
            if not os.path.exists(image_path):
                errors.append(f"Image file not found: {image_path}")
                return False, errors
            
            # Check file size
            file_size = os.path.getsize(image_path)
            if file_size == 0:
                errors.append("Image file is empty")
            elif file_size > 50 * 1024 * 1024:  # 50MB limit
                errors.append("Image file too large (max 50MB)")
            
            # Try to open with PIL
            try:
                with Image.open(image_path) as img:
                    width, height = img.size
                    
                    if width < 50 or height < 50:
                        errors.append("Image too small (minimum 50x50 pixels)")
                    elif width > 4000 or height > 4000:
                        errors.append("Image too large (maximum 4000x4000 pixels)")
                    
                    # Check if image is corrupted
                    img.verify()
            except Exception as e:
                errors.append(f"Cannot open image with PIL: {e}")
            
            # Try to open with OpenCV
            try:
                image = cv2.imread(image_path)
                if image is None:
                    errors.append("Cannot open image with OpenCV")
            except Exception as e:
                errors.append(f"Cannot open image with OpenCV: {e}")
            
        except ImportError as e:
            errors.append(f"Required image processing library not available: {e}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_weather_data(weather_data: Dict) -> Tuple[bool, List[str]]:
        """Validate weather data structure"""
        errors = []
        
        if not isinstance(weather_data, dict):
            errors.append("Weather data must be a dictionary")
            return False, errors
        
        # Check for required weather fields
        recommended_fields = ["temperature", "humidity", "wind_speed", "cloudiness"]
        
        for field in recommended_fields:
            if field not in weather_data:
                logger.warning(f"Weather data missing recommended field: {field}")
        
        # Validate ranges
        validations = {
            "temperature": (-50, 70),  # Celsius
            "humidity": (0, 100),      # Percentage
            "wind_speed": (0, 100),    # m/s
            "cloudiness": (0, 100),    # Percentage
            "pressure": (800, 1200),   # hPa
            "visibility": (0, 50000)   # meters
        }
        
        for field, (min_val, max_val) in validations.items():
            if field in weather_data:
                try:
                    value = float(weather_data[field])
                    if not min_val <= value <= max_val:
                        errors.append(f"{field} value {value} outside valid range [{min_val}, {max_val}]")
                except (ValueError, TypeError):
                    errors.append(f"{field} must be a valid number")
        
        return len(errors) == 0, errors

---

# models/dirt_classifier.py
"""
Enhanced dirt classification model with transfer learning
"""

import torch
import torch.nn as nn
import torchvision.models as models
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class EnhancedDirtClassifier(nn.Module):
    """Enhanced dirt classifier using transfer learning"""
    
    def __init__(self, num_classes: int = 4, backbone: str = "resnet50", 
                 pretrained: bool = True, dropout_rate: float = 0.5):
        super(EnhancedDirtClassifier, self).__init__()
        
        self.num_classes = num_classes
        self.backbone_name = backbone
        
        # Initialize backbone
        if backbone == "resnet50":
            self.backbone = models.resnet50(pretrained=pretrained)
            feature_dim = self.backbone.fc.in_features
            self.backbone.fc = nn.Identity()
        elif backbone == "efficientnet_b0":
            self.backbone = models.efficientnet_b0(pretrained=pretrained)
            feature_dim = self.backbone.classifier[1].in_features
            self.backbone.classifier = nn.Identity()
        else:
            raise ValueError(f"Unsupported backbone: {backbone}")
        
        # Enhanced classifier with attention
        self.attention = nn.Sequential(
            nn.Linear(feature_dim, feature_dim // 4),
            nn.ReLU(inplace=True),
            nn.Linear(feature_dim // 4, feature_dim),
            nn.Sigmoid()
        )
        
        self.classifier = nn.Sequential(
            nn.Dropout(dropout_rate),
            nn.Linear(feature_dim, feature_dim // 2),
            nn.BatchNorm1d(feature_dim // 2),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout_rate / 2),
            nn.Linear(feature_dim // 2, feature_dim // 4),
            nn.BatchNorm1d(feature_dim // 4),
            nn.ReLU(inplace=True),
            nn.Linear(feature_dim // 4, num_classes)
        )
        
        # Additional regression head for cleanliness score
        self.cleanliness_regressor = nn.Sequential(
            nn.Linear(feature_dim, feature_dim // 4),
            nn.ReLU(inplace=True),
            nn.Linear(feature_dim // 4, 1),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        # Extract features
        features = self.backbone(x)
        
        # Apply attention mechanism
        attention_weights = self.attention(features)
        attended_features = features * attention_weights
        
        # Classification
        class_logits = self.classifier(attended_features)
        
        # Regression for cleanliness score
        cleanliness_score = self.cleanliness_regressor(attended_features)
        
        return {
            "classification": class_logits,
            "cleanliness": cleanliness_score,
            "features": features
        }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        total_params = sum(p.numel() for p in self.parameters())
        trainable_params = sum(p.numel() for p in self.parameters() if p.requires_grad)
        
        return {
            "backbone": self.backbone_name,
            "num_classes": self.num_classes,
            "total_parameters": total_params,
            "trainable_parameters": trainable_params,
            "model_size_mb": total_params * 4 / (1024 * 1024)  # Assume float32
        }

def create_dirt_classifier(config: Dict[str, Any]) -> EnhancedDirtClassifier:
    """Factory function to create dirt classifier"""
    
    model_config = {
        "num_classes": config.get("num_classes", 4),
        "backbone": config.get("backbone", "resnet50"),
        "pretrained": config.get("pretrained", True),
        "dropout_rate": config.get("dropout_rate", 0.5)
    }
    
    model = EnhancedDirtClassifier(**model_config)
    
    logger.info(f"Created dirt classifier with config: {model_config}")
    logger.info(f"Model info: {model.get_model_info()}")
    
    return model