#!/bin/bash
# Quick screenshot helper for visual testing
# Usage: ./screenshot.sh [name]
NAME="${1:-screen}"
TIMESTAMP=$(date +%H%M%S)
FILE="/tmp/emu-${NAME}-${TIMESTAMP}.png"
adb -s emulator-5554 exec-out screencap -p > "$FILE" 2>&1
if [ $? -eq 0 ]; then
    echo "📸 Screenshot saved: $FILE"
    echo "   Size: $(du -h "$FILE" | cut -f1)"
else
    echo "❌ Screenshot failed. Is emulator running?"
    adb devices -l
fi
