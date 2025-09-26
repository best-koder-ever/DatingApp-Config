#!/bin/bash
# Create Development Checkpoint

CHECKPOINT_DIR="/home/m/development/DatingApp/checkpoints/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$CHECKPOINT_DIR"

echo "📸 Creating checkpoint at $CHECKPOINT_DIR"

# Save current state
echo "# DatingApp Session Checkpoint - $(date)" > "$CHECKPOINT_DIR/README.md"
echo "Working directory: $(pwd)" >> "$CHECKPOINT_DIR/README.md"

# Save environment variables
env | grep -E "(DEMO_MODE|DOTNET|PATH|FLUTTER)" > "$CHECKPOINT_DIR/environment.txt"

# Save running processes
ps aux | grep -E "(dotnet|flutter|tmux)" > "$CHECKPOINT_DIR/processes.txt"

# Save service status
echo "Checking service status..." 
./dev-status.sh > "$CHECKPOINT_DIR/service_status.txt" 2>&1

# Save tmux sessions
tmux list-sessions > "$CHECKPOINT_DIR/tmux_sessions.txt" 2>/dev/null || echo "No tmux sessions" > "$CHECKPOINT_DIR/tmux_sessions.txt"

# Save git status for all repos
echo "=== DatingApp Main ===" > "$CHECKPOINT_DIR/git_status.txt"
git status --porcelain >> "$CHECKPOINT_DIR/git_status.txt" 2>&1

echo "=== Auth Service ===" >> "$CHECKPOINT_DIR/git_status.txt"
cd auth-service && git status --porcelain >> "$CHECKPOINT_DIR/git_status.txt" 2>&1

echo "=== Flutter App ===" >> "$CHECKPOINT_DIR/git_status.txt"
cd /home/m/development/mobile-apps/flutter/dejtingapp && git status --porcelain >> "$CHECKPOINT_DIR/git_status.txt" 2>&1

# Save current VS Code workspace files
echo "Active VS Code files:" > "$CHECKPOINT_DIR/vscode_state.txt"
ls -la /home/m/development/DatingApp/*.code-workspace >> "$CHECKPOINT_DIR/vscode_state.txt" 2>&1

# Create quick restore commands
echo "#!/bin/bash" > "$CHECKPOINT_DIR/quick_restore.sh"
echo "# Quick restore commands for this checkpoint" >> "$CHECKPOINT_DIR/quick_restore.sh"
echo "cd /home/m/development/DatingApp" >> "$CHECKPOINT_DIR/quick_restore.sh"
echo "export DEMO_MODE=true" >> "$CHECKPOINT_DIR/quick_restore.sh"
echo "./dev-status.sh" >> "$CHECKPOINT_DIR/quick_restore.sh"
chmod +x "$CHECKPOINT_DIR/quick_restore.sh"

echo "✅ Checkpoint saved to: $CHECKPOINT_DIR"
echo "🔄 Restore with: $CHECKPOINT_DIR/quick_restore.sh"

# Create symlink to latest checkpoint
ln -sfn "$CHECKPOINT_DIR" "/home/m/development/DatingApp/checkpoints/latest"
echo "📂 Latest checkpoint linked at: checkpoints/latest"
