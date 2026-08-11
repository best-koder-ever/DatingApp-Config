#!/usr/bin/env bash
# Cleanup audio feedback files older than 30 days.
# Transcript data remains in the SQLite database.
# Run daily via cron or manually.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FEEDBACK_DIR="${SCRIPT_DIR}/../bot-service/BotService/Data/UserFeedback"
MAX_AGE_DAYS="${MAX_AGE_DAYS:-30}"

if [[ ! -d "$FEEDBACK_DIR" ]]; then
  echo "Feedback directory $FEEDBACK_DIR does not exist — nothing to clean."
  exit 0
fi

echo "🧹 Cleaning audio feedback older than ${MAX_AGE_DAYS} days from $FEEDBACK_DIR"

deleted=0
total_size=0

while IFS= read -r -d '' file; do
  size=$(stat -c%s "$file" 2>/dev/null || echo 0)
  total_size=$((total_size + size))
  rm -f "$file"
  deleted=$((deleted + 1))
  echo "  Deleted: $(basename "$file") (${size} bytes)"
done < <(find "$FEEDBACK_DIR" -name "*.m4a" -type f -mtime "+${MAX_AGE_DAYS}" -print0 2>/dev/null || true)

# Also clean very small files (<100 bytes) that are probably corrupt/empty
while IFS= read -r -d '' file; do
  size=$(stat -c%s "$file" 2>/dev/null || echo 0)
  if [[ $size -lt 100 ]] && [[ $size -gt 0 ]]; then
    total_size=$((total_size + size))
    rm -f "$file"
    deleted=$((deleted + 1))
    echo "  Deleted (corrupt/tiny): $(basename "$file") (${size} bytes)"
  fi
done < <(find "$FEEDBACK_DIR" -name "*.m4a" -type f -size -100c -print0 2>/dev/null || true)

if [[ $deleted -gt 0 ]]; then
  echo "✅ Cleaned $deleted files (${total_size} bytes freed)"
else
  echo "✅ No files to clean — all within ${MAX_AGE_DAYS}-day retention window"
fi
