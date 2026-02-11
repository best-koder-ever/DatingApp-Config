#!/bin/bash
# T003: Generate test skeletons for all controller actions
# Scans controllers, creates failing xUnit tests marked with [Fact(Skip = "Not implemented")]

set -uo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

TESTS_CREATED=0

echo "🧬 Generating test skeletons for all services..."

generate_controller_tests() {
    local SERVICE_DIR=$1
    local CONTROLLER_FILE=$2
    local CONTROLLER_NAME=$(basename "$CONTROLLER_FILE" .cs)
    # Find the actual test project directory (handles nested structures)
    local TEST_DIR=""
    for candidate in "$SERVICE_DIR/${SERVICE_DIR##*/}.Tests" "$SERVICE_DIR/$(echo $SERVICE_DIR | sed 's/-service/Service/;s/^./\U&/')Service.Tests" "$SERVICE_DIR/$(ls $SERVICE_DIR 2>/dev/null | grep '\.Tests$' | head -1)"; do
        if [ -d "$candidate" ] 2>/dev/null; then TEST_DIR="$candidate"; break; fi
    done
    # Fallback: find .Tests.csproj and use its directory
    if [ -z "$TEST_DIR" ]; then
        TEST_DIR=$(find "$SERVICE_DIR" -maxdepth 2 -name '*.Tests.csproj' -printf '%h
' 2>/dev/null | head -1)
    fi
    if [ -z "$TEST_DIR" ]; then echo "    ⚠️  No .Tests dir found for $SERVICE_DIR"; return; fi
    local TEST_FILE="$TEST_DIR/${CONTROLLER_NAME}Tests.cs"
    
    mkdir -p "$TEST_DIR"
    
    # Extract namespace
    local NAMESPACE=$(grep "^namespace" "$SERVICE_DIR/Controllers/$CONTROLLER_NAME.cs" | sed 's/namespace \(.*\);/\1/' | tr -d '\r')
    
    # Extract action methods (simplified - looks for [HttpGet], [HttpPost], etc.)
    local ACTIONS=$(grep -E '^\s*\[(HttpGet|HttpPost|HttpPut|HttpDelete|HttpPatch)' "$SERVICE_DIR/Controllers/$CONTROLLER_NAME.cs" | wc -l)
    
    if [ "$ACTIONS" -gt 0 ] && [ ! -f "$TEST_FILE" ]; then
        cat > "$TEST_FILE" << EOFTEST
using Xunit;
using $NAMESPACE;
using Microsoft.AspNetCore.Mvc;
using System.Threading.Tasks;

namespace ${NAMESPACE}.Tests
{
    /// <summary>
    /// Auto-generated test skeleton for $CONTROLLER_NAME
    /// TODO: Implement actual test logic
    /// </summary>
    public class ${CONTROLLER_NAME}Tests
    {
        // TODO: Add test setup (arrange)
        
        [Fact(Skip = "Not implemented - T003 skeleton")]
        public async Task Controller_Actions_Should_Have_Tests()
        {
            // Arrange: Set up test data and dependencies
            
            // Act: Call the controller action
            
            // Assert: Verify the result
            Assert.True(false, "Implement test for $CONTROLLER_NAME");
        }
        
        // TODO: Add test for each action method
        // Found $ACTIONS action methods in $CONTROLLER_NAME
    }
}
EOFTEST
        echo "  ✅ Created $TEST_FILE ($ACTIONS actions)"
        TESTS_CREATED=$((TESTS_CREATED+1))
    fi
}

# Scan all services
SERVICES=(
    "UserService"
    "MatchmakingService"
    "photo-service"
    "swipe-service"
    "messaging-service"
)

for SERVICE in "${SERVICES[@]}"; do
    if [ -d "$SERVICE/Controllers" ]; then
        echo "📁 Scanning $SERVICE/Controllers..."
        
        for CONTROLLER in "$SERVICE/Controllers"/*Controller.cs; do
            if [ -f "$CONTROLLER" ]; then
                generate_controller_tests "$SERVICE" "$CONTROLLER"
            fi
        done
    fi
done

echo ""
echo "✅ Test skeleton generation complete"
echo "   Created: $TESTS_CREATED test files"
echo ""
echo "📝 Next steps:"
echo "   1. Review generated test files"
echo "   2. Remove [Fact(Skip = ...)] and implement tests"
echo "   3. Run: dotnet test"
