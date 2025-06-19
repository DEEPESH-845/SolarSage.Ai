"""
Demo script for Solar Panel Optimization System
"""

import sys
from pathlib import Path
import json
from datetime import datetime

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from config.logging_config import setup_logging
from main import SolarPanelOptimizationSystem

def create_demo_data():
    """Create demo data for testing"""
    demo_panels = [
        {
            "panel_id": "DEMO_SP001",
            "image_path": "data/input/demo_panel_dirty.jpg",
            "latitude": 28.6139,   # Delhi, India
            "longitude": 77.2090,
            "installation_date": "2023-01-15",
            "panel_type": "monocrystalline",
            "rated_power": 400  # watts
        },
        {
            "panel_id": "DEMO_SP002", 
            "image_path": "data/input/demo_panel_clean.jpg",
            "latitude": 19.0760,   # Mumbai, India
            "longitude": 72.8777,
            "installation_date": "2023-03-20",
            "panel_type": "polycrystalline", 
            "rated_power": 350  # watts
        },
        {
            "panel_id": "DEMO_SP003",
            "image_path": "data/input/demo_panel_moderate.jpg", 
            "latitude": 12.9716,   # Bangalore, India
            "longitude": 77.5946,
            "installation_date": "2022-11-10",
            "panel_type": "monocrystalline",
            "rated_power": 450  # watts
        }
    ]
    
    return demo_panels

def run_demo():
    """Run the demo"""
    print("="*60)
    print("SOLAR PANEL OPTIMIZATION SYSTEM - DEMO")
    print("Qualcomm AI Hackathon")
    print("="*60)
    
    # Setup logging
    setup_logging()
    
    # Create demo data
    demo_panels = create_demo_data()
    
    print(f"\nDemo will process {len(demo_panels)} solar panels:")
    for panel in demo_panels:
        print(f"  - {panel['panel_id']}: {panel['panel_type']} panel at ({panel['latitude']}, {panel['longitude']})")
    
    print("\nStarting demo processing...")
    
    # Initialize system
    system = SolarPanelOptimizationSystem()
    
    # Process panels
    results = system.process_batch(demo_panels)
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"demo_results_{timestamp}.json"
    output_path = system.save_results(results, output_file)
    
    # Display summary
    print("\n" + "="*60)
    print("DEMO RESULTS SUMMARY")
    print("="*60)
    
    successful = [r for r in results if r.get("workflow_status") == "completed"]
    action_required = [r for r in successful if r.get("final_recommendation", {}).get("action_required", False)]
    
    print(f"Total panels processed: {len(results)}")
    print(f"Successfully processed: {len(successful)}")
    print(f"Panels requiring action: {len(action_required)}")
    print(f"Panels with no action needed: {len(successful) - len(action_required)}")
    
    if output_path:
        print(f"\nDetailed results saved to: {output_path}")
    
    # Show individual panel results
    print("\nIndividual Panel Results:")
    print("-" * 40)
    
    for result in successful:
        panel_id = result.get("panel_id", "Unknown")
        recommendation = result.get("final_recommendation", {})
        
        action_status = "ACTION REQUIRED" if recommendation.get("action_required") else "NO ACTION"
        urgency = recommendation.get("urgency_level", "unknown")
        reason = recommendation.get("reason", "No reason provided")
        
        print(f"\n{panel_id}:")
        print(f"  Status: {action_status}")
        print(f"  Urgency: {urgency.upper()}")
        print(f"  Reason: {reason}")
    
    print("\n" + "="*60)
    print("Demo completed successfully!")
    print("="*60)

if __name__ == "__main__":
    run_demo()