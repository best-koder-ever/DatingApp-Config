#!/bin/bash
# Display summary of overnight automation results

REPORT_FILE="reports/overnight-$(date +%Y%m%d).md"

if [ ! -f "$REPORT_FILE" ]; then
    echo "❌ No overnight report found for today"
    echo "   Run: ./scripts/overnight-full-build.sh"
    exit 1
fi

cat "$REPORT_FILE"

echo ""
echo "📂 Detailed logs available in:"
ls -lh logs/*$(date +%Y%m%d)*.log 2>/dev/null || echo "   No logs found"
