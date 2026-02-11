#!/bin/bash
# Stitch MCP Setup with Manual Authentication (No Browser Issues)
set -e

echo "🧵 Google Stitch MCP Setup (Manual Auth Method)"
echo ""
echo "This uses copy-paste authentication instead of browser redirects."
echo "More reliable for remote/headless systems."
echo ""
read -p "Press Enter to start..."

# Ensure gcloud is in PATH
export PATH="/home/m/.stitch-mcp/google-cloud-sdk/bin:$PATH"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 1/4: Google Cloud Authentication"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "You'll see a URL. Open it in your browser and login."
echo "After logging in, you'll get a verification code."
echo "Copy and paste that code back here."
echo ""
read -p "Press Enter to get the authentication URL..."

# Manual auth
gcloud auth login --no-launch-browser

echo ""
echo "✅ Google Cloud authentication complete!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 2/4: Application Default Credentials"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Same process: URL → Login → Copy code → Paste here"
echo ""
read -p "Press Enter to get the second authentication URL..."

# Application default credentials
gcloud auth application-default login --no-launch-browser

echo ""
echo "✅ Application credentials set!"
echo ""

# Verify authentication worked
ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>/dev/null | head -1)

if [ -z "$ACCOUNT" ]; then
    echo "❌ ERROR: No authenticated account found!"
    echo ""
    echo "Please run the auth commands manually:"
    echo "  gcloud auth login --no-launch-browser"
    echo "  gcloud auth application-default login --no-launch-browser"
    exit 1
fi

echo "✅ Authenticated as: $ACCOUNT"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 3/4: Configuring Stitch MCP for Claude Code"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Run the init command
npx @_davideast/stitch-mcp init -c cc -t http --yes

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 4/4: Verifying Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Verify
npx @_davideast/stitch-mcp doctor

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 Setup Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Next steps:"
echo ""
echo "  1. Start the proxy server (in a separate terminal):"
echo "     cd /home/m/development/DatingApp"
echo "     ./start-stitch-proxy.sh"
echo ""
echo "  2. In Claude, ask for designs:"
echo '     "Using Stitch, create a dating app profile card"'
echo ""
echo "The proxy must be running for Stitch to work!"
echo ""
