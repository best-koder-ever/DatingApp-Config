#!/bin/bash

# 🤖 Automatic AI Context Preservation System
# Monitors VS Code activity and auto-updates AI context files

# Configuration
CONTEXT_FILE="/home/m/development/DatingApp/AI_CONTEXT.md"
BACKUP_DIR="/home/m/development/DatingApp/ai_context_backups"
LOG_FILE="/home/m/development/DatingApp/context_auto_backup.log"
PID_FILE="/tmp/ai_context_monitor.pid"

# Settings (customize these)
TIME_INTERVAL=300  # 5 minutes in seconds
PROMPT_THRESHOLD=5 # Auto-backup after N file saves
WATCH_DIRECTORIES=(
    "/home/m/development/DatingApp"
    "/home/m/development/mobile-apps/flutter/dejtingapp"
)

# Global counters
SAVE_COUNTER=0
SESSION_START_TIME=$(date +%s)

# Logging function
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
    echo "🤖 AI Context Monitor: $1"
}

# Check if VS Code is running
is_vscode_running() {
    pgrep -f "code" > /dev/null
}

# Get current VS Code workspace
get_current_workspace() {
    # Try to detect workspace from VS Code process
    ps aux | grep -E "code.*DatingApp|code.*dejtingapp" | head -1 | grep -o "/home/[^[:space:]]*" || echo "unknown"
}

# Create context snapshot
create_context_snapshot() {
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local snapshot_file="$BACKUP_DIR/auto_snapshot_$timestamp.md"
    
    mkdir -p "$BACKUP_DIR"
    
    cat > "$snapshot_file" << EOF
# Auto Context Snapshot - $(date)

## Session Information
- **Start Time**: $(date -d @$SESSION_START_TIME)
- **Duration**: $(($(date +%s) - SESSION_START_TIME)) seconds
- **File Saves**: $SAVE_COUNTER
- **VS Code Running**: $(is_vscode_running && echo "Yes" || echo "No")
- **Current Workspace**: $(get_current_workspace)

## Current System State
### Git Status
\`\`\`
$(cd /home/m/development/DatingApp && git status --short 2>/dev/null || echo "No git repository")
\`\`\`

### Recent Commands (from history)
\`\`\`
$(tail -10 ~/.bash_history 2>/dev/null || echo "History not available")
\`\`\`

### Service Status
\`\`\`
$(cd /home/m/development/DatingApp && ./dev_status.sh 2>/dev/null || echo "dev_status.sh not available")
\`\`\`

### Recent File Changes (last hour)
\`\`\`
$(find /home/m/development/DatingApp -type f -mmin -60 -not -path "*/.*" -not -path "*/node_modules/*" -not -path "*/bin/*" -not -path "*/obj/*" 2>/dev/null | head -20 || echo "No recent changes")
\`\`\`

## Next Session Restoration
1. Attach AI_CONTEXT.md to new AI conversation
2. Reference this snapshot for current state
3. Current task: [MANUAL: Add your current task here]

## Auto-Generated Notes
- This snapshot was auto-created by the AI Context Monitor
- Monitor PID: $$
- Configuration: $TIME_INTERVAL sec intervals, $PROMPT_THRESHOLD save threshold
EOF

    log_message "Created snapshot: $snapshot_file"
    
    # Update main context file with latest session info
    update_main_context_file "$snapshot_file"
}

# Update main context file with session info
update_main_context_file() {
    local snapshot_file="$1"
    
    if [[ -f "$CONTEXT_FILE" ]]; then
        # Create session update section
        local session_update="

## 📝 Latest Auto Session Update - $(date)
**Monitor Status**: Active (PID: $$)
**Session Duration**: $(($(date +%s) - SESSION_START_TIME)) seconds
**File Saves This Session**: $SAVE_COUNTER
**Last Snapshot**: $(basename "$snapshot_file")

**Quick Context Restoration**:
1. Current workspace: $(get_current_workspace)
2. VS Code running: $(is_vscode_running && echo "Yes" || echo "No")
3. Recent activity: $(tail -1 ~/.bash_history 2>/dev/null || echo "No recent commands")

---"

        # Add session update to context file
        echo "$session_update" >> "$CONTEXT_FILE"
        log_message "Updated main context file"
    else
        log_message "Warning: Main context file not found: $CONTEXT_FILE"
    fi
}

# Monitor file system changes
monitor_file_changes() {
    log_message "Starting file system monitor"
    
    # Use inotify to watch for file saves
    inotifywait -m -r -e modify,create,move "${WATCH_DIRECTORIES[@]}" 2>/dev/null | while read path action file; do
        # Filter for relevant files
        if [[ "$file" =~ \.(cs|ts|dart|json|md|py|sh)$ ]]; then
            SAVE_COUNTER=$((SAVE_COUNTER + 1))
            log_message "File change detected: $path$file (count: $SAVE_COUNTER)"
            
            # Auto-backup after threshold
            if (( SAVE_COUNTER >= PROMPT_THRESHOLD )); then
                log_message "Threshold reached, creating backup"
                create_context_snapshot
                SAVE_COUNTER=0
            fi
        fi
    done &
}

# Time-based backup
time_based_backup() {
    while true; do
        sleep "$TIME_INTERVAL"
        
        if is_vscode_running; then
            log_message "Time-based backup triggered"
            create_context_snapshot
        else
            log_message "VS Code not running, skipping time-based backup"
        fi
    done &
}

# VS Code shutdown detection
monitor_vscode_shutdown() {
    local last_vscode_state=true
    
    while true; do
        local current_vscode_state=$(is_vscode_running)
        
        if [[ "$last_vscode_state" == true && "$current_vscode_state" == false ]]; then
            log_message "VS Code shutdown detected, creating final backup"
            create_context_snapshot
        fi
        
        last_vscode_state=$current_vscode_state
        sleep 30  # Check every 30 seconds
    done &
}

# Cleanup function
cleanup() {
    log_message "Shutting down AI Context Monitor"
    # Kill background processes
    jobs -p | xargs -r kill
    rm -f "$PID_FILE"
    exit 0
}

# Start monitoring
start_monitor() {
    # Check if already running
    if [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
        echo "❌ AI Context Monitor already running (PID: $(cat "$PID_FILE"))"
        exit 1
    fi
    
    # Save PID
    echo $$ > "$PID_FILE"
    
    # Setup signal handlers
    trap cleanup SIGINT SIGTERM EXIT
    
    log_message "Starting AI Context Monitor (PID: $$)"
    log_message "Config: ${TIME_INTERVAL}s intervals, ${PROMPT_THRESHOLD} save threshold"
    log_message "Watching: ${WATCH_DIRECTORIES[*]}"
    
    # Create initial snapshot
    create_context_snapshot
    
    # Start monitoring functions
    monitor_file_changes
    time_based_backup  
    monitor_vscode_shutdown
    
    # Keep main process alive
    while true; do
        sleep 60
        log_message "Monitor alive (saves: $SAVE_COUNTER, uptime: $(($(date +%s) - SESSION_START_TIME))s)"
    done
}

# Command handling
case "${1:-start}" in
    start)
        start_monitor
        ;;
    stop)
        if [[ -f "$PID_FILE" ]]; then
            PID=$(cat "$PID_FILE")
            if kill "$PID" 2>/dev/null; then
                echo "✅ Stopped AI Context Monitor (PID: $PID)"
                rm -f "$PID_FILE"
            else
                echo "❌ Monitor not running or already stopped"
                rm -f "$PID_FILE"
            fi
        else
            echo "❌ Monitor not running"
        fi
        ;;
    status)
        if [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
            echo "✅ AI Context Monitor running (PID: $(cat "$PID_FILE"))"
            echo "📊 Log file: $LOG_FILE"
            echo "📁 Backups: $BACKUP_DIR"
            echo "🔍 Recent activity:"
            tail -5 "$LOG_FILE" 2>/dev/null || echo "No recent activity"
        else
            echo "❌ AI Context Monitor not running"
        fi
        ;;
    backup)
        echo "🔄 Creating manual backup..."
        create_context_snapshot
        echo "✅ Backup created"
        ;;
    logs)
        echo "📜 Recent AI Context Monitor logs:"
        tail -20 "$LOG_FILE" 2>/dev/null || echo "No logs available"
        ;;
    *)
        echo "Usage: $0 {start|stop|status|backup|logs}"
        echo ""
        echo "Commands:"
        echo "  start  - Start the AI context monitor"
        echo "  stop   - Stop the AI context monitor"
        echo "  status - Check monitor status"
        echo "  backup - Create manual backup"
        echo "  logs   - View recent logs"
        echo ""
        echo "Features:"
        echo "  • Auto-backup every $TIME_INTERVAL seconds"
        echo "  • Auto-backup after $PROMPT_THRESHOLD file saves"
        echo "  • Backup on VS Code shutdown"
        echo "  • File system change monitoring"
        ;;
esac
