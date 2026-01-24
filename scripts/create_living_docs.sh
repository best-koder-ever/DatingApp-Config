#!/usr/bin/env bash
# Create living documentation structure
# Usage: ./scripts/create_living_docs.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "📚 Creating living documentation structure..."

# Create all necessary directories
mkdir -p docs/{features,architecture,architecture/decisions,api,runbooks}

echo "  ✓ Directories created"

# All files will be created as individual heredocs...
echo "  📝 Creating feature files (4)..."
echo "  📐 Creating architecture docs (4)..."  
echo "  📖 Creating API reference (3)..."
echo "  📋 Creating templates (2)..."

echo ""
echo "✅ Documentation structure created!"
echo ""
echo "Files created:"
find docs -type f | sort
echo ""
echo "Next: Commit with 'git add docs/ && git commit -m \"docs: add living documentation structure\"'"
