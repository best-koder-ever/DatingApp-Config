#!/bin/bash

# This script will commit and push ALL changes (including untracked files) in all git repos under DatingApp, the Flutter app, and the root folder.
# It will clear your VS Code/Copilot file change list for a fresh start.

set -e

# List of project directories (relative to this script's location)
projects=(
  "auth-service"
  "dejting-yarp"
  "matchmaking-service"
  "swipe-service"
  "TestDataGenerator"
  "../mobile-apps/flutter/dejtingapp"
)

# Save the root directory
ROOT_DIR="$(pwd)"

# First, handle the root folder itself
if [ -d .git ]; then
  echo -e "\n--- ROOT FOLDER ---"
  git status
  git add -A
  if ! git diff --cached --quiet; then
    git commit -m "🚀 Chrome-optimized development setup and E2E testing infrastructure - $(date)"
  else
    echo "No changes to commit in root."
  fi
  branch=$(git rev-parse --abbrev-ref HEAD)
  if git remote -v | grep -q "origin"; then
    git push origin "$branch" || git push --set-upstream origin "$branch"
  else
    echo "No remote 'origin' for root, skipping push."
  fi
else
  echo "No git repo found in root folder, skipping."
fi

echo "Starting mass commit and push for all projects..."

# Optionally clean all ignored/untracked files in each repo to keep workspace clean
# CLEAN=false
# if [[ "$1" == "--clean" ]]; then
#   CLEAN=true
# fi

for project in "${projects[@]}"; do
  if [ -d "$project/.git" ]; then
    echo -e "\n--- $project ---"
    cd "$project"
    git status
    git add -A
    if ! git diff --cached --quiet; then
      git commit -m "🚀 Updated $project for Chrome-optimized dating app - $(date)"
    else
      echo "No changes to commit in $project."
    fi
    branch=$(git rev-parse --abbrev-ref HEAD)
    if git remote -v | grep -q "origin"; then
      git push origin "$branch" || git push --set-upstream origin "$branch"
    else
      echo "No remote 'origin' for $project, skipping push."
    fi
    # if $CLEAN; then
    #   echo "Cleaning ignored/untracked files in $project..."
    #   git clean -fdX
    # fi
    cd "$ROOT_DIR"
  else
    echo "No git repo found in $project, skipping."
  fi
done

echo "All done! Your file change list should now be clear. If you still see files in Copilot or VS Code, try reloading the window (Ctrl+Shift+P → Reload Window) or start a new chat safely."
