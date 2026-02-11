#!/bin/bash
# Complete Stitch MCP Setup in One Go
set -e

echo "🧵 Complete Google Stitch MCP Setup"
echo ""
echo "This will:"
echo "  1. Authenticate you with Google Cloud (opens browser 2x)"
echo "  2. Configure Stitch MCP for Claude Code"
echo "  3. Verify the setup"
echo ""
echo "⚠️  IMPORTANT: You'll see 2 browser windows open"
echo "   - First: Login to Google"
echo "   - Second: Grant application permissions"
echo ""
read -p "Press Enter to start setup..."

# Ensure gcloud is in PATH
export PATH="/home/m/.stitch-mcp/google-cloud-sdk/bin:$PATH"

echo ""
echo "Step 1/4: Authenticating with Google Cloud..."
echo ""
echo "📌 A browser window will open. Sign in with your Google account."
echo ""

# Authenticate
gcloud auth login

echo ""
echo "✅ Google Cloud authentication complete!"
echo ""
echo "Step 2/4: Setting up Application Default Credentials..."
echo ""
echo "📌 Another browser window will open. Grant permissions."
echo ""

# Application default credentials
gcloud auth application-default login

echo ""
echo "✅ Application credentials set!"
echo ""
echo "Step 3/4: Configuring Stitch MCP for Claude Code..."
echo ""

# Run the init command (it should now find the authentication)
npx @_davideast/stitch-mcp init -c cc -t http --yes

echo ""
echo "Step 4/4: Verifying setup..."
echo ""

# Verify
npx @_davideast/stitch-mcp doctor

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 Setup Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Next steps:"
echo "  1. Start the proxy server:"
echo "     ./start-stitch-proxy.sh"
echo ""
echo "  2. Ask Claude to generate designs:"
echo '     "Using Stitch, create a dating app profile card"'
echo ""
