#!/bin/bash
# 🧪 Test Linear MCP Integration

echo "🧪 Testing Linear MCP Integration"
echo "================================="

# Check if Linear server exists
if [ -f ~/.config/mcp/linear-server/server.js ]; then
    echo "✅ Linear MCP server installed"
else
    echo "❌ Linear MCP server not found"
    exit 1
fi

# Check if config.json includes Linear
if grep -q "linear" ~/.config/mcp/config.json; then
    echo "✅ Linear configured in MCP config"
else
    echo "❌ Linear not configured in MCP"
    exit 1
fi

# Check dependencies
echo ""
echo "📦 Checking dependencies..."
cd ~/.config/mcp/linear-server

if npm list @linear/sdk > /dev/null 2>&1; then
    echo "✅ Linear SDK installed"
else
    echo "❌ Linear SDK missing"
fi

if npm list @modelcontextprotocol/sdk > /dev/null 2>&1; then
    echo "✅ MCP SDK installed"
else
    echo "❌ MCP SDK missing"
fi

echo ""
echo "🔧 Configuration status:"
if grep -q '"LINEAR_API_KEY": ""' ~/.config/mcp/config.json; then
    echo "⚠️  Linear API key not configured"
    echo "   Run: ~/.config/mcp/setup_linear_token.sh"
else
    echo "✅ Linear API key configured"
fi

echo ""
echo "📁 Project structure:"
echo "   📂 ~/.config/mcp/linear-server/     - Linear MCP server"
echo "   📄 ~/.config/mcp/config.json        - MCP configuration"
echo "   🔧 ~/.config/mcp/setup_linear_token.sh - API key setup"
echo "   🎯 ~/.config/mcp/linear_workflows.sh - Workflow helpers"

echo ""
echo "🎯 Next steps:"
echo "1. Get Linear API key: https://linear.app/myappismyapp/settings/api"
echo "2. Configure key: ~/.config/mcp/setup_linear_token.sh"
echo "3. Create project: ~/.config/mcp/linear_workflows.sh structure"
echo "4. View workspace: https://linear.app/myappismyapp/team/MYA/active"
