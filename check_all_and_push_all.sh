#!/bin/bash

# Exit immediately if a command fails
set -e

# List of project directories
projects=("auth-service" "dejting-yarp" "user-service" "matchmaking-service" "swipe-service")

# Navigate to the root directory
cd ~/development/DatingApp/

# Loop through each project directory
for project in "${projects[@]}"; do
  echo "Checking project: $project"
  if [ -d "$project" ]; then
    cd $project

    # Check for uncommitted changes
    if [ -n "$(git status --porcelain)" ]; then
      echo "Changes detected in $project. Committing and pushing..."
      
      # Stage all changes, including untracked files
      git add -A
      
      # Commit changes with a detailed message
      git commit -m "Update $project: $(date). Modified files: $(git diff --name-only)"
      
      # Push changes to the main branch
      git push origin main
    else
      echo "No changes to commit for $project"
    fi

    # Navigate back to the root directory
    cd ..
  else
    echo "Directory $project does not exist. Skipping..."
  fi
done