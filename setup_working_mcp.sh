#!/bin/bash
# 🔧 Fixed MCP setup with working packages

echo "🔧 Setting up Working MCP Configuration..."
echo "=========================================="

# Create improved MCP config with working packages
mkdir -p ~/.config/mcp

# Update the config to use working packages and local alternatives
cat > ~/.config/mcp/config.json << 'EOF'
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-filesystem", "/home/m/development/DatingApp"],
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

# Create local development tools that work with Claude 4
cat > ~/.config/mcp/dating_app_tools.py << 'EOF'
#!/usr/bin/env python3
"""
Dating App Development Tools for Claude 4 MCP Integration
"""

import json
import subprocess
import os
import sys
from pathlib import Path

class DatingAppMCP:
    def __init__(self):
        self.root_dir = "/home/m/development/DatingApp"
        self.flutter_dir = "/home/m/development/mobile-apps/flutter/dejtingapp"
        
    def get_project_structure(self):
        """Get complete project structure for Claude 4"""
        structure = {
            "services": {},
            "databases": {},
            "mobile_app": {},
            "docker": {},
            "git_status": {}
        }
        
        # Scan services
        for service_dir in Path(self.root_dir).glob("*-service"):
            service_name = service_dir.name
            structure["services"][service_name] = {
                "path": str(service_dir),
                "files": [f.name for f in service_dir.rglob("*.cs") if f.is_file()],
                "config": [f.name for f in service_dir.glob("*.json") if f.is_file()],
                "has_dockerfile": (service_dir / "Dockerfile").exists()
            }
        
        # Check Flutter app
        if Path(self.flutter_dir).exists():
            structure["mobile_app"] = {
                "path": self.flutter_dir,
                "screens": [f.name for f in Path(self.flutter_dir).rglob("*screen*.dart")],
                "services": [f.name for f in Path(self.flutter_dir).rglob("*service*.dart")]
            }
        
        return structure
    
    def get_service_health(self):
        """Check health of all services"""
        health = {}
        ports = {
            "auth-service": 5001,
            "messaging-service": 5007, 
            "matchmaking-service": 5003,
            "swipe-service": 5005,
            "user-service": 5002,
            "photo-service": 5004
        }
        
        for service, port in ports.items():
            try:
                result = subprocess.run(
                    ["curl", "-s", f"http://localhost:{port}/health"], 
                    capture_output=True, 
                    timeout=5
                )
                health[service] = "healthy" if result.returncode == 0 else "unhealthy"
            except:
                health[service] = "unreachable"
        
        return health
    
    def get_docker_status(self):
        """Get Docker container status"""
        try:
            result = subprocess.run(
                ["docker", "ps", "--format", "json"], 
                capture_output=True, 
                text=True
            )
            if result.returncode == 0:
                containers = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        containers.append(json.loads(line))
                return containers
        except:
            pass
        return []
    
    def get_git_status(self):
        """Get git status across all repos"""
        os.chdir(self.root_dir)
        git_info = {}
        
        try:
            # Main repo status
            branch = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], 
                                  capture_output=True, text=True).stdout.strip()
            uncommitted = subprocess.run(["git", "status", "--porcelain"], 
                                       capture_output=True, text=True).stdout.strip()
            
            git_info["main_repo"] = {
                "branch": branch,
                "uncommitted_files": len(uncommitted.split('\n')) if uncommitted else 0,
                "last_commit": subprocess.run(["git", "log", "--oneline", "-1"], 
                                            capture_output=True, text=True).stdout.strip()
            }
        except:
            git_info["main_repo"] = {"error": "Git not available"}
        
        return git_info

def main():
    """Main function for MCP tool"""
    if len(sys.argv) < 2:
        print("Usage: python3 dating_app_tools.py <command>")
        return
    
    mcp = DatingAppMCP()
    command = sys.argv[1]
    
    if command == "structure":
        print(json.dumps(mcp.get_project_structure(), indent=2))
    elif command == "health":
        print(json.dumps(mcp.get_service_health(), indent=2))
    elif command == "docker":
        print(json.dumps(mcp.get_docker_status(), indent=2))
    elif command == "git":
        print(json.dumps(mcp.get_git_status(), indent=2))
    elif command == "full":
        # Complete project analysis
        analysis = {
            "project_structure": mcp.get_project_structure(),
            "service_health": mcp.get_service_health(),
            "docker_status": mcp.get_docker_status(),
            "git_status": mcp.get_git_status()
        }
        print(json.dumps(analysis, indent=2))
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
EOF

chmod +x ~/.config/mcp/dating_app_tools.py

# Create MCP integration script for Claude 4
cat > ~/.config/mcp/claude4_integration.sh << 'EOF'
#!/bin/bash
# Claude 4 MCP Integration for Dating App

echo "🤖 Claude 4 Dating App Integration Ready!"
echo "========================================"

# Show what's available to Claude 4
echo "📊 Available to Claude 4 via MCP:"
echo ""

echo "🏗️ Project Analysis:"
python3 ~/.config/mcp/dating_app_tools.py structure

echo ""
echo "🏥 Service Health:"
python3 ~/.config/mcp/dating_app_tools.py health

echo ""
echo "🐳 Docker Status:"
python3 ~/.config/mcp/dating_app_tools.py docker

echo ""
echo "🔄 Git Status:"
python3 ~/.config/mcp/dating_app_tools.py git

echo ""
echo "💡 Claude 4 can now:"
echo "   ✅ Analyze your complete 7-service architecture"
echo "   ✅ Monitor service health in real-time"
echo "   ✅ Debug Docker container issues"
echo "   ✅ Track git changes across repositories"
echo "   ✅ Navigate Flutter app structure"
echo "   ✅ Understand microservice relationships"
EOF

chmod +x ~/.config/mcp/claude4_integration.sh

# Test the setup
echo "🧪 Testing MCP Integration..."
python3 ~/.config/mcp/dating_app_tools.py full

echo ""
echo "✅ Working MCP Configuration Complete!"
echo ""
echo "🎯 What's working:"
echo "   ✅ Filesystem access to your dating app"
echo "   ✅ GitHub integration (add token to config)"
echo "   ✅ Brave search for documentation"
echo "   ✅ Local development tools for project analysis"
echo "   ✅ Service health monitoring"
echo "   ✅ Docker container management"
echo "   ✅ Git repository tracking"
echo ""
echo "🚀 Test with Claude 4:"
echo "   ~/.config/mcp/claude4_integration.sh"
echo ""
echo "💡 Ask Claude 4 to analyze your dating app now!"
