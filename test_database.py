from database.connection import test_database_connection, init_database
from database.models import PanelStatus, CleaningAction, SystemDecision
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from config.settings import settings
import os

def test_full_database():
    print("🧪 Testing Solar Panel Database Setup")
    print("=" * 50)
    
    # Test 1: Database connection
    print("1. Testing database connection...")
    if test_database_connection():
        print("   ✅ Connection successful")
    else:
        print("   ❌ Connection failed")
        return False
    
    # Test 2: Initialize database
    print("\n2. Initializing database...")
    init_database()
    
    # Test 3: Test CRUD operations
    print("\n3. Testing CRUD operations...")
    try:
        engine = create_engine(f"sqlite:///{settings.sqlite_database_path}")
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        # Create test panel status
        test_panel = PanelStatus(
            panel_id="panel_test_001",
            dust_level=0.65,
            classification_confidence=0.87,
            is_dirty=True,
            needs_cleaning=True
        )
        db.add(test_panel)
        db.commit()
        print("   ✅ Created test panel status")
        
        # Read test data
        retrieved_panel = db.query(PanelStatus).filter(
            PanelStatus.panel_id == "panel_test_001"
        ).first()
        
        if retrieved_panel:
            print(f"   ✅ Retrieved panel: {retrieved_panel.panel_id}")
            print(f"      Dust level: {retrieved_panel.dust_level}")
            print(f"      Needs cleaning: {retrieved_panel.needs_cleaning}")
        
        # Create test cleaning action
        test_action = CleaningAction(
            panel_id="panel_test_001",
            action_type="spray",
            water_volume=2.5,
            duration=3.0,
            success=True
        )
        db.add(test_action)
        db.commit()
        print("   ✅ Created test cleaning action")
        
        # Clean up test data
        db.delete(retrieved_panel)
        db.delete(test_action)
        db.commit()
        db.close()
        print("   ✅ Cleaned up test data")
        
    except Exception as e:
        print(f"   ❌ CRUD test failed: {e}")
        return False
    
    print("\n🎉 All database tests passed!")
    print(f"📁 Database file location: {settings.sqlite_database_path}")
    
    # Show database file size
    if os.path.exists(settings.sqlite_database_path):
        size = os.path.getsize(settings.sqlite_database_path)
        print(f"📊 Database size: {size} bytes")
    
    return True

if __name__ == "__main__":
    test_full_database()