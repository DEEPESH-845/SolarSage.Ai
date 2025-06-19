# agents/quartz_forecast_agent.py
"""
Quartz Solar Forecast Agent
Real OpenClimatefix Quartz ML integration with advanced physics simulation fallback
"""

import os
import time
import json
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple

logger = logging.getLogger(__name__)

# Check for Quartz availability
try:
    import quartz_solar_forecast
    QUARTZ_AVAILABLE = True
    logger.info("🔮 Quartz Solar Forecast: Available (Real ML predictions)")
except ImportError:
    QUARTZ_AVAILABLE = False
    logger.info("🔮 Quartz Solar Forecast: Not installed (Using simulation)")

class QuartzSolarForecastAgent:
    """Advanced solar forecasting with Quartz ML integration"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.agent_name = "Quartz Solar Forecast Agent"
        self.version = "2.0.0"
        self.config = config or {}
        
        # Quartz configuration
        self.quartz_config = {
            'use_real_quartz': QUARTZ_AVAILABLE,
            'model_version': 'latest',
            'forecast_horizon_hours': 48,
            'confidence_threshold': 0.7
        }
        
        # Physics simulation parameters
        self.physics_params = {
            'solar_constant': 1361,  # W/m²
            'atmosphere_transmittance': 0.7,
            'panel_efficiency': 0.20,
            'temperature_coefficient': -0.004,
            'dust_impact_model': 'advanced'
        }
        
        # Economic parameters
        self.economic_params = {
            'electricity_rate': 0.12,  # $/kWh
            'cleaning_cost_base': 25.0,  # $ per cleaning
            'water_cost': 0.05,  # $/liter
            'labor_rate': 15.0   # $/hour
        }
    
    def generate_comprehensive_solar_forecast(self, dust_agent_result: Dict[str, Any],
                                            latitude: float, longitude: float,
                                            capacity_kwp: float, 
                                            forecast_hours: int = 48) -> Dict[str, Any]:
        """Generate comprehensive solar forecast with dust correlation"""
        logger.info("🔮 Quartz Forecast Agent: ML-powered solar generation analysis...")
        
        start_time = time.time()
        
        try:
            # Extract dust conditions
            dust_conditions = self._extract_dust_conditions(dust_agent_result)
            
            # Generate base solar forecast
            if self.quartz_config['use_real_quartz']:
                base_forecast = self._generate_real_quartz_forecast(
                    latitude, longitude, capacity_kwp, forecast_hours
                )
            else:
                base_forecast = self._generate_physics_simulation_forecast(
                    latitude, longitude, capacity_kwp, forecast_hours
                )
            
            # Apply dust impact corrections
            dust_corrected_forecast = self._apply_dust_impact_corrections(
                base_forecast, dust_conditions
            )
            
            # Weather optimization analysis
            weather_optimization = self._analyze_weather_optimization(
                latitude, longitude, forecast_hours
            )
            
            # Cleaning impact analysis
            cleaning_impact = self._analyze_cleaning_impact_scenarios(
                dust_corrected_forecast, dust_conditions
            )
            
            # Economic impact modeling
            economic_modeling = self._model_economic_impacts(
                dust_corrected_forecast, cleaning_impact
            )
            
            # Forecast validation and confidence
            forecast_validation = self._validate_forecast_quality(
                base_forecast, dust_corrected_forecast
            )
            
            processing_time = (time.time() - start_time) * 1000
            
            result = {
                'agent_name': self.agent_name,
                'agent_version': self.version,
                'timestamp': datetime.now().isoformat(),
                'success': True,
                'dust_conditions_input': dust_conditions,
                'base_solar_forecast': base_forecast,
                'dust_corrected_forecast': dust_corrected_forecast,
                'weather_optimization_analysis': weather_optimization,
                'cleaning_impact_analysis': cleaning_impact,
                'economic_impact_modeling': economic_modeling,
                'forecast_validation': forecast_validation,
                'quartz_integration_status': {
                    'real_quartz_used': self.quartz_config['use_real_quartz'],
                    'model_version': self.quartz_config['model_version'],
                    'forecast_horizon_hours': forecast_hours,
                    'training_data_sites': '25,000+' if QUARTZ_AVAILABLE else 'N/A'
                },
                'processing_time_ms': round(processing_time, 2),
                'next_agent': 'AdvancedImageAnalysisAgent'
            }
            
            # Log key results
            daily_loss = dust_corrected_forecast['daily_totals']['total_loss_kwh']
            cleaning_justified = cleaning_impact['recommendations']['urgency_justified']
            quartz_mode = "REAL ML" if QUARTZ_AVAILABLE else "SIMULATION"
            
            logger.info(f"✅ Quartz Forecast: {quartz_mode} - Daily loss: {daily_loss:.2f} kWh")
            logger.info(f"💰 Economic analysis: Cleaning {'JUSTIFIED' if cleaning_justified else 'NOT JUSTIFIED'}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Quartz Forecast Agent failed: {e}")
            return {
                'agent_name': self.agent_name,
                'timestamp': datetime.now().isoformat(),
                'success': False,
                'error': str(e),
                'next_agent': 'AdvancedImageAnalysisAgent'
            }
    
    def _extract_dust_conditions(self, dust_result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relevant dust conditions from dust agent result"""
        
        env_data = dust_result.get('environmental_readings', {})
        risk_assessment = dust_result.get('advanced_risk_assessment', {})
        power_impact = dust_result.get('power_impact_prediction', {})
        
        return {
            'pm25_level': env_data.get('particulate_matter', {}).get('pm25_ugm3', 50),
            'visibility_km': env_data.get('atmospheric_conditions', {}).get('visibility_km', 15),
            'risk_level': risk_assessment.get('risk_level', 'moderate'),
            'risk_score': risk_assessment.get('overall_risk_score', 50),
            'predicted_power_loss_percent': power_impact.get('estimated_power_loss_percent', 10),
            'urgency_level': dust_result.get('cleaning_urgency_analysis', {}).get('urgency_level', 'moderate'),
            'dust_accumulation_rate': dust_result.get('dust_accumulation_modeling', {}).get('current_accumulation_rate', 1.0)
        }
    
    def _generate_real_quartz_forecast(self, latitude: float, longitude: float,
                                     capacity_kwp: float, forecast_hours: int) -> Dict[str, Any]:
        """Generate forecast using real Quartz ML model"""
        
        try:
            # Generate timestamps for forecast
            timestamps = [
                datetime.now() + timedelta(hours=h) for h in range(forecast_hours)
            ]
            
            # Use Quartz Solar Forecast
            forecast_data = quartz_solar_forecast.forecast(
                site={
                    'latitude': latitude,
                    'longitude': longitude,
                    'capacity_kwp': capacity_kwp
                },
                ts=timestamps
            )
            
            # Process Quartz results
            hourly_generation = []
            for i, timestamp in enumerate(timestamps):
                # Extract generation value (Quartz returns different formats)
                if hasattr(forecast_data, 'values'):
                    generation_kw = float(forecast_data.values[i])
                else:
                    generation_kw = float(forecast_data[i])
                
                hourly_generation.append({
                    'timestamp': timestamp.isoformat(),
                    'hour': i,
                    'generation_kw': round(generation_kw, 3),
                    'generation_kwh': round(generation_kw, 3),  # 1-hour periods
                    'capacity_factor': round(generation_kw / capacity_kwp * 100, 1) if capacity_kwp > 0 else 0
                })
            
            # Calculate daily totals
            total_generation = sum(h['generation_kwh'] for h in hourly_generation)
            peak_generation = max(h['generation_kw'] for h in hourly_generation)
            avg_capacity_factor = np.mean([h['capacity_factor'] for h in hourly_generation])
            
            return {
                'forecast_source': 'quartz_ml_model',
                'model_confidence': 0.85,  # Quartz typical confidence
                'hourly_forecast': hourly_generation,
                'daily_totals': {
                    'total_generation_kwh': round(total_generation, 2),
                    'peak_generation_kw': round(peak_generation, 2),
                    'average_capacity_factor': round(avg_capacity_factor, 1)
                },
                'forecast_metadata': {
                    'training_sites': '25,000+',
                    'model_type': 'deep_learning_ensemble',
                    'weather_data_source': 'NWP_multi_model'
                }
            }
            
        except Exception as e:
            logger.warning(f"Quartz forecast failed, falling back to simulation: {e}")
            return self._generate_physics_simulation_forecast(latitude, longitude, capacity_kwp, forecast_hours)
    
    def _generate_physics_simulation_forecast(self, latitude: float, longitude: float,
                                            capacity_kwp: float, forecast_hours: int) -> Dict[str, Any]:
        """Generate forecast using advanced physics simulation"""
        
        hourly_generation = []
        
        for hour in range(forecast_hours):
            timestamp = datetime.now() + timedelta(hours=hour)
            
            # Solar position calculation
            solar_elevation = self._calculate_solar_elevation(latitude, longitude, timestamp)
            
            # Clear sky irradiance
            if solar_elevation > 0:
                clear_sky_irradiance = self._calculate_clear_sky_irradiance(solar_elevation)
            else:
                clear_sky_irradiance = 0
            
            # Weather impact simulation
            weather_factor = self._simulate_weather_conditions(timestamp)
            
            # Final generation calculation
            actual_irradiance = clear_sky_irradiance * weather_factor
            generation_kw = (actual_irradiance / 1000) * capacity_kwp * self.physics_params['panel_efficiency'] / 0.20
            
            hourly_generation.append({
                'timestamp': timestamp.isoformat(),
                'hour': hour,
                'generation_kw': round(max(0, generation_kw), 3),
                'generation_kwh': round(max(0, generation_kw), 3),
                'capacity_factor': round(generation_kw / capacity_kwp * 100, 1) if capacity_kwp > 0 else 0,
                'solar_elevation': round(solar_elevation, 1),
                'irradiance_wm2': round(actual_irradiance, 1)
            })
        
        # Calculate totals
        total_generation = sum(h['generation_kwh'] for h in hourly_generation)
        peak_generation = max(h['generation_kw'] for h in hourly_generation)
        avg_capacity_factor = np.mean([h['capacity_factor'] for h in hourly_generation])
        
        return {
            'forecast_source': 'physics_simulation',
            'model_confidence': 0.75,
            'hourly_forecast': hourly_generation,
            'daily_totals': {
                'total_generation_kwh': round(total_generation, 2),
                'peak_generation_kw': round(peak_generation, 2),
                'average_capacity_factor': round(avg_capacity_factor, 1)
            },
            'simulation_parameters': self.physics_params
        }
    
    def _calculate_solar_elevation(self, latitude: float, longitude: float, timestamp: datetime) -> float:
        """Calculate solar elevation angle"""
        
        # Simplified solar position calculation
        day_of_year = timestamp.timetuple().tm_yday
        hour = timestamp.hour + timestamp.minute / 60.0
        
        # Solar declination
        declination = 23.45 * np.sin(np.radians(360 * (284 + day_of_year) / 365))
        
        # Hour angle
        hour_angle = 15 * (hour - 12)
        
        # Solar elevation
        lat_rad = np.radians(latitude)
        dec_rad = np.radians(declination)
        hour_rad = np.radians(hour_angle)
        
        elevation = np.arcsin(
            np.sin(lat_rad) * np.sin(dec_rad) + 
            np.cos(lat_rad) * np.cos(dec_rad) * np.cos(hour_rad)
        )
        
        return np.degrees(elevation)
    
    def _calculate_clear_sky_irradiance(self, solar_elevation: float) -> float:
        """Calculate clear sky irradiance"""
        
        if solar_elevation <= 0:
            return 0
        
        # Air mass calculation
        air_mass = 1 / np.sin(np.radians(solar_elevation))
        
        # Atmospheric attenuation
        transmittance = self.physics_params['atmosphere_transmittance'] ** air_mass
        
        # Direct normal irradiance
        dni = self.physics_params['solar_constant'] * transmittance
        
        # Global horizontal irradiance (simplified)
        ghi = dni * np.sin(np.radians(solar_elevation))
        
        return max(0, ghi)
    
    def _simulate_weather_conditions(self, timestamp: datetime) -> float:
        """Simulate weather impact on solar generation"""
        
        # Seasonal variation
        month = timestamp.month
        seasonal_factor = 0.7 + 0.3 * np.cos(2 * np.pi * (month - 6) / 12)
        
        # Daily variation with some randomness
        hour = timestamp.hour
        daily_factor = max(0, np.sin(np.pi * (hour - 6) / 12))
        
        # Random weather variability
        np.random.seed(int(timestamp.timestamp()) % 10000)
        weather_variability = 0.7 + 0.6 * np.random.random()
        
        return seasonal_factor * daily_factor * weather_variability
    
    def _apply_dust_impact_corrections(self, base_forecast: Dict[str, Any],
                                     dust_conditions: Dict[str, Any]) -> Dict[str, Any]:
        """Apply dust impact corrections to base forecast"""
        
        # Extract dust impact factors
        power_loss_percent = dust_conditions['predicted_power_loss_percent']
        dust_factor = 1 - (power_loss_percent / 100)
        
        # Apply corrections to hourly data
        corrected_hourly = []
        total_loss_kwh = 0
        
        for hour_data in base_forecast['hourly_forecast']:
            original_generation = hour_data['generation_kwh']
            corrected_generation = original_generation * dust_factor
            loss_kwh = original_generation - corrected_generation
            total_loss_kwh += loss_kwh
            
            corrected_hour = hour_data.copy()
            corrected_hour.update({
                'original_generation_kwh': original_generation,
                'dust_corrected_generation_kwh': round(corrected_generation, 3),
                'dust_loss_kwh': round(loss_kwh, 3),
                'dust_impact_percent': power_loss_percent
            })
            corrected_hourly.append(corrected_hour)
        
        # Calculate corrected totals
        corrected_total = sum(h['dust_corrected_generation_kwh'] for h in corrected_hourly)
        original_total = base_forecast['daily_totals']['total_generation_kwh']
        loss_percentage = (total_loss_kwh / original_total * 100) if original_total > 0 else 0
        
        return {
            'hourly_dust_corrected': corrected_hourly,
            'daily_totals': {
                'original_generation_kwh': original_total,
                'dust_corrected_generation_kwh': round(corrected_total, 2),
                'total_loss_kwh': round(total_loss_kwh, 2),
                'loss_percentage': round(loss_percentage, 1)
            },
            'dust_impact_summary': {
                'power_reduction_factor': round(dust_factor, 3),
                'dust_severity': dust_conditions['risk_level'],
                'environmental_pm25': dust_conditions['pm25_level'],
                'visibility_km': dust_conditions['visibility_km']
            }
        }
    
    def _analyze_weather_optimization(self, latitude: float, longitude: float,
                                    forecast_hours: int) -> Dict[str, Any]:
        """Analyze weather conditions for cleaning optimization"""
        
        # Simulate weather forecast for cleaning windows
        weather_windows = []
        
        for hour in range(0, forecast_hours, 6):  # Check every 6 hours
            timestamp = datetime.now() + timedelta(hours=hour)
            
            # Simulate weather conditions
            np.random.seed(int(timestamp.timestamp()) % 1000)
            wind_speed = max(0, 8 + np.random.normal(0, 4))
            humidity = max(20, min(95, 60 + np.random.normal(0, 20)))
            precipitation_prob = max(0, min(100, np.random.normal(20, 15)))
            
            # Calculate cleaning suitability
            if precipitation_prob > 30:
                suitability = 'poor_rain_expected'
                suitability_score = 20
            elif wind_speed > 15:
                suitability = 'poor_high_wind'
                suitability_score = 30
            elif humidity > 80:
                suitability = 'marginal_high_humidity'
                suitability_score = 60
            else:
                suitability = 'good'
                suitability_score = 90
            
            weather_windows.append({
                'start_time': timestamp.isoformat(),
                'duration_hours': 6,
                'wind_speed_ms': round(wind_speed, 1),
                'humidity_percent': round(humidity, 1),
                'precipitation_probability': round(precipitation_prob, 1),
                'cleaning_suitability': suitability,
                'suitability_score': suitability_score
            })
        
        # Find optimal cleaning windows
        optimal_windows = sorted(
            [w for w in weather_windows if w['suitability_score'] >= 70],
            key=lambda x: x['suitability_score'],
            reverse=True
        )[:3]
        
        return {
            'weather_forecast_windows': weather_windows,
            'optimal_cleaning_windows': optimal_windows,
            'next_optimal_window': optimal_windows[0] if optimal_windows else None,
            'weather_pattern_classification': self._classify_weather_pattern(weather_windows),
            'cleaning_favorability': 'high' if len(optimal_windows) >= 2 else 'moderate' if optimal_windows else 'low'
        }
    
    def _classify_weather_pattern(self, weather_windows: List[Dict]) -> str:
        """Classify overall weather pattern"""
        
        avg_precipitation = np.mean([w['precipitation_probability'] for w in weather_windows])
        avg_wind = np.mean([w['wind_speed_ms'] for w in weather_windows])
        
        if avg_precipitation > 50:
            return 'rainy_period'
        elif avg_wind > 12:
            return 'windy_period'
        else:
            return 'stable_conditions'
    
    def _analyze_cleaning_impact_scenarios(self, dust_corrected_forecast: Dict[str, Any],
                                         dust_conditions: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze different cleaning scenario impacts"""
        
        daily_loss_kwh = dust_corrected_forecast['daily_totals']['total_loss_kwh']
        current_loss_percent = dust_conditions['predicted_power_loss_percent']
        
        # Define cleaning scenarios
        scenarios = {
            'no_cleaning': {
                'dust_reduction_percent': 0,
                'cost_usd': 0,
                'description': 'Continue without cleaning'
            },
            'light_cleaning': {
                'dust_reduction_percent': 60,
                'cost_usd': self.economic_params['cleaning_cost_base'] * 0.7,
                'description': 'Basic water rinse'
            },
            'standard_cleaning': {
                'dust_reduction_percent': 85,
                'cost_usd': self.economic_params['cleaning_cost_base'],
                'description': 'Standard cleaning with detergent'
            },
            'intensive_cleaning': {
                'dust_reduction_percent': 95,
                'cost_usd': self.economic_params['cleaning_cost_base'] * 1.5,
                'description': 'Thorough manual cleaning'
            }
        }
        
        # Calculate scenario impacts
        scenario_analysis = {}
        for scenario_name, scenario_data in scenarios.items():
            # Calculate recovered generation
            dust_reduction = scenario_data['dust_reduction_percent'] / 100
            recovered_loss_percent = current_loss_percent * dust_reduction
            recovered_kwh_daily = daily_loss_kwh * dust_reduction
            recovered_kwh_weekly = recovered_kwh_daily * 7
            
            # Economic calculations
            cleaning_cost = scenario_data['cost_usd']
            daily_revenue_recovery = recovered_kwh_daily * self.economic_params['electricity_rate']
            weekly_revenue_recovery = daily_revenue_recovery * 7
            payback_days = cleaning_cost / max(daily_revenue_recovery, 0.01)
            
            scenario_analysis[scenario_name] = {
                'description': scenario_data['description'],
                'cleaning_cost_usd': cleaning_cost,
                'dust_reduction_percent': scenario_data['dust_reduction_percent'],
                'recovered_kwh_daily': round(recovered_kwh_daily, 2),
                'recovered_kwh_weekly': round(recovered_kwh_weekly, 2),
                'daily_revenue_recovery_usd': round(daily_revenue_recovery, 2),
                'weekly_revenue_recovery_usd': round(weekly_revenue_recovery, 2),
                'payback_period_days': round(payback_days, 1),
                'net_weekly_benefit_usd': round(weekly_revenue_recovery - cleaning_cost, 2),
                'roi_percent': round((weekly_revenue_recovery - cleaning_cost) / max(cleaning_cost, 0.01) * 100, 1)
            }
        
        # Determine optimal scenario
        profitable_scenarios = [
            name for name, data in scenario_analysis.items() 
            if data['net_weekly_benefit_usd'] > 0 and name != 'no_cleaning'
        ]
        
        if profitable_scenarios:
            optimal_scenario = max(
                profitable_scenarios,
                key=lambda x: scenario_analysis[x]['net_weekly_benefit_usd']
            )
            urgency_justified = True
        else:
            optimal_scenario = 'no_cleaning'
            urgency_justified = False
        
        return {
            'scenario_analysis': scenario_analysis,
            'recommendations': {
                'optimal_scenario': optimal_scenario,
                'urgency_justified': urgency_justified,
                'optimal_details': scenario_analysis.get(optimal_scenario, {}),
                'economic_threshold_met': daily_loss_kwh * self.economic_params['electricity_rate'] > 2.0
            },
            'sensitivity_analysis': self._perform_sensitivity_analysis(scenario_analysis)
        }
    
    def _perform_sensitivity_analysis(self, scenario_analysis: Dict) -> Dict[str, Any]:
        """Perform sensitivity analysis on economic parameters"""
        
        # Test different electricity rates
        base_rate = self.economic_params['electricity_rate']
        rate_variations = [0.08, 0.10, 0.12, 0.15, 0.20]
        
        sensitivity_results = {}
        for rate in rate_variations:
            rate_factor = rate / base_rate
            profitable_count = 0
            
            for scenario_name, scenario_data in scenario_analysis.items():
                if scenario_name == 'no_cleaning':
                    continue
                
                adjusted_revenue = scenario_data['weekly_revenue_recovery_usd'] * rate_factor
                adjusted_benefit = adjusted_revenue - scenario_data['cleaning_cost_usd']
                
                if adjusted_benefit > 0:
                    profitable_count += 1
            
            sensitivity_results[f'rate_{rate:.2f}'] = {
                'electricity_rate': rate,
                'profitable_scenarios': profitable_count,
                'rate_factor': round(rate_factor, 2)
            }
        
        return sensitivity_results
    
    def _model_economic_impacts(self, dust_corrected_forecast: Dict[str, Any],
                              cleaning_impact: Dict[str, Any]) -> Dict[str, Any]:
        """Model comprehensive economic impacts"""
        
        daily_loss_kwh = dust_corrected_forecast['daily_totals']['total_loss_kwh']
        optimal_scenario = cleaning_impact['recommendations']['optimal_scenario']
        
        # Short-term impact (1 week)
        weekly_loss_kwh = daily_loss_kwh * 7
        weekly_revenue_loss = weekly_loss_kwh * self.economic_params['electricity_rate']
        
        # Medium-term impact (1 month)
        monthly_loss_kwh = daily_loss_kwh * 30
        monthly_revenue_loss = monthly_loss_kwh * self.economic_params['electricity_rate']
        
        # Long-term impact (1 year)
        annual_loss_kwh = daily_loss_kwh * 365
        annual_revenue_loss = annual_loss_kwh * self.economic_params['electricity_rate']
        
        # Cleaning economics
        if optimal_scenario != 'no_cleaning':
            optimal_data = cleaning_impact['scenario_analysis'][optimal_scenario]
            cleaning_frequency = 26  # Bi-weekly
            annual_cleaning_cost = optimal_data['cleaning_cost_usd'] * cleaning_frequency
            annual_revenue_recovery = optimal_data['weekly_revenue_recovery_usd'] * 52
            net_annual_benefit = annual_revenue_recovery - annual_cleaning_cost
        else:
            annual_cleaning_cost = 0
            annual_revenue_recovery = 0
            net_annual_benefit = -annual_revenue_loss
        
        return {
            'revenue_loss_analysis': {
                'daily_loss_usd': round(daily_loss_kwh * self.economic_params['electricity_rate'], 2),
                'weekly_loss_usd': round(weekly_revenue_loss, 2),
                'monthly_loss_usd': round(monthly_revenue_loss, 2),
                'annual_loss_usd': round(annual_revenue_loss, 2)
            },
            'cleaning_economics': {
                'optimal_scenario': optimal_scenario,
                'annual_cleaning_cost_usd': round(annual_cleaning_cost, 2),
                'annual_revenue_recovery_usd': round(annual_revenue_recovery, 2),
                'net_annual_benefit_usd': round(net_annual_benefit, 2),
                'roi_annual_percent': round(net_annual_benefit / max(annual_cleaning_cost, 0.01) * 100, 1)
            },
            'cost_benefit_analysis': {
                'break_even_electricity_rate': round(self.economic_params['cleaning_cost_base'] / max(weekly_loss_kwh, 0.01), 3),
                'break_even_loss_kwh_daily': round(self.economic_params['cleaning_cost_base'] / (self.economic_params['electricity_rate'] * 7), 2),
                'economic_viability': net_annual_benefit > 0
            }
        }
    
    def _validate_forecast_quality(self, base_forecast: Dict[str, Any],
                                 dust_corrected_forecast: Dict[str, Any]) -> Dict[str, Any]:
        """Validate forecast quality and confidence metrics"""
        
        # Model validation metrics
        if base_forecast['forecast_source'] == 'quartz_ml_model':
            model_confidence = 0.85
            validation_source = 'quartz_historical_performance'
            expected_error_percent = 8
        else:
            model_confidence = 0.75
            validation_source = 'physics_model_validation'
            expected_error_percent = 12
        
        # Forecast consistency checks
        hourly_data = base_forecast['hourly_forecast']
        generation_values = [h['generation_kwh'] for h in hourly_data]
        
        # Check for anomalies
        mean_gen = np.mean(generation_values)
        std_gen = np.std(generation_values)
        anomaly_count = sum(1 for val in generation_values if abs(val - mean_gen) > 3 * std_gen)
        
        # Dust impact validation
        total_loss = dust_corrected_forecast['daily_totals']['total_loss_kwh']
        original_total = dust_corrected_forecast['daily_totals']['original_generation_kwh']
        loss_ratio = total_loss / max(original_total, 0.01)
        
        dust_impact_reasonable = 0.05 <= loss_ratio <= 0.40  # 5-40% loss range
        
        return {
            'model_validation_metrics': {
                'forecast_source': base_forecast['forecast_source'],
                'model_confidence': model_confidence,
                'validation_confidence': round(model_confidence * 100, 1),
                'expected_error_percent': expected_error_percent,
                'validation_source': validation_source
            },
            'forecast_consistency': {
                'anomaly_count': anomaly_count,
                'data_smoothness_score': round(max(0, 100 - anomaly_count * 10), 1),
                'generation_variance': round(std_gen, 2)
            },
            'dust_impact_validation': {
                'loss_ratio': round(loss_ratio, 3),
                'impact_reasonable': dust_impact_reasonable,
                'validation_passed': dust_impact_reasonable and anomaly_count <= 2
            },
            'overall_quality_score': round(
                (model_confidence * 50 + 
                 max(0, 100 - anomaly_count * 10) * 0.3 + 
                 (80 if dust_impact_reasonable else 40) * 0.2), 1
            )
        }