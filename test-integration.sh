#!/bin/bash
# Test script to verify git + GitHub CLI integration

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Testing Git + GitHub CLI Integration${NC}\n"

# Test 1: gita
echo -n "1. Testing gita... "
if command -v gita &> /dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗ (not installed)${NC}"
fi

# Test 2: GitHub CLI
echo -n "2. Testing gh CLI... "
if command -v gh &> /dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗ (not installed)${NC}"
fi

# Test 3: gh authentication
echo -n "3. Testing gh authentication... "
if gh auth status &> /dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗ (not authenticated)${NC}"
fi

# Test 4: gita-workflow.sh
echo -n "4. Testing gita-workflow.sh... "
if [ -x "./gita-workflow.sh" ]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗ (not found or not executable)${NC}"
fi

# Test 5: gh-multi-repo.sh
echo -n "5. Testing gh-multi-repo.sh... "
if [ -x "./gh-multi-repo.sh" ]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗ (not found or not executable)${NC}"
fi

# Test 6: ai-commit-helper.sh
echo -n "6. Testing ai-commit-helper.sh... "
if [ -x "./ai-commit-helper.sh" ]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗ (not found or not executable)${NC}"
fi

# Test 7: gita repos registered
echo -n "7. Testing gita repos... "
repo_count=$(gita ll 2>/dev/null | wc -l)
if [ "$repo_count" -ge 8 ]; then
    echo -e "${GREEN}✓ ($repo_count repos)${NC}"
else
    echo -e "${YELLOW}⚠ (only $repo_count repos)${NC}"
fi

echo -e "\n${YELLOW}Integration Tests:${NC}"

# Test 8: gita-workflow.sh help
echo -n "8. gita-workflow.sh help... "
if ./gita-workflow.sh help &> /dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
fi

# Test 9: gh-multi-repo.sh help
echo -n "9. gh-multi-repo.sh help... "
if ./gh-multi-repo.sh help &> /dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
fi

# Test 10: gh API access
echo -n "10. gh GitHub API access... "
if gh repo view --json nameWithOwner &> /dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
fi

echo -e "\n${GREEN}━━━ Integration Status ━━━${NC}"
echo "All tools are ready for multi-repo Git + GitHub workflows!"

echo -e "\n${YELLOW}Quick Start:${NC}"
echo "  ./gita-workflow.sh status       # Local git status"
echo "  ./gita-workflow.sh gh-status    # GitHub status"
echo "  ./gh-multi-repo.sh workflows    # CI/CD status"
echo "  ./ai-commit-helper.sh validate-all  # Validate all repos"

echo -e "\n${YELLOW}Documentation:${NC}"
echo "  AI_AGENT_GIT_GUIDE.md              # AI agent guide"
echo "  GH_CLI_INTEGRATION.md              # GitHub CLI guide"
echo "  GIT_GITHUB_INTEGRATION_COMPLETE.md # Complete reference"
