from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
from datetime import datetime
import os
import sys
from sqlalchemy.orm import Session

# Add parent directory to path to import agents
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.image_classifier import ImageClassifierAgent
from database.connection import get_db, init_database
from database.models import PanelStatus, CleaningAction, SystemDecision, SystemLog

app = FastAPI(title="Solar Panel Cleaning System", version="1.0.0")

# Add CORS middleware for Flask frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5000", "http://127.0.0.1:5000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database and classifier
init_database()
classifier = ImageClassifierAgent()

class PanelRequest(BaseModel):
    panel_id: str = "panel_01"

@app.get("/")
async def root():
    return {
        "message": "🌞 Solar Panel Cleaning System Running!",
        "status": "online",
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "water_level": 85,
        "camera_status": "online",
        "system_temperature": "25°C"
    }

@app.post("/analyze")
async def analyze_panel(request: PanelRequest, db: Session = Depends(get_db)):
    """Analyze a solar panel for dust levels"""
    try:
        image_path = f"data/images/{request.panel_id}_test.jpg"
        
        # Classify dust level
        result = classifier.classify_dust_level(image_path)
        
        # Check if classification failed
        if "error" in result:
            return {"error": f"Image classification failed: {result['error']}", "panel_id": request.panel_id}
          result["panel_id"] = request.panel_id
        result["timestamp"] = datetime.now().isoformat()
        
        # Make decision based on dust level
        if result["dust_level"] > 0.6:
            decision = "spray_now"
            action = "🚿 Cleaning initiated - High dust detected"
            spray_duration = 8
        elif result["dust_level"] > 0.3:
            decision = "schedule_cleaning"
            action = "⏰ Cleaning scheduled - Moderate dust detected"
            spray_duration = 5
        else:
            decision = "no_action"
            action = "✅ Panel is clean - No action needed"
            spray_duration = 0
        
        # Save panel status to database
        panel_status = PanelStatus(
            panel_id=request.panel_id,
            dust_level=result["dust_level"],
            classification_confidence=result["confidence"],
            is_dirty=result["dust_level"] > 0.3,
            needs_cleaning=result["dust_level"] > 0.6,
            image_path=image_path
        )
        db.add(panel_status)
        
        # Create comprehensive decision
        decision_data = {
            "decision_id": f"decision_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "panel_id": request.panel_id,
            "dust_level": result["dust_level"],
            "status": result["status"],
            "confidence": result["confidence"],
            "decision": decision,
            "action": action,
            "spray_duration": spray_duration,
            "water_volume": spray_duration * 20 if spray_duration > 0 else 0,
            "timestamp": result["timestamp"]
        }
        
        # Save decision to database
        system_decision = SystemDecision(
            decision_id=decision_data["decision_id"],
            decision_data=json.dumps(decision_data),
            panels_involved=request.panel_id,
            action_taken=decision,
            execution_status="completed"
        )
        db.add(system_decision)
        
        # Save decision to file (for backward compatibility)
        os.makedirs("data/decisions", exist_ok=True)
        with open("data/decisions/latest_decision.json", "w") as f:
            json.dump(decision_data, f, indent=2)
          db.commit()
        return decision_data
        
    except Exception as e:
        db.rollback()
        return {"error": f"Analysis failed: {str(e)}", "panel_id": request.panel_id}

@app.get("/latest-decision")
async def get_latest_decision(db: Session = Depends(get_db)):
    """Get the latest cleaning decision"""
    try:
        # Get from database first
        latest = db.query(SystemDecision).order_by(SystemDecision.timestamp.desc()).first()
        if latest:
            return json.loads(latest.decision_data)
        
        # Fallback to file
        with open("data/decisions/latest_decision.json", "r") as f:
            return json.load(f)
    except:
        return {"message": "No decisions made yet. Try /analyze first!"}

@app.post("/spray")
async def spray_panel(request: PanelRequest, db: Session = Depends(get_db)):
    """Simulate spraying water on solar panel"""
    try:
        spray_result = {
            "panel_id": request.panel_id,
            "action": "🚿 spray_completed",
            "duration_seconds": 5,
            "water_used_ml": 100,
            "pressure": "optimal",
            "timestamp": datetime.now().isoformat(),
            "next_check": "in 24 hours"
        }
        
        # Save cleaning action to database
        cleaning_action = CleaningAction(
            panel_id=request.panel_id,
            action_type="spray",
            water_volume=100,
            duration=5.0,
            success=True
        )
        db.add(cleaning_action)
        db.commit()
        
        return spray_result
        
    except Exception as e:
        db.rollback()
        return {"error": f"Spray operation failed: {str(e)}", "panel_id": request.panel_id}

@app.get("/panels")
async def list_panels(db: Session = Depends(get_db)):
    """Get list of all panels and their status"""
    try:
        # Get latest status for each panel from database
        panels_data = []
        panel_ids = ["panel_01", "panel_02", "panel_03", "panel_04"]
    
    for panel_id in panel_ids:
        latest_status = db.query(PanelStatus).filter(
            PanelStatus.panel_id == panel_id
        ).order_by(PanelStatus.timestamp.desc()).first()
        
        if latest_status:
            if latest_status.needs_cleaning:
                status = "needs_cleaning"
            elif latest_status.is_dirty:
                status = "moderate_dust"
            else:
                status = "clean"
            last_cleaned = latest_status.timestamp.strftime("%Y-%m-%d")
        else:
            status = "unknown"
            last_cleaned = "Never"
              panels_data.append({
                "id": panel_id,
                "status": status,
                "last_cleaned": last_cleaned
            })
        
        return {
            "total_panels": len(panels_data),
            "panels": panels_data
        }
        
    except Exception as e:
        return {"error": f"Failed to retrieve panels: {str(e)}", "total_panels": 0, "panels": []}

@app.get("/panels/{panel_id}/history")
async def get_panel_history(panel_id: str, db: Session = Depends(get_db)):
    """Get historical data for a specific panel"""
    status_history = db.query(PanelStatus).filter(
        PanelStatus.panel_id == panel_id
    ).order_by(PanelStatus.timestamp.desc()).limit(10).all()
    
    cleaning_history = db.query(CleaningAction).filter(
        CleaningAction.panel_id == panel_id
    ).order_by(CleaningAction.timestamp.desc()).limit(10).all()
    
    return {
        "panel_id": panel_id,
        "status_history": [status.to_dict() for status in status_history],
        "cleaning_history": [action.to_dict() for action in cleaning_history]
    }

@app.get("/system/logs")
async def get_system_logs(db: Session = Depends(get_db)):
    """Get recent system logs"""
    logs = db.query(SystemLog).order_by(SystemLog.timestamp.desc()).limit(50).all()
    return [log.to_dict() for log in logs]

@app.get("/system/stats")
async def get_system_stats(db: Session = Depends(get_db)):
    """Get system statistics"""
    total_panels = 4
    total_cleanings = db.query(CleaningAction).count()
    total_analyses = db.query(PanelStatus).count()
    
    return {
        "total_panels": total_panels,
        "total_cleanings": total_cleanings,
        "total_analyses": total_analyses,
        "system_uptime": "24 hours",
        "water_used_total": total_cleanings * 100,  # ml
        "avg_dust_level": 0.35
    }