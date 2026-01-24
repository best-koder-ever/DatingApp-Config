#!/bin/bash
# Gita-based workflow for multi-repo management
# This replaces the old commit_and_push_all.sh with better practices

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

show_help() {
  cat << EOF
${GREEN}Gita Workflow Helper${NC}

Usage: $0 [COMMAND] [OPTIONS]

Commands:
  status, st         Show status of all repos
  commit, ci         Commit changes in all repos (interactive)
  commit-auto        Auto-commit with generated messages
  push               Push all repos with commits
  pull               Pull latest from all repos
  fetch              Fetch from all remotes
  sync               Pull, commit, and push everything
  clean              Clean build artifacts from all repos
  gh-status          Show GitHub status (issues, PRs) - requires gh CLI
  workflows          Check GitHub Actions status - requires gh CLI

Options:
  -h, --help         Show this help

Examples:
  $0 status                    # See what changed
  $0 commit                    # Interactively commit each repo
  $0 commit-auto               # Auto-commit with messages
  $0 sync                      # Full sync: pull, commit, push
  $0 gh-status                 # GitHub issues/PRs overview
  $0 workflows                 # CI/CD pipeline status

${YELLOW}Individual repo work:${NC}
  cd AuthService && git commit -m "Your detailed message"
  $0 push                      # Push all repos that need it

${YELLOW}For more GitHub CLI features:${NC}
  ./gh-multi-repo.sh --help
EOF
}

repo_status() {
  echo -e "${BLUE}━━━ Repository Status ━━━${NC}\n"
  gita ll
  echo ""
  gita super status --short
}

interactive_commit() {
  echo -e "${YELLOW}Interactive commit mode${NC}\n"
  
  # Get repos with changes
  changed_repos=$(gita super status --porcelain | grep -v "^$" | awk '{print $NF}' | sort -u | sed 's/:$//')
  
  if [ -z "$changed_repos" ]; then
    echo -e "${GREEN}✓ No changes to commit${NC}"
    return
  fi
  
  echo "Repos with changes:"
  echo "$changed_repos" | nl
  echo ""
  
  for repo in $changed_repos; do
    echo -e "\n${YELLOW}━━━ $repo ━━━${NC}"
    (cd "$(gita ls | grep "$repo" | awk '{print $2}')" && git status --short)
    
    read -p "Commit message (or 'skip'): " msg
    
    if [ "$msg" = "skip" ] || [ -z "$msg" ]; then
      echo -e "${YELLOW}⊘ Skipped${NC}"
      continue
    fi
    
    (cd "$(gita ls | grep "$repo" | awk '{print $2}')" && git add -A && git commit -m "$msg")
    echo -e "${GREEN}✓ Committed${NC}"
  done
}

auto_commit() {
  echo -e "${YELLOW}Auto-commit mode${NC}\n"
  
  gita super status --porcelain | grep -v "^$" | while read -r line; do
    repo=$(echo "$line" | awk '{print $NF}' | sed 's/:$//')
    repo_path=$(gita ls | grep "^$repo" | awk '{print $2}')
    
    if [ -n "$(cd "$repo_path" && git status --porcelain)" ]; then
      echo -e "${YELLOW}━━━ $repo ━━━${NC}"
      
      cd "$repo_path"
      
      # Generate smart commit message
      changed=$(git status --porcelain | wc -l)
      new_files=$(git status --porcelain | grep "^??" | wc -l)
      modified=$(git status --porcelain | grep "^ M\\|^M" | wc -l)
      
      msg="chore: update $repo"
      [ $new_files -gt 0 ] && msg="$msg - $new_files new file(s)"
      [ $modified -gt 0 ] && msg="$msg - $modified modified"
      msg="$msg - $(date +%Y-%m-%d)"
      
      git add -A
      git commit -m "$msg"
      echo -e "${GREEN}✓ $msg${NC}\n"
    fi
  done
}

push_all() {
  echo -e "${BLUE}Pushing all repos...${NC}\n"
  gita super push
  echo -e "${GREEN}✓ Push complete${NC}"
}

pull_all() {
  echo -e "${BLUE}Pulling all repos...${NC}\n"
  gita super pull
  echo -e "${GREEN}✓ Pull complete${NC}"
}

fetch_all() {
  echo -e "${BLUE}Fetching all repos...${NC}\n"
  gita super fetch
  echo -e "${GREEN}✓ Fetch complete${NC}"
}

sync_all() {
  echo -e "${GREEN}Full sync: pull → commit → push${NC}\n"
  pull_all
  echo ""
  auto_commit
  echo ""
  push_all
  echo -e "\n${GREEN}✅ Sync complete!${NC}"
}

clean_builds() {
  echo -e "${YELLOW}Cleaning build artifacts...${NC}\n"
  
  for service in AuthService UserService MatchmakingService dejting-yarp \
                 messaging-service swipe-service photo-service TestDataGenerator; do
    if [ -d "$service" ]; then
      echo "Cleaning $service..."
      ( cd "$service" && dotnet clean --nologo -v q 2>/dev/null || true )
    fi
  done
  
  echo -e "${GREEN}✓ Clean complete${NC}"
}

# GitHub CLI integration
gh_status() {
  if ! command -v gh &> /dev/null; then
    echo -e "${RED}GitHub CLI (gh) not installed${NC}"
    echo "Install with: sudo apt install gh"
    exit 1
  fi
  
  if [ ! -f "./gh-multi-repo.sh" ]; then
    echo -e "${RED}gh-multi-repo.sh not found${NC}"
    exit 1
  fi
  
  echo -e "${BLUE}Delegating to gh-multi-repo.sh...${NC}\n"
  ./gh-multi-repo.sh status
}

gh_workflows() {
  if ! command -v gh &> /dev/null; then
    echo -e "${RED}GitHub CLI (gh) not installed${NC}"
    echo "Install with: sudo apt install gh"
    exit 1
  fi
  
  if [ ! -f "./gh-multi-repo.sh" ]; then
    echo -e "${RED}gh-multi-repo.sh not found${NC}"
    exit 1
  fi
  
  echo -e "${BLUE}Delegating to gh-multi-repo.sh...${NC}\n"
  ./gh-multi-repo.sh workflows
}

# Main command dispatch
case "${1:-status}" in
  status|st)
    repo_status
    ;;
  commit|ci)
    interactive_commit
    ;;
  commit-auto)
    auto_commit
    ;;
  push)
    push_all
    ;;
  pull)
    pull_all
    ;;
  fetch)
    fetch_all
    ;;
  sync)
    sync_all
    ;;
  clean)
    clean_builds
    ;;
  gh-status)
    gh_status
    ;;
  workflows)
    gh_workflows
    ;;
  -h|--help|help)
    show_help
    ;;
  *)
    echo -e "${RED}Unknown command: $1${NC}"
    show_help
    exit 1
    ;;
esac
