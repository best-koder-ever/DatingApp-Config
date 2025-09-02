#!/bin/bash
# 🔧 Setting up MCP plugins for Dating App development

echo "🔧 Setting up MCP plugins for Dating App development..."
echo "======================================================"

# Check if Node.js is installed
if ! command -v npm &> /dev/null; then
    echo "❌ Node.js/npm not found. Installing..."
    curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
    sudo apt-get install -y nodejs
fi

# Check if Python is installed
if ! command -v pip &> /dev/null; then
    echo "❌ Python/pip not found. Installing..."
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip
fi

# Create MCP config directory
echo "📁 Creating MCP configuration directory..."
mkdir -p ~/.config/mcp

# Install MCP CLI
echo "📦 Installing MCP CLI..."
npm install -g @modelcontextprotocol/cli || {
    echo "⚠️  NPM install failed, trying pip..."
    pip install mcp --user
}

# Install essential MCP servers
echo "🔌 Installing MCP servers..."

# 1. Filesystem MCP - For code navigation
echo "  📁 Installing Filesystem MCP..."
npm install -g @modelcontextprotocol/server-filesystem

# 2. Git MCP - For repository management  
echo "  🔄 Installing Git MCP..."
npm install -g @modelcontextprotocol/server-git

# 3. Database MCP - For MySQL/Entity Framework
echo "  🗄️  Installing Database MCP..."
npm install -g @modelcontextprotocol/server-database

# 4. Docker MCP - For container management
echo "  🐳 Installing Docker MCP..."
npm install -g @modelcontextprotocol/server-docker

# 5. GitHub MCP - For repository integration
echo "  🐙 Installing GitHub MCP..."
npm install -g @modelcontextprotocol/server-github

# 6. Brave Search MCP - For documentation lookup
echo "  🔍 Installing Brave Search MCP..."
npm install -g @modelcontextprotocol/server-brave-search

# Create MCP configuration
echo "⚙️  Creating MCP configuration..."
cat > ~/.config/mcp/config.json << 'EOF'
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-filesystem", "/home/m/development/DatingApp"],
      "env": {}
    },
    "git": {
      "command": "npx", 
      "args": ["@modelcontextprotocol/server-git", "/home/m/development/DatingApp"],
      "env": {}
    },
    "database": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-database"],
      "env": {
        "DATABASE_URL": "mysql://localhost:3306/dating_app"
      }
    },
    "docker": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-docker"],
      "env": {}
    },
    "github": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": ""
      }
    },
    "brave-search": {
      "command": "npx", 
      "args": ["@modelcontextprotocol/server-brave-search"],
      "env": {
        "BRAVE_API_KEY": ""
      }
    }
  }
}
EOF

# Set proper permissions
chmod 644 ~/.config/mcp/config.json

echo "✅ MCP configuration created!"
echo ""
echo "🔑 Next steps - Add your API keys:"
echo "1. GitHub token: Edit ~/.config/mcp/config.json and add your GitHub token"
echo "   Get token from: https://github.com/settings/tokens"
echo "2. Brave API key: Get from https://api.search.brave.com/app/keys"
echo ""
echo "🚀 Test MCP setup:"
echo "   mcp list-servers"
echo ""
echo "💡 Your Claude 4 can now:"
echo "   ✅ Navigate your entire dating app codebase"
echo "   ✅ Manage git repositories across all services"
echo "   ✅ Query your MySQL databases directly"
echo "   ✅ Control Docker containers"
echo "   ✅ Search GitHub and documentation"
echo "   ✅ Access real-time development context"
echo ""
echo "🎯 Next: Run ./setup_dating_app_mcp.sh for project-specific setup"
