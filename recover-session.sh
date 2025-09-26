#!/bin/bash
# Session Recovery Script

echo "🔄 Recovering DatingApp session..."

# Check for latest checkpoint
if [ -L "/home/m/development/DatingApp/checkpoints/latest" ]; then
    LATEST_CHECKPOINT=$(readlink "/home/m/development/DatingApp/checkpoints/latest")
    echo "📂 Found checkpoint: $LATEST_CHECKPOINT"
    
    echo "📋 Previous session info:"
    if [ -f "$LATEST_CHECKPOINT/README.md" ]; then
        cat "$LATEST_CHECKPOINT/README.md"
    fi
    
    echo ""
    echo "🔧 Previous environment:"
    if [ -f "$LATEST_CHECKPOINT/environment.txt" ]; then
        grep "DEMO_MODE" "$LATEST_CHECKPOINT/environment.txt" || echo "DEMO_MODE was not set"
    fi
    
    echo ""
    echo "⚙️ Previous service status:"
    if [ -f "$LATEST_CHECKPOINT/service_status.txt" ]; then
        head -20 "$LATEST_CHECKPOINT/service_status.txt"
    fi
fi

# Restore to DatingApp directory
cd /home/m/development/DatingApp

# Set demo mode
export DEMO_MODE=true
echo "✅ Set DEMO_MODE=true"

# Check if tmux session exists
if tmux has-session -t "datingapp-dev" 2>/dev/null; then
    echo "📱 Found existing tmux session 'datingapp-dev'"
    echo "🔗 Attach with: tmux attach-session -t datingapp-dev"
else
    echo "🆕 No existing tmux session found"
    echo "🚀 Create new session with: ./start-dev-session.sh"
fi

# Check current service status
echo ""
echo "🔍 Current service status:"
./dev-status.sh

# Check for Python virtual environment
if [ -d "/home/m/development/mobile-apps/flutter/dejtingapp/.venv" ]; then
    echo "🐍 Python virtual environment found"
    echo "🔗 Activate with: cd /home/m/development/mobile-apps/flutter/dejtingapp && source .venv/bin/activate"
else
    echo "⚠️ Python virtual environment not found"
fi

echo ""
echo "🎯 Quick actions:"
echo "  ./start-dev-session.sh    - Start new tmux session"
echo "  ./dev-restart.sh          - Restart all services"
echo "  ./quick_api_test.py       - Test API endpoints"
echo "  ./create-checkpoint.sh    - Save current state"

# Check if we should auto-start services
echo ""
read -p "🚀 Start services automatically? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Starting services..."
    ./dev-start.sh
fi
