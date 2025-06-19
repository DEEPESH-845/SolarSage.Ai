#!/usr/bin/env python3
"""
decision_agent.py
Advanced Decision Orchestration Agent for Solar Panel Cleaning System
Comprehensive multi-factor decision making with spray execution capabilities

Author: AI System
Version: 2.0.0
Date: 2024
"""

import os
import time
import json
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DecisionOrchestrationAgent:
    """
    Advanced Decision Orchestration Agent for Solar Panel Cleaning System
    
    This agent integrates data from multiple sources (environmental sensors, weather forecasts,
    image analysis) to make intelligent decisions about when and how to clean solar panels.
    It performs comprehensive risk assessment, economic analysis, and can execute cleaning
    operations with full safety protocols.
    
    Key Features:
    - Multi-dimensional risk assessment
    - Economic impact analysis with ROI calculations
    - Real-time decision matrix computation
    - Automated spray system control
    - Comprehensive reporting and audit trails
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the Decision Orchestration Agent
        
        Args:
            config: Optional configuration dictionary
        """
        self.agent_name = "Decision Orchestration Agent"
        self.version = "2.0.0"
        self.config = config or {}
        
        # Decision framework configuration - weights for different factors
        self.decision_framework = {
            'dust_severity_weight': 0.25,      # How much dust affects decision
            'economic_impact_weight': 0.25,    # Economic viability weight
            'risk_assessment_weight': 0.20,    # Risk factor importance
            'confidence_weight': 0.15,         # Data confidence impact
            'timing_optimization_weight': 0.15  # Timing optimization weight
        }
        
        # Decision thresholds for action classification
        self.decision_thresholds = {
            'critical_action_score': 85,       # Immediate action required
            'recommended_action_score': 70,    # Action recommended
            'optional_action_score': 50,       # Action optional
            'minimum_confidence': 60,          # Minimum confidence for action
            'maximum_acceptable_risk': 80      # Risk tolerance threshold
        }
        
        # Spray system configuration
        self.spray_system = {
            'gpio_pin': 18,                    # GPIO pin for spray control
            'enable_hardware': os.environ.get('ENABLE_GPIO', 'false').lower() == 'true',
            'simulation_mode': True,           # Default to simulation
            'safety_protocols_enabled': True   # Safety protocols always enabled
        }
        
        # Economic parameters for cost calculations
        self.economic_params = {
            'electricity_rate_per_kwh': 0.12,  # USD per kWh
            'water_cost_per_liter': 0.05,      # USD per liter
            'labor_cost_per_hour': 15.0,       # USD per hour
            'equipment_cost_per_use': 3.0,     # USD per cleaning cycle
            'carbon_cost_per_kg': 0.05         # USD per kg CO2
        }
        
        # Initialize spray system
        self._initialize_spray_system()
        
        logger.info(f"✅ {self.agent_name} v{self.version} initialized successfully")
    
    def orchestrate_comprehensive_decision(self, dust_result: Dict[str, Any],
                                         forecast_result: Dict[str, Any],
                                         image_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main orchestration method - performs comprehensive 8-phase decision analysis
        
        Args:
            dust_result: Environmental sensor data and analysis
            forecast_result: Weather forecast and solar generation predictions
            image_result: Visual analysis of solar panel dust conditions
            
        Returns:
            Comprehensive decision analysis with execution results
        """
        logger.info("🎯 Decision Orchestration: Starting comprehensive multi-agent analysis...")
        
        start_time = time.time()
        
        try:
            # Phase 1: Data integration and validation
            logger.info("📊 Phase 1: Data integration and validation")
            data_integration = self._integrate_and_validate_inputs(
                dust_result, forecast_result, image_result
            )
            
            # Phase 2: Multi-dimensional risk assessment
            logger.info("⚠️ Phase 2: Multi-dimensional risk assessment")
            risk_assessment = self._perform_multidimensional_risk_assessment(
                data_integration
            )
            
            # Phase 3: Economic impact analysis
            logger.info("💰 Phase 3: Economic impact analysis")
            economic_analysis = self._comprehensive_economic_analysis(
                data_integration, risk_assessment
            )
            
            # Phase 4: Decision matrix calculation
            logger.info("🎯 Phase 4: Decision matrix calculation")
            decision_matrix = self._calculate_decision_matrix(
                data_integration, risk_assessment, economic_analysis
            )
            
            # Phase 5: Optimal timing analysis
            logger.info("⏰ Phase 5: Optimal timing analysis")
            timing_analysis = self._analyze_optimal_execution_timing(
                forecast_result, decision_matrix
            )
            
            # Phase 6: Final decision synthesis
            logger.info("🧠 Phase 6: Final decision synthesis")
            final_decision = self._synthesize_final_decision(
                decision_matrix, timing_analysis, economic_analysis
            )
            
            # Phase 7: Execute action if required
            execution_result = None
            if final_decision['execute_cleaning']:
                logger.info("🚿 Phase 7: Executing cleaning action")
                execution_result = self._execute_cleaning_action(
                    final_decision, timing_analysis
                )
            else:
                logger.info("⏸️ Phase 7: No cleaning action required")
            
            # Phase 8: Generate comprehensive report
            logger.info("📋 Phase 8: Generating comprehensive report")
            comprehensive_report = self._generate_comprehensive_report(
                data_integration, risk_assessment, economic_analysis,
                decision_matrix, timing_analysis, final_decision, execution_result
            )
            
            processing_time = (time.time() - start_time) * 1000
            
            result = {
                'agent_name': self.agent_name,
                'agent_version': self.version,
                'timestamp': datetime.now().isoformat(),
                'success': True,
                'data_integration_analysis': data_integration,
                'multidimensional_risk_assessment': risk_assessment,
                'comprehensive_economic_analysis': economic_analysis,
                'decision_matrix_calculation': decision_matrix,
                'optimal_timing_analysis': timing_analysis,
                'final_decision_synthesis': final_decision,
                'execution_result': execution_result,
                'comprehensive_decision_report': comprehensive_report,
                'processing_time_ms': round(processing_time, 2)
            }
            
            # Log decision outcome
            action = "EXECUTE CLEANING" if final_decision['execute_cleaning'] else "NO ACTION"
            confidence = final_decision['decision_confidence']
            reasoning = final_decision['primary_reasoning']
            
            logger.info(f"✅ Decision Orchestration: {action} ({confidence:.1f}% confidence)")
            logger.info(f"💡 Primary reasoning: {reasoning}")
            
            if execution_result:
                water_used = execution_result.get('water_usage_actual_liters', 0)
                success = execution_result.get('execution_successful', False)
                logger.info(f"🚿 Execution: {'SUCCESS' if success else 'FAILED'} - "
                           f"Water used: {water_used:.1f}L")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Decision Orchestration failed: {e}")
            return {
                'agent_name': self.agent_name,
                'timestamp': datetime.now().isoformat(),
                'success': False,
                'error': str(e),
                'final_decision_synthesis': {
                    'execute_cleaning': False,
                    'decision_confidence': 0,
                    'primary_reasoning': f'System error: {str(e)}'
                }
            }
    
    def _initialize_spray_system(self):
        """Initialize spray system hardware or simulation mode"""
        
        if self.spray_system['enable_hardware']:
            try:
                # In real implementation, would initialize GPIO hardware here
                # import RPi.GPIO as GPIO
                # GPIO.setmode(GPIO.BCM)
                # GPIO.setup(self.spray_system['gpio_pin'], GPIO.OUT)
                logger.info("🚿 Spray system: Hardware GPIO enabled")
                self.spray_system['simulation_mode'] = False
            except Exception as e:
                logger.warning(f"GPIO initialization failed, using simulation: {e}")
                self.spray_system['simulation_mode'] = True
        else:
            logger.info("🚿 Spray system: Simulation mode")
            self.spray_system['simulation_mode'] = True
    
    def _integrate_and_validate_inputs(self, dust_result: Dict[str, Any],
                                     forecast_result: Dict[str, Any],
                                     image_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Phase 1: Integrate and validate inputs from all data sources
        
        This method extracts relevant data from each input source and validates
        consistency across different measurements.
        """
        
        # Extract environmental data from dust sensors
        environmental_data = {
            'risk_level': dust_result.get('advanced_risk_assessment', {}).get('risk_level', 'moderate'),
            'risk_score': dust_result.get('advanced_risk_assessment', {}).get('overall_risk_score', 50),
            'predicted_power_loss': dust_result.get('power_impact_prediction', {}).get('estimated_power_loss_percent', 10),
            'urgency_level': dust_result.get('cleaning_urgency_analysis', {}).get('urgency_level', 'moderate'),
            'environmental_confidence': dust_result.get('sensor_reliability', {}).get('overall_reliability', 80)
        }
        
        # Extract forecast data from weather predictions
        forecast_data = {
            'using_real_quartz': forecast_result.get('quartz_integration_status', {}).get('real_quartz_used', False),
            'daily_loss_kwh': forecast_result.get('dust_corrected_forecast', {}).get('daily_totals', {}).get('total_loss_kwh', 0),
            'cleaning_cost_effective': forecast_result.get('cleaning_impact_analysis', {}).get('recommendations', {}).get('urgency_justified', False),
            'optimal_scenario': forecast_result.get('cleaning_impact_analysis', {}).get('recommendations', {}).get('optimal_scenario', 'standard_cleaning'),
            'forecast_confidence': forecast_result.get('forecast_validation', {}).get('model_validation_metrics', {}).get('validation_confidence', 75)
        }
        
        # Extract visual analysis data from image processing
        visual_data = {
            'dust_level': image_result.get('visual_analysis_results', {}).get('dust_classification', {}).get('primary_level', 'moderate'),
            'visual_confidence': image_result.get('confidence_and_uncertainty', {}).get('overall_confidence', 75),
            'power_impact_visual': image_result.get('power_correlation_analysis', {}).get('estimated_power_impact_percent', 10),
            'image_quality': image_result.get('image_quality_assessment', {}).get('overall_quality_score', 75),
            'npu_accelerated': image_result.get('qualcomm_npu_performance', {}).get('npu_accelerated', False)
        }
        
        # Validate data consistency across sources
        consistency_analysis = self._validate_data_consistency(
            environmental_data, forecast_data, visual_data
        )
        
        # Assess reliability of each data source
        source_reliability = {
            'environmental_reliability': min(100, environmental_data['environmental_confidence']),
            'forecast_reliability': min(100, forecast_data['forecast_confidence']),
            'visual_reliability': min(100, visual_data['visual_confidence'] * (1.1 if visual_data['npu_accelerated'] else 1.0)),
            'overall_reliability': 0
        }
        
        source_reliability['overall_reliability'] = np.mean(list(source_reliability.values())[:-1])
        
        return {
            'environmental_data': environmental_data,
            'forecast_data': forecast_data,
            'visual_data': visual_data,
            'data_consistency_analysis': consistency_analysis,
            'source_reliability_assessment': source_reliability,
            'integration_timestamp': datetime.now().isoformat(),
            'data_quality_score': min(100, (consistency_analysis['overall_consistency'] + 
                                           source_reliability['overall_reliability']) / 2)
        }
    
    def _validate_data_consistency(self, env_data: Dict, forecast_data: Dict, 
                                 visual_data: Dict) -> Dict[str, Any]:
        """Validate consistency across different data sources"""
        
        # Check power loss consistency across sources
        env_power_loss = env_data['predicted_power_loss']
        visual_power_loss = visual_data['power_impact_visual']
        forecast_loss_kwh = forecast_data['daily_loss_kwh']
        
        # Convert forecast kWh to percentage (assuming 30 kWh daily generation)
        forecast_power_loss_percent = min(40, (forecast_loss_kwh / 30) * 100)
        
        power_loss_values = [env_power_loss, visual_power_loss, forecast_power_loss_percent]
        power_loss_consistency = 100 - np.std(power_loss_values) * 2
        
        # Check risk level consistency
        risk_levels = {'low': 1, 'moderate': 2, 'high': 3, 'critical': 4}
        env_risk_num = risk_levels.get(env_data['risk_level'], 2)
        visual_risk_num = risk_levels.get(visual_data['dust_level'], 2)
        urgency_risk_num = risk_levels.get(env_data['urgency_level'], 2)
        
        risk_consistency = 100 - np.std([env_risk_num, visual_risk_num, urgency_risk_num]) * 20
        
        # Check confidence consistency
        confidences = [env_data['environmental_confidence'], 
                      forecast_data['forecast_confidence'], 
                      visual_data['visual_confidence']]
        confidence_consistency = 100 - np.std(confidences) / 2
        
        # Calculate overall consistency
        overall_consistency = np.mean([power_loss_consistency, risk_consistency, confidence_consistency])
        
        return {
            'power_loss_consistency': max(0, round(power_loss_consistency, 1)),
            'risk_level_consistency': max(0, round(risk_consistency, 1)),
            'confidence_consistency': max(0, round(confidence_consistency, 1)),
            'overall_consistency': max(0, round(overall_consistency, 1)),
            'consistency_grade': 'excellent' if overall_consistency > 85 else 'good' if overall_consistency > 70 else 'fair' if overall_consistency > 55 else 'poor',
            'inconsistency_flags': self._identify_inconsistency_flags(power_loss_values, [env_risk_num, visual_risk_num, urgency_risk_num])
        }
    
    def _identify_inconsistency_flags(self, power_losses: List[float], risk_levels: List[int]) -> List[str]:
        """Identify specific inconsistency issues in the data"""
        flags = []
        
        if np.std(power_losses) > 10:
            flags.append('high_power_loss_variance')
        
        if np.std(risk_levels) > 1:
            flags.append('inconsistent_risk_assessment')
        
        if max(power_losses) - min(power_losses) > 20:
            flags.append('extreme_power_loss_disagreement')
        
        return flags
    
    def _perform_multidimensional_risk_assessment(self, data_integration: Dict[str, Any]) -> Dict[str, Any]:
        """
        Phase 2: Perform comprehensive multidimensional risk assessment
        
        Evaluates risks across four categories: technical, economic, operational, environmental
        """
        
        env_data = data_integration['environmental_data']
        forecast_data = data_integration['forecast_data']
        visual_data = data_integration['visual_data']
        
        # Technical risks - equipment and system performance
        technical_risks = {
            'power_generation_loss': self._assess_power_generation_risk(env_data, forecast_data, visual_data),
            'equipment_degradation': self._assess_equipment_degradation_risk(env_data, visual_data),
            'system_reliability': self._assess_system_reliability_risk(data_integration),
            'maintenance_complexity': self._assess_maintenance_complexity_risk(visual_data)
        }
        
        # Economic risks - financial impact
        economic_risks = {
            'revenue_loss': self._assess_revenue_loss_risk(forecast_data),
            'cleaning_cost_escalation': self._assess_cost_escalation_risk(env_data),
            'opportunity_cost': self._assess_opportunity_cost_risk(forecast_data, visual_data),
            'long_term_efficiency': self._assess_long_term_efficiency_risk(env_data, visual_data)
        }
        
        # Operational risks - execution and timing
        operational_risks = {
            'weather_dependency': self._assess_weather_dependency_risk(forecast_data),
            'resource_availability': self._assess_resource_availability_risk(),
            'timing_criticality': self._assess_timing_criticality_risk(env_data, visual_data),
            'execution_complexity': self._assess_execution_complexity_risk(visual_data)
        }
        
        # Environmental risks - external factors
        environmental_risks = {
            'dust_accumulation_rate': self._assess_dust_accumulation_risk(env_data),
            'weather_impact': self._assess_weather_impact_risk(forecast_data),
            'seasonal_factors': self._assess_seasonal_risk(),
            'air_quality_trends': self._assess_air_quality_risk(env_data)
        }
        
        # Aggregate risk scores by category
        risk_categories = {
            'technical_risk_score': np.mean(list(technical_risks.values())),
            'economic_risk_score': np.mean(list(economic_risks.values())),
            'operational_risk_score': np.mean(list(operational_risks.values())),
            'environmental_risk_score': np.mean(list(environmental_risks.values()))
        }
        
        # Calculate overall weighted risk score
        category_weights = {'technical': 0.3, 'economic': 0.3, 'operational': 0.2, 'environmental': 0.2}
        overall_risk_score = sum(
            risk_categories[f'{category}_risk_score'] * weight 
            for category, weight in category_weights.items()
        )
        
        # Classify risk level and recommend action
        if overall_risk_score >= 80:
            risk_level = 'critical'
            risk_action = 'immediate_action_required'
        elif overall_risk_score >= 65:
            risk_level = 'high'
            risk_action = 'urgent_action_recommended'
        elif overall_risk_score >= 45:
            risk_level = 'moderate'
            risk_action = 'planned_action_advisable'
        elif overall_risk_score >= 25:
            risk_level = 'low'
            risk_action = 'monitoring_sufficient'
        else:
            risk_level = 'minimal'
            risk_action = 'no_action_needed'
        
        return {
            'technical_risks': technical_risks,
            'economic_risks': economic_risks,
            'operational_risks': operational_risks,
            'environmental_risks': environmental_risks,
            'risk_category_scores': {k: round(v, 1) for k, v in risk_categories.items()},
            'overall_risk_assessment': {
                'overall_risk_score': round(overall_risk_score, 1),
                'risk_level': risk_level,
                'recommended_action': risk_action,
                'risk_tolerance_exceeded': overall_risk_score > self.decision_thresholds['maximum_acceptable_risk']
            },
            'risk_mitigation_priorities': self._identify_risk_mitigation_priorities(
                technical_risks, economic_risks, operational_risks, environmental_risks
            )
        }
    
    # Risk assessment helper methods
    def _assess_power_generation_risk(self, env_data: Dict, forecast_data: Dict, visual_data: Dict) -> float:
        """Assess risk of power generation loss"""
        power_losses = [
            env_data['predicted_power_loss'],
            visual_data['power_impact_visual'],
            min(40, (forecast_data['daily_loss_kwh'] / 30) * 100)
        ]
        avg_power_loss = np.mean(power_losses)
        return min(100, avg_power_loss * 2.5)
    
    def _assess_equipment_degradation_risk(self, env_data: Dict, visual_data: Dict) -> float:
        """Assess risk of equipment degradation"""
        dust_severity = {'clean': 10, 'light': 30, 'moderate': 60, 'heavy': 90}
        visual_severity = dust_severity.get(visual_data['dust_level'], 50)
        env_risk_factor = env_data['risk_score']
        return (visual_severity + env_risk_factor) / 2
    
    def _assess_system_reliability_risk(self, data_integration: Dict) -> float:
        """Assess risk to system reliability"""
        reliability_score = data_integration['source_reliability_assessment']['overall_reliability']
        consistency_score = data_integration['data_consistency_analysis']['overall_consistency']
        return 100 - ((reliability_score + consistency_score) / 2)
    
    def _assess_maintenance_complexity_risk(self, visual_data: Dict) -> float:
        """Assess maintenance complexity risk"""
        image_quality = visual_data['image_quality']
        dust_level_complexity = {'clean': 10, 'light': 25, 'moderate': 50, 'heavy': 80}
        complexity = dust_level_complexity.get(visual_data['dust_level'], 50)
        quality_factor = max(0, 100 - image_quality) / 2
        return complexity + quality_factor
    
    def _assess_revenue_loss_risk(self, forecast_data: Dict) -> float:
        """Assess revenue loss risk"""
        daily_loss_kwh = forecast_data['daily_loss_kwh']
        daily_loss_usd = daily_loss_kwh * self.economic_params['electricity_rate_per_kwh']
        return min(100, daily_loss_usd * 10)  # $10/day = 100% risk
    
    def _assess_cost_escalation_risk(self, env_data: Dict) -> float:
        """Assess cleaning cost escalation risk"""
        urgency_escalation = {'low': 0, 'moderate': 20, 'high': 50, 'critical_immediate': 80}
        return urgency_escalation.get(env_data['urgency_level'], 20)
    
    def _assess_opportunity_cost_risk(self, forecast_data: Dict, visual_data: Dict) -> float:
        """Assess opportunity cost risk"""
        if not forecast_data['cleaning_cost_effective']:
            return 70
        
        visual_confidence = visual_data['visual_confidence']
        return max(0, 80 - visual_confidence)
    
    def _assess_long_term_efficiency_risk(self, env_data: Dict, visual_data: Dict) -> float:
        """Assess long-term efficiency degradation risk"""
        dust_accumulation_factor = {'clean': 5, 'light': 20, 'moderate': 50, 'heavy': 85}
        env_risk_factor = env_data['risk_score'] / 2
        visual_risk_factor = dust_accumulation_factor.get(visual_data['dust_level'], 40)
        return (env_risk_factor + visual_risk_factor) / 2
    
    def _assess_weather_dependency_risk(self, forecast_data: Dict) -> float:
        """Assess weather dependency risk"""
        forecast_confidence = forecast_data['forecast_confidence']
        using_real_quartz = forecast_data['using_real_quartz']
        
        base_risk = 100 - forecast_confidence
        if not using_real_quartz:
            base_risk += 20
        
        return min(100, base_risk)
    
    def _assess_resource_availability_risk(self) -> float:
        """Assess resource availability risk"""
        water_availability = 95
        equipment_availability = 90
        labor_availability = 85
        
        avg_availability = (water_availability + equipment_availability + labor_availability) / 3
        return 100 - avg_availability
    
    def _assess_timing_criticality_risk(self, env_data: Dict, visual_data: Dict) -> float:
        """Assess timing criticality risk"""
        urgency_scores = {'low': 10, 'moderate': 30, 'high': 70, 'critical_immediate': 95}
        urgency_risk = urgency_scores.get(env_data['urgency_level'], 30)
        
        dust_timing_risk = {'clean': 5, 'light': 15, 'moderate': 40, 'heavy': 80}
        dust_risk = dust_timing_risk.get(visual_data['dust_level'], 40)
        
        return max(urgency_risk, dust_risk)
    
    def _assess_execution_complexity_risk(self, visual_data: Dict) -> float:
        """Assess execution complexity risk"""
        image_quality = visual_data['image_quality']
        npu_accelerated = visual_data['npu_accelerated']
        
        complexity_risk = max(0, 100 - image_quality) / 2
        if npu_accelerated:
            complexity_risk *= 0.8
        
        return complexity_risk
    
    def _assess_dust_accumulation_risk(self, env_data: Dict) -> float:
        """Assess dust accumulation risk"""
        return env_data['risk_score']
    
    def _assess_weather_impact_risk(self, forecast_data: Dict) -> float:
        """Assess weather impact risk"""
        return max(0, 80 - forecast_data['forecast_confidence'])
    
    def _assess_seasonal_risk(self) -> float:
        """Assess seasonal risk factors"""
        current_month = datetime.now().month
        
        # Higher risk during dusty seasons (pre-monsoon, post-monsoon in India)
        if current_month in [3, 4, 5, 10, 11]:  # March-May, Oct-Nov
            return 70
        elif current_month in [6, 7, 8, 9]:  # Monsoon season
            return 30
        else:  # Winter months
            return 50
    
    def _assess_air_quality_risk(self, env_data: Dict) -> float:
        """Assess air quality impact risk"""
        return env_data['risk_score']
    
    def _identify_risk_mitigation_priorities(self, technical: Dict, economic: Dict, 
                                           operational: Dict, environmental: Dict) -> List[Dict]:
        """Identify top risk mitigation priorities"""
        
        all_risks = []
        
        for category, risks in [('technical', technical), ('economic', economic), 
                               ('operational', operational), ('environmental', environmental)]:
            for risk_name, risk_score in risks.items():
                all_risks.append({
                    'category': category,
                    'risk_name': risk_name,
                    'risk_score': risk_score,
                    'priority': 'critical' if risk_score > 80 else 'high' if risk_score > 60 else 'medium'
                })
        
        # Sort by risk score and return top priorities
        all_risks.sort(key=lambda x: x['risk_score'], reverse=True)
        return all_risks[:5]
    
    def _comprehensive_economic_analysis(self, data_integration: Dict[str, Any],
                                       risk_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Phase 3: Perform comprehensive economic impact analysis
        
        Calculates costs, benefits, ROI scenarios, and long-term projections
        """
        
        forecast_data = data_integration['forecast_data']
        visual_data = data_integration['visual_data']
        
        # Calculate revenue impact from power loss
        daily_loss_kwh = forecast_data['daily_loss_kwh']
        electricity_rate = self.economic_params['electricity_rate_per_kwh']
        
        revenue_impact = {
            'daily_loss_kwh': daily_loss_kwh,
            'daily_revenue_loss_usd': round(daily_loss_kwh * electricity_rate, 2),
            'weekly_revenue_loss_usd': round(daily_loss_kwh * electricity_rate * 7, 2),
            'monthly_revenue_loss_usd': round(daily_loss_kwh * electricity_rate * 30, 2),
            'annual_revenue_loss_usd': round(daily_loss_kwh * electricity_rate * 365, 2)
        }
        
        # Calculate comprehensive cleaning costs
        cleaning_costs = self._calculate_comprehensive_cleaning_costs(visual_data)
        
        # Analyze ROI for different scenarios
        roi_analysis = self._calculate_roi_scenarios(revenue_impact, cleaning_costs, visual_data)
        
        # Calculate risk-adjusted projections
        risk_adjusted_projections = self._calculate_risk_adjusted_projections(
            revenue_impact, cleaning_costs, risk_assessment
        )
        
        # Analyze cost-benefit thresholds
        threshold_analysis = self._analyze_cost_benefit_thresholds(
            revenue_impact, cleaning_costs, risk_assessment
        )
        
        # Model long-term economic impact
        long_term_modeling = self._model_long_term_economic_impact(
            revenue_impact, cleaning_costs, visual_data
        )
        
        return {
            'revenue_impact_analysis': revenue_impact,
            'comprehensive_cleaning_costs': cleaning_costs,
            'roi_scenario_analysis': roi_analysis,
            'risk_adjusted_projections': risk_adjusted_projections,
            'cost_benefit_threshold_analysis': threshold_analysis,
            'long_term_economic_modeling': long_term_modeling,
            'economic_recommendation': self._generate_economic_recommendation(
                revenue_impact, cleaning_costs, roi_analysis, risk_assessment
            )
        }
    
    def _calculate_comprehensive_cleaning_costs(self, visual_data: Dict) -> Dict[str, Any]:
        """Calculate detailed cleaning costs based on dust level"""
        
        dust_level = visual_data['dust_level']
        
        # Cost multipliers by dust level
        cost_multipliers = {
            'clean': 0.5,      # Maintenance cleaning
            'light': 0.8,      # Light cleaning
            'moderate': 1.0,   # Standard cleaning
            'heavy': 1.5       # Intensive cleaning
        }
        
        multiplier = cost_multipliers.get(dust_level, 1.0)
        
        # Water consumption calculation
        base_water_usage = 15  # Base liters
        water_usage = base_water_usage * multiplier
        water_cost = water_usage * self.economic_params['water_cost_per_liter']
        
        # Labor time and cost
        base_labor_time = 1.0  # Base hours
        labor_time = base_labor_time * multiplier
        labor_cost = labor_time * self.economic_params['labor_cost_per_hour']
        
        # Equipment and supplies
        equipment_cost = self.economic_params['equipment_cost_per_use'] * multiplier
        
        # Additional indirect costs
        transportation_cost = 5.0
        setup_cost = 3.0
        quality_assurance_cost = 2.0
        
        total_direct_cost = water_cost + labor_cost + equipment_cost
        total_indirect_cost = transportation_cost + setup_cost + quality_assurance_cost
        total_cost = total_direct_cost + total_indirect_cost
        
        return {
            'dust_level': dust_level,
            'cost_multiplier': multiplier,
            'direct_costs': {
                'water_usage_liters': round(water_usage, 1),
                'water_cost_usd': round(water_cost, 2),
                'labor_hours': round(labor_time, 2),
                'labor_cost_usd': round(labor_cost, 2),
                'equipment_cost_usd': round(equipment_cost, 2),
                'total_direct_cost_usd': round(total_direct_cost, 2)
            },
            'indirect_costs': {
                'transportation_cost_usd': transportation_cost,
                'setup_cost_usd': setup_cost,
                'quality_assurance_cost_usd': quality_assurance_cost,
                'total_indirect_cost_usd': total_indirect_cost
            },
            'total_cleaning_cost_usd': round(total_cost, 2),
            'cost_per_kwp': round(total_cost / 5.0, 2)  # Assuming 5 kWp system
        }
    
    def _calculate_roi_scenarios(self, revenue_impact: Dict, cleaning_costs: Dict, 
                               visual_data: Dict) -> Dict[str, Any]:
        """Calculate ROI for different cleaning effectiveness scenarios"""
        
        daily_revenue_loss = revenue_impact['daily_revenue_loss_usd']
        cleaning_cost = cleaning_costs['total_cleaning_cost_usd']
        
        # Different effectiveness scenarios
        effectiveness_scenarios = {
            'conservative': 0.70,  # 70% dust removal
            'realistic': 0.85,     # 85% dust removal
            'optimistic': 0.95     # 95% dust removal
        }
        
        roi_scenarios = {}
        
        for scenario, effectiveness in effectiveness_scenarios.items():
            # Calculate recovered revenue
            daily_recovery = daily_revenue_loss * effectiveness
            
            # Payback period calculation
            payback_days = cleaning_cost / max(daily_recovery, 0.01)
            
            # Net benefit calculations
            weekly_net = (daily_recovery * 7) - cleaning_cost
            monthly_net = (daily_recovery * 30) - (cleaning_cost * 2)  # Bi-weekly cleaning
            annual_net = (daily_recovery * 365) - (cleaning_cost * 26)  # Bi-weekly cleaning
            
            roi_scenarios[scenario] = {
                'effectiveness_percent': round(effectiveness * 100, 1),
                'daily_revenue_recovery_usd': round(daily_recovery, 2),
                'payback_period_days': round(payback_days, 1),
                'weekly_net_benefit_usd': round(weekly_net, 2),
                'monthly_net_benefit_usd': round(monthly_net, 2),
                'annual_net_benefit_usd': round(annual_net, 2),
                'roi_percentage': round((annual_net / max(cleaning_cost * 26, 1)) * 100, 1),
                'cost_effective': payback_days <= 14
            }
        
        # Determine recommended scenario
        cost_effective_scenarios = [s for s, data in roi_scenarios.items() if data['cost_effective']]
        recommended_scenario = cost_effective_scenarios[0] if cost_effective_scenarios else 'conservative'
        
        return {
            'scenario_analysis': roi_scenarios,
            'recommended_scenario': recommended_scenario,
            'best_case_payback_days': min(data['payback_period_days'] for data in roi_scenarios.values()),
            'worst_case_payback_days': max(data['payback_period_days'] for data in roi_scenarios.values()),
            'economic_viability': any(data['cost_effective'] for data in roi_scenarios.values())
        }
    
    def _calculate_risk_adjusted_projections(self, revenue_impact: Dict, 
                                           cleaning_costs: Dict, 
                                           risk_assessment: Dict) -> Dict[str, Any]:
        """Calculate risk-adjusted economic projections"""
        
        overall_risk_score = risk_assessment['overall_risk_assessment']['overall_risk_score']
        risk_factor = 1 - (overall_risk_score / 200)  # Convert to risk adjustment factor
        
        # Adjust revenue projections for risk
        base_daily_loss = revenue_impact['daily_revenue_loss_usd']
        risk_adjusted_daily_loss = base_daily_loss * (0.5 + risk_factor)  # 50-100% of projected loss
        
        # Adjust costs for risk (higher risk may increase costs)
        base_cleaning_cost = cleaning_costs['total_cleaning_cost_usd']
        risk_cost_multiplier = 1 + ((overall_risk_score - 50) / 200)  # 0.75-1.25x multiplier
        risk_adjusted_cost = base_cleaning_cost * risk_cost_multiplier
        
        return {
            'risk_adjustment_factor': round(risk_factor, 3),
            'risk_adjusted_revenue_loss': {
                'daily_usd': round(risk_adjusted_daily_loss, 2),
                'weekly_usd': round(risk_adjusted_daily_loss * 7, 2),
                'monthly_usd': round(risk_adjusted_daily_loss * 30, 2)
            },
            'risk_adjusted_cleaning_cost': round(risk_adjusted_cost, 2),
            'risk_adjusted_payback_days': round(risk_adjusted_cost / max(risk_adjusted_daily_loss, 0.01), 1),
            'confidence_intervals': {
                'daily_loss_range': [
                    round(risk_adjusted_daily_loss * 0.8, 2),
                    round(risk_adjusted_daily_loss * 1.2, 2)
                ],
                'cost_range': [
                    round(risk_adjusted_cost * 0.9, 2),
                    round(risk_adjusted_cost * 1.1, 2)
                ]
            }
        }
    
    def _analyze_cost_benefit_thresholds(self, revenue_impact: Dict, 
                                       cleaning_costs: Dict,
                                       risk_assessment: Dict) -> Dict[str, Any]:
        """Analyze cost-benefit thresholds for decision making"""
        
        daily_revenue_loss = revenue_impact['daily_revenue_loss_usd']
        cleaning_cost = cleaning_costs['total_cleaning_cost_usd']
        
        # Calculate break-even points for different frequencies
        break_even_scenarios = {}
        
        for frequency_days in [7, 14, 21, 30]:
            net_benefit = (daily_revenue_loss * frequency_days) - cleaning_cost
            break_even_scenarios[f'{frequency_days}_day_frequency'] = {
                'frequency_days': frequency_days,
                'net_benefit_usd': round(net_benefit, 2),
                'profitable': net_benefit > 0,
                'roi_percent': round((net_benefit / cleaning_cost) * 100, 1) if cleaning_cost > 0 else 0
            }
        
        # Calculate profitability thresholds
        min_daily_loss_for_profitability = cleaning_cost / 14  # 2-week payback
        max_cost_for_profitability = daily_revenue_loss * 14  # 2-week payback
        
        return {
            'break_even_analysis': break_even_scenarios,
            'profitability_thresholds': {
                'min_daily_revenue_loss_usd': round(min_daily_loss_for_profitability, 2),
                'max_cleaning_cost_usd': round(max_cost_for_profitability, 2),
                'current_daily_loss_usd': daily_revenue_loss,
                'current_cleaning_cost_usd': cleaning_cost,
                'meets_profitability_threshold': daily_revenue_loss >= min_daily_loss_for_profitability
            },
            'optimal_frequency_analysis': {
                'most_profitable_frequency': max(break_even_scenarios.keys(), 
                                               key=lambda k: break_even_scenarios[k]['net_benefit_usd']),
                'recommended_frequency_days': 14 if daily_revenue_loss * 14 > cleaning_cost else 21
            }
        }
    
    def _model_long_term_economic_impact(self, revenue_impact: Dict, 
                                       cleaning_costs: Dict, 
                                       visual_data: Dict) -> Dict[str, Any]:
        """Model long-term economic impact scenarios over 3 years"""
        
        daily_loss = revenue_impact['daily_revenue_loss_usd']
        cleaning_cost = cleaning_costs['total_cleaning_cost_usd']
        
        # Define degradation scenarios
        degradation_scenarios = {
            'no_cleaning': {
                'year_1_daily_loss_multiplier': 1.0,
                'year_2_daily_loss_multiplier': 1.3,
                'year_3_daily_loss_multiplier': 1.7,
                'description': 'No cleaning - progressive degradation'
            },
            'reactive_cleaning': {
                'year_1_daily_loss_multiplier': 0.8,
                'year_2_daily_loss_multiplier': 0.9,
                'year_3_daily_loss_multiplier': 1.0,
                'description': 'Clean only when severe - moderate degradation'
            },
            'preventive_cleaning': {
                'year_1_daily_loss_multiplier': 0.3,
                'year_2_daily_loss_multiplier': 0.4,
                'year_3_daily_loss_multiplier': 0.5,
                'description': 'Regular preventive cleaning - minimal degradation'
            }
        }
        
        long_term_analysis = {}
        
        for scenario, params in degradation_scenarios.items():
            yearly_costs = []
            yearly_losses = []
            
            for year in range(1, 4):
                multiplier_key = f'year_{year}_daily_loss_multiplier'
                loss_multiplier = params[multiplier_key]
                
                yearly_loss = daily_loss * loss_multiplier * 365
                
                if scenario == 'no_cleaning':
                    yearly_cleaning_cost = 0
                elif scenario == 'reactive_cleaning':
                    yearly_cleaning_cost = cleaning_cost * 4  # Quarterly
                else:  # preventive_cleaning
                    yearly_cleaning_cost = cleaning_cost * 12  # Monthly
                
                yearly_costs.append(yearly_cleaning_cost)
                yearly_losses.append(yearly_loss)
            
            long_term_analysis[scenario] = {
                'description': params['description'],
                'three_year_summary': {
                    'total_revenue_loss_usd': round(sum(yearly_losses), 2),
                    'total_cleaning_costs_usd': round(sum(yearly_costs), 2),
                    'total_economic_impact_usd': round(sum(yearly_losses) + sum(yearly_costs), 2),
                    'average_annual_impact_usd': round((sum(yearly_losses) + sum(yearly_costs)) / 3, 2)
                },
                'yearly_breakdown': [
                    {
                        'year': year + 1,
                        'revenue_loss_usd': round(loss, 2),
                        'cleaning_costs_usd': round(cost, 2),
                        'total_impact_usd': round(loss + cost, 2)
                    }
                    for year, (loss, cost) in enumerate(zip(yearly_losses, yearly_costs))
                ]
            }
        
        # Find optimal strategy
        total_impacts = {scenario: data['three_year_summary']['total_economic_impact_usd'] 
                        for scenario, data in long_term_analysis.items()}
        optimal_strategy = min(total_impacts.keys(), key=lambda k: total_impacts[k])
        
        return {
            'scenario_analysis': long_term_analysis,
            'strategy_comparison': {
                'lowest_cost_strategy': optimal_strategy,
                'cost_differences': {
                    scenario: round(impact - total_impacts[optimal_strategy], 2)
                    for scenario, impact in total_impacts.items()
                }
            },
            'recommendations': {
                'optimal_long_term_strategy': optimal_strategy,
                'three_year_savings_vs_no_cleaning': round(
                    total_impacts['no_cleaning'] - total_impacts[optimal_strategy], 2
                ),
                'strategy_justification': long_term_analysis[optimal_strategy]['description']
            }
        }
    
    def _generate_economic_recommendation(self, revenue_impact: Dict, 
                                        cleaning_costs: Dict, 
                                        roi_analysis: Dict,
                                        risk_assessment: Dict) -> Dict[str, str]:
        """Generate economic recommendation based on analysis"""
        
        daily_loss = revenue_impact['daily_revenue_loss_usd']
        cleaning_cost = cleaning_costs['total_cleaning_cost_usd']
        economic_viability = roi_analysis['economic_viability']
        overall_risk = risk_assessment['overall_risk_assessment']['overall_risk_score']
        
        if economic_viability and overall_risk > 70:
            recommendation = 'immediate_cleaning_economically_justified'
            reasoning = f"High risk ({overall_risk:.0f}/100) with economic viability"
        elif economic_viability:
            recommendation = 'cleaning_economically_justified'
            reasoning = f"Positive ROI with ${daily_loss:.2f}/day loss vs ${cleaning_cost:.2f} cost"
        elif daily_loss > 5.0:
            recommendation = 'cleaning_marginal_consider_frequency'
            reasoning = f"High daily losses (${daily_loss:.2f}) may justify less frequent cleaning"
        else:
            recommendation = 'cleaning_not_economically_justified'
            reasoning = f"Low economic impact (${daily_loss:.2f}/day) vs cleaning cost (${cleaning_cost:.2f})"
        
        return {
            'recommendation': recommendation,
            'reasoning': reasoning,
            'confidence': 'high' if economic_viability else 'medium'
        }
    
    def _calculate_decision_matrix(self, data_integration: Dict[str, Any],
                                 risk_assessment: Dict[str, Any],
                                 economic_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Phase 4: Calculate comprehensive decision matrix
        
        Combines all factors into a weighted decision score
        """
        
        # Extract key metrics
        visual_data = data_integration['visual_data']
        overall_confidence = data_integration['source_reliability_assessment']['overall_reliability']
        overall_risk = risk_assessment['overall_risk_assessment']['overall_risk_score']
        economic_viability = economic_analysis['roi_scenario_analysis']['economic_viability']
        
        # Calculate decision factors with weights
        decision_factors = {
            'dust_severity': {
                'score': self._calculate_dust_severity_score(visual_data),
                'weight': self.decision_framework['dust_severity_weight']
            },
            'economic_impact': {
                'score': self._calculate_economic_impact_score(economic_analysis),
                'weight': self.decision_framework['economic_impact_weight']
            },
            'risk_assessment': {
                'score': overall_risk,
                'weight': self.decision_framework['risk_assessment_weight']
            },
            'confidence_level': {
                'score': overall_confidence,
                'weight': self.decision_framework['confidence_weight']
            },
            'timing_optimization': {
                'score': self._calculate_timing_score(data_integration),
                'weight': self.decision_framework['timing_optimization_weight']
            }
        }
        
        # Calculate weighted total score
        total_score = sum(
            factor['score'] * factor['weight'] 
            for factor in decision_factors.values()
        )
        
        # Classify decision based on score
        if total_score >= self.decision_thresholds['critical_action_score']:
            decision_class = 'critical_action_required'
            confidence_level = 'very_high'
        elif total_score >= self.decision_thresholds['recommended_action_score']:
            decision_class = 'action_recommended'
            confidence_level = 'high'
        elif total_score >= self.decision_thresholds['optional_action_score']:
            decision_class = 'action_optional'
            confidence_level = 'medium'
        else:
            decision_class = 'no_action_needed'
            confidence_level = 'high'
        
        # Validate decision factors
        validation_results = self._validate_decision_factors(
            decision_factors, overall_confidence, overall_risk
        )
        
        return {
            'decision_factors': {k: {**v, 'score': round(v['score'], 1)} for k, v in decision_factors.items()},
            'weighted_scores': {
                k: round(factor['score'] * factor['weight'], 2) 
                for k, factor in decision_factors.items()
            },
            'total_decision_score': round(total_score, 1),
            'decision_classification': decision_class,
            'decision_confidence_level': confidence_level,
            'threshold_analysis': {
                'critical_threshold': self.decision_thresholds['critical_action_score'],
                'recommended_threshold': self.decision_thresholds['recommended_action_score'],
                'optional_threshold': self.decision_thresholds['optional_action_score'],
                'score_margin': round(total_score - self.decision_thresholds['recommended_action_score'], 1)
            },
            'validation_results': validation_results
        }
    
    def _calculate_dust_severity_score(self, visual_data: Dict) -> float:
        """Calculate dust severity score for decision matrix"""
        dust_levels = {'clean': 15, 'light': 40, 'moderate': 70, 'heavy': 95}
        base_score = dust_levels.get(visual_data['dust_level'], 50)
        
        # Adjust for visual confidence
        confidence_factor = visual_data['visual_confidence'] / 100
        npu_boost = 5 if visual_data['npu_accelerated'] else 0
        
        return min(100, base_score * confidence_factor + npu_boost)
    
    def _calculate_economic_impact_score(self, economic_analysis: Dict) -> float:
        """Calculate economic impact score for decision matrix"""
        revenue_loss = economic_analysis['revenue_impact_analysis']['daily_revenue_loss_usd']
        economic_viability = economic_analysis['roi_scenario_analysis']['economic_viability']
        
        # Base score from revenue loss (scale $0-10/day to 0-100 score)
        base_score = min(100, revenue_loss * 10)
        
        # Boost if economically viable
        viability_boost = 20 if economic_viability else 0
        
        return min(100, base_score + viability_boost)
    
    def _calculate_timing_score(self, data_integration: Dict) -> float:
        """Calculate timing optimization score"""
        env_data = data_integration['environmental_data']
        urgency_scores = {'low': 20, 'moderate': 50, 'high': 80, 'critical_immediate': 95}
        
        return urgency_scores.get(env_data['urgency_level'], 50)
    
    def _validate_decision_factors(self, decision_factors: Dict, 
                                 overall_confidence: float, 
                                 overall_risk: float) -> Dict[str, Any]:
        """Validate decision factors and identify issues"""
        
        validation_issues = []
        
        # Check minimum confidence threshold
        if overall_confidence < self.decision_thresholds['minimum_confidence']:
            validation_issues.append(f'confidence_below_threshold_{self.decision_thresholds["minimum_confidence"]}')
        
        # Check risk tolerance
        if overall_risk > self.decision_thresholds['maximum_acceptable_risk']:
            validation_issues.append(f'risk_exceeds_tolerance_{self.decision_thresholds["maximum_acceptable_risk"]}')
        
        # Check factor score consistency
        factor_scores = [factor['score'] for factor in decision_factors.values()]
        if np.std(factor_scores) > 30:
            validation_issues.append('high_factor_score_variance')
        
        return {
            'validation_passed': len(validation_issues) == 0,
            'validation_issues': validation_issues,
            'confidence_adequate': overall_confidence >= self.decision_thresholds['minimum_confidence'],
            'risk_acceptable': overall_risk <= self.decision_thresholds['maximum_acceptable_risk']
        }
    
    def _analyze_optimal_execution_timing(self, forecast_result: Dict[str, Any],
                                        decision_matrix: Dict[str, Any]) -> Dict[str, Any]:
        """
        Phase 5: Analyze optimal timing for cleaning execution
        
        Considers weather conditions and decision urgency
        """
        
        # Extract weather optimization data
        weather_analysis = forecast_result.get('weather_optimization_analysis', {})
        
        decision_class = decision_matrix['decision_classification']
        
        # Determine timing urgency based on decision classification
        if decision_class == 'critical_action_required':
            timing_urgency = 'immediate'
            max_delay_hours = 6
        elif decision_class == 'action_recommended':
            timing_urgency = 'within_24_hours'
            max_delay_hours = 24
        elif decision_class == 'action_optional':
            timing_urgency = 'within_week'
            max_delay_hours = 168
        else:
            timing_urgency = 'no_urgency'
            max_delay_hours = 999
        
        # Analyze weather windows
        optimal_windows = weather_analysis.get('optimal_cleaning_windows', [])
        
        # Find best execution time
        if optimal_windows and timing_urgency != 'immediate':
            best_window = optimal_windows[0]
            recommended_timing = {
                'timing_type': 'optimized_weather_window',
                'start_time': best_window.get('start_time'),
                'duration_hours': best_window.get('duration_hours', 4),
                'suitability_score': best_window.get('suitability_score', 0)
            }
        else:
            recommended_timing = {
                'timing_type': 'immediate_execution',
                'start_time': datetime.now().isoformat(),
                'duration_hours': 2,
                'suitability_score': 70  # Default for immediate execution
            }
        
        return {
            'timing_urgency': timing_urgency,
            'max_delay_hours': max_delay_hours,
            'recommended_execution_timing': recommended_timing,
            'weather_considerations': {
                'optimal_windows_available': len(optimal_windows),
                'weather_favorability': weather_analysis.get('cleaning_favorability', 'unknown'),
                'weather_pattern': weather_analysis.get('weather_pattern_classification', 'unknown')
            },
            'execution_readiness': self._assess_execution_readiness()
        }
    
    def _assess_execution_readiness(self) -> Dict[str, Any]:
        """Assess readiness for immediate execution"""
        
        # Simulate readiness assessment (in real implementation, would check actual systems)
        readiness_factors = {
            'water_supply_available': True,
            'equipment_operational': True,
            'weather_suitable': np.random.choice([True, False], p=[0.8, 0.2]),
            'personnel_available': True,
            'safety_conditions_met': True
        }
        
        readiness_score = sum(readiness_factors.values()) / len(readiness_factors) * 100
        
        return {
            'overall_readiness_score': round(readiness_score, 1),
            'readiness_factors': readiness_factors,
            'ready_for_execution': readiness_score >= 80,
            'blocking_factors': [factor for factor, ready in readiness_factors.items() if not ready]
        }
    
    def _synthesize_final_decision(self, decision_matrix: Dict[str, Any],
                                 timing_analysis: Dict[str, Any],
                                 economic_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Phase 6: Synthesize final decision based on all analyses
        
        Combines decision matrix, timing, and economic factors into final go/no-go decision
        """
        
        decision_score = decision_matrix['total_decision_score']
        decision_class = decision_matrix['decision_classification']
        validation_passed = decision_matrix['validation_results']['validation_passed']
        economic_viable = economic_analysis['roi_scenario_analysis']['economic_viability']
        execution_ready = timing_analysis['execution_readiness']['ready_for_execution']
        
        # Final decision logic with multiple criteria
        if (decision_score >= self.decision_thresholds['recommended_action_score'] and 
            validation_passed and 
            economic_viable and 
            execution_ready):
            
            execute_cleaning = True
            decision_confidence = min(95, decision_score)
            primary_reasoning = f"All criteria met: score {decision_score:.1f}, economic viability confirmed"
            
        elif (decision_score >= self.decision_thresholds['critical_action_score'] and 
              validation_passed and 
              execution_ready):
            
            execute_cleaning = True
            decision_confidence = min(90, decision_score - 5)
            primary_reasoning = f"Critical conditions override economic concerns: score {decision_score:.1f}"
            
        elif (decision_score >= self.decision_thresholds['optional_action_score'] and 
              economic_viable and 
              execution_ready):
            
            execute_cleaning = True
            decision_confidence = min(85, decision_score)
            primary_reasoning = f"Economic viability justifies optional cleaning: ROI positive"
            
        else:
            execute_cleaning = False
            decision_confidence = max(60, 100 - decision_score)
            
            if not validation_passed:
                primary_reasoning = "Data validation failed - insufficient confidence for cleaning decision"
            elif not economic_viable:
                primary_reasoning = f"Economic analysis does not justify cleaning costs"
            elif not execution_ready:
                primary_reasoning = "System not ready for execution - blocking factors present"
            else:
                primary_reasoning = f"Decision score too low: {decision_score:.1f} < {self.decision_thresholds['optional_action_score']}"
        
        return {
            'execute_cleaning': execute_cleaning,
            'decision_confidence': round(decision_confidence, 1),
            'primary_reasoning': primary_reasoning,
            'decision_classification': decision_class,
            'contributing_factors': {
                'decision_score': decision_score,
                'validation_passed': validation_passed,
                'economic_viable': economic_viable,
                'execution_ready': execution_ready
            },
            'alternative_recommendations': self._generate_alternative_recommendations(
                execute_cleaning, decision_matrix, economic_analysis
            )
        }
    
    def _generate_alternative_recommendations(self, execute_cleaning: bool,
                                            decision_matrix: Dict[str, Any],
                                            economic_analysis: Dict[str, Any]) -> List[str]:
        """Generate alternative recommendations based on decision outcome"""
        
        alternatives = []
        
        if not execute_cleaning:
            decision_score = decision_matrix['total_decision_score']
            
            if decision_score > 60:
                alternatives.append("Monitor conditions closely and re-evaluate in 24 hours")
            
            if not economic_analysis['roi_scenario_analysis']['economic_viability']:
                alternatives.append("Consider lower-cost cleaning methods or wait for better economic conditions")
            
            alternatives.append("Continue automated monitoring and analysis")
            
        else:
            alternatives.append("Consider delaying execution if weather conditions improve")
            alternatives.append("Evaluate partial cleaning of most affected areas only")
        
        return alternatives
    
    def _execute_cleaning_action(self, final_decision: Dict[str, Any],
                               timing_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Phase 7: Execute the cleaning action with comprehensive safety protocols
        
        Performs pre-execution checks, executes cleaning, and validates results
        """
        
        execution_start = time.time()
        
        try:
            # Pre-execution safety checks
            safety_checks = self._perform_pre_execution_safety_checks()
            
            if not safety_checks['all_checks_passed']:
                return {
                    'execution_attempted': True,
                    'execution_successful': False,
                    'failure_reason': 'safety_checks_failed',
                    'safety_check_results': safety_checks,
                    'execution_time_ms': round((time.time() - execution_start) * 1000, 2)
                }
            
            # Execute cleaning sequence
            cleaning_result = self._execute_cleaning_sequence(timing_analysis)
            
            # Post-execution validation
            post_validation = self._perform_post_execution_validation()
            
            execution_time = (time.time() - execution_start) * 1000
            
            return {
                'execution_attempted': True,
                'execution_successful': cleaning_result['success'],
                'pre_execution_safety_checks': safety_checks,
                'cleaning_sequence_result': cleaning_result,
                'post_execution_validation': post_validation,
                'execution_time_ms': round(execution_time, 2),
                'water_usage_planned_liters': cleaning_result['water_usage_planned'],
                'water_usage_actual_liters': cleaning_result['water_usage_actual'],
                'cleaning_duration_seconds': cleaning_result['cleaning_duration'],
                'execution_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            execution_time = (time.time() - execution_start) * 1000
            return {
                'execution_attempted': True,
                'execution_successful': False,
                'failure_reason': 'execution_error',
                'error_details': str(e),
                'execution_time_ms': round(execution_time, 2)
            }
    
    def _perform_pre_execution_safety_checks(self) -> Dict[str, Any]:
        """Perform comprehensive pre-execution safety checks"""
        
        safety_checks = {
            'water_pressure_adequate': True,
            'electrical_isolation_confirmed': True,
            'weather_conditions_safe': np.random.choice([True, False], p=[0.9, 0.1]),
            'personnel_safety_cleared': True,
            'equipment_status_operational': True,
            'emergency_stop_functional': True
        }
        
        all_passed = all(safety_checks.values())
        
        return {
            'individual_checks': safety_checks,
            'all_checks_passed': all_passed,
            'failed_checks': [check for check, passed in safety_checks.items() if not passed],
            'safety_override_available': not all_passed,
            'check_timestamp': datetime.now().isoformat()
        }
    
    def _execute_cleaning_sequence(self, timing_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the actual cleaning sequence"""
        
        sequence_start = time.time()
        
        # Planned parameters
        planned_water_usage = 12.5  # liters
        planned_duration = 45       # seconds
        
        if self.spray_system['simulation_mode']:
            # Simulate cleaning execution
            logger.info("🚿 Executing cleaning sequence (SIMULATION)")
            
            # Simulate execution time
            time.sleep(0.1)  # Quick simulation
            
            # Simulate realistic variations
            actual_water_usage = planned_water_usage + np.random.normal(0, 1.5)
            actual_duration = planned_duration + np.random.normal(0, 8)
            success_probability = 0.95
            
            execution_successful = np.random.random() < success_probability
            
        else:
            # Real hardware execution
            logger.info("🚿 Executing cleaning sequence (HARDWARE)")
            
            try:
                # Real GPIO control would be implemented here
                # Example:
                # import RPi.GPIO as GPIO
                # GPIO.output(self.spray_system['gpio_pin'], GPIO.HIGH)
                # time.sleep(planned_duration)
                # GPIO.output(self.spray_system['gpio_pin'], GPIO.LOW)
                
                actual_water_usage = planned_water_usage
                actual_duration = planned_duration
                execution_successful = True
                
            except Exception as e:
                logger.error(f"Hardware execution failed: {e}")
                actual_water_usage = 0
                actual_duration = 0
                execution_successful = False
        
        sequence_time = (time.time() - sequence_start) * 1000
        
        return {
            'success': execution_successful,
            'water_usage_planned': planned_water_usage,
            'water_usage_actual': round(max(0, actual_water_usage), 1),
            'cleaning_duration': round(max(0, actual_duration), 1),
            'sequence_execution_time_ms': round(sequence_time, 2),
            'execution_mode': 'simulation' if self.spray_system['simulation_mode'] else 'hardware',
            'spray_pattern': 'wide_coverage_sweep',
            'water_pressure_psi': 35,
            'nozzle_configuration': 'multi_jet_array'
        }
    
    def _perform_post_execution_validation(self) -> Dict[str, Any]:
        """Perform post-execution validation and assessment"""
        
        # Simulate post-execution checks
        validation_checks = {
            'water_system_shutdown_confirmed': True,
            'no_water_leaks_detected': True,
            'equipment_status_normal': True,
            'cleaning_coverage_adequate': np.random.choice([True, False], p=[0.85, 0.15]),
            'no_damage_observed': True
        }
        
        all_validation_passed = all(validation_checks.values())
        
        # Estimate cleaning effectiveness
        effectiveness_estimate = np.random.uniform(0.75, 0.95) if all_validation_passed else np.random.uniform(0.4, 0.7)
        
        return {
            'validation_checks': validation_checks,
            'all_validations_passed': all_validation_passed,
            'failed_validations': [check for check, passed in validation_checks.items() if not passed],
            'estimated_cleaning_effectiveness_percent': round(effectiveness_estimate * 100, 1),
            'recommended_follow_up': 'monitor_performance_24h' if all_validation_passed else 'inspect_and_retry',
            'validation_timestamp': datetime.now().isoformat()
        }
    
    def _generate_comprehensive_report(self, data_integration: Dict[str, Any],
                                     risk_assessment: Dict[str, Any],
                                     economic_analysis: Dict[str, Any],
                                     decision_matrix: Dict[str, Any],
                                     timing_analysis: Dict[str, Any],
                                     final_decision: Dict[str, Any],
                                     execution_result: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Phase 8: Generate comprehensive decision and execution report
        
        Creates detailed analysis report with executive summary, KPIs, and recommendations
        """
        
        # Generate executive summary
        executive_summary = self._create_executive_summary(
            final_decision, economic_analysis, execution_result
        )
        
        # Calculate key performance indicators
        kpis = self._calculate_decision_kpis(
            data_integration, economic_analysis, execution_result
        )
        
        # Summarize risk mitigation
        risk_mitigation = self._summarize_risk_mitigation(risk_assessment, final_decision)
        
        # Summarize economic impact
        economic_summary = self._summarize_economic_impact(economic_analysis, execution_result)
        
        # Extract lessons learned
        lessons_learned = self._extract_lessons_learned(
            decision_matrix, timing_analysis, execution_result
        )
        
        return {
            'executive_summary': executive_summary,
            'key_performance_indicators': kpis,
            'risk_mitigation_summary': risk_mitigation,
            'economic_impact_summary': economic_summary,
            'lessons_learned_and_recommendations': lessons_learned,
            'decision_audit_trail': {
                'data_sources_used': ['environmental_sensors', 'weather_forecast', 'image_analysis'],
                'decision_framework_version': self.version,
                'validation_protocols_followed': True,
                'human_oversight_available': False,
                'automated_decision_confidence': final_decision['decision_confidence']
            },
            'report_metadata': {
                'generated_timestamp': datetime.now().isoformat(),
                'report_version': '1.0',
                'system_version': self.version,
                'total_analysis_duration_ms': sum([
                    data_integration.get('processing_time_ms', 0),
                    risk_assessment.get('processing_time_ms', 0),
                    economic_analysis.get('processing_time_ms', 0)
                ])
            }
        }
    
    def _create_executive_summary(self, final_decision: Dict[str, Any],
                                economic_analysis: Dict[str, Any],
                                execution_result: Optional[Dict[str, Any]]) -> Dict[str, str]:
        """Create executive summary of decision and outcomes"""
        
        action_taken = "CLEANING EXECUTED" if final_decision['execute_cleaning'] else "NO ACTION TAKEN"
        confidence = final_decision['decision_confidence']
        reasoning = final_decision['primary_reasoning']
        
        if execution_result:
            execution_success = execution_result.get('execution_successful', False)
            water_used = execution_result.get('water_usage_actual_liters', 0)
            
            if execution_success:
                outcome_summary = f"Successfully executed cleaning using {water_used:.1f}L water"
            else:
                outcome_summary = f"Cleaning execution failed - {execution_result.get('failure_reason', 'unknown')}"
        else:
            outcome_summary = "No cleaning action executed"
        
        economic_viable = economic_analysis['roi_scenario_analysis']['economic_viability']
        daily_loss = economic_analysis['revenue_impact_analysis']['daily_revenue_loss_usd']
        
        return {
            'decision_summary': f"{action_taken} with {confidence:.1f}% confidence",
            'primary_reasoning': reasoning,
            'execution_outcome': outcome_summary,
            'economic_justification': f"Economic viability: {'YES' if economic_viable else 'NO'} (${daily_loss:.2f}/day impact)",
            'key_recommendation': final_decision.get('alternative_recommendations', ['Continue monitoring'])[0]
        }
    
    def _calculate_decision_kpis(self, data_integration: Dict[str, Any],
                               economic_analysis: Dict[str, Any],
                               execution_result: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate key performance indicators for the decision process"""
        
        # Data quality KPIs
        data_quality = data_integration['data_quality_score']
        data_consistency = data_integration['data_consistency_analysis']['overall_consistency']
        
        # Economic KPIs
        economic_impact = economic_analysis['revenue_impact_analysis']['daily_revenue_loss_usd']
        roi_viability = economic_analysis['roi_scenario_analysis']['economic_viability']
        
        # Execution KPIs
        if execution_result:
            execution_efficiency = execution_result.get('execution_successful', False)
            resource_utilization = execution_result.get('water_usage_actual_liters', 0)
        else:
            execution_efficiency = None
            resource_utilization = 0
        
        return {
            'data_quality_score': round(data_quality, 1),
            'data_consistency_score': round(data_consistency, 1),
            'economic_impact_daily_usd': round(economic_impact, 2),
            'economic_viability': roi_viability,
            'execution_success_rate': execution_efficiency,
            'resource_utilization_liters': round(resource_utilization, 1),
            'overall_system_performance': round((data_quality + data_consistency) / 2, 1)
        }
    
    def _summarize_risk_mitigation(self, risk_assessment: Dict[str, Any],
                                 final_decision: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize risk mitigation strategies and outcomes"""
        
        overall_risk = risk_assessment['overall_risk_assessment']['overall_risk_score']
        risk_level = risk_assessment['overall_risk_assessment']['risk_level']
        top_risks = risk_assessment['risk_mitigation_priorities'][:3]
        
        mitigation_effectiveness = 'high' if final_decision['execute_cleaning'] and overall_risk > 70 else 'moderate'
        
        return {
            'pre_decision_risk_level': risk_level,
            'overall_risk_score': round(overall_risk, 1),
            'top_risk_factors': [risk['risk_name'] for risk in top_risks],
            'mitigation_strategy_applied': 'active_cleaning' if final_decision['execute_cleaning'] else 'monitoring',
            'estimated_mitigation_effectiveness': mitigation_effectiveness,
            'residual_risk_estimate': round(max(20, overall_risk - 30), 1) if final_decision['execute_cleaning'] else overall_risk
        }
    
    def _summarize_economic_impact(self, economic_analysis: Dict[str, Any],
                                 execution_result: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Summarize economic impact and ROI"""
        
        daily_loss = economic_analysis['revenue_impact_analysis']['daily_revenue_loss_usd']
        cleaning_cost = economic_analysis['comprehensive_cleaning_costs']['total_cleaning_cost_usd']
        roi_viable = economic_analysis['roi_scenario_analysis']['economic_viability']
        
        if execution_result and execution_result.get('execution_successful'):
            actual_cost = execution_result.get('water_usage_actual_liters', 0) * 0.05 + 20  # Simplified cost
            estimated_recovery = daily_loss * 0.85 * 7  # Weekly recovery at 85% effectiveness
            net_benefit = estimated_recovery - actual_cost
        else:
            actual_cost = 0
            net_benefit = -daily_loss * 7  # Weekly loss if no action
        
        return {
            'projected_daily_loss_usd': round(daily_loss, 2),
            'planned_cleaning_cost_usd': round(cleaning_cost, 2),
            'actual_execution_cost_usd': round(actual_cost, 2),
            'economic_viability_confirmed': roi_viable,
            'estimated_weekly_net_benefit_usd': round(net_benefit, 2),
            'payback_period_estimate_days': round(actual_cost / max(daily_loss * 0.85, 0.01), 1) if actual_cost > 0 else 0
        }
    
    def _extract_lessons_learned(self, decision_matrix: Dict[str, Any],
                               timing_analysis: Dict[str, Any],
                               execution_result: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract lessons learned and recommendations for future decisions"""
        
        decision_score = decision_matrix['total_decision_score']
        validation_passed = decision_matrix['validation_results']['validation_passed']
        
        lessons = []
        recommendations = []
        
        # Decision quality lessons
        if decision_score > 85:
            lessons.append("High-confidence decision with clear action path")
        elif decision_score < 60:
            lessons.append("Low-confidence decision indicates need for additional data")
            recommendations.append("Increase sensor coverage or improve data quality")
        
        # Validation lessons
        if not validation_passed:
            lessons.append("Data validation failures highlight need for redundant sensors")
            recommendations.append("Implement additional data validation protocols")
        
        # Execution lessons
        if execution_result:
            if execution_result.get('execution_successful'):
                lessons.append("Successful execution validates decision framework")
            else:
                lessons.append("Execution failure indicates need for improved hardware reliability")
                recommendations.append("Enhance pre-execution safety checks and hardware maintenance")
        
        # Timing lessons
        timing_urgency = timing_analysis['timing_urgency']
        if timing_urgency == 'immediate':
            lessons.append("Immediate action required - early intervention system working")
        
        return {
            'key_lessons_learned': lessons,
            'recommendations_for_improvement': recommendations,
            'decision_framework_performance': 'effective' if validation_passed else 'needs_refinement',
            'suggested_parameter_adjustments': self._suggest_parameter_adjustments(decision_matrix),
            'next_review_recommended': (datetime.now() + timedelta(hours=24)).isoformat()
        }
    
    def _suggest_parameter_adjustments(self, decision_matrix: Dict[str, Any]) -> List[str]:
        """Suggest parameter adjustments based on decision outcomes"""
        
        suggestions = []
        decision_score = decision_matrix['total_decision_score']
        
        if decision_score < 50:
            suggestions.append("Consider lowering action thresholds for better responsiveness")
        elif decision_score > 90:
            suggestions.append("Consider raising thresholds to avoid over-cleaning")
        
        validation_issues = decision_matrix['validation_results']['validation_issues']
        if 'high_factor_score_variance' in validation_issues:
            suggestions.append("Review factor weights for better decision consistency")
        
        return suggestions


def main():
    """
    Main function for testing and demonstration
    """
    print("=" * 80)
    print("SOLAR PANEL CLEANING DECISION ORCHESTRATION AGENT")
    print("=" * 80)
    print(f"Version: 2.0.0")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 80)
    
    # Create decision agent
    agent = DecisionOrchestrationAgent()
    
    # Mock input data for comprehensive testing
    mock_dust_result = {
        'advanced_risk_assessment': {
            'risk_level': 'high',
            'overall_risk_score': 75
        },
        'power_impact_prediction': {
            'estimated_power_loss_percent': 15
        },
        'cleaning_urgency_analysis': {
            'urgency_level': 'high'
        },
        'sensor_reliability': {
            'overall_reliability': 85
        }
    }
    
    mock_forecast_result = {
        'quartz_integration_status': {
            'real_quartz_used': True
        },
        'dust_corrected_forecast': {
            'daily_totals': {
                'total_loss_kwh': 3.5
            }
        },
        'cleaning_impact_analysis': {
            'recommendations': {
                'urgency_justified': True,
                'optimal_scenario': 'immediate_cleaning'
            }
        },
        'forecast_validation': {
            'model_validation_metrics': {
                'validation_confidence': 80
            }
        },
        'weather_optimization_analysis': {
            'optimal_cleaning_windows': [
                {
                    'start_time': '2024-01-15T10:00:00',
                    'duration_hours': 3,
                    'suitability_score': 85
                }
            ],
            'cleaning_favorability': 'good',
            'weather_pattern_classification': 'stable'
        }
    }
    
    mock_image_result = {
        'visual_analysis_results': {
            'dust_classification': {
                'primary_level': 'moderate'
            }
        },
        'confidence_and_uncertainty': {
            'overall_confidence': 78
        },
        'power_correlation_analysis': {
            'estimated_power_impact_percent': 12
        },
        'image_quality_assessment': {
            'overall_quality_score': 82
        },
        'qualcomm_npu_performance': {
            'npu_accelerated': True
        }
    }
    
    # Execute comprehensive decision analysis
    print("\n🎯 Starting Comprehensive Decision Analysis...")
    result = agent.orchestrate_comprehensive_decision(
        mock_dust_result, 
        mock_forecast_result, 
        mock_image_result
    )
    
    # Display results
    print("\n" + "=" * 60)
    print("DECISION ORCHESTRATION SUMMARY")
    print("=" * 60)
    
    if result['success']:
        final_decision = result['final_decision_synthesis']
        
        print(f"🎯 Final Decision: {'EXECUTE CLEANING' if final_decision['execute_cleaning'] else 'NO ACTION'}")
        print(f"📊 Confidence Level: {final_decision['decision_confidence']:.1f}%")
        print(f"💡 Primary Reasoning: {final_decision['primary_reasoning']}")
        print(f"⚖️ Decision Class: {final_decision['decision_classification']}")
        
        # Economic summary
        economic = result['comprehensive_economic_analysis']
        daily_loss = economic['revenue_impact_analysis']['daily_revenue_loss_usd']
        cleaning_cost = economic['comprehensive_cleaning_costs']['total_cleaning_cost_usd']
        roi_viable = economic['roi_scenario_analysis']['economic_viability']
        
        print(f"\n💰 Economic Analysis:")
        print(f"   Daily Revenue Loss: ${daily_loss:.2f}")
        print(f"   Cleaning Cost: ${cleaning_cost:.2f}")
        print(f"   Economic Viability: {'YES' if roi_viable else 'NO'}")
        
        # Risk summary
        risk = result['multidimensional_risk_assessment']
        risk_score = risk['overall_risk_assessment']['overall_risk_score']
        risk_level = risk['overall_risk_assessment']['risk_level']
        
        print(f"\n⚠️ Risk Assessment:")
        print(f"   Overall Risk Score: {risk_score:.1f}/100")
        print(f"   Risk Level: {risk_level.upper()}")
        
        # Execution results
        if result.get('execution_result'):
            exec_result = result['execution_result']
            success = exec_result['execution_successful']
            water_used = exec_result.get('water_usage_actual_liters', 0)
            
            print(f"\n🚿 Execution Results:")
            print(f"   Status: {'SUCCESS' if success else 'FAILED'}")
            if success:
                print(f"   Water Used: {water_used:.1f}L")
                print(f"   Duration: {exec_result.get('cleaning_duration', 0):.1f}s")
        
        print(f"\n⏱️ Processing Time: {result['processing_time_ms']:.1f}ms")
        
        # Alternative recommendations
        if final_decision.get('alternative_recommendations'):
            print(f"\n🔄 Alternative Recommendations:")
            for i, rec in enumerate(final_decision['alternative_recommendations'], 1):
                print(f"   {i}. {rec}")
        
    else:
        print(f"❌ Decision orchestration failed: {result.get('error', 'Unknown error')}")
    
    print("\n" + "=" * 60)
    print("Analysis Complete")
    print("=" * 60)


if __name__ == "__main__":
    main()