#!/bin/bash
# Script to save Copilot chat to a timestamped Markdown file in the copilot_logs directory and auto-commit/push to GitHub
# Now with deduplication: will not save if content is identical to the last 3 logs

LOG_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$LOG_DIR/.." # Move to repo root
FILENAME="$LOG_DIR/$(date +%Y-%m-%d-%H%M%S)-copilot-chat.md"

# Capture chat
TMPFILE=$(mktemp)
echo "Paste your Copilot chat below. Press Ctrl+D when done."
cat > "$TMPFILE"

# Deduplication: compare to last 3 logs
IS_DUPLICATE=false
for old in $(ls -t "$LOG_DIR"/*.md 2>/dev/null | head -n 3); do
  if cmp -s "$TMPFILE" "$old"; then
    IS_DUPLICATE=true
    break
  fi
done

if $IS_DUPLICATE; then
  echo "This chat is identical to one of the last 3 logs. Not saving duplicate."
  rm "$TMPFILE"
  exit 0
fi

mv "$TMPFILE" "$FILENAME"
echo "Saved Copilot chat to $FILENAME"

git add "$FILENAME"
git commit -m "Add Copilot chat log: $(basename $FILENAME)"
git push
