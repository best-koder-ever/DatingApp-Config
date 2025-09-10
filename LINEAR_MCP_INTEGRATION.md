# 🎯 Linear MCP Integration Guide for Dating App

This guide helps you connect your .NET microservices and Flutter app with Linear project management using Model Context Protocol (MCP).

## 🚀 Quick Setup

1. **Run Linear MCP Setup:**
   ```bash
   cd /home/m/development/DatingApp
   chmod +x setup_linear_mcp.sh
   ./setup_linear_mcp.sh
   ```

2. **Get Linear API Key:**
   - Go to https://linear.app/myappismyapp/settings/api
   - Create "Personal API key" 
   - Copy the token

3. **Configure API Key:**
   ```bash
   ~/.config/mcp/setup_linear_token.sh
   ```

4. **Create Project Structure:**
   ```bash
   ~/.config/mcp/linear_workflows.sh structure
   ```

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Linear Workspace                         │
│         https://linear.app/myappismyapp/team/MYA/active     │
└─────────────────────────────────────────────────────────────┘
                                │
                          MCP Integration
                                │
┌─────────────────────────────────────────────────────────────┐
│                    MCP Server Layer                         │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │ Linear MCP  │ │   Git MCP   │ │ GitHub MCP  │           │
│  │   Server    │ │   Server    │ │   Server    │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
└─────────────────────────────────────────────────────────────┘
                                │
                    Development Environment
                                │
┌─────────────────────────────────────────────────────────────┐
│                Dating App Ecosystem                         │
│                                                             │
│  Backend Services (.NET Core 8.0):                         │
│  ├── 🔐 AuthService         (Port 5001)                   │
│  ├── 💬 messaging-service    (Port 5007)                   │
│  ├── 🤝 MatchmakingService  (Port 5003)                   │
│  ├── 👆 swipe-service        (Port 5005)                   │
│  ├── 👤 UserService         (Port 5002)                   │
│  └── 📸 photo-service        (Port 5004)                   │
│                                                             │
│  Frontend:                                                  │
│  └── 📱 Flutter App          (dejtingapp)                  │
│                                                             │
│  Infrastructure:                                            │
│  ├── 🐳 Docker Compose                                     │
│  ├── 🗄️ MySQL Databases                                    │
│  └── 🔄 SignalR WebSockets                                 │
└─────────────────────────────────────────────────────────────┘
```

## 🎯 Linear Project Structure

The MCP integration will create this issue structure in your Linear workspace:

### Epic: Dating App Development
- **🏗️ Backend Infrastructure Setup** (Priority: High)
  - Set up Docker orchestration for 7 microservices
  - Configure MySQL databases
  - Implement health checks and monitoring

- **🔐 Authentication Service** (Priority: High)
  - JWT token management
  - User registration/login
  - Password security & validation

- **💬 Real-time Messaging** (Priority: Medium)
  - SignalR WebSocket implementation
  - Message persistence
  - Content moderation

- **🤝 Matchmaking Algorithm** (Priority: Medium)
  - Compatibility scoring
  - Preference matching
  - Performance optimization

- **📱 Flutter Mobile App** (Priority: High)
  - Cross-platform UI/UX
  - API integration
  - Real-time features

- **📸 Photo Management** (Priority: Low)
  - Secure upload system
  - Image processing
  - Storage optimization

- **🧪 Testing & Quality** (Priority: Medium)
  - Unit tests for all services
  - Integration tests
  - E2E mobile testing

## 🔧 MCP Tools Available

### Linear Integration Tools:
1. **create_issue** - Create new Linear issues
2. **get_issues** - Fetch and filter issues
3. **update_issue** - Update issue status/details
4. **get_team_info** - Get team and workflow states
5. **create_project_structure** - Bootstrap complete project

### Development Tools:
1. **Git MCP** - Repository management
2. **GitHub MCP** - Issue synchronization
3. **Database MCP** - Query MySQL directly
4. **Docker MCP** - Container management
5. **Filesystem MCP** - Code navigation

## 🔄 Workflow Examples

### Creating Issues from Git Commits:
```bash
# When you commit a bug fix:
git commit -m "fix: SignalR callback type errors in messaging service"

# MCP can automatically create Linear issue:
# "🐛 Fix SignalR callback type errors"
# With context from the commit and affected files
```

### Syncing Backend Services:
```bash
# Check all service status and create Linear issues for problems:
./linear_workflows.sh sync

# Creates issues like:
# "🔧 Auth Service returning 500 errors"
# "🐳 Docker container health check failing"
```

### Project Status Updates:
```bash
# Generate weekly Linear report:
./linear_workflows.sh report

# Shows:
# - Completed issues per service
# - Blocking issues requiring attention
# - Test coverage progress
```

## 🎨 Label System

Your Linear workspace will use these labels:

- **Service Labels:**
  - `AuthService` - Authentication issues
  - `messaging-service` - Chat/messaging issues
  - `MatchmakingService` - Algorithm issues
  - `swipe-service` - User interaction issues
  - `UserService` - Profile management issues
  - `photo-service` - Media handling issues
  - `flutter-app` - Mobile app issues

- **Type Labels:**
  - `bug` - Bug fixes needed
  - `feature` - New functionality
  - `infrastructure` - DevOps/setup issues
  - `testing` - QA and testing
  - `documentation` - Docs updates

- **Priority Labels:**
  - `critical` - Production blocking
  - `high` - Important for next release
  - `medium` - Nice to have
  - `low` - Future consideration

## 📊 Integration Benefits

### For .NET Services:
- ✅ Automatic issue creation from exceptions
- ✅ Link commits to specific service issues
- ✅ Track API endpoint development
- ✅ Monitor service health in Linear

### For Flutter App:
- ✅ Track feature development progress
- ✅ Link UI issues to backend dependencies
- ✅ Manage testing across devices
- ✅ Track app store deployment

### For Project Management:
- ✅ Single source of truth for all work
- ✅ Real-time sync with development
- ✅ Automated reporting and metrics
- ✅ Clear dependencies between services

## 🔗 Key URLs

- **Linear Workspace:** https://linear.app/myappismyapp/team/MYA/active
- **MCP Config:** `~/.config/mcp/config.json`
- **API Settings:** https://linear.app/myappismyapp/settings/api
- **Team Settings:** https://linear.app/myappismyapp/team/MYA/settings

## 🚀 Next Steps

1. **Complete Setup:** Run the setup script and configure your API key
2. **Create Structure:** Bootstrap your project issues in Linear
3. **Start Development:** Begin linking commits to Linear issues
4. **Monitor Progress:** Use Linear to track development across all services
5. **Automate Workflows:** Set up automated issue creation and updates

Your dating app development will now be fully integrated with Linear for comprehensive project management! 🎯
