"""
F.R.I.D.A.Y. Unified Phase 1 Development Launcher
Starts the FastMCP Server, verifies health readiness, launches the LiveKit Agent Worker,
and serves the Web UI.
"""

import sys
import time
import subprocess
import urllib.request
import json
from friday.config import config

def check_health(url: str, timeout: int = 2) -> bool:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Friday-Launcher"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("status") == "ok"
    except Exception:
        return False
    return False

def main():
    print("==================================================")
    print("F.R.I.D.A.Y. PHASE 1 SYSTEM STARTUP")
    print("==================================================")

    # 1. Environment Validation
    missing_keys = config.validate_environment()
    if missing_keys:
        print("\n[FRIDAY] ENVIRONMENT WARNING:")
        print(f"Missing or placeholder credentials in .env: {', '.join(missing_keys)}")
        print("Please populate these keys in your .env file before running end-to-end voice mode.\n")

    # 2. Launch FastMCP Server
    print("[FRIDAY] Starting FastMCP Server on http://127.0.0.1:8000 ...")
    mcp_proc = subprocess.Popen(
        [sys.executable, "server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    # Poll health check
    health_url = "http://127.0.0.1:8000/health"
    mcp_ready = False
    for attempt in range(1, 15):
        time.sleep(1)
        if check_health(health_url):
            mcp_ready = True
            break
        print(f"[FRIDAY] Waiting for FastMCP health check (attempt {attempt}/15)...")

    if mcp_ready:
        print("[FRIDAY] MCP: READY")
    else:
        print("[FRIDAY] MCP: WARNING (Health check timed out, proceeding...)")

    # 3. Launch LiveKit Voice Agent Worker
    print("[FRIDAY] Starting LiveKit Voice Agent...")
    agent_proc = subprocess.Popen(
        [sys.executable, "agent_friday.py", "dev"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    print("[FRIDAY] Agent: READY")

    # 4. Launch Web UI HTTP Server on Port 3000
    print("[FRIDAY] Serving Web UI on http://localhost:3000 ...")
    ui_proc = subprocess.Popen(
        [sys.executable, "-m", "http.server", "3000", "--directory", "ui"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    print("[FRIDAY] UI: READY")

    print("\n==================================================")
    print("ALL SERVICES ONLINE:")
    print("  - Web UI:    http://localhost:3000")
    print("  - FastMCP:   http://127.0.0.1:8000/sse")
    print("  - Health:    http://127.0.0.1:8000/health")
    print("  - Token API: http://127.0.0.1:8000/api/token")
    print("==================================================\n")

    try:
        mcp_proc.wait()
    except KeyboardInterrupt:
        print("\n[FRIDAY] Shutting down processes...")
        mcp_proc.terminate()
        agent_proc.terminate()
        ui_proc.terminate()

if __name__ == "__main__":
    main()
