#!/bin/bash
# Quick setup for AI-assisted development
# Run this after GitHub API rate limit resets

set -e

echo "🚀 DatingApp AI Development Setup"
echo "=================================="
echo ""

# Check rate limit
echo "1. Checking GitHub API rate limit..."
RATE_INFO=$(gh api rate_limit --jq '.resources.graphql | "Used: \(.used)/\(.limit), Resets at: \(.reset | strftime("%Y-%m-%d %H:%M:%S"))"')
echo "   $RATE_INFO"
echo ""

USED=$(gh api rate_limit --jq '.resources.graphql.used')
if [[ $USED -gt 4500 ]]; then
  echo "   ⚠️  Rate limit nearly exhausted. Wait for reset before running sync."
  read -p "   Continue anyway? (y/N) " -n 1 -r
  echo
  [[ ! $REPLY =~ ^[Yy]$ ]] && exit 0
fi

# Install Aider if not present
echo "2. Checking Aider installation..."
if command -v aider >/dev/null 2>&1; then
  echo "   ✅ Aider installed ($(aider --version))"
else
  echo "   📦 Installing Aider..."
  pip install aider-chat
fi
echo ""

# Check API keys
echo "3. Checking AI API keys..."
if [[ -n "${ANTHROPIC_API_KEY:-}" ]]; then
  echo "   ✅ Anthropic API key configured (Claude)"
elif [[ -n "${OPENAI_API_KEY:-}" ]]; then
  echo "   ✅ OpenAI API key configured (GPT-4)"
elif [[ -n "${GOOGLE_API_KEY:-}" ]]; then
  echo "   ✅ Google API key configured (Gemini)"
else
  echo "   ⚠️  No AI API key found"
  echo ""
  echo "   Set one of:"
  echo "     export ANTHROPIC_API_KEY='sk-ant-...'  # Recommended (Claude)"
  echo "     export OPENAI_API_KEY='sk-...'          # Alternative (GPT-4)"
  echo "     export GOOGLE_API_KEY='...'             # Alternative (Gemini)"
  echo ""
  echo "   Add to ~/.bashrc to persist"
  read -p "   Continue without API key? (y/N) " -n 1 -r
  echo
  [[ ! $REPLY =~ ^[Yy]$ ]] && exit 0
fi
echo ""

# Sync issues with rich descriptions
echo "4. Syncing tasks to GitHub Projects with rich descriptions..."
read -p "   Run sync script now? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
  bash scripts/sync_mvp_project.sh
  echo ""
  echo "   ✅ Sync complete!"
else
  echo "   ⏭️  Skipped sync (run manually: bash scripts/sync_mvp_project.sh)"
fi
echo ""

# Show next steps
echo "✅ Setup Complete!"
echo ""
echo "📋 Your GitHub Projects Board:"
echo "   https://github.com/users/best-koder-ever/projects/2"
echo ""
echo "🔧 Quick Commands:"
echo ""
echo "   # View a rich issue"
echo "   gh issue view 7 --web"
echo ""
echo "   # Implement with CLI agent (Aider)"
echo "   ./scripts/implement_task.sh T024"
echo ""
echo "   # Delegate to GitHub Copilot"
echo "   gh issue comment 7 --body '@copilot implement this'"
echo ""
echo "   # Check what's ready to work on"
echo "   gh issue list --repo best-koder-ever/DatingApp-Config --label 'ai-ready' --state open"
echo ""
echo "📚 Documentation:"
echo "   - AI Strategy: docs/AI_AGENT_STRATEGY.md"
echo "   - CLI Setup: docs/CLI_AGENT_SETUP.md"
echo "   - Issue Tracking: docs/ENHANCED_ISSUE_TRACKING.md"
echo ""
echo "🎯 Recommended First Tasks:"
echo "   T015 - Documentation (GitHub Copilot) - Test async delegation"
echo "   T024 - Photo moderation (Aider CLI) - Test local iteration"
echo ""
echo "Happy coding! 🚀"
