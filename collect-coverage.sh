#!/bin/bash
# Collect test coverage across all services

set -e

echo "🧪 Collecting test coverage for all services..."

SERVICES=(
  "UserService/UserService.Tests"
  "MatchmakingService/MatchmakingService.Tests"
  "swipe-service/SwipeService.Tests"
  "photo-service/PhotoService.Tests"
  "messaging-service/MessagingService.Tests"
  "dejting-yarp/src/dejting-yarp.Tests"
)

# Create coverage directory
mkdir -p coverage

total_tested=0
total_services=0

for service_test in "${SERVICES[@]}"; do
  service_name=$(basename "$(dirname "$service_test")")
  echo ""
  echo "📊 Testing $service_name..."
  
  cd "$service_test"
  
  # Run tests with coverage collection
  dotnet test \
    --collect:"XPlat Code Coverage" \
    --results-directory:"../../coverage/${service_name}" \
    --logger:"console;verbosity=minimal" \
    -- DataCollectionRunSettings.DataCollectors.DataCollector.Configuration.Format=cobertura,opencover
  
  if [ $? -eq 0 ]; then
    echo "  ✅ $service_name tests passed"
    ((total_tested++))
  else
    echo "  ❌ $service_name tests failed"
  fi
  
  ((total_services++))
  cd - > /dev/null
done

echo ""
echo "════════════════════════════════════════"
echo "📈 Coverage Summary: $total_tested/$total_services services tested"
echo "Coverage reports in: ./coverage/"
echo ""
echo "To view coverage:"
echo "  1. Install reportgenerator: dotnet tool install -g dotnet-reportgenerator-globaltool"
echo "  2. Run: ./generate-coverage-report.sh"
echo "════════════════════════════════════════"
