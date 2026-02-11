#!/bin/bash
# Google Stitch MCP Proxy Server Launcher
# Run this AFTER completing authentication

set -e

echo "🧵 Starting Google Stitch MCP Proxy Server..."
echo ""
echo "⚠️  IMPORTANT: Keep this terminal open while using Stitch!"
echo ""
echo "📌 Usage in Claude:"
echo "   Ask Claude to generate designs using Stitch"
echo '   Example: "Using Stitch, create a dating app profile card"'
echo ""
echo "Press Ctrl+C to stop the proxy"
echo ""
echo "─────────────────────────────────────────"
echo ""

# Ensure PATH includes gcloud
export PATH="/home/m/.stitch-mcp/google-cloud-sdk/bin:$PATH"

# Start the proxy
npx @_davideast/stitch-mcp proxy
