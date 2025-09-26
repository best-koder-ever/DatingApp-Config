# 🔄 Session Persistence Guide for DatingApp Development

## 📋 **Quick Session Recovery Commands**

### Immediate Session Backup
```bash
# Save current environment state
cd /home/m/development/DatingApp
echo "# Session State - $(date)" > session_state.sh
echo "export DEMO_MODE=true" >> session_state.sh
echo "cd /home/m/development/DatingApp" >> session_state.sh
echo "# Last working directory: $(pwd)" >> session_state.sh
```

### Restore Session Quickly
```bash
# Restore saved session
cd /home/m/development/DatingApp
source session_state.sh
./dev-status.sh
```

## 🖥️ **Persistent Terminal Sessions with tmux**

### Start Development Session
```bash
# Create named tmux session for DatingApp
tmux new-session -d -s "datingapp-dev"

# Split into multiple panes for different services
tmux split-window -h
tmux split-window -v
tmux select-pane -t 0
tmux split-window -v

# Label windows
tmux rename-window "DatingApp-Dev"
```

### Tmux Session Management
```bash
# List all sessions
tmux list-sessions

# Attach to existing session
tmux attach-session -t "datingapp-dev"

# Detach from session (keeps it running)
# Press: Ctrl+b, then d

# Kill session when done
tmux kill-session -t "datingapp-dev"
```

### Automated tmux Setup Script
```bash
#!/bin/bash
# File: /home/m/development/DatingApp/start-dev-session.sh

# Create tmux session with all services
tmux new-session -d -s "datingapp-dev" -c "/home/m/development/DatingApp"

# Window 1: Services monitoring
tmux rename-window "Services"
tmux send-keys "cd /home/m/development/DatingApp && ./dev-status.sh" C-m

# Window 2: API testing
tmux new-window -t "datingapp-dev" -n "API-Tests" -c "/home/m/development/DatingApp"
tmux send-keys "source /home/m/development/mobile-apps/flutter/dejtingapp/.venv/bin/activate" C-m

# Window 3: Flutter development
tmux new-window -t "datingapp-dev" -n "Flutter" -c "/home/m/development/mobile-apps/flutter/dejtingapp"
tmux send-keys "source .venv/bin/activate" C-m

# Window 4: Logs monitoring
tmux new-window -t "datingapp-dev" -n "Logs" -c "/home/m/development/DatingApp"
tmux send-keys "tail -f auth-service/test_output.log" C-m

# Attach to session
tmux attach-session -t "datingapp-dev"
```

## 💾 **VS Code Workspace Persistence**

### Save Workspace State
Your `.code-workspace` file already saves:
- ✅ Open folders and files
- ✅ Terminal sessions
- ✅ Extension settings
- ✅ Debug configurations

### Auto-save Settings
```json
// Add to VS Code settings.json
{
  "files.autoSave": "afterDelay",
  "files.autoSaveDelay": 1000,
  "workbench.editor.restoreViewState": true,
  "terminal.integrated.persistentSessionReviveProcess": "onRestart"
}
```

## 🗂️ **Project State Snapshots**

### Create Development Checkpoint
```bash
#!/bin/bash
# File: /home/m/development/DatingApp/create-checkpoint.sh

CHECKPOINT_DIR="/home/m/development/DatingApp/checkpoints/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$CHECKPOINT_DIR"

# Save current state
echo "Creating checkpoint at $CHECKPOINT_DIR"

# Save environment variables
env | grep -E "(DEMO_MODE|DOTNET|PATH)" > "$CHECKPOINT_DIR/environment.txt"

# Save running processes
ps aux | grep -E "(dotnet|flutter|tmux)" > "$CHECKPOINT_DIR/processes.txt"

# Save service status
./dev-status.sh > "$CHECKPOINT_DIR/service_status.txt" 2>&1

# Save git status for all repos
echo "=== DatingApp Main ===" > "$CHECKPOINT_DIR/git_status.txt"
git status >> "$CHECKPOINT_DIR/git_status.txt" 2>&1

echo "=== Auth Service ===" >> "$CHECKPOINT_DIR/git_status.txt"
cd auth-service && git status >> "$CHECKPOINT_DIR/git_status.txt" 2>&1

echo "=== Flutter App ===" >> "$CHECKPOINT_DIR/git_status.txt"
cd /home/m/development/mobile-apps/flutter/dejtingapp && git status >> "$CHECKPOINT_DIR/git_status.txt" 2>&1

echo "Checkpoint saved to: $CHECKPOINT_DIR"
```

### Restore from Checkpoint
```bash
#!/bin/bash
# File: /home/m/development/DatingApp/restore-checkpoint.sh

LATEST_CHECKPOINT=$(ls -t /home/m/development/DatingApp/checkpoints/ | head -1)
CHECKPOINT_DIR="/home/m/development/DatingApp/checkpoints/$LATEST_CHECKPOINT"

echo "Restoring from checkpoint: $LATEST_CHECKPOINT"

# Restore environment
echo "Environment variables to restore:"
cat "$CHECKPOINT_DIR/environment.txt"

echo "Previous service status:"
cat "$CHECKPOINT_DIR/service_status.txt"

echo "Git status at checkpoint:"
cat "$CHECKPOINT_DIR/git_status.txt"
```

## 🚀 **Automated Session Startup**

### Morning Startup Script
```bash
#!/bin/bash
# File: /home/m/development/DatingApp/morning-startup.sh

echo "🌅 Starting DatingApp Development Session"

# 1. Start tmux session
./start-dev-session.sh

# 2. Start all services
export DEMO_MODE=true
./dev-start.sh

# 3. Wait for services to be ready
sleep 10

# 4. Run quick health check
./dev-status.sh

# 5. Open VS Code with workspace
code DatingApp.code-workspace

echo "✅ Development environment ready!"
echo "📱 Tmux session: tmux attach-session -t datingapp-dev"
echo "🔍 Service status: ./dev-status.sh"
echo "🧪 Quick test: ./quick_api_test.py"
```

## 🔄 **Session Recovery After Restart**

### Auto-recovery Script
```bash
#!/bin/bash
# File: /home/m/development/DatingApp/recover-session.sh

echo "🔄 Recovering DatingApp session after restart..."

# 1. Check if services were running before
if [ -f "/tmp/datingapp_was_running" ]; then
    echo "Previous session detected, restarting services..."
    export DEMO_MODE=true
    ./dev-start.sh
fi

# 2. Restore Python virtual environment
cd /home/m/development/mobile-apps/flutter/dejtingapp
source .venv/bin/activate

# 3. Check for tmux sessions
if tmux has-session -t "datingapp-dev" 2>/dev/null; then
    echo "Existing tmux session found, attaching..."
    tmux attach-session -t "datingapp-dev"
else
    echo "Creating new tmux session..."
    ./start-dev-session.sh
fi
```

## 📝 **Session State Tracking**

### Service State Tracker
```bash
#!/bin/bash
# File: /home/m/development/DatingApp/track-session.sh

# Create session tracking file
echo "Session started: $(date)" > /tmp/datingapp_session_info
echo "Working directory: $(pwd)" >> /tmp/datingapp_session_info
echo "DEMO_MODE: $DEMO_MODE" >> /tmp/datingapp_session_info

# Track when services start
if pgrep -f "AuthService" > /dev/null; then
    echo "Services are running" > /tmp/datingapp_was_running
fi

# Create exit trap to save state
trap 'echo "Session ended: $(date)" >> /tmp/datingapp_session_info' EXIT
```

## 🎯 **Quick Commands for Session Management**

```bash
# Save current state instantly
alias save-session="cd /home/m/development/DatingApp && ./create-checkpoint.sh"

# Restore last session
alias restore-session="cd /home/m/development/DatingApp && ./recover-session.sh"

# Quick status check
alias check-dev="cd /home/m/development/DatingApp && ./dev-status.sh"

# Morning startup
alias start-dev="cd /home/m/development/DatingApp && ./morning-startup.sh"
```

## 💡 **Best Practices**

### Before Closing VS Code
1. ✅ Run `./create-checkpoint.sh` to save current state
2. ✅ Commit any important changes to git
3. ✅ Note any running processes in session notes
4. ✅ Save any important terminal outputs

### When Reopening
1. ✅ Run `./recover-session.sh` to restore state
2. ✅ Check `./dev-status.sh` for service health
3. ✅ Reattach to tmux session if available
4. ✅ Review any checkpoint notes

### Emergency Recovery
```bash
# If everything fails, nuclear option:
cd /home/m/development/DatingApp
export DEMO_MODE=true
./dev-restart.sh
./quick_api_test.py
# Check AI_CONTEXT.md for complete project context
```

---

**🎯 Remember**: With the comprehensive `AI_CONTEXT.md` file, even if your session is lost, any AI assistant can quickly understand your project setup and help restore your working environment!
