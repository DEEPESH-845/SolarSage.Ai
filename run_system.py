#!/usr/bin/env python3
"""Start the FastAPI backend and the Flask frontend together.

The frontend does not need the backend to be running — it calls the same
service layer in-process. The backend is started here so the REST API and its
/docs page are available for hardware and external clients.
"""

import socket
import subprocess
import sys
import time

from Backend.config.settings import settings

COMMANDS = [
    ("FastAPI backend", [sys.executable, "-m", "uvicorn", "Backend.api.main:app",
                         "--host", settings.api_host, "--port", str(settings.api_port)]),
    ("Flask frontend", [sys.executable, "Frontend/app.py"]),
]


def port_is_free(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(("127.0.0.1", port))
            return True
        except OSError:
            return False


def check_ports():
    """macOS AirPlay Receiver squats on port 5000 — fail with a usable message."""
    busy = [(name, port) for name, port in
            (("API_PORT", settings.api_port), ("FRONTEND_PORT", settings.frontend_port))
            if not port_is_free(port)]
    for var, port in busy:
        print(f"❌ Port {port} is already in use. Free it, or set {var} to another port")
        print(f"   (e.g. {var}={port + 1} python run_system.py).")
        if port == 5000 and sys.platform == "darwin":
            print("   On macOS this is usually AirPlay Receiver: "
                  "System Settings → General → AirDrop & Handoff.")
    return not busy


def main():
    print("🌞 Solar Panel Cleaning System")
    print("=" * 60)
    print(f"🔧 Backend (FastAPI):  http://localhost:{settings.api_port}")
    print(f"🌐 Frontend (Flask):   http://localhost:{settings.frontend_port}")
    print(f"📚 API Documentation:  http://localhost:{settings.api_port}/docs")
    print("=" * 60)
    print("Press Ctrl+C to stop")

    if not check_ports():
        return 1

    processes = []
    try:
        for name, command in COMMANDS:
            print(f"▶️  Starting {name}...")
            processes.append(subprocess.Popen(command))

        # Exit as soon as either process dies, so a crashed server is visible.
        while True:
            for process in processes:
                code = process.poll()
                if code is not None:
                    print(f"\n❌ A server exited with code {code}")
                    return code
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n🛑 Stopping...")
        return 0
    finally:
        for process in processes:
            if process.poll() is None:
                process.terminate()
        for process in processes:
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
        print("✅ Shutdown complete")


if __name__ == "__main__":
    sys.exit(main())
