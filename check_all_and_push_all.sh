#!/bin/bash

# List of project directories
projects=("auth-service" "dejting-yarp" "UserService")

# Navigate to the root directory
cd ~/development/DatingApp/

# Loop through each project directory
for project in "${projects[@]}"; do
  echo "Checking project: $project"
  cd $project

  # Check for uncommitted changes
  git status

  # Commit and push changes if any
  if [ -n "$(git status --porcelain)" ]; then
    git add .
    git commit -m "Committing changes for $project"
    git push origin main
  else
    echo "No changes to commit for $project"
  fi

  # Navigate back to the root directory
  cd ..
done