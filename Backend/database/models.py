from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import json

Base = declarative_base()

class PanelStatus(Base):
    __tablename__ = "panel_status"
    
    id = Column(Integer, primary_key=True, index=True)
    panel_id = Column(String(50), index=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    dust_level = Column(Float)
    classification_confidence = Column(Float)
    is_dirty = Column(Boolean, default=False)
    needs_cleaning = Column(Boolean, default=False)
    image_path = Column(String(255))
    
    def to_dict(self):
        return {
            "id": self.id,
            "panel_id": self.panel_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "dust_level": self.dust_level,
            "classification_confidence": self.classification_confidence,
            "is_dirty": self.is_dirty,
            "needs_cleaning": self.needs_cleaning,
            "image_path": self.image_path
        }

class CleaningAction(Base):
    __tablename__ = "cleaning_actions"
    
    id = Column(Integer, primary_key=True, index=True)
    panel_id = Column(String(50), index=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    action_type = Column(String(20), nullable=False)  # "spray", "schedule", "skip"
    water_volume = Column(Float)
    duration = Column(Float)
    success = Column(Boolean, default=False)
    error_message = Column(Text)
    
    def to_dict(self):
        return {
            "id": self.id,
            "panel_id": self.panel_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "action_type": self.action_type,
            "water_volume": self.water_volume,
            "duration": self.duration,
            "success": self.success,
            "error_message": self.error_message
        }

class SystemDecision(Base):
    __tablename__ = "system_decisions"
    
    id = Column(Integer, primary_key=True, index=True)
    decision_id = Column(String(50), unique=True, index=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    decision_data = Column(Text, nullable=False)  # JSON string
    panels_involved = Column(String(500))  # Comma-separated panel IDs
    action_taken = Column(String(50))
    execution_status = Column(String(20), default="pending")  # pending, completed, failed
    
    def to_dict(self):
        return {
            "id": self.id,
            "decision_id": self.decision_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "decision_data": json.loads(self.decision_data) if self.decision_data else {},
            "panels_involved": self.panels_involved.split(",") if self.panels_involved else [],
            "action_taken": self.action_taken,
            "execution_status": self.execution_status
        }

class SystemLog(Base):
    __tablename__ = "system_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    level = Column(String(10), nullable=False)  # INFO, WARNING, ERROR
    component = Column(String(50), nullable=False)  # agent name or system component
    message = Column(Text, nullable=False)
    details = Column(Text)  # Additional JSON data
    
    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "level": self.level,
            "component": self.component,
            "message": self.message,
            "details": json.loads(self.details) if self.details else {}
        }