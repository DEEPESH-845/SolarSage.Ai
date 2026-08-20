#!/usr/bin/env python3
"""Start the FastAPI backend and the Next.js console together.

Two processes, because they are two deployments: the API serves JSON on
API_PORT, and the console renders pages on 3000 by reading that API from its
server. Set API_URL in web/.env.local if the API is not on the default port.
"""

import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path

from Backend.config.settings import settings

WEB_DIR = Path(__file__).resolve().parent / "web"
WEB_PORT = 3000


def commands():
    npm = shutil.which("npm")
    if npm is None:
        raise SystemExit("❌ npm was not found. Install Node.js 20+ to run the console.")

    return [
        ("FastAPI backend", [sys.executable, "-m", "uvicorn", "Backend.api.main:app",
                             "--host", settings.api_host, "--port", str(settings.api_port)], None),
        ("Next.js console", [npm, "run", "dev"], WEB_DIR),
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
    busy = [(name, port) for name, port in
            (("API_PORT", settings.api_port), ("the console", WEB_PORT))
            if not port_is_free(port)]
    for var, port in busy:
        print(f"❌ Port {port} is already in use. Free it, or set {var} to another port.")
    return not busy


def check_dependencies():
    if not (WEB_DIR / "node_modules").is_dir():
        print("❌ The console's dependencies are not installed.")
        print(f"   Run: cd {WEB_DIR.name} && npm install")
        return False
    return True


def main():
    print("🌞 Solar Panel Cleaning System")
    print("=" * 60)
    print(f"🔧 Backend (FastAPI):  http://localhost:{settings.api_port}")
    print(f"🌐 Console (Next.js):  http://localhost:{WEB_PORT}")
    print(f"📚 API documentation:  http://localhost:{settings.api_port}/docs")
    print("=" * 60)
    print("Press Ctrl+C to stop")

    if not check_dependencies() or not check_ports():
        return 1

    processes = []
    try:
        for name, command, cwd in commands():
            print(f"▶️  Starting {name}...")
            processes.append(subprocess.Popen(command, cwd=cwd))

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
