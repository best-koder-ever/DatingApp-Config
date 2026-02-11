#!/bin/bash
# AI Agent Git Helper - Validates commits before they happen

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Function to validate a single repo before commit
validate_repo() {
  local repo_path=$1
  local errors=0
  
  echo -e "${YELLOW}Validating $repo_path...${NC}"
  
  cd "$repo_path"
  
  # Check if there are changes to commit
  if [ -z "$(git status --porcelain)" ]; then
    echo -e "${GREEN}✓ No changes to commit${NC}"
    return 0
  fi
  
  # Check for build artifacts
  if git status --porcelain | grep -E "(bin/|obj/|\.dll|\.pdb|\.exe|\.cache)"; then
    echo -e "${RED}✗ ERROR: Build artifacts detected!${NC}"
    echo -e "  Run: dotnet clean or remove bin/obj folders"
    ((errors++))
  fi
  
  # Check for database files
  if git status --porcelon | grep -E "(\.db$|\.db-shm|\.db-wal|\.sqlite)"; then
    echo -e "${RED}✗ ERROR: Database files detected!${NC}"
    echo -e "  These should be in .gitignore"
    ((errors++))
  fi
  
  # Check for secrets
  if git status --porcelain | grep -E "(\.key$|\.pem$|\.env$|secrets\.json)"; then
    echo -e "${RED}✗ ERROR: Secret files detected!${NC}"
    echo -e "  NEVER commit secrets!"
    ((errors++))
  fi
  
  # Check for .gitignore
  if [ ! -f ".gitignore" ]; then
    echo -e "${YELLOW}⚠ WARNING: No .gitignore file${NC}"
    echo -e "  Consider adding one"
  fi
  
  # Show what will be committed
  echo -e "${YELLOW}Changes to be committed:${NC}"
  git status --short | head -20
  
  if [ $(git status --porcelain | wc -l) -gt 20 ]; then
    echo "  ... and $(($(git status --porcelain | wc -l) - 20)) more files"
  fi
  
  if [ $errors -gt 0 ]; then
    echo -e "${RED}✗ Validation FAILED with $errors error(s)${NC}"
    return 1
  fi
  
  echo -e "${GREEN}✓ Validation passed${NC}"
  return 0
}

# Main logic
case "${1:-validate}" in
  validate)
    # Validate current directory if it's a git repo
    if git rev-parse --git-dir > /dev/null 2>&1; then
      validate_repo "$(pwd)"
    else
      echo -e "${RED}Not in a git repository${NC}"
      exit 1
    fi
    ;;
    
  validate-all)
    # Validate all service repos
    ROOT="/home/m/development/DatingApp"
    SERVICES="AuthService UserService MatchmakingService dejting-yarp messaging-service swipe-service photo-service TestDataGenerator"
    
    all_valid=true
    for service in $SERVICES; do
      if [ -d "$ROOT/$service/.git" ]; then
        if ! validate_repo "$ROOT/$service"; then
          all_valid=false
        fi
        cd "$ROOT"
      fi
    done
    
    if $all_valid; then
      echo -e "\n${GREEN}✅ All repos validated successfully${NC}"
      exit 0
    else
      echo -e "\n${RED}❌ Some repos have validation errors${NC}"
      exit 1
    fi
    ;;
    
  safe-commit)
    # Validate and commit if safe
    if validate_repo "$(pwd)"; then
      if [ -z "$2" ]; then
        echo -e "${RED}Error: Commit message required${NC}"
        echo "Usage: $0 safe-commit \"Your commit message\""
        exit 1
      fi
      
      git add -A
      git commit -m "$2"
      echo -e "${GREEN}✓ Committed successfully${NC}"
    else
      echo -e "${RED}Commit aborted due to validation errors${NC}"
      exit 1
    fi
    ;;
    
  clean-artifacts)
    # Clean build artifacts from current repo
    if git rev-parse --git-dir > /dev/null 2>&1; then
      echo "Cleaning build artifacts..."
      
      # .NET artifacts
      find . -type d -name "bin" -exec rm -rf {} + 2>/dev/null || true
      find . -type d -name "obj" -exec rm -rf {} + 2>/dev/null || true
      find . -type f -name "*.dll" -delete 2>/dev/null || true
      find . -type f -name "*.pdb" -delete 2>/dev/null || true
      find . -type f -name "*.cache" -delete 2>/dev/null || true
      
      # Or use dotnet if available
      if command -v dotnet &> /dev/null; then
        dotnet clean --nologo -v q 2>/dev/null || true
      fi
      
      echo -e "${GREEN}✓ Cleaned${NC}"
    fi
    ;;
    
  suggest-message)
    # Suggest commit message based on changes
    if [ -z "$(git status --porcelain)" ]; then
      echo "No changes to commit"
      exit 0
    fi
    
    # Analyze changes
    added=$(git status --porcelain | grep "^A" | wc -l)
    modified=$(git status --porcelain | grep "^ M" | wc -l)
    deleted=$(git status --porcelain | grep "^ D" | wc -l)
    
    # Get changed files
    files=$(git status --porcelain | awk '{print $2}' | head -5)
    
    # Determine service name from path
    service=$(basename "$(pwd)")
    
    echo -e "${YELLOW}Suggested commit messages:${NC}"
    echo ""
    
    if [ $added -gt 0 ] && [ $modified -eq 0 ]; then
      echo "feat($service): add new functionality"
    elif [ $modified -gt 0 ] && [ $added -eq 0 ]; then
      echo "refactor($service): update implementation"
    elif [ $deleted -gt 0 ]; then
      echo "refactor($service): remove obsolete code"
    else
      echo "chore($service): update $service"
    fi
    
    echo "fix($service): correct [describe bug]"
    echo "docs($service): update documentation"
    echo "test($service): add/update tests"
    
    echo ""
    echo -e "${YELLOW}Changed files (first 5):${NC}"
    echo "$files"
    ;;
    
  *)
    cat << EOF
AI Agent Git Helper

Usage: $0 <command>

Commands:
  validate          Validate current repo for commit safety
  validate-all      Validate all service repos
  safe-commit "msg" Validate and commit if safe
  clean-artifacts   Remove build artifacts (bin/obj/dll/pdb)
  suggest-message   Get commit message suggestions
  
Examples:
  $0 validate
  $0 safe-commit "feat(auth): add JWT refresh token"
  $0 clean-artifacts
  $0 suggest-message

Exit codes:
  0 - Success/validated
  1 - Validation failed or error
  
EOF
    ;;
esac
