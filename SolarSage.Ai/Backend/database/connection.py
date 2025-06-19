import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.settings import settings
import os

# Create data directory if it doesn't exist
os.makedirs("data", exist_ok=True)

# SQLite database URL
SQLITE_DATABASE_URL = f"sqlite:///{settings.sqlite_database_path}"

engine = create_engine(
    SQLITE_DATABASE_URL, 
    connect_args={"check_same_thread": False}  # SQLite specific
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    from database.models import Base
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_database():
    """Initialize database with tables"""
    create_tables()
    print(f"✅ SQLite database initialized at {settings.sqlite_database_path}")

def test_database_connection():
    """Test database connection"""
    try:
        # Test with raw SQLite3
        conn = sqlite3.connect(settings.sqlite_database_path)
        cursor = conn.cursor()
        cursor.execute("SELECT sqlite_version();")
        version = cursor.fetchone()
        conn.close()
        print(f"✅ SQLite connection successful. Version: {version[0]}")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    test_database_connection()
    init_database() 