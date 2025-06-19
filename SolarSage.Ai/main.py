#!/usr/bin/env python3
"""
Solar Panel Cleaning System - Main Entry Point
Enhanced for Flask Frontend Integration
"""
import threading
import time
import uvicorn
from api.main import app
from database.connection import init_database

def start_api_server():
    """Start FastAPI server"""
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

def main():
    print("🌞 Starting Solar Panel Cleaning System...")
    print("=" * 50)
    
    # Initialize database first
    print("🗃️  Initializing database...")
    init_database()
    
    # Start API server in background
    print("🔧 Starting FastAPI backend server...")
    api_thread = threading.Thread(target=start_api_server, daemon=True)
    api_thread.start()
    
    print("✅ System started!")
    print("🌐 API Server: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("🎨 Flask Frontend: Start with 'python flask_frontend/app.py'")
    print("🚀 Or use 'python run_system.py' to start everything")
    print("=" * 50)
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 System stopped")

if __name__ == "__main__":
    main()