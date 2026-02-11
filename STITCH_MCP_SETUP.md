# Google Stitch MCP Setup Guide

## What is Google Stitch MCP?

**Google Stitch** is an AI-powered UI/UX design generation tool that creates professional mobile and web UI designs. The MCP (Model Context Protocol) integration lets you use it directly from Claude Code!

## ⚡ Quick Setup (5-10 minutes)

### Step 1: Authenticate with Google Cloud

Open a **NEW terminal** and run these commands:

```bash
# 1. Add gcloud to PATH
export PATH="/home/m/.stitch-mcp/google-cloud-sdk/bin:$PATH"

# 2. Login to Google Cloud (opens browser)
CLOUDSDK_CONFIG="/home/m/.stitch-mcp/config" gcloud auth login

# 3. Setup Application Default Credentials (opens browser again)
CLOUDSDK_CONFIG="/home/m/.stitch-mcp/config" gcloud auth application-default login
```

**This will open your browser TWICE:**
1. First: Login to your Google account
2. Second: Grant application permissions

### Step 2: Complete MCP Setup

After authentication, run:

```bash
cd /home/m/development/DatingApp
npx @_davideast/stitch-mcp init -c cc -t http
```

**Select**:
- Client: `claude-code` (or `cc`)
- Transport: `http`

This will:
✅ Verify your Google Cloud authentication  
✅ Generate MCP configuration for Claude Code  
✅ Set up the Stitch proxy server  

### Step 3: Verify Installation

```bash
npx @_davideast/stitch-mcp doctor
```

### Step 4: Start the Proxy Server

```bash
npx @_davideast/stitch-mcp proxy
```

Keep this terminal open! The proxy needs to run while you use Stitch.

---

## 🎨 Using Google Stitch

### In Claude Code/Desktop:

Once configured, you can ask Claude things like:

```
"Generate a modern dating app profile card with:
- Large profile photo with rounded corners
- Name and age overlay
- Match score badge (92%)
- Bio preview
- Like/Pass buttons at bottom
- Coral color scheme (#FF7F50)"
```

Stitch will:
1. Generate professional UI mockups
2. Provide HTML/CSS/Flutter code
3. Show multiple design variations
4. Export assets (images, icons, etc.)

---

## 🔧 Troubleshooting

### Authentication Failed

```bash
# Logout and reauthenticate
npx @_davideast/stitch-mcp logout
npx @_davideast/stitch-mcp init -c cc -t http
```

### Proxy Won't Start

```bash
# Check if another process is using the port
npx @_davideast/stitch-mcp doctor
```

### Permission Denied

```bash
# Ensure gcloud is in PATH
export PATH="/home/m/.stitch-mcp/google-cloud-sdk/bin:$PATH"
```

---

## 📁 Configuration Location

After setup, your MCP configuration will be at:
- **Claude Desktop**: `~/.config/Claude/claude_desktop_config.json`
- **Claude Code**: Cursor/Code settings

---

## 🚀 Next Steps

1. **Complete authentication** (browser-based, ~2 minutes)
2. **Start proxy server** (keep terminal open)
3. **Generate your first design** in Claude!

### Example First Prompt:

```
"Using Stitch, generate a Flutter ProfileCard widget for a dating app.
Should have:
- Stack layout with background image
- Gradient overlay
- Name/age text in bottom left
- Match score chip in top right
- Coral brand colors
- Modern, clean design"
```

Stitch will generate:
- Visual mockup
- Flutter code
- Multiple variations
- Export-ready assets

---

## 🎯 Why Stitch + Widgetbook = Perfect Combo

1. **Stitch**: Generate professional designs with AI
2. **Widgetbook**: Implement and maintain them in code
3. **Git**: Version control for everything

**Workflow**:
```
Stitch (AI design) → Widgetbook (implementation) → Git (persistence)
```

You get:
✅ Pro-quality designs (AI-generated)  
✅ Consistent components (Widgetbook catalog)  
✅ Full version control (Git)  
✅ Long-term maintainability (design tokens)  

---

## 🛟 Need Help?

- Stitch Docs: https://stitch.withgoogle.com/docs
- MCP Docs: https://modelcontextprotocol.io
- Issues: https://github.com/google/stitch-mcp

**Ready to start?** Open a new terminal and run the authentication commands above!
