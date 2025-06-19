# agents/dust_detection_agent.py
"""
Advanced Dust Detection Agent
Multi-sensor environmental analysis with power impact prediction
"""

import os
import time
import json
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple

logger = logging.getLogger(__name__)

class AdvancedDustDetectionAgent:
    """Advanced dust detection with multi-sensor environmental analysis"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.agent_name = "Advanced Dust Detection Agent"
        self.version = "2.0.0"
        self.config = config or {}
        
        # Sensor configuration
        self.sensors = {
            'pm25_sensor': True,
            'visibility_sensor': True,
            'wind_sensor': True,
            'humidity_sensor': True,
            'temperature_sensor': True
        }
        
        # Environmental thresholds
        self.thresholds = {
            'pm25_critical': 150,  # μg/m³
            'pm25_high': 75,
            'pm25_moderate': 35,
            'visibility_poor': 5,  # km
            'wind_cleaning': 10,   # m/s
            'humidity_high': 70    # %
        }
        
        # Risk assessment weights
        self.risk_weights = {
            'pm25_weight': 0.35,
            'visibility_weight': 0.25,
            'wind_weight': 0.15,
            'humidity_weight': 0.15,
            'historical_weight': 0.10
        }
    
    def detect_comprehensive_dust_conditions(self) -> Dict[str, Any]:
        """Perform comprehensive dust detection analysis"""
        logger.info("🌪️ Dust Detection Agent: Multi-sensor environmental analysis...")
        
        start_time = time.time()
        
        try:
            # Environmental sensor readings
            environmental_readings = self._collect_environmental_data()
            
            # Historical trend analysis
            historical_analysis = self._analyze_historical_trends()
            
            # Multi-factor risk assessment
            risk_assessment = self._perform_advanced_risk_assessment(
                environmental_readings, historical_analysis
            )
            
            # Power impact prediction
            power_impact = self._predict_power_impact(environmental_readings, risk_assessment)
            
            # Cleaning urgency analysis
            urgency_analysis = self._analyze_cleaning_urgency(
                environmental_readings, risk_assessment, power_impact
            )
            
            # Dust accumulation modeling
            accumulation_model = self._model_dust_accumulation(environmental_readings)
            
            # Sensor reliability assessment
            sensor_reliability = self._assess_sensor_reliability()
            
            processing_time = (time.time() - start_time) * 1000
            
            result = {
                'agent_name': self.agent_name,
                'agent_version': self.version,
                'timestamp': datetime.now().isoformat(),
                'success': True,
                'environmental_readings': environmental_readings,
                'historical_trend_analysis': historical_analysis,
                'advanced_risk_assessment': risk_assessment,
                'power_impact_prediction': power_impact,
                'cleaning_urgency_analysis': urgency_analysis,
                'dust_accumulation_modeling': accumulation_model,
                'sensor_reliability': sensor_reliability,
                'processing_time_ms': round(processing_time, 2),
                'next_agent': 'QuartzSolarForecastAgent'
            }
            
            # Log key results
            risk_level = risk_assessment['risk_level']
            risk_score = risk_assessment['overall_risk_score']
            urgency = urgency_analysis['urgency_level']
            
            logger.info(f"✅ Dust Detection: {risk_level} risk ({risk_score:.1f}/100) - "
                       f"Urgency: {urgency}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Dust Detection Agent failed: {e}")
            return {
                'agent_name': self.agent_name,
                'timestamp': datetime.now().isoformat(),
                'success': False,
                'error': str(e),
                'next_agent': 'QuartzSolarForecastAgent'
            }
    
    def _collect_environmental_data(self) -> Dict[str, Any]:
        """Collect comprehensive environmental sensor data"""
        
        # Simulate realistic sensor readings with some variability
        np.random.seed(int(time.time()) % 1000)
        
        # Particulate matter readings
        base_pm25 = 45 + np.random.normal(0, 15)
        pm25_ugm3 = max(5, base_pm25)
        pm10_ugm3 = pm25_ugm3 * 1.8  # PM10 typically 1.5-2x PM2.5
        
        particulate_matter = {
            'pm25_ugm3': round(pm25_ugm3, 1),
            'pm10_ugm3': round(pm10_ugm3, 1),
            'dust_concentration_index': min(100, pm25_ugm3 / 3),
            'air_quality_index': self._calculate_aqi(pm25_ugm3),
            'measurement_timestamp': datetime.now().isoformat()
        }
        
        # Atmospheric conditions
        visibility_base = 12 + np.random.normal(0, 4)
        visibility_km = max(0.5, visibility_base)
        
        atmospheric_conditions = {
            'visibility_km': round(visibility_km, 1),
            'atmospheric_haze_level': max(0, 20 - visibility_km) / 20 * 100,
            'optical_depth_estimate': round(max(0.1, 1 - visibility_km / 20), 2),
            'dust_scattering_coefficient': round(pm25_ugm3 * 0.003, 3)
        }
        
        # Meteorological data
        wind_speed = max(0, 6 + np.random.normal(0, 3))
        humidity = max(20, min(95, 60 + np.random.normal(0, 15)))
        temperature = 25 + np.random.normal(0, 8)
        
        meteorological_data = {
            'wind_speed_ms': round(wind_speed, 1),
            'wind_direction_deg': round(np.random.uniform(0, 360), 0),
            'relative_humidity_percent': round(humidity, 1),
            'temperature_celsius': round(temperature, 1),
            'atmospheric_pressure_hpa': round(1013 + np.random.normal(0, 15), 1),
            'wind_cleaning_potential': min(100, wind_speed / 15 * 100)
        }
        
        # Dust source analysis
        dust_sources = self._analyze_dust_sources(wind_speed, pm25_ugm3)
        
        return {
            'particulate_matter': particulate_matter,
            'atmospheric_conditions': atmospheric_conditions,
            'meteorological_data': meteorological_data,
            'dust_source_analysis': dust_sources,
            'sensor_status': {sensor: 'operational' for sensor in self.sensors.keys()},
            'data_quality_score': self._calculate_data_quality_score()
        }
    
    def _calculate_aqi(self, pm25: float) -> int:
        """Calculate Air Quality Index from PM2.5"""
        if pm25 <= 12:
            return int(50 * pm25 / 12)
        elif pm25 <= 35.4:
            return int(50 + 50 * (pm25 - 12) / (35.4 - 12))
        elif pm25 <= 55.4:
            return int(100 + 50 * (pm25 - 35.4) / (55.4 - 35.4))
        elif pm25 <= 150.4:
            return int(150 + 50 * (pm25 - 55.4) / (150.4 - 55.4))
        else:
            return min(500, int(200 + 100 * (pm25 - 150.4) / 100))
    
    def _analyze_dust_sources(self, wind_speed: float, pm25: float) -> Dict[str, Any]:
        """Analyze potential dust sources and transport"""
        
        # Dust source categories
        sources = {
            'local_resuspension': min(100, pm25 / 2 + wind_speed * 5),
            'construction_activities': max(0, np.random.normal(20, 10)),
            'traffic_emissions': max(0, np.random.normal(15, 8)),
            'agricultural_sources': max(0, np.random.normal(10, 6)),
            'long_range_transport': max(0, pm25 - 30) if pm25 > 30 else 0
        }
        
        # Dominant source
        dominant_source = max(sources.keys(), key=lambda k: sources[k])
        
        return {
            'source_contributions': {k: round(v, 1) for k, v in sources.items()},
            'dominant_source': dominant_source,
            'transport_potential': round(min(100, wind_speed / 20 * 100), 1),
            'deposition_rate_estimate': round(max(0, 100 - wind_speed * 8), 1)
        }
    
    def _calculate_data_quality_score(self) -> float:
        """Calculate overall data quality score"""
        # Simulate sensor reliability
        base_quality = 85 + np.random.normal(0, 10)
        return round(max(50, min(100, base_quality)), 1)
    
    def _analyze_historical_trends(self) -> Dict[str, Any]:
        """Analyze historical dust accumulation trends"""
        
        # Simulate historical data patterns
        current_hour = datetime.now().hour
        current_month = datetime.now().month
        
        # Daily patterns
        daily_pattern = {
            'peak_dust_hours': [6, 7, 8, 17, 18, 19],  # Morning and evening traffic
            'current_hour_risk': 'high' if current_hour in [6, 7, 8, 17, 18, 19] else 'moderate',
            'diurnal_variation_percent': 35
        }
        
        # Seasonal patterns
        seasonal_factor = self._get_seasonal_dust_factor(current_month)
        
        # Baseline comparison
        baseline_pm25 = 35  # Historical average
        current_deviation = np.random.normal(0, 15)
        
        baseline_comparison = {
            'historical_baseline_pm25': baseline_pm25,
            'current_deviation_percent': round(current_deviation, 1),
            'trend_classification': 'above_baseline' if current_deviation > 10 else 'below_baseline' if current_deviation < -10 else 'near_baseline',
            'accumulation_rate_trend': 'increasing' if current_deviation > 5 else 'stable'
        }
        
        return {
            'daily_patterns': daily_pattern,
            'seasonal_analysis': seasonal_factor,
            'baseline_comparison': baseline_comparison,
            'trend_confidence': round(75 + np.random.uniform(-15, 15), 1)
        }
    
    def _get_seasonal_dust_factor(self, month: int) -> Dict[str, Any]:
        """Get seasonal dust accumulation factors"""
        
        # Seasonal patterns for Delhi, India (can be customized)
        seasonal_factors = {
            1: {'factor': 0.8, 'season': 'winter', 'description': 'Moderate dust, stable weather'},
            2: {'factor': 0.9, 'season': 'winter_end', 'description': 'Increasing dust activity'},
            3: {'factor': 1.3, 'season': 'pre_monsoon', 'description': 'High dust storms'},
            4: {'factor': 1.5, 'season': 'pre_monsoon', 'description': 'Peak dust season'},
            5: {'factor': 1.4, 'season': 'pre_monsoon', 'description': 'Very high dust activity'},
            6: {'factor': 0.7, 'season': 'monsoon_start', 'description': 'Rain reduces dust'},
            7: {'factor': 0.5, 'season': 'monsoon', 'description': 'Minimal dust accumulation'},
            8: {'factor': 0.6, 'season': 'monsoon', 'description': 'Low dust levels'},
            9: {'factor': 0.8, 'season': 'monsoon_end', 'description': 'Dust levels increasing'},
            10: {'factor': 1.2, 'season': 'post_monsoon', 'description': 'Rising dust activity'},
            11: {'factor': 1.1, 'season': 'post_monsoon', 'description': 'Moderate-high dust'},
            12: {'factor': 0.9, 'season': 'winter_start', 'description': 'Stabilizing conditions'}
        }
        
        current_season = seasonal_factors[month]
        
        return {
            'seasonal_factor': current_season['factor'],
            'current_season': current_season['season'],
            'seasonal_description': current_season['description'],
            'expected_dust_level': 'high' if current_season['factor'] > 1.2 else 'moderate' if current_season['factor'] > 0.8 else 'low'
        }
    
    def _perform_advanced_risk_assessment(self, env_data: Dict[str, Any], 
                                        historical: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive risk assessment"""
        
        # Extract key metrics
        pm25 = env_data['particulate_matter']['pm25_ugm3']
        visibility = env_data['atmospheric_conditions']['visibility_km']
        wind_speed = env_data['meteorological_data']['wind_speed_ms']
        humidity = env_data['meteorological_data']['relative_humidity_percent']
        seasonal_factor = historical['seasonal_analysis']['seasonal_factor']
        
        # Individual risk scores
        pm25_risk = min(100, (pm25 / self.thresholds['pm25_critical']) * 100)
        visibility_risk = max(0, (self.thresholds['visibility_poor'] * 2 - visibility) / self.thresholds['visibility_poor'] * 50)
        wind_risk = max(0, 50 - (wind_speed / self.thresholds['wind_cleaning']) * 50)
        humidity_risk = max(0, (humidity - 50) / 20 * 30)
        seasonal_risk = (seasonal_factor - 0.5) / 1.0 * 50
        
        # Weighted overall risk
        overall_risk = (
            pm25_risk * self.risk_weights['pm25_weight'] +
            visibility_risk * self.risk_weights['visibility_weight'] +
            wind_risk * self.risk_weights['wind_weight'] +
            humidity_risk * self.risk_weights['humidity_weight'] +
            seasonal_risk * self.risk_weights['historical_weight']
        )
        
        # Risk level classification
        if overall_risk >= 80:
            risk_level = 'critical'
            risk_description = 'Extreme dust accumulation conditions'
        elif overall_risk >= 65:
            risk_level = 'high'
            risk_description = 'Significant dust accumulation expected'
        elif overall_risk >= 45:
            risk_level = 'moderate'
            risk_description = 'Moderate dust accumulation likely'
        elif overall_risk >= 25:
            risk_level = 'low'
            risk_description = 'Minimal dust accumulation expected'
        else:
            risk_level = 'minimal'
            risk_description = 'Very low dust accumulation risk'
        
        return {
            'individual_risk_scores': {
                'pm25_risk': round(pm25_risk, 1),
                'visibility_risk': round(visibility_risk, 1),
                'wind_cleaning_risk': round(wind_risk, 1),
                'humidity_risk': round(humidity_risk, 1),
                'seasonal_risk': round(seasonal_risk, 1)
            },
            'overall_risk_score': round(overall_risk, 1),
            'risk_level': risk_level,
            'risk_description': risk_description,
            'contributing_factors': self._identify_risk_factors(pm25_risk, visibility_risk, wind_risk),
            'risk_trend': 'increasing' if overall_risk > 60 else 'stable'
        }
    
    def _identify_risk_factors(self, pm25_risk: float, visibility_risk: float, wind_risk: float) -> List[str]:
        """Identify primary contributing risk factors"""
        factors = []
        
        if pm25_risk > 70:
            factors.append('high_particulate_matter')
        if visibility_risk > 60:
            factors.append('poor_atmospheric_visibility')
        if wind_risk > 50:
            factors.append('insufficient_wind_cleaning')
        
        return factors
    
    def _predict_power_impact(self, env_data: Dict[str, Any], 
                            risk_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Predict power generation impact from dust accumulation"""
        
        # Base power loss calculation
        pm25 = env_data['particulate_matter']['pm25_ugm3']
        visibility = env_data['atmospheric_conditions']['visibility_km']
        overall_risk = risk_assessment['overall_risk_score']
        
        # Power loss correlation models
        pm25_power_loss = min(30, pm25 / 5)  # ~1% loss per 5 μg/m³
        visibility_power_loss = max(0, (15 - visibility) / 15 * 20)
        risk_power_loss = overall_risk / 100 * 25
        
        # Combined power loss estimate
        estimated_loss = (pm25_power_loss + visibility_power_loss + risk_power_loss) / 3
        
        # Power loss categories
        if estimated_loss >= 20:
            impact_category = 'severe'
            cleaning_priority = 'immediate'
        elif estimated_loss >= 15:
            impact_category = 'high'
            cleaning_priority = 'urgent'
        elif estimated_loss >= 10:
            impact_category = 'moderate'
            cleaning_priority = 'recommended'
        elif estimated_loss >= 5:
            impact_category = 'low'
            cleaning_priority = 'optional'
        else:
            impact_category = 'minimal'
            cleaning_priority = 'not_needed'
        
        return {
            'estimated_power_loss_percent': round(estimated_loss, 1),
            'impact_category': impact_category,
            'cleaning_priority': cleaning_priority,
            'power_loss_components': {
                'pm25_contribution': round(pm25_power_loss, 1),
                'visibility_contribution': round(visibility_power_loss, 1),
                'risk_factor_contribution': round(risk_power_loss, 1)
            },
            'confidence_level': round(80 - abs(estimated_loss - 12) * 2, 1),  # Higher confidence near typical values
            'economic_impact_estimate': self._estimate_economic_impact(estimated_loss)
        }
    
    def _estimate_economic_impact(self, power_loss_percent: float) -> Dict[str, float]:
        """Estimate economic impact of power loss"""
        
        # Assumptions: 5kW system, 6 hours peak sun, $0.12/kWh
        system_capacity = 5.0  # kW
        peak_sun_hours = 6.0
        electricity_rate = 0.12  # $/kWh
        
        daily_generation = system_capacity * peak_sun_hours
        daily_loss_kwh = daily_generation * (power_loss_percent / 100)
        daily_loss_usd = daily_loss_kwh * electricity_rate
        
        return {
            'daily_loss_kwh': round(daily_loss_kwh, 2),
            'daily_loss_usd': round(daily_loss_usd, 2),
            'weekly_loss_usd': round(daily_loss_usd * 7, 2),
            'monthly_loss_usd': round(daily_loss_usd * 30, 2),
            'annual_loss_usd': round(daily_loss_usd * 365, 2)
        }
    
    def _analyze_cleaning_urgency(self, env_data: Dict[str, Any],
                                risk_assessment: Dict[str, Any],
                                power_impact: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze cleaning urgency based on all factors"""
        
        risk_score = risk_assessment['overall_risk_score']
        power_loss = power_impact['estimated_power_loss_percent']
        pm25 = env_data['particulate_matter']['pm25_ugm3']
        
        # Urgency scoring
        risk_urgency = min(100, risk_score * 1.2)
        power_urgency = min(100, power_loss * 4)
        environmental_urgency = min(100, pm25 / 2)
        
        # Weighted urgency score
        urgency_score = (risk_urgency * 0.4 + power_urgency * 0.4 + environmental_urgency * 0.2)
        
        # Urgency classification
        if urgency_score >= 85:
            urgency_level = 'critical_immediate'
            time_window = '0-6 hours'
            justification = 'Extreme conditions require immediate cleaning'
        elif urgency_score >= 70:
            urgency_level = 'high'
            time_window = '6-24 hours'
            justification = 'High dust levels causing significant power loss'
        elif urgency_score >= 50:
            urgency_level = 'moderate'
            time_window = '1-3 days'
            justification = 'Moderate dust accumulation, cleaning advisable'
        elif urgency_score >= 30:
            urgency_level = 'low'
            time_window = '3-7 days'
            justification = 'Low dust levels, routine cleaning sufficient'
        else:
            urgency_level = 'minimal'
            time_window = '1-2 weeks'
            justification = 'Minimal dust impact, cleaning not urgent'
        
        return {
            'urgency_score': round(urgency_score, 1),
            'urgency_level': urgency_level,
            'recommended_time_window': time_window,
            'urgency_justification': justification,
            'urgency_components': {
                'risk_based_urgency': round(risk_urgency, 1),
                'power_impact_urgency': round(power_urgency, 1),
                'environmental_urgency': round(environmental_urgency, 1)
            },
            'weather_window_consideration': self._assess_weather_window(env_data)
        }
    
    def _assess_weather_window(self, env_data: Dict[str, Any]) -> Dict[str, str]:
        """Assess weather conditions for cleaning window"""
        
        wind_speed = env_data['meteorological_data']['wind_speed_ms']
        humidity = env_data['meteorological_data']['relative_humidity_percent']
        
        if wind_speed > 15 or humidity > 80:
            window_suitability = 'poor'
            recommendation = 'wait_for_better_conditions'
        elif wind_speed > 10 or humidity > 70:
            window_suitability = 'marginal'
            recommendation = 'proceed_with_caution'
        else:
            window_suitability = 'good'
            recommendation = 'optimal_for_cleaning'
        
        return {
            'current_window_suitability': window_suitability,
            'cleaning_recommendation': recommendation
        }
    
    def _model_dust_accumulation(self, env_data: Dict[str, Any]) -> Dict[str, Any]:
        """Model dust accumulation patterns and predictions"""
        
        pm25 = env_data['particulate_matter']['pm25_ugm3']
        wind_speed = env_data['meteorological_data']['wind_speed_ms']
        humidity = env_data['meteorological_data']['relative_humidity_percent']
        
        # Accumulation rate modeling
        base_accumulation = pm25 / 10  # Base rate from PM2.5
        wind_factor = max(0.1, 1 - wind_speed / 20)  # Wind reduces accumulation
        humidity_factor = 1 + max(0, humidity - 60) / 100  # High humidity increases adhesion
        
        accumulation_rate = base_accumulation * wind_factor * humidity_factor
        
        # Predict accumulation over time
        time_predictions = {}
        for hours in [6, 12, 24, 48, 72]:
            accumulated = accumulation_rate * (hours / 24)
            power_impact = min(35, accumulated * 2)
            time_predictions[f'{hours}h'] = {
                'accumulated_dust_relative': round(accumulated, 2),
                'predicted_power_loss_percent': round(power_impact, 1)
            }
        
        return {
            'current_accumulation_rate': round(accumulation_rate, 2),
            'accumulation_factors': {
                'pm25_contribution': round(base_accumulation, 2),
                'wind_reduction_factor': round(wind_factor, 2),
                'humidity_adhesion_factor': round(humidity_factor, 2)
            },
            'time_based_predictions': time_predictions,
            'cleaning_threshold_estimate': '24-48 hours at current rate'
        }
    
    def _assess_sensor_reliability(self) -> Dict[str, Any]:
        """Assess reliability of sensor measurements"""
        
        # Simulate sensor reliability assessment
        sensor_reliabilities = {}
        for sensor in self.sensors.keys():
            base_reliability = 90 + np.random.normal(0, 8)
            sensor_reliabilities[sensor] = max(50, min(100, base_reliability))
        
        overall_reliability = np.mean(list(sensor_reliabilities.values()))
        
        return {
            'individual_sensor_reliability': {k: round(v, 1) for k, v in sensor_reliabilities.items()},
            'overall_reliability': round(overall_reliability, 1),
            'data_confidence_level': 'high' if overall_reliability > 85 else 'medium' if overall_reliability > 70 else 'low',
            'calibration_status': 'recent' if overall_reliability > 80 else 'due',
            'measurement_uncertainty': round(max(5, 100 - overall_reliability), 1)
        }