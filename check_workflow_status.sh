#!/bin/bash

echo "🚀 DATING APP CI/CD PIPELINE STATUS CHECK"
echo "==========================================="
echo ""

# Get repository info
REPO_URL="https://github.com/best-koder-ever/DatingApp-Config"
echo "📋 Repository: $REPO_URL"
echo "🔗 Actions URL: $REPO_URL/actions"
echo ""

# Check latest workflow run
echo "⚡ Latest workflow runs:"
gh run list --limit 3 2>/dev/null || echo "❌ Unable to fetch workflow status (GitHub CLI issue)"

echo ""
echo "🎯 What's being tested in the CI/CD pipeline:"
echo "  ✅ Flutter Frontend (Mobile App)"
echo "    - Code analysis and linting"
echo "    - Unit tests with coverage"
echo "    - Web build compilation"
echo ""
echo "  ✅ .NET Microservices (5 services)"
echo "    - AuthService: Authentication & JWT"
echo "    - UserService: User profiles & management"
echo "    - MatchmakingService: Dating algorithm"
echo "    - swipe-service: Like/dislike functionality"
echo "    - photo-service: Image upload & management"
echo ""
echo "  ✅ Docker Containerization"
echo "    - Building production images"
echo "    - Pushing to GitHub Container Registry"
echo ""
echo "  ✅ End-to-End Testing"
echo "    - Full system integration tests"
echo "    - API endpoint validation"
echo "    - Frontend-backend interaction"
echo ""

echo "🌟 EXPECTED OUTCOME: All green checkmarks ✅"
echo "🚀 TO VIEW LIVE: Open $REPO_URL/actions in your browser"
