#!/bin/bash
# 🧠 Smart AI Memory System for Dating App Development
# Automatically tracks code changes, git history, and project progress

echo "🧠 SMART AI MEMORY SYSTEM"
echo "========================="

# Function to generate automatic project context for AI  
generate_ai_context() {
    local context_file="$HOME/.dating_app_context.md"
    
    echo "📊 Generating comprehensive project context for AI..."
    
    cat > "$context_file" << EOF
# 💕 Dating App Development Context
Generated: $(date)
Project: $(pwd)

## 🔄 Development Session History
$(tail -20 "$HOME/.dating_app_memory.log" 2>/dev/null || echo "First session")

## 📈 Recent Code Changes  
$(git log --oneline -15 --pretty=format:"%h %s (%cr)")

## 🌟 Current Branch Status
Branch: $(git branch --show-current)
Uncommitted changes: $(git status --porcelain | wc -l) files
$(git status --porcelain | head -10)

## 🏗️ Project Architecture
Services:
$(ls -la | grep -E "(auth-service|matchmaking-service|dejting-yarp|TestDataGenerator)" | awk '{print "  - " $9}')

Flutter App:
$(ls -la ../mobile-apps/flutter/dejtingapp 2>/dev/null | head -5 | awk '{print "  - " $9}')

## 📝 Recent File Changes
$(git diff --name-only HEAD~10..HEAD | sort | uniq)

## 🔧 Build/Test Results
Last successful build: $(git log --grep="build\|test" --oneline -1)
$(tail -30 /tmp/build_results.log 2>/dev/null || echo "No recent build logs")

## 🐛 Open Issues/TODOs
$(grep -r "TODO\|FIXME\|BUG\|HACK" . --include="*.cs" --include="*.dart" --include="*.yml" | head -15)

## 💾 Database & Migrations
$(git log --oneline --grep="migration\|database\|schema\|model" -10)

## 📦 Dependencies Status
Auth Service:
$(grep -A 5 -B 5 "PackageReference" auth-service/AuthService.csproj 2>/dev/null | head -10)

Matchmaking Service:  
$(grep -A 5 -B 5 "PackageReference" matchmaking-service/MatchmakingService.csproj 2>/dev/null | head -10)

## 🎯 Last AI Session Context
$(cat "$HOME/.last_ai_session.md" 2>/dev/null || echo "No previous AI session")

## 🔍 Performance & Issues
$(git log --grep="fix\|bug\|performance\|optimize" --oneline -5)
EOF

    # Save session timestamp
    echo "$(date): Generated context for AI session" >> "$HOME/.dating_app_memory.log"
    
    echo "✅ Persistent context saved: $context_file"
    echo "📝 This gives AI complete project understanding across sessions!"
    return 0
}

# Function to create smart AI prompts with full context
smart_ai_prompt() {
    local prompt_type="$1"
    local user_question="$2"
    
    generate_ai_context
    local context_file="$HOME/.dating_app_context.md"
    
    # Save this session info for next time
    echo "Session $(date): $prompt_type - $user_question" >> "$HOME/.dating_app_memory.log"
    
    case "$prompt_type" in
        "plan")
            echo "🎯 Smart AI Planning with Full Context..."
            if command -v gemini &> /dev/null; then
                local ai_response=$(gemini "Based on this dating app project context: $(cat $context_file)

                Help me plan the next development phase. Consider:
                - Recent code changes and commits
                - Current project structure  
                - Open TODOs and issues
                - Services that exist vs what's needed for a complete dating app
                - Previous AI sessions and context
                
                What should I focus on next?")
                
                echo "$ai_response"
                echo "$ai_response" > "$HOME/.last_ai_session.md"
            else
                echo "❌ Gemini CLI not found. Install with: npm install -g @google/generative-ai"
            fi
            ;;
        "review")
            echo "🔍 Smart AI Review with Full Context..."
            if command -v gemini &> /dev/null; then
                local ai_response=$(gemini "Review my dating app based on this context: $(cat $context_file)

                Analyze:
                - Recent changes and their quality
                - Architecture decisions
                - Missing components for a complete dating app
                - Security and performance concerns
                - Technical debt
                - Progress since last session
                
                Provide specific recommendations.")
                
                echo "$ai_response"
                echo "$ai_response" > "$HOME/.last_ai_session.md"
            else
                echo "❌ Gemini CLI not found"
            fi
            ;;
        "debug")
            echo "🐛 Smart AI Debugging with Full Context..."
            if command -v gemini &> /dev/null; then
                local ai_response=$(gemini "Help debug this dating app issue: $user_question

                Project context: $(cat $context_file)
                
                Consider the current codebase, recent changes, and architecture when suggesting solutions.")
                
                echo "$ai_response"
                echo "DEBUG: $user_question - $ai_response" > "$HOME/.last_ai_session.md"
            else
                echo "❌ Gemini CLI not found"
            fi
            ;;
        "status")
            echo "📊 Smart Project Analysis..."
            if command -v gemini &> /dev/null; then
                local ai_response=$(gemini "Analyze my dating app project status: $(cat $context_file)

                Provide:
                - What's been accomplished recently
                - Current development phase assessment  
                - Completion percentage for core dating app features
                - Next logical development steps
                - Potential blockers or issues
                - Changes since last AI session")
                
                echo "$ai_response"
                echo "$ai_response" > "$HOME/.last_ai_session.md"
            else
                echo "❌ Gemini CLI not found"
            fi
            ;;
        "continue")
            echo "🔄 Continuing from last session..."
            if [[ -f "$HOME/.last_ai_session.md" ]]; then
                echo "📋 Last AI session:"
                cat "$HOME/.last_ai_session.md"
                echo ""
                echo "🎯 Generated fresh context for continuation..."
                cat "$context_file"
            else
                echo "No previous session found. Starting fresh..."
                smart_ai_prompt "status"
            fi
            ;;
    esac
}

# Function to auto-track development progress
auto_track_progress() {
    echo "📈 Auto-tracking development progress..."
    
    # Track commits with dating app context
    local recent_commits=$(git log --oneline -5 --grep="feat\|fix\|add\|implement")
    local files_changed=$(git diff --name-only HEAD~1)
    local services_touched=$(echo "$files_changed" | grep -E "(auth-service|user-service|matchmaking|swipe|photo)" | cut -d'/' -f1 | sort -u)
    
    echo "Recent Progress:"
    echo "- Commits: $(echo "$recent_commits" | wc -l) feature commits"
    echo "- Files changed: $(echo "$files_changed" | wc -l) files"
    echo "- Services updated: $services_touched"
    
    # Auto-generate progress summary
    cat > "/tmp/auto_progress.md" << EOF
# Auto-Generated Progress Report
Date: $(date)

## Recent Development Activity
$recent_commits

## Services Modified
$services_touched

## Files Changed  
$files_changed

## Suggested Next Steps
$(smart_ai_prompt "plan" "" 2>/dev/null | tail -10)
EOF

    echo "✅ Progress auto-tracked in /tmp/auto_progress.md"
}

# Main menu for smart memory system
case "${1:-menu}" in
    "context")
        generate_ai_context
        cat "$HOME/.dating_app_context.md"
        ;;
    "smart-plan")
        smart_ai_prompt "plan"
        ;;
    "smart-review") 
        smart_ai_prompt "review"
        ;;
    "smart-debug")
        smart_ai_prompt "debug" "$2"
        ;;
    "smart-status")
        smart_ai_prompt "status"
        ;;
    "continue")
        smart_ai_prompt "continue"
        ;;
    "auto-track")
        auto_track_progress
        ;;
    "memory")
        echo "🧠 AI Memory History:"
        echo "==================="
        tail -20 "$HOME/.dating_app_memory.log" 2>/dev/null || echo "No memory history yet"
        echo ""
        echo "📋 Last AI Session:"
        echo "=================="
        cat "$HOME/.last_ai_session.md" 2>/dev/null || echo "No previous AI session"
        ;;
    "reset-memory")
        echo "🗑️ Clearing AI memory..."
        rm -f "$HOME/.dating_app_memory.log" "$HOME/.last_ai_session.md" "$HOME/.dating_app_context.md"
        echo "✅ Memory cleared. Fresh start!"
        ;;
    *)
        echo "🧠 Smart AI Memory System"
        echo "========================"
        echo ""
        echo "Commands:"
        echo "  context      - Generate full project context for AI"
        echo "  smart-plan   - AI planning with complete context"
        echo "  smart-review - AI review with code history"
        echo "  smart-debug  - AI debugging with project context"
        echo "  smart-status - Auto-analyze project status"
        echo "  continue     - Continue from last AI session"
        echo "  auto-track   - Auto-track development progress"
        echo "  memory       - Show AI memory history"
        echo "  reset-memory - Clear all AI memory (fresh start)"
        echo ""
        echo "💡 Persistent memory across sessions - never lose context again!"
        echo "🔄 Your AI remembers previous conversations and project state!"
        ;;
esac
