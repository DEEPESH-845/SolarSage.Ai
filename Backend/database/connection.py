import sqlite3

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from Backend.config.settings import settings

DB_PATH = settings.db_path
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(
    f"sqlite:///{DB_PATH}",
    connect_args={"check_same_thread": False},  # SQLite specific
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    from Backend.database.models import Base

    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")


def get_db():
    """FastAPI dependency: yields a session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_database():
    """Initialize database with tables"""
    create_tables()
    print(f"✅ SQLite database initialized at {DB_PATH}")


def test_database_connection():
    """Test database connection"""
    try:
        conn = sqlite3.connect(DB_PATH)
        version = conn.execute("SELECT sqlite_version();").fetchone()
        conn.close()
        print(f"✅ SQLite connection successful. Version: {version[0]}")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


if __name__ == "__main__":
    test_database_connection()
    init_database()
