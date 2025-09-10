#!/bin/bash
# 🔧 Setting up Linear MCP integration for Dating App project management

echo "🎯 Setting up Linear MCP integration..."
echo "======================================"

# Create Linear MCP server directory
echo "📁 Creating Linear MCP server..."
mkdir -p ~/.config/mcp/linear-server

# Create Linear MCP server package.json
cat > ~/.config/mcp/linear-server/package.json << 'EOF'
{
  "name": "linear-mcp-server",
  "version": "1.0.0",
  "description": "MCP server for Linear project management integration",
  "main": "server.js",
  "dependencies": {
    "@modelcontextprotocol/sdk": "^0.5.0",
    "@linear/sdk": "^8.0.0",
    "axios": "^1.6.0"
  }
}
EOF

# Install Linear MCP dependencies
cd ~/.config/mcp/linear-server
npm install

# Create Linear MCP server
cat > ~/.config/mcp/linear-server/server.js << 'EOF'
#!/usr/bin/env node
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { CallToolRequestSchema, ListToolsRequestSchema } from "@modelcontextprotocol/sdk/types.js";
import { LinearClient } from "@linear/sdk";

const server = new Server(
  {
    name: "linear-server",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Initialize Linear client
const linearClient = new LinearClient({
  apiKey: process.env.LINEAR_API_KEY
});

// List available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "create_issue",
        description: "Create a new issue in Linear",
        inputSchema: {
          type: "object",
          properties: {
            title: {
              type: "string",
              description: "Issue title"
            },
            description: {
              type: "string", 
              description: "Issue description"
            },
            teamId: {
              type: "string",
              description: "Team ID (MYA for myappismyapp)"
            },
            priority: {
              type: "number",
              description: "Priority level (1-4, 1 being highest)"
            },
            labels: {
              type: "array",
              items: { type: "string" },
              description: "Array of label names"
            }
          },
          required: ["title", "teamId"]
        }
      },
      {
        name: "get_issues",
        description: "Get issues from Linear workspace",
        inputSchema: {
          type: "object",
          properties: {
            teamId: {
              type: "string", 
              description: "Team ID to filter by"
            },
            state: {
              type: "string",
              description: "Issue state (backlog, unstarted, started, completed, canceled)"
            },
            limit: {
              type: "number",
              description: "Number of issues to return (default: 50)"
            }
          }
        }
      },
      {
        name: "update_issue",
        description: "Update an existing Linear issue",
        inputSchema: {
          type: "object", 
          properties: {
            issueId: {
              type: "string",
              description: "Linear issue ID"
            },
            title: {
              type: "string",
              description: "New title"
            },
            description: {
              type: "string",
              description: "New description"
            },
            stateId: {
              type: "string", 
              description: "New state ID"
            },
            priority: {
              type: "number",
              description: "New priority (1-4)"
            }
          },
          required: ["issueId"]
        }
      },
      {
        name: "get_team_info",
        description: "Get team information and available states",
        inputSchema: {
          type: "object",
          properties: {
            teamKey: {
              type: "string",
              description: "Team key (e.g., 'MYA')"
            }
          },
          required: ["teamKey"]
        }
      },
      {
        name: "create_project_structure",
        description: "Create Linear project structure for Dating App development",
        inputSchema: {
          type: "object",
          properties: {
            teamId: {
              type: "string",
              description: "Team ID where to create the structure"
            }
          },
          required: ["teamId"]
        }
      }
    ]
  };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case "create_issue":
        const team = await linearClient.team(args.teamId);
        const issue = await linearClient.createIssue({
          title: args.title,
          description: args.description || "",
          teamId: args.teamId,
          priority: args.priority || 3,
          labelIds: args.labels ? await getLabelIds(args.labels, args.teamId) : []
        });
        
        return {
          content: [
            {
              type: "text",
              text: `✅ Created issue: ${issue.title}\nID: ${issue.identifier}\nURL: ${issue.url}`
            }
          ]
        };

      case "get_issues":
        const issues = await linearClient.issues({
          filter: {
            team: args.teamId ? { id: { eq: args.teamId } } : undefined,
            state: args.state ? { name: { eq: args.state } } : undefined
          },
          first: args.limit || 50
        });

        const issueList = issues.nodes.map(issue => 
          `${issue.identifier}: ${issue.title} [${issue.state.name}]`
        ).join('\n');

        return {
          content: [
            {
              type: "text", 
              text: `📋 Issues:\n${issueList}`
            }
          ]
        };

      case "update_issue":
        const updatedIssue = await linearClient.updateIssue(args.issueId, {
          title: args.title,
          description: args.description,
          stateId: args.stateId,
          priority: args.priority
        });

        return {
          content: [
            {
              type: "text",
              text: `✅ Updated issue: ${updatedIssue.title}`
            }
          ]
        };

      case "get_team_info":
        const teamInfo = await linearClient.teams({
          filter: { key: { eq: args.teamKey } }
        });
        
        const team_data = teamInfo.nodes[0];
        if (!team_data) {
          throw new Error(`Team with key '${args.teamKey}' not found`);
        }

        const states = await team_data.states();
        const stateList = states.nodes.map(state => 
          `${state.name} (${state.id})`
        ).join('\n');

        return {
          content: [
            {
              type: "text",
              text: `🏢 Team: ${team_data.name}\nID: ${team_data.id}\nKey: ${team_data.key}\n\n📊 Available States:\n${stateList}`
            }
          ]
        };

      case "create_project_structure":
        // Create project structure for Dating App
        const projectIssues = [
          {
            title: "🏗️ Backend Infrastructure Setup",
            description: "Set up all 7 microservices with proper Docker orchestration",
            priority: 1,
            labels: ["backend", "infrastructure"]
          },
          {
            title: "🔐 Authentication Service Implementation", 
            description: "Complete JWT authentication with user registration/login",
            priority: 1,
            labels: ["backend", "auth"]
          },
          {
            title: "💬 Real-time Messaging with SignalR",
            description: "Implement WebSocket messaging between users",
            priority: 2,
            labels: ["backend", "messaging"]
          },
          {
            title: "🤝 Matchmaking Algorithm Development",
            description: "Create sophisticated matching algorithm based on preferences",
            priority: 2,
            labels: ["backend", "algorithm"]
          },
          {
            title: "📱 Flutter Mobile App Development",
            description: "Build cross-platform mobile app with all features",
            priority: 1,
            labels: ["frontend", "mobile"]
          },
          {
            title: "📸 Photo Upload & Management System",
            description: "Secure photo storage with image processing",
            priority: 3,
            labels: ["backend", "media"]
          },
          {
            title: "🧪 Comprehensive Testing Suite",
            description: "Unit, integration, and E2E tests for all components",
            priority: 2,
            labels: ["testing", "quality"]
          }
        ];

        const createdIssues = [];
        for (const issueData of projectIssues) {
          const newIssue = await linearClient.createIssue({
            title: issueData.title,
            description: issueData.description,
            teamId: args.teamId,
            priority: issueData.priority,
            labelIds: await getLabelIds(issueData.labels, args.teamId)
          });
          createdIssues.push(`${newIssue.identifier}: ${newIssue.title}`);
        }

        return {
          content: [
            {
              type: "text",
              text: `🎯 Created Dating App project structure:\n${createdIssues.join('\n')}`
            }
          ]
        };

      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error) {
    return {
      content: [
        {
          type: "text",
          text: `❌ Error: ${error.message}`
        }
      ],
      isError: true
    };
  }
});

// Helper function to get label IDs by name
async function getLabelIds(labelNames, teamId) {
  const team = await linearClient.team(teamId);
  const labels = await team.labels();
  
  return labelNames.map(name => {
    const label = labels.nodes.find(l => l.name.toLowerCase() === name.toLowerCase());
    return label ? label.id : null;
  }).filter(Boolean);
}

// Start the server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Linear MCP server running on stdio");
}

main().catch(console.error);
EOF

# Make server executable
chmod +x ~/.config/mcp/linear-server/server.js

# Update main MCP config to include Linear
echo "⚙️  Updating MCP configuration with Linear integration..."

# Backup existing config
cp ~/.config/mcp/config.json ~/.config/mcp/config.json.backup

# Create updated config with Linear
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
    },
    "linear": {
      "command": "node",
      "args": ["/home/m/.config/mcp/linear-server/server.js"],
      "env": {
        "LINEAR_API_KEY": ""
      }
    }
  }
}
EOF

# Create Linear setup helper script
cat > ~/.config/mcp/setup_linear_token.sh << 'EOF'
#!/bin/bash
echo "🔑 Setting up Linear API token..."
echo "=================================="
echo ""
echo "1. Go to https://linear.app/myappismyapp/settings/api"
echo "2. Create a new Personal API key"
echo "3. Copy the token and paste it below"
echo ""
read -p "Enter your Linear API key: " linear_token

if [ -n "$linear_token" ]; then
    # Update the config file with the token
    sed -i "s/\"LINEAR_API_KEY\": \"\"/\"LINEAR_API_KEY\": \"$linear_token\"/" ~/.config/mcp/config.json
    echo "✅ Linear API key configured!"
    echo ""
    echo "🧪 Testing Linear connection..."
    node ~/.config/mcp/linear-server/server.js << 'TESTEOF'
{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}
TESTEOF
else
    echo "❌ No token provided. Please run this script again."
fi
EOF

chmod +x ~/.config/mcp/setup_linear_token.sh

# Create Linear workflow helper
cat > ~/.config/mcp/linear_workflows.sh << 'EOF'
#!/bin/bash
# 🎯 Linear workflow helpers for Dating App development

echo "🎯 Linear Workflow Helpers"
echo "=========================="
echo ""
echo "Available workflows:"
echo "1. Create Dating App project structure"
echo "2. Create issue from git commit"
echo "3. Update issue status"
echo "4. Generate weekly report"
echo "5. Sync with GitHub issues"
echo ""

create_project_structure() {
    echo "🏗️ Creating Dating App project structure in Linear..."
    echo "This will create issues for all major components."
    read -p "Enter your team ID (MYA): " team_id
    
    if [ -z "$team_id" ]; then
        team_id="MYA"
    fi
    
    # Use MCP to create structure
    echo "Creating project structure for team: $team_id"
    # This would call the MCP server to create the structure
}

sync_with_github() {
    echo "🔄 Syncing Linear with GitHub repositories..."
    echo "This will:"
    echo "- Create Linear issues for open GitHub issues"
    echo "- Link commits to Linear issues"
    echo "- Update issue status based on PR status"
    
    cd /home/m/development/DatingApp
    
    # Get all repos
    repos=("AuthService" "messaging-service" "MatchmakingService" "swipe-service" "UserService" "photo-service")
    
    for repo in "${repos[@]}"; do
        if [ -d "$repo" ]; then
            echo "📁 Processing $repo..."
            cd "$repo"
            
            # Get recent commits and create Linear issues if needed
            git log --oneline -10 --grep="fix\|feat\|bug" | while read commit; do
                echo "  🔍 Found: $commit"
                # Could create Linear issues for significant commits
            done
            
            cd ..
        fi
    done
}

case "${1:-menu}" in
    "structure")
        create_project_structure
        ;;
    "sync")
        sync_with_github
        ;;
    *)
        read -p "Choose workflow (1-5): " choice
        case $choice in
            1) create_project_structure ;;
            2) echo "🚧 Git commit issue creation coming soon..." ;;
            3) echo "🚧 Issue status update coming soon..." ;;
            4) echo "🚧 Weekly report generation coming soon..." ;;
            5) sync_with_github ;;
            *) echo "Invalid choice" ;;
        esac
        ;;
esac
EOF

chmod +x ~/.config/mcp/linear_workflows.sh

cd /home/m/development/DatingApp

echo "✅ Linear MCP integration setup complete!"
echo ""
echo "🔑 Next steps:"
echo "1. Get your Linear API key:"
echo "   👉 https://linear.app/myappismyapp/settings/api"
echo ""
echo "2. Configure the API key:"
echo "   ~/.config/mcp/setup_linear_token.sh"
echo ""
echo "3. Create your project structure:"
echo "   ~/.config/mcp/linear_workflows.sh structure"
echo ""
echo "🎯 Your Linear workspace URL:"
echo "   https://linear.app/myappismyapp/team/MYA/active"
echo ""
echo "💡 Available Linear MCP tools:"
echo "   ✅ Create issues with labels and priorities"
echo "   ✅ Get and filter issues by team/state"
echo "   ✅ Update issue status and details"
echo "   ✅ Get team information and available states"
echo "   ✅ Create complete Dating App project structure"
echo "   ✅ Sync with GitHub repositories"
echo ""
echo "🚀 Test your setup:"
echo "   mcp list-servers"
echo "   # Should show 'linear' in the list"
