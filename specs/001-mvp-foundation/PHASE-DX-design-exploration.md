# Phase DX: Design Exploration System

**Status**: Ready to Implement  
**Priority**: P2 (Supports US1-US4 UI development)  
**Estimated Effort**: 4-6 hours  
**Start Date**: 2026-02-03  
**Dependencies**: Stitch MCP setup (✅ Complete)

---

## Overview

Establish a systematic approach to organizing AI-generated design explorations from Google Stitch, enabling multiple theme variants, clear user story traceability, and iterative refinement before implementation.

### Goals

1. **Organize Stitch outputs** - Structured storage for HTML/CSS/screenshots from AI design generation
2. **Track design-to-story relationships** - Link designs to user stories (US1-US4) with many-to-many support
3. **Enable theme exploration** - Compare multiple design variants before selecting production theme
4. **Maintain design history** - Git-tracked exploration archive for rollback and comparison
5. **Automate documentation** - Generate cross-reference indices from metadata

### Non-Goals

- Automatic HTML-to-Flutter conversion (manual conversion with AI assistance)
- Design system token extraction (future phase)
- Automated visual regression testing (future phase)

---

## Architecture

### Directory Structure

```
/home/m/development/DatingApp/
├── specs/001-mvp-foundation/
│   ├── design-explorations/           🆕 NEW - Design metadata & mapping
│   │   ├── README.md                 (Index of all explorations)
│   │   ├── SCREEN_MAP.md             (Screen ↔ User Story matrix)
│   │   ├── by-story/                 (Story-centric views)
│   │   │   ├── US1.md               (All designs for US1)
│   │   │   ├── US2.md               (All designs for US2)
│   │   │   ├── US3.md               (All designs for US3)
│   │   │   └── US4.md               (All designs for US4)
│   │   └── by-component/             (Component-centric views)
│   │       ├── navigation.md        (All nav variants)
│   │       ├── profile-card.md      (All card variants)
│   │       └── match-celebration.md (All celebration variants)
│   │
│   └── PHASE-DX-design-exploration.md (This document)

/home/m/development/mobile-apps/flutter/dejtingapp/
├── design-explorations/               🆕 NEW - Raw Stitch outputs
│   ├── README.md                     (Quick start guide)
│   ├── .stitch-metadata.json         (Automation hints)
│   │
│   ├── stitch-designs/               (AI-generated HTML/CSS)
│   │   ├── profile-card/
│   │   │   ├── variant-01-coral/
│   │   │   │   ├── design.html      (Stitch HTML output)
│   │   │   │   ├── preview.png      (Screenshot from Stitch)
│   │   │   │   └── metadata.yaml    (User stories, theme, status)
│   │   │   ├── variant-02-purple/
│   │   │   └── variant-03-material3/
│   │   │
│   │   ├── match-celebration/
│   │   │   ├── variant-01-confetti/
│   │   │   └── variant-02-minimal/
│   │   │
│   │   ├── chat-interface/
│   │   ├── filter-settings/
│   │   └── onboarding-wizard/
│   │
│   ├── theme-variants/               (Cross-component theme studies)
│   │   ├── coral-light/
│   │   │   ├── palette.json         (Color tokens)
│   │   │   ├── typography.json      (Font tokens)
│   │   │   └── examples/            (Screenshots)
│   │   ├── purple-material3/
│   │   └── dark-mode/
│   │
│   └── competitive-research/         (Inspiration & benchmarks)
│       ├── hinge/
│       ├── bumble/
│       └── tinder/
```

---

## File Format Specifications

### 1. Design Variant Metadata (`metadata.yaml`)

**Location**: `design-explorations/stitch-designs/[component]/[variant]/metadata.yaml`

**Schema**:
```yaml
# Variant Identification
component: profile-card          # kebab-case component name
variant: variant-01-coral        # variant-NN-theme-name
theme: coral-light              # Theme variant name
status: exploring               # exploring | approved | implemented | rejected

# Traceability
user_stories:                   # List of user story IDs
  - US1                        # Profile creation onboarding
  - US2                        # Discovery swipe screen
  - US4                        # Profile view
screens:                        # Flutter screen paths
  - lib/screens/onboarding_wizard_screen.dart
  - lib/swipe_screen.dart
  - lib/profile_screen.dart

# Design Metadata
created: 2026-02-03             # ISO date
author: Stitch AI (Gemini 3 Flash)
stitch_project_id: "8469203751545122197"
stitch_screen_id: "2f35fe61f38c4a3a95cafb9fc59e7e6e"

# Implementation
implementation_status: not_started  # not_started | in_progress | complete
flutter_widget_path: null          # Path when implemented
widgetbook_story_path: null        # Path to Widgetbook story

# Design Decisions
notes: |
  First Stitch-generated design. Features:
  - Large photo with gradient overlay
  - Purple "92% match" badge
  - Three action buttons: Pass, Like, Super Like
  - Plus Jakarta Sans typography
  - Dark mode optimized
  
strengths:
  - Professional gradient overlay
  - Clear action hierarchy
  - Material Design principles

concerns:
  - Match badge might be too prominent
  - Button spacing needs accessibility review
  - Photo aspect ratio not optimized for varied content

alternative_variants:
  - variant-02-purple: Less prominent badge, different colors
  - variant-03-material3: Pure Material 3 tokens

# Technical Metadata
html_file: design.html
preview_file: preview.png
stitch_download_url: https://lh3.googleusercontent.com/...
```

### 2. SCREEN_MAP.md Template

**Location**: `specs/001-mvp-foundation/design-explorations/SCREEN_MAP.md`

```markdown
# Screen-to-User-Story Mapping

Auto-generated from design variant metadata. Last updated: 2026-02-03

## Overview

This document maps Flutter screens to user stories and tracks design explorations for each screen.

## Mapping Table

| Screen | Component | User Stories | Design Variants | Status | Implementation |
|--------|-----------|--------------|-----------------|--------|----------------|
| `swipe_screen.dart` | ProfileCard | US2 | 3 variants | ✅ Approved (variant-01) | ✅ [profile_card.dart](../../mobile-apps/flutter/dejtingapp/lib/widgets/discovery/profile_card.dart) |
| `onboarding_wizard_screen.dart` | ProfileCard | US1 | 3 variants | 🔄 Exploring | ❌ Pending |
| TBD | MatchCelebration | US2 | 0 variants | 📋 Planned | ❌ Not started |
| `matches_screen.dart` | ChatInterface | US3 | 0 variants | 📋 Planned | ❌ Not started |

## By User Story

### US1: First-Time Profile Creation
**Screens**: 6 screens  
**Components**: ProfileCard (view), OnboardingWizard, PhotoUpload, PreferencesForm  
**Design Coverage**: 40% (4/10 components have explorations)

- ✅ ProfileCard - 3 variants ([Details](#profilecard))
- ❌ OnboardingWizard - 0 variants
- ❌ PhotoUpload - 0 variants
- ❌ PreferencesForm - 0 variants

### US2: Daily Match Discovery
**Screens**: 3 screens  
**Components**: ProfileCard, SwipeGestures, MatchCelebration, MatchList  
**Design Coverage**: 25% (1/4 components)

- ✅ ProfileCard - 3 variants ([Details](#profilecard))
- ❌ MatchCelebration - 0 variants (🔥 HIGH PRIORITY)
- ❌ SwipeGestures - 0 variants (interaction design)
- ❌ MatchList - 0 variants

### US3: Secure Match Messaging
**Screens**: 2 screens  
**Components**: ChatInterface, MessageBubble, MatchList  
**Design Coverage**: 0%

- ❌ ChatInterface - 0 variants (🔥 HIGH PRIORITY)
- ❌ MessageBubble - 0 variants
- ❌ MatchList (shared with US2)

### US4: Safety & Recovery Controls
**Screens**: 4 screens  
**Components**: ProfileCard (view), BlockDialog, ReportForm, PrivacySettings  
**Design Coverage**: 25%

- ✅ ProfileCard - 3 variants (shared)
- ❌ BlockDialog - 0 variants
- ❌ ReportForm - 0 variants
- ❌ PrivacySettings - 0 variants

## Component Details

### ProfileCard
**Used in**: US1, US2, US4  
**Variants**: 3  
**Status**: ✅ Approved (variant-01-coral)  
**Implementation**: ✅ Complete ([profile_card.dart](../../mobile-apps/flutter/dejtingapp/lib/widgets/discovery/profile_card.dart))

| Variant | Theme | Status | Preview | Notes |
|---------|-------|--------|---------|-------|
| variant-01-coral | Coral Light | ✅ Approved | [preview.png](../../mobile-apps/flutter/dejtingapp/design-explorations/stitch-designs/profile-card/variant-01-coral/preview.png) | Production choice. Gradient overlay, purple badge |
| variant-02-purple | Purple Material3 | 🔄 Exploring | TBD | More vibrant colors, material tokens |
| variant-03-minimal | Minimal Light | 📋 Planned | TBD | Cleaner, less overlay |

**Decision Rationale**: Variant-01 selected for professional gradient overlay and clear action hierarchy. Alternative variants preserved for future dark mode and theme exploration.

---

## Automated Updates

This file is auto-generated from `metadata.yaml` files in design-explorations.

**Regenerate**:
```bash
cd /home/m/development/DatingApp
./scripts/generate-screen-map.sh
```

**Last scan**: 2026-02-03 20:30:00  
**Total variants**: 3  
**Components covered**: 1/15 (7%)  
**User stories covered**: 3/4 (75%)
```

### 3. Component Index Template (`by-component/profile-card.md`)

```markdown
# ProfileCard Design Explorations

**Component**: ProfileCard  
**Used in**: US1 (Profile View), US2 (Discovery), US4 (Privacy Controls)  
**Flutter Path**: `lib/widgets/discovery/profile_card.dart`  
**Status**: ✅ Implemented

## Variants

### Variant 01: Coral Light (PRODUCTION) ✅

**Path**: `design-explorations/stitch-designs/profile-card/variant-01-coral/`  
**Theme**: Coral Light  
**Status**: Approved → Implemented  
**Created**: 2026-02-03  

**Preview**:
![ProfileCard Variant 01](../../../mobile-apps/flutter/dejtingapp/design-explorations/stitch-designs/profile-card/variant-01-coral/preview.png)

**Features**:
- Large photo with 0.75 aspect ratio
- Linear gradient overlay (transparent → dark)
- Purple gradient "92% match" badge
- Name/age in 4xl bold white text
- Bio text with semi-transparent white
- 3 action buttons: Pass (white), Like (red), Super Like (teal)
- Material shadows and hover animations

**Implementation**: [profile_card.dart](../../../mobile-apps/flutter/dejtingapp/lib/widgets/discovery/profile_card.dart)

**Stitch Details**:
- Project: DatingApp UI Components (8469203751545122197)
- Screen ID: 2f35fe61f38c4a3a95cafb9fc59e7e6e
- Model: Gemini 3 Flash
- [View HTML](../../../mobile-apps/flutter/dejtingapp/design-explorations/stitch-designs/profile-card/variant-01-coral/design.html)

---

### Variant 02: Purple Material3 (EXPLORING) 🔄

**Status**: Planned  
**Goal**: More vibrant purple theme using Material 3 color tokens  
**Changes from V01**: Stronger purple primary, Material 3 elevation, updated typography scale

---

## User Story Context

### US1: Profile Creation → View Own Profile
User sees their profile as others would see it. Same layout but with "Edit" controls instead of swipe actions.

**Differences**: Replace action buttons with "Edit Profile" FAB.

### US2: Discovery → Swipe Through Candidates
Primary use case. User makes quick Like/Pass decisions.

**Requirements**:
- Photo must be prominent (>60% screen real estate)
- Action buttons clearly visible
- Match score badge attention-grabbing but not overwhelming

### US4: Safety → View Blocked User Profile (Read-only)
After blocking, user can still view profile but cannot interact.

**Differences**: Remove all action buttons, add "Blocked" indicator, prevent navigation to chat.

---

## Design Decisions

### Why Gradient Overlay?
- **Problem**: White text on light photos unreadable
- **Solution**: Dark gradient ensures 4.5:1 WCAG contrast ratio
- **Alternative Considered**: Drop shadow on text (rejected: less clean)

### Why 3 Action Buttons?
- **Standard**: Pass + Like + Super Like matches industry (Tinder, Bumble, Hinge)
- **User Research**: Users expect "super like" for strong interest signals
- **Alternative Considered**: 2 buttons only (rejected: limits user expression)

### Why Purple for Match Badge?
- **Brand**: Aligns with existing `primary: #7f13ec` theme token
- **Attention**: Purple stands out against photo backgrounds (tested on 20 sample photos)
- **Alternative**: Green (rejected: too "gamified"), Red (rejected: conflicts with Like button)

---

## Open Questions

1. **Photo Aspect Ratio**: 0.75 (3:4) vs 0.8 (4:5)? Current crops tall photos significantly.
2. **Badge Position**: Top-right vs top-left for increased visibility?
3. **Action Button Size**: Current 56dp (Pass/Super) → 64dp (Like). Increase Pass to 64dp for accessibility?
4. **Dark Mode**: When implementing dark theme, invert gradient direction or use different approach?

---

## Next Steps

1. Generate variant-02 with purple Material 3 theme
2. A/B test badge position (top-right vs top-left)
3. Conduct accessibility audit (color contrast, touch targets)
4. Create dark mode variant (variant-04)
```

---

## Implementation Phases

### Phase 1: Foundation Setup (1-2 hours)
**Goal**: Create directory structure and documentation templates

**Tasks**:
1. Create `design-explorations/` folder in Flutter app
2. Create `design-explorations/` folder in specs
3. Set up folder structure per architecture diagram
4. Create README.md templates
5. Create metadata.yaml template
6. Add to Git with proper .gitignore rules

**Deliverables**:
- ✅ Complete folder structure
- ✅ Template files
- ✅ Initial README.md with usage instructions

### Phase 2: First Design Import (30 min)
**Goal**: Import existing ProfileCard Stitch design

**Tasks**:
1. Move `/home/m/Downloads/download.html` to `design-explorations/stitch-designs/profile-card/variant-01-coral/design.html`
2. Download screenshot from Stitch URL, save as `preview.png`
3. Create `metadata.yaml` for variant-01
4. Document design decisions in component index

**Deliverables**:
- ✅ ProfileCard variant-01 fully documented
- ✅ First metadata.yaml example

### Phase 3: Mapping Documentation (1 hour)
**Goal**: Create cross-reference indices

**Tasks**:
1. Create SCREEN_MAP.md with ProfileCard entry
2. Create `by-component/profile-card.md` detailed doc
3. Create `by-story/US1.md`, `US2.md`, `US4.md` with ProfileCard references
4. Document user story contexts (how same component differs per story)

**Deliverables**:
- ✅ SCREEN_MAP.md with 1 component (template for future)
- ✅ 3 by-story indices
- ✅ 1 by-component detailed doc

### Phase 4: Automation Scripts (1-2 hours)
**Goal**: Automate index generation from metadata

**Tasks**:
1. Create `scripts/generate-screen-map.sh`
2. Create `scripts/scan-design-metadata.py` (parses all metadata.yaml)
3. Create `scripts/new-stitch-variant.sh` (wizard for adding new designs)
4. Add validation script (check metadata format, broken references)

**Deliverables**:
- ✅ `generate-screen-map.sh` - Auto-generates SCREEN_MAP.md
- ✅ `new-stitch-variant.sh` - Interactive wizard for new variants
- ✅ Pre-commit hook for metadata validation

### Phase 5: Next Designs (Ongoing)
**Goal**: Generate and document 2-3 more components

**Suggested Order** (based on user story priority):
1. **MatchCelebration** (US2 - HIGH PRIORITY) - "It's a Match!" screen
2. **ChatInterface** (US3 - HIGH PRIORITY) - Messaging layout
3. **OnboardingWizard** (US1) - Multi-step profile creation
4. **FilterSettings** (US2) - Age/distance preference sliders

**Per Component**:
1. Generate 2-3 theme variants with Stitch
2. Create metadata.yaml for each
3. Update SCREEN_MAP.md (run automation script)
4. Document design decisions in by-component doc

---

## Automation Scripts

### `scripts/generate-screen-map.sh`

```bash
#!/bin/bash
# Generate SCREEN_MAP.md from metadata.yaml files

set -euo pipefail

DESIGN_DIR="/home/m/development/mobile-apps/flutter/dejtingapp/design-explorations/stitch-designs"
OUTPUT_FILE="/home/m/development/DatingApp/specs/001-mvp-foundation/design-explorations/SCREEN_MAP.md"

echo "# Screen-to-User-Story Mapping" > "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "Auto-generated from design variant metadata. Last updated: $(date -I)" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# Implementation: Python script to parse YAML and generate markdown
python3 /home/m/development/DatingApp/scripts/scan-design-metadata.py "$DESIGN_DIR" >> "$OUTPUT_FILE"

echo "✅ SCREEN_MAP.md updated"
```

### `scripts/new-stitch-variant.sh`

```bash
#!/bin/bash
# Interactive wizard for adding new Stitch design variant

set -euo pipefail

echo "🎨 New Stitch Design Variant Wizard"
echo ""

# Prompt for component name
read -p "Component name (kebab-case, e.g., 'profile-card'): " COMPONENT
read -p "Variant number (e.g., '02'): " VARIANT_NUM
read -p "Theme name (e.g., 'purple'): " THEME
read -p "User stories (comma-separated, e.g., 'US1,US2'): " STORIES

VARIANT_NAME="variant-${VARIANT_NUM}-${THEME}"
VARIANT_DIR="/home/m/development/mobile-apps/flutter/dejtingapp/design-explorations/stitch-designs/${COMPONENT}/${VARIANT_NAME}"

# Create directory structure
mkdir -p "$VARIANT_DIR"

# Create metadata.yaml template
cat > "${VARIANT_DIR}/metadata.yaml" << EOF
component: ${COMPONENT}
variant: ${VARIANT_NAME}
theme: ${THEME}
status: exploring

user_stories:
$(echo "$STORIES" | tr ',' '\n' | sed 's/^/  - /')

screens: []

created: $(date -I)
author: Stitch AI (Gemini 3 Flash)
stitch_project_id: "8469203751545122197"
stitch_screen_id: ""

implementation_status: not_started
flutter_widget_path: null
widgetbook_story_path: null

notes: |
  

strengths: []
concerns: []
alternative_variants: []

html_file: design.html
preview_file: preview.png
stitch_download_url: ""
EOF

echo ""
echo "✅ Created: ${VARIANT_DIR}"
echo ""
echo "Next steps:"
echo "1. Download Stitch HTML → ${VARIANT_DIR}/design.html"
echo "2. Download screenshot → ${VARIANT_DIR}/preview.png"
echo "3. Edit metadata.yaml with Stitch project/screen IDs"
echo "4. Run: ./scripts/generate-screen-map.sh"
```

### `scripts/scan-design-metadata.py`

```python
#!/usr/bin/env python3
"""
Scan design-explorations for metadata.yaml files and generate indices.
"""

import sys
from pathlib import Path
import yaml
from collections import defaultdict

def scan_designs(base_dir: Path):
    """Scan all metadata.yaml files and return structured data."""
    designs = []
    
    for metadata_file in base_dir.rglob("metadata.yaml"):
        with open(metadata_file, 'r') as f:
            data = yaml.safe_load(f)
            data['_path'] = metadata_file.parent
            designs.append(data)
    
    return designs

def generate_mapping_table(designs):
    """Generate markdown table of all components."""
    # Group by component
    by_component = defaultdict(list)
    for d in designs:
        by_component[d['component']].append(d)
    
    print("## Mapping Table\n")
    print("| Component | User Stories | Design Variants | Status | Implementation |")
    print("|-----------|--------------|-----------------|--------|----------------|")
    
    for component, variants in sorted(by_component.items()):
        stories = set()
        for v in variants:
            stories.update(v.get('user_stories', []))
        
        status = "✅ Approved" if any(v['status'] == 'approved' for v in variants) else "🔄 Exploring"
        impl = "✅ Complete" if any(v['implementation_status'] == 'complete' for v in variants) else "❌ Pending"
        
        print(f"| {component} | {', '.join(sorted(stories))} | {len(variants)} variants | {status} | {impl} |")
    
    print("\n")

def generate_by_story(designs):
    """Generate by-story breakdown."""
    by_story = defaultdict(list)
    for d in designs:
        for story in d.get('user_stories', []):
            by_story[story].append(d)
    
    print("## By User Story\n")
    
    for story in sorted(by_story.keys()):
        components = by_story[story]
        print(f"### {story}")
        print(f"**Components**: {len(components)}\n")
        
        for comp in components:
            status_icon = "✅" if comp['status'] == 'approved' else "🔄" if comp['status'] == 'exploring' else "❌"
            print(f"- {status_icon} {comp['component']} - {comp['variant']}")
        
        print("\n")

if __name__ == "__main__":
    base_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    designs = scan_designs(base_dir)
    
    generate_mapping_table(designs)
    generate_by_story(designs)
    
    print(f"---\n\n**Last scan**: {Path.cwd()}\n")
    print(f"**Total variants**: {len(designs)}")
```

---

## Success Criteria

### Phase 1-2 Complete
- ✅ Folder structure created
- ✅ ProfileCard variant-01 documented with metadata.yaml
- ✅ README.md with quick start guide

### Phase 3 Complete
- ✅ SCREEN_MAP.md shows ProfileCard → US1, US2, US4 mapping
- ✅ by-component/profile-card.md documents design decisions
- ✅ by-story/*.md files reference ProfileCard

### Phase 4 Complete
- ✅ `generate-screen-map.sh` regenerates SCREEN_MAP.md in <5 seconds
- ✅ `new-stitch-variant.sh` creates boilerplate for new designs
- ✅ Validation script catches missing files or broken references

### Phase 5 (Ongoing Success)
- ✅ 10+ component variants documented
- ✅ All 4 user stories have design coverage
- ✅ Team can find designs by story OR by component
- ✅ Design decisions are documented and searchable

---

## Integration with Existing Workflow

### With User Stories (specs/001-mvp-foundation/)
- SCREEN_MAP.md becomes source of truth for design coverage
- User journey docs link to design-explorations for visual references
- FEATURE_MAP.md gets "Design Coverage" column

### With Flutter Development
- Developers reference design-explorations before implementing
- Widgetbook stories link back to original Stitch designs
- metadata.yaml tracks implementation status

### With Stitch MCP
- Generate design → `new-stitch-variant.sh` → metadata.yaml → regenerate indices
- Store Stitch project/screen IDs for re-generation if needed
- Track which Gemini model generated each design (quality comparison)

---

## Future Enhancements (Post Phase 5)

1. **Visual Regression Testing**: Screenshot comparison across variants
2. **Token Extraction**: Parse HTML/CSS to extract design tokens automatically
3. **Figma Integration**: Import Stitch designs to Figma for handoff
4. **A/B Testing Metadata**: Track which variants were A/B tested and results
5. **Component Library**: Generate component catalog website from metadata
6. **Dark Mode Variants**: Systematic dark mode exploration per component
7. **Accessibility Audit**: Track WCAG compliance per variant in metadata

---

## References

- [FEATURE_MAP.md](FEATURE_MAP.md) - API-to-User-Story traceability
- [User Journeys](features/user-journeys/) - Detailed user story flows
- [Stitch MCP Setup](../../STITCH_MCP_SUCCESS.md) - AI design tool configuration
- [UI/UX Strategy](../../UI_UX_STRATEGY_FOR_NON_DESIGNERS.md) - Design philosophy

---

**Next Action**: Begin Phase 1 - Foundation Setup
