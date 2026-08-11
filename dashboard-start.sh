#!/bin/bash
# Start the DatingApp dev control dashboard
# Dashboard: http://127.0.0.1:9100

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

VENV_PYTHON="$SCRIPT_DIR/.venv/bin/python"

if [ ! -f "$VENV_PYTHON" ]; then
    echo "❌ Virtual environment not found. Run: python3 -m venv .venv && .venv/bin/pip install nicegui httpx"
    exit 1
fi

# Check if already running
if pgrep -f "dev_dashboard.py" > /dev/null; then
    echo "⚠️  Dashboard already running at http://127.0.0.1:9100"
    echo "   Stop first with: ./dashboard-stop.sh"
    exit 0
fi

echo "🚀 Starting dev dashboard..."
nohup "$VENV_PYTHON" dev_dashboard.py > /tmp/dashboard.log 2>&1 &
PID=$!
sleep 2

if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:9100 | grep -q 200; then
    echo "✅ Dashboard running at http://127.0.0.1:9100 (PID $PID)"
else
    echo "⚠️  Dashboard started (PID $PID) but not responding yet. Check /tmp/dashboard.log"
fi
