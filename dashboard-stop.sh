#!/bin/bash
# Stop the DatingApp dev control dashboard

set -euo pipefail

PIDS=$(pgrep -f "dev_dashboard.py" 2>/dev/null || true)

if [ -z "$PIDS" ]; then
    echo "ℹ️  Dashboard is not running"
    exit 0
fi

echo "🛑 Stopping dashboard (PIDs: $PIDS)..."
pkill -f "dev_dashboard.py"
sleep 1

if pgrep -f "dev_dashboard.py" > /dev/null 2>&1; then
    echo "⚠️  Force killing..."
    pkill -9 -f "dev_dashboard.py"
fi

echo "✅ Dashboard stopped"
