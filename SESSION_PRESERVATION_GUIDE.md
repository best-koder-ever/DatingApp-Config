# 🧠 AI Session Preservation Guide

## The Problem
AI conversations reset when:
- Browser tabs close or refresh
- VS Code restarts
- Network disconnections occur
- Session timeouts happen
- Moving between devices

## The Solution Strategy

### 📋 **Essential Files to Always Include**

When starting ANY new AI conversation about this project, **ALWAYS attach these files**:

1. **`AI_CONTEXT.md`** - Complete project context (MOST IMPORTANT)
2. **`TROUBLESHOOTING.md`** - Debugging procedures  
3. **`API_DOCUMENTATION.md`** - Complete API reference
4. **`QUICK_REFERENCE.md`** - Emergency commands

### 🎯 **Perfect AI Conversation Starter Template**

Copy this template for new AI sessions:

```
Hi! I'm working on a .NET microservices dating app with Flutter frontend. 

**ATTACHED FILES:**
- AI_CONTEXT.md (complete project overview)
- TROUBLESHOOTING.md (debugging guide)
- [specific files relevant to current issue]

**CURRENT ISSUE:** [describe your problem]

**PROJECT CONTEXT:** 7 microservices (AuthService, UserService, PhotoService, MessagingService, MatchmakingService, SwipeService, YARP Gateway) with JWT authentication using "DatingApp-Issuer" and "DatingApp-Audience". Demo mode available with Swedish demo users.

Please review the attached context files first, then help me with [specific request].
```

### 💡 **Context Preservation Techniques**

#### 1. **Bookmark Key Information**
Save these locations for quick access:
- `/home/m/development/DatingApp/AI_CONTEXT.md`
- `/home/m/development/DatingApp/TROUBLESHOOTING.md`
- `/home/m/development/DatingApp/SESSION_PRESERVATION_GUIDE.md`

#### 2. **Create Session Snapshots**
Before major changes, create a snapshot:
```bash
cd /home/m/development/DatingApp
echo "## Session Snapshot - $(date)" >> SESSION_LOG.md
echo "**Current Status:** [describe what you're working on]" >> SESSION_LOG.md
echo "**Last Successful State:** [describe working state]" >> SESSION_LOG.md
echo "**Next Steps:** [list next actions]" >> SESSION_LOG.md
echo "" >> SESSION_LOG.md
```

#### 3. **Export Conversation History**
If your AI interface supports it:
- Export conversation as markdown
- Save to `/home/m/development/DatingApp/CONVERSATIONS/`
- Include date and topic in filename

#### 4. **Document Decisions**
Add important decisions to AI_CONTEXT.md:
```bash
# Add to AI_CONTEXT.md under "Recent Decisions" section
echo "- $(date): [Decision made and rationale]" >> AI_CONTEXT.md
```

### 🔄 **Recovery Workflow**

If you lose context and start fresh:

1. **Immediately attach** `AI_CONTEXT.md`
2. **State current problem** clearly
3. **Reference the documentation** created
4. **Provide current status** from these commands:
   ```bash
   cd /home/m/development/DatingApp
   ./dev_status.sh
   ```

### 🎯 **Context File Maintenance**

#### Weekly Updates
```bash
cd /home/m/development/DatingApp
# Update context with current status
echo "## Weekly Update - $(date)" >> AI_CONTEXT.md
echo "**Services Status:** $(./dev_status.sh | head -5)" >> AI_CONTEXT.md
echo "**Recent Changes:** [list changes made this week]" >> AI_CONTEXT.md
```

#### Before Major Changes
```bash
# Backup current state
cp AI_CONTEXT.md "AI_CONTEXT_backup_$(date +%Y%m%d_%H%M).md"
```

### 📱 **Cross-Device Synchronization**

If working from multiple devices:

1. **Git commit** documentation changes frequently:
   ```bash
   cd /home/m/development/DatingApp
   git add AI_CONTEXT.md TROUBLESHOOTING.md API_DOCUMENTATION.md QUICK_REFERENCE.md
   git commit -m "Update AI context documentation"
   git push
   ```

2. **Cloud storage** backup for critical files
3. **Browser bookmarks** sync for quick access

### 🚨 **Emergency Context Recovery**

If you completely lose context:

1. Open `/home/m/development/DatingApp/AI_CONTEXT.md`
2. Use this exact prompt:
   ```
   I've lost my AI conversation context. I'm working on a .NET microservices dating app. 
   Here's my complete project context file - please read it and help me continue where I left off.
   
   [Attach AI_CONTEXT.md]
   
   Current issue: [describe problem]
   ```

3. The AI should immediately understand the full project scope

### 💾 **Backup Strategy**

```bash
#!/bin/bash
# Daily backup script
DATE=$(date +%Y%m%d)
BACKUP_DIR="/home/m/development/DatingApp/backups/$DATE"
mkdir -p "$BACKUP_DIR"

# Backup all context files
cp AI_CONTEXT.md "$BACKUP_DIR/"
cp TROUBLESHOOTING.md "$BACKUP_DIR/"
cp API_DOCUMENTATION.md "$BACKUP_DIR/"
cp QUICK_REFERENCE.md "$BACKUP_DIR/"

echo "Context files backed up to $BACKUP_DIR"
```

---

## 🎯 **The Golden Rule**

**NEVER start an AI conversation about this project without attaching `AI_CONTEXT.md`**

This file contains everything an AI needs to understand:
- Complete architecture
- All service configurations  
- Demo user information
- Development commands
- Troubleshooting procedures
- JWT configuration details
- File structure maps

With this file attached, any AI assistant can immediately pick up where you left off!
