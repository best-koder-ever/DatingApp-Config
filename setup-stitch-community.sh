#!/bin/bash
# Alternative: Community Stitch MCP Setup (Simpler)
set -e

echo "🧵 Community Stitch MCP Setup (Alternative Method)"
echo ""
echo "This is simpler than the official version!"
echo ""

# 1. Authenticate with Google Cloud (this part usually works)
echo "Step 1/4: Google Cloud Authentication..."
gcloud auth login

# 2. Set up application default credentials
echo ""
echo "Step 2/4: Application Default Credentials..."
gcloud auth application-default login

# 3. Get your Google Cloud project ID
echo ""
echo "Step 3/4: Google Cloud Project Setup..."
echo ""
echo "Enter your Google Cloud Project ID:"
echo "(Find it at: https://console.cloud.google.com/)"
read -p "Project ID: " PROJECT_ID

gcloud config set project "$PROJECT_ID"
gcloud auth application-default set-quota-project "$PROJECT_ID"

# 4. Enable Stitch API
echo ""
echo "Step 4/4: Enabling Stitch API..."
gcloud beta services mcp enable stitch.googleapis.com

echo ""
echo "✅ Setup complete!"
echo ""
echo "Now add this to Claude Desktop config:"
echo ""
echo '~/.config/Claude/claude_desktop_config.json'
echo ""
echo '{'
echo '  "mcpServers": {'
echo '    "stitch": {'
echo '      "command": "npx",'
echo '      "args": ["stitch-mcp"]'
echo '    }'
echo '  }'
echo '}'
echo ""
