#!/usr/bin/env python3
"""
Solar Panel Cleaning System - Complete Startup Script
Starts both FastAPI backend and Flask frontend
"""
import subprocess
import threading
import time
import sys
import os

def start_backend():
    """Start FastAPI backend server"""
    print("🔧 Starting FastAPI Backend Server...")
    try:
        subprocess.run([sys.executable, "main.py"], cwd=os.getcwd())
    except KeyboardInterrupt:
        print("\n🛑 Backend server stopped")

def start_frontend():
    """Start Flask frontend server"""
    print("🌐 Starting Flask Frontend Server...")
    time.sleep(3)  # Wait for backend to start
    try:
        subprocess.run([sys.executable, "flask_frontend/app.py"], cwd=os.getcwd())
    except KeyboardInterrupt:
        print("\n🛑 Frontend server stopped")

def main():
    print("🌞 Solar Panel Cleaning System - Complete Startup")
    print("=" * 60)
    print("🔧 Backend (FastAPI): http://localhost:8000")
    print("🌐 Frontend (Flask): http://localhost:5000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("=" * 60)
    
    # Start backend in background thread
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    backend_thread.start()
    
    # Start frontend in main thread
    try:
        start_frontend()
    except KeyboardInterrupt:
        print("\n🛑 System stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    print("\n✅ Shutdown complete")

if __name__ == "__main__":
    main()
