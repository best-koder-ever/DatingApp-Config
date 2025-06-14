#!/bin/bash
# Script to save Copilot chat to a timestamped Markdown file in the copilot_logs directory

LOG_DIR="$(dirname "$0")/copilot_logs"
mkdir -p "$LOG_DIR"
FILENAME="$LOG_DIR/$(date +%Y-%m-%d-%H%M%S)-copilot-chat.md"

echo "Paste your Copilot chat below. Press Ctrl+D when done."
cat > "$FILENAME"
echo "Saved Copilot chat to $FILENAME"
