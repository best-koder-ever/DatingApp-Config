#!/bin/bash

# Exit immediately if a command fails
set -e

# Corrected paths for the projects
projects=("auth-service" "dejting-yarp" "user-service" "matchmaking-service" "swipe-service" "photo-service" "TestDataGenerator" "../mobile-apps/flutter/dejtingapp")
declare -A project_remotes
project_remotes["user-service"]="https://github.com/best-koder-ever/UserService.git"
project_remotes["matchmaking-service"]="https://github.com/best-koder-ever/MatchmakingService.git"
project_remotes["swipe-service"]="https://github.com/best-koder-ever/swipe-service.git"
project_remotes["auth-service"]="https://github.com/best-koder-ever/auth-service.git"
project_remotes["dejting-yarp"]="https://github.com/best-koder-ever/dejting-yarp.git"
project_remotes["photo-service"]="https://github.com/best-koder-ever/photo-service.git"
project_remotes["TestDataGenerator"]="https://github.com/best-koder-ever/TestDataGenerator.git"
project_remotes["../mobile-apps/flutter/dejtingapp"]=""

# Navigate to the root directory
cd ~/development/DatingApp/

# Loop through each project directory
for project in "${projects[@]}"; do
  echo "Checking project: $project"
  
  # Check if the directory exists
  if [ -d "$project" ]; then
    cd "$project" # Use quotes to handle potential spaces in project names

    # Ensure the directory is a Git repository
    if [ -d ".git" ]; then
      # Check if remote 'origin' is configured, if not, add it
      if ! git remote -v | grep -q "^origin\s"; then
        if [ -n "${project_remotes[$project]}" ]; then
          echo "Adding remote origin ${project_remotes[$project]} to $project"
          git remote add origin "${project_remotes[$project]}"
        else
          echo "No remote URL configured for $project. Skipping remote operations."
        fi
      fi

      # Fetch latest changes from origin
      # We'll attempt to fetch, but continue if it fails (e.g. new repo)
      git fetch origin main || echo "Could not fetch from origin/main for $project. This might be a new repository."

      # Check for uncommitted changes
      if [ -n "$(git status --porcelain)" ]; then
        echo "Changes detected in $project. Committing and pushing..."
        
        # Stage all changes, including untracked files
        git add -A
        
        # Commit changes with a detailed message
        # Ensure commit message is not empty if git diff --name-only is empty after add -A (e.g. only new files)
        commit_msg="Update $project: $(date)."
        modified_files=$(git diff --cached --name-only)
        if [ -n "$modified_files" ]; then
          commit_msg="$commit_msg Modified files: $modified_files"
        else
          commit_msg="$commit_msg New files added." # Or some other generic message
        fi
        git commit -m "$commit_msg"
        
        # Push changes to the main branch
        # Check if remote 'origin' exists before pushing
        if git remote -v | grep -q "^origin\s"; then
          git push origin main
        else
          echo "Remote 'origin' not configured for $project. Skipping push."
        fi
      else
        echo "No changes to commit for $project"
      fi
    else
      echo "Directory $project is not a Git repository. Skipping..."
      echo "Hint: Run 'git init' in $project if it should be a Git repository."
    fi

    # Navigate back to the root directory
    cd ~/development/DatingApp/
  else
    echo "Directory $project does not exist. Skipping..."
  fi
done

echo "Script finished."