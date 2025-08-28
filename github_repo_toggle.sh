#!/bin/bash

# 🎯 GitHub Repository Visibility Toggle Script
# This script toggles ALL your repositories between private and public
# PUBLIC repos = UNLIMITED GitHub Actions minutes for FREE! 🚀

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Script configuration
GITHUB_USERNAME="best-koder-ever"
SCRIPT_NAME="GitHub Repository Visibility Toggle"

echo -e "${PURPLE}🎯 $SCRIPT_NAME${NC}"
echo -e "${CYAN}=================================================${NC}"

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    echo -e "${RED}❌ GitHub CLI (gh) is not installed!${NC}"
    echo -e "${YELLOW}💡 Install with: sudo apt install gh${NC}"
    echo -e "${YELLOW}💡 Then authenticate: gh auth login${NC}"
    exit 1
fi

# Check if user is authenticated
if ! gh auth status &> /dev/null; then
    echo -e "${RED}❌ Not authenticated with GitHub CLI!${NC}"
    echo -e "${YELLOW}💡 Run: gh auth login${NC}"
    exit 1
fi

# Function to display usage
show_usage() {
    echo -e "${CYAN}Usage:${NC}"
    echo -e "  $0 ${GREEN}public${NC}     # Make ALL repos public (FREE Actions!)"
    echo -e "  $0 ${YELLOW}private${NC}    # Make ALL repos private (Limited Actions)"
    echo -e "  $0 ${BLUE}status${NC}     # Show current visibility of all repos"
    echo ""
    echo -e "${CYAN}Examples:${NC}"
    echo -e "  $0 public      # 🚀 Enable unlimited GitHub Actions"
    echo -e "  $0 private     # 🔒 Make repos private again"
    echo -e "  $0 status      # 📊 Check current repo visibility"
}

# Function to get all repositories
get_all_repos() {
    echo -e "${BLUE}📋 Fetching all repositories for $GITHUB_USERNAME...${NC}" >&2
    gh repo list "$GITHUB_USERNAME" --limit 1000 --json name,visibility,isPrivate
}

# Function to show repository status
show_repo_status() {
    echo -e "${BLUE}📊 Current Repository Visibility Status:${NC}"
    echo -e "${CYAN}=================================================${NC}"
    
    local repos_json=$(get_all_repos)
    
    # Check if we got valid JSON
    if ! echo "$repos_json" | jq empty 2>/dev/null; then
        echo -e "${RED}❌ Error fetching repositories. Response:${NC}"
        echo "$repos_json"
        return 1
    fi
    
    local public_count=0
    local private_count=0
    
    echo "$repos_json" | jq -r '.[] | "\(.name)|\(.visibility)|\(.isPrivate)"' | while IFS='|' read -r name visibility is_private; do
        if [ "$is_private" = "true" ]; then
            echo -e "🔒 ${YELLOW}$name${NC} - ${RED}PRIVATE${NC} (Limited Actions: 2,000 min/month)"
        else
            echo -e "🌍 ${GREEN}$name${NC} - ${GREEN}PUBLIC${NC} (Unlimited Actions: FREE!)"
        fi
    done
    
    echo -e "${CYAN}=================================================${NC}"
    echo -e "${GREEN}📊 Summary:${NC}"
    
    # Count repos properly
    public_count=$(echo "$repos_json" | jq '[.[] | select(.isPrivate == false)] | length')
    private_count=$(echo "$repos_json" | jq '[.[] | select(.isPrivate == true)] | length')
    total_count=$(echo "$repos_json" | jq 'length')
    
    echo -e "   ${GREEN}Public repos: $public_count${NC} (FREE Actions)"
    echo -e "   ${YELLOW}Private repos: $private_count${NC} (Limited Actions)"
    echo -e "   ${BLUE}Total repos: $total_count${NC}"
    
    if [ "$private_count" -gt 0 ]; then
        echo -e "${YELLOW}💡 Run '$0 public' to get unlimited GitHub Actions!${NC}"
    fi
}

# Function to toggle repositories to public
make_repos_public() {
    echo -e "${GREEN}🚀 Making ALL repositories PUBLIC (Unlimited GitHub Actions!)${NC}"
    echo -e "${CYAN}=================================================${NC}"
    
    local repos_json=$(get_all_repos)
    local changed_count=0
    local already_public_count=0
    
    echo "$repos_json" | jq -r '.[] | select(.isPrivate == true) | .name' | while read -r repo_name; do
        if [ ! -z "$repo_name" ]; then
            echo -e "${BLUE}🌍 Making $repo_name public...${NC}"
            if gh repo edit "$GITHUB_USERNAME/$repo_name" --visibility public --accept-visibility-change-consequences; then
                echo -e "   ${GREEN}✅ $repo_name is now PUBLIC${NC}"
                ((changed_count++))
            else
                echo -e "   ${RED}❌ Failed to make $repo_name public${NC}"
            fi
        fi
    done
    
    # Count already public repos
    already_public_count=$(echo "$repos_json" | jq '[.[] | select(.isPrivate == false)] | length')
    
    echo -e "${CYAN}=================================================${NC}"
    echo -e "${GREEN}🎉 Operation Complete!${NC}"
    echo -e "   ${GREEN}Already public: $already_public_count repos${NC}"
    echo -e "   ${BLUE}Changed to public: Files processed${NC}"
    echo -e "${YELLOW}🚀 You now have UNLIMITED GitHub Actions minutes!${NC}"
    echo -e "${YELLOW}💡 All your CI/CD pipelines will run for FREE!${NC}"
}

# Function to toggle repositories to private
make_repos_private() {
    echo -e "${YELLOW}🔒 Making ALL repositories PRIVATE${NC}"
    echo -e "${CYAN}=================================================${NC}"
    echo -e "${RED}⚠️  WARNING: This will limit GitHub Actions to 2,000 min/month${NC}"
    
    read -p "Are you sure you want to make all repos private? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}🚫 Operation cancelled${NC}"
        exit 0
    fi
    
    local repos_json=$(get_all_repos)
    local changed_count=0
    local already_private_count=0
    
    echo "$repos_json" | jq -r '.[] | select(.isPrivate == false) | .name' | while read -r repo_name; do
        if [ ! -z "$repo_name" ]; then
            echo -e "${YELLOW}🔒 Making $repo_name private...${NC}"
            if gh repo edit "$GITHUB_USERNAME/$repo_name" --visibility private --accept-visibility-change-consequences; then
                echo -e "   ${GREEN}✅ $repo_name is now PRIVATE${NC}"
                ((changed_count++))
            else
                echo -e "   ${RED}❌ Failed to make $repo_name private${NC}"
            fi
        fi
    done
    
    # Count already private repos
    already_private_count=$(echo "$repos_json" | jq '[.[] | select(.isPrivate == true)] | length')
    
    echo -e "${CYAN}=================================================${NC}"
    echo -e "${GREEN}🎉 Operation Complete!${NC}"
    echo -e "   ${YELLOW}Already private: $already_private_count repos${NC}"
    echo -e "   ${BLUE}Changed to private: Files processed${NC}"
    echo -e "${RED}⚠️  GitHub Actions now limited to 2,000 min/month${NC}"
}

# Main script logic
case "${1:-}" in
    "public")
        make_repos_public
        echo ""
        show_repo_status
        ;;
    "private")
        make_repos_private
        echo ""
        show_repo_status
        ;;
    "status")
        show_repo_status
        ;;
    "--help"|"-h"|"")
        show_usage
        echo ""
        show_repo_status
        ;;
    *)
        echo -e "${RED}❌ Invalid option: $1${NC}"
        echo ""
        show_usage
        exit 1
        ;;
esac

echo -e "${PURPLE}✨ GitHub Repository Toggle Complete! ✨${NC}"
