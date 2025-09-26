#!/bin/bash
# DatingApp Development Session Startup

echo "🌅 Starting DatingApp Development Session"

# Create tmux session with all services
tmux new-session -d -s "datingapp-dev" -c "/home/m/development/DatingApp"

# Window 1: Services monitoring
tmux rename-window "Services"
tmux send-keys "export DEMO_MODE=true && ./dev-status.sh" C-m

# Window 2: API testing
tmux new-window -t "datingapp-dev" -n "API-Tests" -c "/home/m/development/DatingApp"
tmux send-keys "source /home/m/development/mobile-apps/flutter/dejtingapp/.venv/bin/activate" C-m

# Window 3: Flutter development  
tmux new-window -t "datingapp-dev" -n "Flutter" -c "/home/m/development/mobile-apps/flutter/dejtingapp"
tmux send-keys "source .venv/bin/activate" C-m

# Window 4: Logs monitoring
tmux new-window -t "datingapp-dev" -n "Logs" -c "/home/m/development/DatingApp"
tmux send-keys "tail -f auth-service/test_output.log" C-m

# Select first window
tmux select-window -t "datingapp-dev:Services"

echo "✅ Tmux session 'datingapp-dev' created"
echo "📱 Attach with: tmux attach-session -t datingapp-dev"
echo "🔄 Detach with: Ctrl+b, then d"
