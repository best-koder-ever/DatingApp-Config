#!/bin/bash

# 🔄 Git Hook: Auto-update AI Context on commits
# Install: ln -sf ../../git-ai-context-hook.sh .git/hooks/post-commit

CONTEXT_FILE="/home/m/development/DatingApp/AI_CONTEXT.md"
BACKUP_DIR="/home/m/development/DatingApp/ai_context_backups"

# Get commit information
COMMIT_HASH=$(git rev-parse HEAD)
COMMIT_MSG=$(git log -1 --pretty=%B)
COMMIT_FILES=$(git diff-tree --no-commit-id --name-only -r HEAD)
AUTHOR=$(git log -1 --pretty=%an)
TIMESTAMP=$(date)

echo "🔄 Auto-updating AI context after commit..."

# Create commit-based context update
cat >> "$CONTEXT_FILE" << EOF

## 📝 Auto-Updated After Commit - $TIMESTAMP
**Commit**: $COMMIT_HASH
**Author**: $AUTHOR
**Message**: $COMMIT_MSG

**Files Changed**:
$(echo "$COMMIT_FILES" | sed 's/^/- /')

**Development Status**: Code changes committed, context auto-updated

---
EOF

# Create backup with commit info
mkdir -p "$BACKUP_DIR"
BACKUP_FILE="$BACKUP_DIR/commit_context_$(date +%Y%m%d_%H%M%S).md"

cat > "$BACKUP_FILE" << EOF
# Context Update After Commit

## Commit Details
- **Hash**: $COMMIT_HASH
- **Author**: $AUTHOR  
- **Date**: $TIMESTAMP
- **Message**: $COMMIT_MSG

## Changed Files
$COMMIT_FILES

## Project State
$(cd /home/m/development/DatingApp && ./dev_status.sh 2>/dev/null || echo "Status check not available")

## For Next AI Session
1. Reference this commit context
2. Latest changes are committed and documented
3. Ready to continue with next feature/fix
EOF

echo "✅ AI context updated and backed up: $(basename "$BACKUP_FILE")"
