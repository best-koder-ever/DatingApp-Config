#!/bin/bash
# GitHub CLI helper for multi-repo management
# Integrates gh with gita for powerful repository operations

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Service repos
SERVICES=(
  "AuthService"
  "UserService"
  "MatchmakingService"
  "dejting-yarp"
  "messaging-service"
  "swipe-service"
  "photo-service"
  "TestDataGenerator"
)

ROOT_DIR="/home/m/development/DatingApp"

show_help() {
  cat << EOF
${GREEN}GitHub CLI Multi-Repo Helper${NC}

Usage: $0 <command> [options]

Commands:
  ${BLUE}status${NC}        Show GitHub status for all repos (issues, PRs)
  ${BLUE}issues${NC}        List open issues across all repos
  ${BLUE}prs${NC}           List open pull requests across all repos
  ${BLUE}create-pr${NC}     Create PR in current repo
  ${BLUE}sync${NC}          Sync all repos with GitHub (fetch + pull)
  ${BLUE}workflows${NC}     Show GitHub Actions workflow status
  ${BLUE}releases${NC}      List latest releases for all repos
  ${BLUE}clone-all${NC}     Clone all service repos (for new setup)
  ${BLUE}repo-info${NC}     Show detailed info for all repos

Examples:
  $0 status          # GitHub status overview
  $0 issues          # All open issues
  $0 create-pr       # Create PR from current branch
  $0 workflows       # Check CI/CD status
  $0 sync            # Pull latest from all repos

EOF
}

check_auth() {
  if ! gh auth status >/dev/null 2>&1; then
    echo -e "${RED}GitHub CLI not authenticated!${NC}"
    echo "Run: gh auth login"
    exit 1
  fi
}

repo_status() {
  echo -e "${BLUE}━━━ GitHub Repository Status ━━━${NC}\n"
  
  for service in "${SERVICES[@]}"; do
    if [ -d "$ROOT_DIR/$service/.git" ]; then
      cd "$ROOT_DIR/$service"
      
      # Check if it's a GitHub repo
      if git remote get-url origin 2>/dev/null | grep -q "github.com"; then
        echo -e "${YELLOW}$service${NC}"
        
        # Get repo info
        gh repo view --json nameWithOwner,description,isPrivate,updatedAt \
          --template '  Repo: {{.nameWithOwner}}{{"\n"}}  Updated: {{.updatedAt | timefmt "2006-01-02"}}{{"\n"}}' 2>/dev/null || \
          echo "  (Unable to fetch repo info)"
        
        # Count issues and PRs
        issues=$(gh issue list --limit 1000 --json number 2>/dev/null | jq '. | length' || echo "0")
        prs=$(gh pr list --limit 1000 --json number 2>/dev/null | jq '. | length' || echo "0")
        
        echo -e "  Issues: $issues  |  PRs: $prs"
        echo ""
      fi
      cd "$ROOT_DIR"
    fi
  done
}

list_issues() {
  echo -e "${BLUE}━━━ Open Issues Across All Repos ━━━${NC}\n"
  
  for service in "${SERVICES[@]}"; do
    if [ -d "$ROOT_DIR/$service/.git" ]; then
      cd "$ROOT_DIR/$service"
      
      if git remote get-url origin 2>/dev/null | grep -q "github.com"; then
        local_issues=$(gh issue list --limit 10 --json number,title,labels \
          --template '{{range .}}  #{{.number}} {{.title}}{{"\n"}}{{end}}' 2>/dev/null)
        
        if [ -n "$local_issues" ]; then
          echo -e "${YELLOW}$service:${NC}"
          echo "$local_issues"
          echo ""
        fi
      fi
      cd "$ROOT_DIR"
    fi
  done
}

list_prs() {
  echo -e "${BLUE}━━━ Open Pull Requests Across All Repos ━━━${NC}\n"
  
  for service in "${SERVICES[@]}"; do
    if [ -d "$ROOT_DIR/$service/.git" ]; then
      cd "$ROOT_DIR/$service"
      
      if git remote get-url origin 2>/dev/null | grep -q "github.com"; then
        local_prs=$(gh pr list --limit 10 --json number,title,headRefName,state \
          --template '{{range .}}  #{{.number}} [{{.headRefName}}] {{.title}} ({{.state}}){{"\n"}}{{end}}' 2>/dev/null)
        
        if [ -n "$local_prs" ]; then
          echo -e "${YELLOW}$service:${NC}"
          echo "$local_prs"
          echo ""
        fi
      fi
      cd "$ROOT_DIR"
    fi
  done
}

create_pr() {
  if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}Not in a git repository${NC}"
    exit 1
  fi
  
  local current_branch=$(git rev-parse --abbrev-ref HEAD)
  
  if [ "$current_branch" = "main" ] || [ "$current_branch" = "master" ]; then
    echo -e "${RED}Cannot create PR from main/master branch${NC}"
    echo "Create a feature branch first: git checkout -b feature/your-feature"
    exit 1
  fi
  
  echo -e "${YELLOW}Creating PR for branch: $current_branch${NC}"
  
  # Push current branch
  git push -u origin "$current_branch" 2>&1
  
  # Create PR interactively
  gh pr create --web
}

sync_all() {
  echo -e "${BLUE}Syncing all repos with GitHub...${NC}\n"
  
  for service in "${SERVICES[@]}"; do
    if [ -d "$ROOT_DIR/$service/.git" ]; then
      echo -e "${YELLOW}━━━ $service ━━━${NC}"
      cd "$ROOT_DIR/$service"
      
      git fetch --all --prune
      
      local branch=$(git rev-parse --abbrev-ref HEAD)
      if [ "$branch" = "main" ] || [ "$branch" = "master" ]; then
        git pull origin "$branch"
        echo -e "${GREEN}✓ Synced${NC}\n"
      else
        echo -e "${YELLOW}⚠ On branch '$branch', skipping pull${NC}\n"
      fi
      
      cd "$ROOT_DIR"
    fi
  done
}

list_workflows() {
  echo -e "${BLUE}━━━ GitHub Actions Workflow Status ━━━${NC}\n"
  
  for service in "${SERVICES[@]}"; do
    if [ -d "$ROOT_DIR/$service/.git" ]; then
      cd "$ROOT_DIR/$service"
      
      if git remote get-url origin 2>/dev/null | grep -q "github.com"; then
        local runs=$(gh run list --limit 5 --json workflowName,status,conclusion,createdAt \
          --template '{{range .}}  {{.workflowName}}: {{.status}} ({{.conclusion}}){{"\n"}}{{end}}' 2>/dev/null)
        
        if [ -n "$runs" ]; then
          echo -e "${YELLOW}$service:${NC}"
          echo "$runs"
          echo ""
        fi
      fi
      cd "$ROOT_DIR"
    fi
  done
}

list_releases() {
  echo -e "${BLUE}━━━ Latest Releases ━━━${NC}\n"
  
  for service in "${SERVICES[@]}"; do
    if [ -d "$ROOT_DIR/$service/.git" ]; then
      cd "$ROOT_DIR/$service"
      
      if git remote get-url origin 2>/dev/null | grep -q "github.com"; then
        local release=$(gh release list --limit 1 --json tagName,name,publishedAt \
          --template '{{range .}}  {{.tagName}} - {{.name}} ({{.publishedAt | timefmt "2006-01-02"}}){{"\n"}}{{end}}' 2>/dev/null)
        
        if [ -n "$release" ]; then
          echo -e "${YELLOW}$service:${NC}"
          echo "$release"
        else
          echo -e "${YELLOW}$service:${NC}  No releases"
        fi
        echo ""
      fi
      cd "$ROOT_DIR"
    fi
  done
}

clone_all() {
  echo -e "${BLUE}Cloning all service repositories...${NC}\n"
  
  local ORG="best-koder-ever"
  
  cd "$ROOT_DIR"
  
  for service in "${SERVICES[@]}"; do
    if [ ! -d "$service" ]; then
      echo -e "${YELLOW}Cloning $service...${NC}"
      gh repo clone "$ORG/$service" "$service" || echo "  Failed to clone (might not exist)"
    else
      echo -e "${GREEN}$service already exists${NC}"
    fi
  done
  
  echo -e "\n${GREEN}✓ Clone complete${NC}"
}

repo_info() {
  echo -e "${BLUE}━━━ Detailed Repository Information ━━━${NC}\n"
  
  for service in "${SERVICES[@]}"; do
    if [ -d "$ROOT_DIR/$service/.git" ]; then
      cd "$ROOT_DIR/$service"
      
      if git remote get-url origin 2>/dev/null | grep -q "github.com"; then
        echo -e "${YELLOW}$service${NC}"
        gh repo view --json name,description,url,isPrivate,defaultBranchRef,stargazerCount,forkCount \
          --template 'Name: {{.name}}
URL: {{.url}}
Default Branch: {{.defaultBranchRef.name}}
Stars: {{.stargazerCount}} | Forks: {{.forkCount}}
Private: {{.isPrivate}}
Description: {{.description}}
' 2>/dev/null || echo "  (Unable to fetch info)"
        echo ""
      fi
      cd "$ROOT_DIR"
    fi
  done
}

# Main command dispatch
check_auth

case "${1:-help}" in
  status)
    repo_status
    ;;
  issues)
    list_issues
    ;;
  prs)
    list_prs
    ;;
  create-pr)
    create_pr
    ;;
  sync)
    sync_all
    ;;
  workflows)
    list_workflows
    ;;
  releases)
    list_releases
    ;;
  clone-all)
    clone_all
    ;;
  repo-info)
    repo_info
    ;;
  help|-h|--help)
    show_help
    ;;
  *)
    echo -e "${RED}Unknown command: $1${NC}\n"
    show_help
    exit 1
    ;;
esac
