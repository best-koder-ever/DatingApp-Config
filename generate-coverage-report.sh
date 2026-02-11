#!/bin/bash
# Generate HTML coverage reports from collected coverage data

if [ ! -d "coverage" ]; then
  echo "❌ No coverage data found. Run ./collect-coverage.sh first"
  exit 1
fi

echo "📊 Generating coverage reports..."

# Find all coverage.cobertura.xml files
reports=$(find coverage -name "coverage.cobertura.xml" | tr '\n' ';')

if [ -z "$reports" ]; then
  echo "❌ No coverage files found in coverage/"
  exit 1
fi

# Generate combined report
reportgenerator \
  "-reports:${reports}" \
  "-targetdir:coverage/report" \
  "-reporttypes:Html;TextSummary;Badges" \
  "-verbosity:Info"

echo ""
echo "✅ Coverage report generated!"
echo ""
echo "View report: file://$(pwd)/coverage/report/index.html"
echo ""

# Display summary if available
if [ -f "coverage/report/Summary.txt" ]; then
  echo "════════════════════════════════════════"
  cat coverage/report/Summary.txt
  echo "════════════════════════════════════════"
fi
