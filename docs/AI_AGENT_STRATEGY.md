# AI Agent Strategy for DatingApp Development

## Issue Description Best Practices

### Current State ❌
```markdown
Spec task: `T024`

Source: `specs/001-mvp-foundation/tasks.md`
```

**Problem**: Zero context for humans OR AI. You/AI must:
- Read 5 different files to understand the task
- Guess which services are affected
- Figure out dependencies manually
- Invent acceptance criteria from scratch

### Better Approach ✅
```markdown
## 📋 Overview

**Task**: Enhance PhotoService moderation + blur tagging  
**Phase**: User Story 1 – First-Time Profile Creation  
**Priority**: P1 (blocks MVP)

### Why This Matters

Photos are the primary trust signal in dating apps. Without automated moderation we risk
NSFW content harming users. Privacy controls (MatchOnly blur) differentiate us from
competitors and give users agency over who sees their photos.

---

## ✅ Acceptance Criteria

- [ ] PhotoService applies ML-based moderation on upload (flag NSFW, violence, etc.)
- [ ] Pipeline generates blurred versions for MatchOnly privacy level  
- [ ] Privacy metadata stored in PhotoMetadata table with levels: Everyone, MatchOnly
- [ ] Non-matches see blur; matches see original (consistent with Tinder UX)
- [ ] Processing completes <10s per 6-photo batch
- [ ] Integration test covers upload → moderation → privacy enforcement flow

---

## 🔗 Dependencies

**Blocks**: T025 (onboarding status transitions)  
**Blocked By**: T023 (wizard must save privacy preferences first)  
**Related**: T027 (audit logging for photo moderation events)

---

## 📂 Affected Components

**Services**:
- `photo-service/Services/ModerationService.cs` - Add ML.NET moderation
- `photo-service/Services/ImageProcessingService.cs` - Generate blur pipeline
- `photo-service/Data/PhotoMetadata.cs` - Add PrivacyLevel enum

**Contracts**:
- `specs/001-mvp-foundation/contracts/api-spec.md` - PhotoUpload response schema
- Update `PhotoMetadataDto` with privacyLevel field

**Flutter**:
- `mobile-apps/flutter/dejtingapp/lib/services/photo_service.dart` - Handle privacy in upload
- `lib/widgets/photo_privacy_toggle.dart` - UI controls

**Database**:
- Migration: Add PrivacyLevel column to PhotoMetadata table

---

## 🧪 Testing Strategy

**Unit Tests**:
```bash
dotnet test photo-service.Tests --filter Category=Moderation
```

**Integration Test** (api_tests.py):
```python
def test_photo_privacy_enforcement():
    # Upload photo with MatchOnly privacy
    # Verify non-matched user sees blur
    # Verify matched user sees original
```

**Flutter Visual Test**:
```bash
flutter test integration_test/visual_photo_upload_test.dart
```

---

## 📊 Success Criteria Link

- **SC-001**: Track photo moderation rejection rate (target: <5%)
- **SC-002**: Upload processing latency P95 <10s

---

## 📚 References

- [Spec](https://github.com/best-koder-ever/DatingApp-Config/blob/001-mvp-foundation/specs/001-mvp-foundation/spec.md#user-story-1---first-time-profile-creation-priority-p1) (User Story 1, scenario 3)
- [API Contract](https://github.com/best-koder-ever/DatingApp-Config/blob/001-mvp-foundation/specs/001-mvp-foundation/contracts/api-spec.md#photo-upload)
- [Research](https://github.com/best-koder-ever/DatingApp-Config/blob/001-mvp-foundation/specs/001-mvp-foundation/research.md#photo-moderation-approaches) (ML.NET vs Azure Content Moderator tradeoffs)

---

**Estimated Effort**: 5-8 hours (3h moderation, 2h blur pipeline, 2h privacy enforcement, 1h testing)
```

### Benefits of Rich Descriptions

**For Humans**:
- ✅ Understand task without reading 5 spec files
- ✅ See dependencies before starting work
- ✅ Clear definition of "done"
- ✅ Know what to test

**For AI Agents (Claude/GPT/Copilot)**:
- ✅ Full context in single read (saves 10+ file reads)
- ✅ Knows which files to edit (no guessing)
- ✅ Can generate tests from acceptance criteria
- ✅ Links to authoritative spec docs for clarifications
- ✅ Understands business value ("why") not just technical task

**For Teams**:
- ✅ New developers onboard faster
- ✅ Code reviews reference acceptance criteria
- ✅ Product owners can validate without reading code
- ✅ Stakeholders see progress with context

---

## AI Agent Execution: CLI vs Cloud (GitHub Copilot)

### Option 1: CLI Agents (Aider, Cursor CLI, OpenAI API)

**When to Use**:
- ✅ Complex multi-file refactors (e.g., rename service, migrate DB)
- ✅ Need full repo context (search across 50+ files)
- ✅ Batch operations (update all DTOs, fix all tests)
- ✅ Local experimentation before committing

**Example**:
```bash
# Use Aider to implement T024 across multiple services
aider --message "Implement T024: photo moderation + blur pipeline" \
  photo-service/Services/ModerationService.cs \
  photo-service/Services/ImageProcessingService.cs \
  photo-service/Data/PhotoMetadata.cs \
  specs/001-mvp-foundation/contracts/api-spec.md
```

**Pros**:
- Full repo access
- Can run tests locally
- Iterative refinement
- Privacy (local execution)

**Cons**:
- Requires local setup
- You manage the conversation
- No automatic PR creation

---

### Option 2: GitHub Copilot Workspace (Cloud Agents)

**When to Use**:
- ✅ Well-defined issues with clear acceptance criteria
- ✅ Want automatic PR creation
- ✅ Delegate entire task (not just code gen)
- ✅ Need collaboration (assign to agent, review later)

**How It Works**:
1. Issue has rich description (like template above)
2. You assign issue to GitHub Copilot (@copilot)
3. Agent reads issue + linked specs
4. Agent plans implementation across services
5. Agent creates PR with:
   - Code changes
   - Tests
   - PR description linking to acceptance criteria
6. You review, request changes, or merge

**Example**:
```bash
# Create issue from script (after rate limit resets)
gh issue create --repo best-koder-ever/DatingApp-Config \
  --title "T024 – Enhance PhotoService moderation + blur tagging" \
  --body "$(cat /tmp/t024-rich-description.md)" \
  --assignee @me \
  --label "ai-ready,mvp,p1"

# Then assign to Copilot in web UI or:
gh issue comment 15 --body "@copilot please implement this task following acceptance criteria"
```

**Pros**:
- Async delegation (work while you sleep)
- Automatic PR workflow
- Consistent with team process
- Audit trail (issue → PR → merge)

**Cons**:
- Requires well-written issues
- Less interactive iteration
- GitHub quota limits

---

## Recommended Strategy for DatingApp MVP

### Phase Distribution

| Scenario | Tool | Why |
|----------|------|-----|
| **Foundational refactors** (T015-T017) | **CLI (Aider/Cursor)** | Complex analysis, multi-service changes, need context |
| **Well-scoped features** (T021-T029) | **GitHub Copilot Workspace** | Clear acceptance criteria, can delegate and review async |
| **Integration tasks** (T042-T045) | **CLI + human pairing** | Requires testing, debugging, iterative refinement |
| **Documentation** (T060, T072) | **GitHub Copilot** | Straightforward, benefits from issue-to-PR workflow |
| **Quick fixes** (bugs, typos) | **VS Code Copilot Chat** | Inline, immediate, no ceremony |

### Hybrid Workflow Example: Implementing User Story 1

1. **Morning**: Create rich issues for T022-T029 using updated sync script
2. **Assign T022, T023, T024 to GitHub Copilot** - wake up to 3 PRs
3. **Review PRs**, request changes via comments
4. **Use CLI agent (Aider) for T025** (DB migration - needs local testing)
5. **Assign T026-T029 to Copilot** after T022-T025 merge
6. **Use Copilot Chat for small fixes** during PR review

---

## Immediate Actions for Your Project

### 1. Update Sync Script to Generate Rich Descriptions

Add function to `sync_mvp_project.sh`:
```bash
generate_issue_body() {
  local task_id="$1"
  local task_title="$2"
  local task_phase="$3"
  
  cat <<EOF
## 📋 Task: $task_title

**Phase**: $task_phase  
**Spec Task ID**: $task_id

### Context
[Auto-populated from specs/001-mvp-foundation/spec.md]

### Acceptance Criteria
- [ ] Check specs/001-mvp-foundation/tasks.md for details
- [ ] Verify against contracts/ API specs
- [ ] Add integration test coverage

### References
- [Spec](https://github.com/best-koder-ever/DatingApp-Config/blob/001-mvp-foundation/specs/001-mvp-foundation/spec.md)
- [Tasks](https://github.com/best-koder-ever/DatingApp-Config/blob/001-mvp-foundation/specs/001-mvp-foundation/tasks.md#$task_id)
EOF
}
```

Then update issue creation:
```bash
gh issue create --repo "$REPO" \
  --title "$task_id – $task_title" \
  --body "$(generate_issue_body "$task_id" "$task_title" "$task_phase")"
```

### 2. Manually Enhance Key Issues Now

After rate limit resets, update T024, T029, T032, T021 with rich descriptions using:
```bash
gh issue edit 7 --body "$(cat t024-enhanced.md)"
```

### 3. Add AI-Ready Labels

```bash
# Label issues that are well-specified for AI agents
gh issue edit 7 --add-label "ai-ready,mvp,p1"
```

### 4. Test GitHub Copilot Delegation

Pick one well-defined task (e.g., T015 - documentation) and assign to Copilot:
```bash
gh issue comment 1 --body "@copilot implement this following the acceptance criteria in the issue"
```

---

## Long-Term: Template System

Create issue templates in `.github/ISSUE_TEMPLATE/`:

**spec-task.md**:
```yaml
name: Spec Task
about: Implementation task from spec-driven development
title: 'T### – [TASK TITLE]'
labels: ['spec-task', 'mvp']
assignees: []
body:
  - type: markdown
    attributes:
      value: |
        ## 📋 Overview
        <!-- Auto-filled by sync script -->
        
  - type: checkboxes
    attributes:
      label: Acceptance Criteria
      options:
        - label: Criteria 1
        - label: Criteria 2
        
  - type: textarea
    attributes:
      label: Affected Components
      description: Services, files, contracts affected
```

---

## Summary Recommendations

**For Your DatingApp MVP**:

1. **Invest in rich issue descriptions now** - saves 10x time during implementation
2. **Use GitHub Copilot Workspace for P1 tasks** (T021-T029) - they're well-specified and benefit from async delegation
3. **Use CLI agents (Aider) for exploratory work** (T015-T017, T032) - need context and iteration
4. **Keep Copilot Chat for review/fixes** - fast feedback during PR review
5. **Update sync script to auto-generate rich bodies** - eliminates manual work

**ROI Calculation**:
- 30 minutes to write rich description for T024
- Saves 2 hours of AI/human context switching during implementation
- Prevents 1 hour of rework from misunderstanding requirements
- Net savings: 2.5 hours per task × 42 tasks = **105 hours saved**

Make the investment now. Your future self (and AI assistants) will thank you.
