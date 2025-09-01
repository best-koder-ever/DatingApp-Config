#!/bin/bash
# 🤖 Dual AI Development Setup Script
# Sets up Gemini CLI + GitHub Copilot integration for your dating app

echo "🚀 Setting up Dual AI Development Environment"
echo "============================================="
echo "Copilot (VS Code) + Gemini CLI for your dating app"
echo ""

# Function to check if Gemini CLI is installed
check_gemini_cli() {
    if command -v gemini &> /dev/null; then
        echo "✅ Gemini CLI is already installed"
        gemini --version 2>/dev/null || echo "   (Version check failed, but command exists)"
        return 0
    else
        echo "❌ Gemini CLI not found"
        return 1
    fi
}

# Function to install Gemini CLI
install_gemini_cli() {
    echo "📦 Installing Gemini CLI..."
    
    # Check if npm is available
    if command -v npm &> /dev/null; then
        echo "Using npm to install Gemini CLI..."
        npm install -g @google/generative-ai-cli
    elif command -v npx &> /dev/null; then
        echo "Using npx to install Gemini CLI..."
        npx @google/generative-ai-cli
    else
        echo "❌ npm/npx not found. Please install Node.js first:"
        echo "   curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -"
        echo "   sudo apt-get install -y nodejs"
        return 1
    fi
}

# Function to set up useful aliases
setup_aliases() {
    echo "🔧 Setting up AI development aliases..."
    
    ALIAS_FILE="$HOME/.ai_development_aliases"
    
    cat > "$ALIAS_FILE" << 'EOF'
# 🤖 AI Development Aliases for Dating App
# Add to your .bashrc or .zshrc: source ~/.ai_development_aliases

# Gemini CLI shortcuts for dating app development
alias ai-review="gemini 'Review my latest dating app changes for best practices and security'"
alias ai-plan="gemini 'Help me plan the next feature for my dating app. Current tech: .NET microservices + Flutter mobile'"
alias ai-debug="gemini 'Help me debug this dating app issue: '"
alias ai-optimize="gemini 'Suggest performance optimizations for my dating app architecture'"
alias ai-security="gemini 'Review my dating app for security vulnerabilities and best practices'"
alias ai-scale="gemini 'How can I improve my dating app scalability for 10k+ concurrent users?'"

# Combined workflow aliases
alias ai-feature="ai-plan && echo 'Now implement with GitHub Copilot in VS Code!'"
alias ai-commit="ai-review && echo 'If review looks good, commit your changes!'"

# Dating app specific AI prompts
alias ai-matching="gemini 'Optimize my dating app matching algorithm for better accuracy'"
alias ai-realtime="gemini 'Best practices for real-time messaging in dating apps'"
alias ai-mobile="gemini 'Flutter dating app UI/UX best practices and performance tips'"
alias ai-backend="gemini 'Dating app .NET microservices architecture optimization'"

# Development workflow
alias dev-cycle="echo '🚀 AI Development Cycle:'; echo '1. ai-plan (planning)'; echo '2. Code with Copilot'; echo '3. ai-review (before commit)'; echo '4. ./github_helpers.sh pro (CI/CD)'"
EOF

    echo "✅ AI aliases created in $ALIAS_FILE"
    echo "💡 Add this to your .bashrc or .zshrc:"
    echo "   echo 'source $ALIAS_FILE' >> ~/.bashrc"
    echo ""
}

# Function to set up VS Code integration
setup_vscode_integration() {
    echo "🔧 Setting up VS Code integration..."
    
    VSCODE_SETTINGS="$HOME/.vscode/settings.json"
    VSCODE_DIR="$HOME/.vscode"
    
    # Create .vscode directory if it doesn't exist
    mkdir -p "$VSCODE_DIR"
    
    # Create or update VS Code settings for optimal Copilot + Gemini workflow
    cat > "$VSCODE_SETTINGS" << 'EOF'
{
    "github.copilot.enable": {
        "*": true,
        "yaml": true,
        "plaintext": false,
        "markdown": true,
        "csharp": true,
        "dart": true,
        "dockerfile": true
    },
    "github.copilot.advanced": {
        "debug.overrideEngine": "copilot-chat"
    },
    "terminal.integrated.defaultProfile.linux": "bash",
    "terminal.integrated.profiles.linux": {
        "bash": {
            "path": "/bin/bash",
            "args": ["-l"]
        }
    },
    "files.associations": {
        "*.md": "markdown",
        "github_helpers.sh": "shellscript",
        "Dockerfile": "dockerfile"
    },
    "editor.suggestSelection": "first",
    "editor.tabCompletion": "on",
    "editor.wordBasedSuggestions": false
}
EOF

    echo "✅ VS Code settings configured for optimal AI development"
    echo "📝 Enhanced Copilot settings for your dating app tech stack"
    echo ""
}

# Function to create AI development cheat sheet
create_cheat_sheet() {
    echo "📝 Creating AI development cheat sheet..."
    
    cat > "$HOME/ai_development_cheatsheet.md" << 'EOF'
# 🤖 AI Development Cheat Sheet for Dating App

## Quick Commands

### GitHub Helpers with AI
```bash
./github_helpers.sh ar    # AI code review
./github_helpers.sh ap    # AI feature planning  
./github_helpers.sh ao    # AI optimization
./github_helpers.sh pro   # Professional CI/CD
```

### Direct Gemini Commands
```bash
ai-review                 # Review latest changes
ai-plan                   # Plan next features
ai-debug "issue here"     # Debug help
ai-optimize               # Performance suggestions
```

## Development Workflow

### 1. Planning Phase
```bash
ai-plan                   # Get feature ideas
./github_helpers.sh ap    # Detailed planning
```

### 2. Implementation Phase
- Open VS Code
- Use GitHub Copilot for real-time assistance
- Write comments to guide Copilot suggestions

### 3. Review Phase
```bash
ai-review                 # Code review
./github_helpers.sh ar    # Comprehensive review
```

### 4. Deployment Phase
```bash
./github_helpers.sh pro   # Professional CI/CD
```

## Dating App Specific Prompts

### Architecture
```bash
gemini "How should I structure my dating app for 100k users?"
gemini "Best microservices patterns for dating apps"
```

### Features
```bash
gemini "Implement real-time matching notifications"
gemini "Optimize swipe performance in Flutter"
```

### Performance
```bash
gemini "Database optimization for user matching queries"
gemini "Flutter app performance for image-heavy profiles"
```

### Security
```bash
gemini "Dating app security best practices"
gemini "Secure photo upload and storage patterns"
```

## VS Code + Copilot Tips

1. Write descriptive comments for better suggestions
2. Use Ctrl+Space to trigger suggestions
3. Tab to accept, Escape to dismiss
4. Use Copilot Chat for complex explanations

## Pro Tips

- Start with Gemini for planning
- Implement with Copilot for speed
- Review with Gemini for quality
- Use both for complex problems
EOF

    echo "✅ Cheat sheet created: ~/ai_development_cheatsheet.md"
    echo ""
}

# Main setup flow
main() {
    echo "🎯 Setting up dual AI development for your dating app..."
    echo ""
    
    # Check current status
    echo "📋 Checking current setup..."
    check_gemini_cli
    GEMINI_INSTALLED=$?
    
    # Install Gemini CLI if needed
    if [ $GEMINI_INSTALLED -ne 0 ]; then
        echo ""
        read -p "Install Gemini CLI? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            install_gemini_cli
        fi
    fi
    
    echo ""
    read -p "Set up AI development aliases? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        setup_aliases
    fi
    
    echo ""
    read -p "Configure VS Code for optimal AI development? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        setup_vscode_integration
    fi
    
    echo ""
    read -p "Create AI development cheat sheet? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        create_cheat_sheet
    fi
    
    echo ""
    echo "🎉 Dual AI development setup complete!"
    echo ""
    echo "🚀 Next steps:"
    echo "1. Restart your terminal or run: source ~/.ai_development_aliases"
    echo "2. Test: ai-plan"
    echo "3. Test: ./github_helpers.sh ar"
    echo "4. Open VS Code and enjoy enhanced Copilot!"
    echo ""
    echo "💡 Read the cheat sheet: cat ~/ai_development_cheatsheet.md"
    echo "🤖 Your dating app development is now AI-supercharged!"
}

# Run the setup
main "$@"
