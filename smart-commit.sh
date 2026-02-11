#!/bin/bash
# Smart commit script with better practices

set -e

# Configuration
REPOS=(
  "AuthService"
  "UserService"
  "MatchmakingService"
  "dejting-yarp"
  "messaging-service"
  "swipe-service"
  "photo-service"
  "TestDataGenerator"
  "../mobile-apps/flutter/dejtingapp"
)

ROOT_DIR="/home/m/development/DatingApp"
cd "$ROOT_DIR"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check and commit a repo
process_repo() {
  local repo=$1
  local repo_path
  
  if [[ "$repo" == ../* ]]; then
    repo_path="$ROOT_DIR/$repo"
  else
    repo_path="$ROOT_DIR/$repo"
  fi
  
  if [ ! -d "$repo_path/.git" ]; then
    echo -e "${YELLOW}⚠ Skipping $repo (not a git repo)${NC}"
    return
  fi
  
  cd "$repo_path"
  
  # Check for changes
  if [ -z "$(git status --porcelain)" ]; then
    echo -e "${GREEN}✓ $repo - No changes${NC}"
    return
  fi
  
  echo -e "\n${YELLOW}━━━ $repo ━━━${NC}"
  git status --short
  
  # Interactive mode: ask for commit message
  if [ "$INTERACTIVE" = true ]; then
    read -p "Commit message for $repo (skip to skip): " msg
    if [ -z "$msg" ]; then
      echo -e "${YELLOW}⊘ Skipped${NC}"
      return
    fi
  else
    # Auto-generate meaningful commit message
    changed_files=$(git status --porcelain | wc -l)
    msg="[Auto] Update $repo - $changed_files file(s) changed - $(date +%Y-%m-%d)"
  fi
  
  git add -A
  git commit -m "$msg"
  
  # Push if requested
  if [ "$PUSH" = true ]; then
    local branch=$(git rev-parse --abbrev-ref HEAD)
    if git remote | grep -q "origin"; then
      echo -e "${GREEN}⬆ Pushing to origin/$branch${NC}"
      git push origin "$branch" -q 2>&1 || git push --set-upstream origin "$branch" -q 2>&1
    fi
  fi
  
  echo -e "${GREEN}✓ Committed${NC}"
}

# Parse arguments
INTERACTIVE=false
PUSH=false

while [[ $# -gt 0 ]]; do
  case $1 in
    -i|--interactive)
      INTERACTIVE=true
      shift
      ;;
    -p|--push)
      PUSH=true
      shift
      ;;
    -h|--help)
      echo "Usage: $0 [-i|--interactive] [-p|--push]"
      echo "  -i, --interactive  Ask for commit message for each repo"
      echo "  -p, --push        Push after committing"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

echo -e "${GREEN}🚀 Processing repositories...${NC}\n"

# Process each repository
for repo in "${REPOS[@]}"; do
  process_repo "$repo"
  cd "$ROOT_DIR"
done

# Handle root repo
echo -e "\n${YELLOW}━━━ ROOT (DatingApp) ━━━${NC}"
if [ -n "$(git status --porcelain)" ]; then
  git status --short
  if [ "$INTERACTIVE" = true ]; then
    read -p "Commit message for root: " msg
    if [ -n "$msg" ]; then
      git add -A
      git commit -m "$msg"
      if [ "$PUSH" = true ]; then
        git push origin "$(git rev-parse --abbrev-ref HEAD)" -q 2>&1
      fi
    fi
  else
    git add -A
    git commit -m "[Auto] Update root - $(date +%Y-%m-%d)"
    if [ "$PUSH" = true ]; then
      git push origin "$(git rev-parse --abbrev-ref HEAD)" -q 2>&1
    fi
  fi
  echo -e "${GREEN}✓ Root committed${NC}"
else
  echo -e "${GREEN}✓ ROOT - No changes${NC}"
fi

echo -e "\n${GREEN}✅ All done!${NC}"
