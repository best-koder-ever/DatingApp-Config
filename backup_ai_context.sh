#!/bin/bash

# 🧠 AI Context Backup Script
# Preserves all AI conversation context for future sessions

DATE=$(date +%Y%m%d_%H%M)
BACKUP_DIR="/home/m/development/DatingApp/ai_context_backups/$DATE"

echo "🧠 Creating AI Context Backup..."
mkdir -p "$BACKUP_DIR"

# Backup all context files
echo "📋 Backing up context files..."
cp AI_CONTEXT.md "$BACKUP_DIR/" 2>/dev/null || echo "⚠️  AI_CONTEXT.md not found"
cp TROUBLESHOOTING.md "$BACKUP_DIR/" 2>/dev/null || echo "⚠️  TROUBLESHOOTING.md not found"
cp API_DOCUMENTATION.md "$BACKUP_DIR/" 2>/dev/null || echo "⚠️  API_DOCUMENTATION.md not found"
cp QUICK_REFERENCE.md "$BACKUP_DIR/" 2>/dev/null || echo "⚠️  QUICK_REFERENCE.md not found"
cp SESSION_PRESERVATION_GUIDE.md "$BACKUP_DIR/" 2>/dev/null || echo "⚠️  SESSION_PRESERVATION_GUIDE.md not found"

# Create session snapshot
echo "📸 Creating session snapshot..."
cat > "$BACKUP_DIR/SESSION_SNAPSHOT.md" << EOF
# Session Snapshot - $DATE

## Current Working Directory
$(pwd)

## Git Status
$(git status --short 2>/dev/null || echo "Not a git repository")

## Recent Commands (from history)
$(history | tail -10)

## Service Status
$(./dev_status.sh 2>/dev/null || echo "dev_status.sh not available")

## Environment Variables
DEMO_MODE=${DEMO_MODE:-"not set"}

## Next Session Instructions
1. Attach AI_CONTEXT.md to new AI conversation
2. Reference this snapshot for current state
3. Continue with: [ADD YOUR CURRENT TASK HERE]

## Notes
[ADD ANY IMPORTANT NOTES FOR NEXT SESSION]
EOF

# Create quick restore instructions
cat > "$BACKUP_DIR/RESTORE_INSTRUCTIONS.md" << EOF
# 🔄 How to Restore This AI Context

## For New AI Conversation:

1. **Attach these files to AI chat:**
   - AI_CONTEXT.md (MOST IMPORTANT)
   - TROUBLESHOOTING.md  
   - SESSION_SNAPSHOT.md

2. **Use this prompt:**
   \`\`\`
   Hi! I'm continuing work on my .NET microservices dating app project.
   
   ATTACHED: Complete project context files including AI_CONTEXT.md
   
   Please review the attached context files first. The project has 7 microservices 
   with JWT authentication using "DatingApp-Issuer" and "DatingApp-Audience".
   
   Current status from my session snapshot: [check SESSION_SNAPSHOT.md]
   
   I need help with: [YOUR CURRENT ISSUE]
   \`\`\`

3. **The AI should immediately understand everything!**

## Quick Project Overview:
- 7 microservices: AuthService, UserService, PhotoService, MessagingService, MatchmakingService, SwipeService, YARP Gateway
- Flutter mobile app frontend  
- JWT with RSA-256 signing
- Demo mode with Swedish demo users
- Complete documentation suite created
EOF

echo "✅ Backup created in: $BACKUP_DIR"
echo ""
echo "📋 Files backed up:"
ls -la "$BACKUP_DIR"
echo ""
echo "🎯 To restore context in new AI session:"
echo "   1. Attach AI_CONTEXT.md"
echo "   2. Reference SESSION_SNAPSHOT.md"
echo "   3. Use RESTORE_INSTRUCTIONS.md as template"
echo ""
echo "💡 Pro tip: Bookmark this location for quick access!"
