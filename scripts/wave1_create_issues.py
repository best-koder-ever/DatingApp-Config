#!/usr/bin/env python3
"""
Wave 1 — open 6 Copilot agent issues in their respective code repos.

Idempotent: skips tasks whose issue already exists in the target repo
(matched by '[T### / NNN]' title prefix).

Usage:
  python3 scripts/wave1_create_issues.py --dry-run   # show titles + bodies
  python3 scripts/wave1_create_issues.py --apply     # actually create
"""
from __future__ import annotations
import argparse, json, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / ".cache" / "wave1-issues.json"

# ─────────────────────── Wave 1 task slate ───────────────────────

TASKS = [
    {
        "tid": "T516", "spec": "005",
        "repo": "best-koder-org/mobile_dejtingapp",
        "title": "Wire compatibility-questions step into onboarding coordinator",
        "estimate": "~2h",
        "files": [
            "lib/services/onboarding_coordinator.dart",
            "lib/screens/wizard/compatibility_questions_screen.dart (existing — reference)",
            "lib/screens/wizard/ (insert step between current 5 and 6)",
        ],
        "spec_quote": "T516 [P1] [Flutter] Integrate into onboarding flow — add compatibility screen after current step 5 (preferences). Update OnboardingCoordinator to include new step. Make skippable but encouraged.",
        "ac": [
            "New onboarding step `compatibilityQuestions` registered in `OnboardingCoordinator` after the preferences step.",
            "Step routes to existing `CompatibilityQuestionsScreen`.",
            "Skippable: a 'Skip for now' button advances to the next step without recording answers.",
            "Encouraged: copy explains the value (e.g., 'Better matches in 2 minutes').",
            "If the user already answered some questions, the screen resumes where they left off (existing screen behaviour — verify, do not regress).",
            "No regressions in existing onboarding wizard tests.",
        ],
        "dod": "Run `flutter analyze --no-fatal-infos --no-fatal-warnings` and `flutter test` — both green. Add at least one widget test that drives the new step end-to-end (or extends an existing wizard test).",
        "refs": [
            "Spec: specs/005-core-differentiation/tasks.md line 110",
            "Existing screen: lib/screens/wizard/compatibility_questions_screen.dart",
            "Existing service: lib/services/compatibility_service.dart",
        ],
        "notes": "Do not modify CompatibilityQuestionsScreen itself — reuse as-is. Scope is purely the coordinator wiring.",
    },
    {
        "tid": "T517", "spec": "005",
        "repo": "best-koder-org/mobile_dejtingapp",
        "title": "Compatibility settings screen (view + edit answers)",
        "estimate": "~3h",
        "files": [
            "lib/screens/compatibility_settings_screen.dart (new)",
            "lib/screens/settings_screen.dart (add navigation entry)",
            "test/screens/compatibility_settings_screen_test.dart (new)",
        ],
        "spec_quote": "T517 [P1] [Flutter] Create compatibility settings screen — accessible from profile/settings, allows re-answering questions anytime. Shows current answers with edit capability.",
        "ac": [
            "New screen `CompatibilitySettingsScreen` accessible from settings screen.",
            "Lists all questions with the user's current answer highlighted.",
            "Tapping a question lets the user re-answer (single-tap commits via existing `CompatibilityService.submitAnswer`).",
            "Voice-eligible questions show the existing voice answer flow when applicable.",
            "Empty-state copy if the user hasn't answered yet, with a CTA to take the questionnaire.",
            "Loading + error states handled (use the same patterns as other settings sub-screens).",
        ],
        "dod": "`flutter analyze` clean; `flutter test` green; new widget test covers happy path (load → render → edit → save).",
        "refs": [
            "Spec: specs/005-core-differentiation/tasks.md line 116",
            "Service: lib/services/compatibility_service.dart",
            "Settings parent: lib/screens/settings_screen.dart",
        ],
        "notes": "Do NOT modify CompatibilityService or backend. Use existing GET /api/compatibility/questions and POST /api/compatibility/answers via the service layer.",
    },
    {
        "tid": "T518", "spec": "005",
        "repo": "best-koder-org/MatchmakingService",
        "title": "Unit tests for CompatibilityController",
        "estimate": "~3h",
        "files": [
            "MatchmakingService.Tests/Controllers/CompatibilityControllerTests.cs (new)",
        ],
        "spec_quote": "T518 [P0] [Test] Unit tests for CompatibilityController — test all 3 endpoints, auth enforcement, validation, upsert behavior, missing question ID handling",
        "ac": [
            "New xUnit test class `CompatibilityControllerTests` with at least 12 test methods.",
            "Cover: GET /api/compatibility/questions (auth required, returns active questions in SortOrder).",
            "Cover: POST /api/compatibility/answers (auth required, upsert behaviour — first call inserts, second call updates same row).",
            "Cover: POST validation — rejects unknown question id (404 or 400), rejects unauthenticated (401).",
            "Cover: GET /api/compatibility/answers/{keycloakId} (returns the caller's answers; verify behaviour for other users per controller's existing rules).",
            "Cover: GET /api/compatibility/score/{otherKeycloakId} (returns score DTO when both users have answers; returns neutral when not).",
            "Use `Microsoft.EntityFrameworkCore.InMemory` for the DbContext, fresh `Guid.NewGuid()` per test.",
            "Mock `ICompatibilityScorer` where needed via Moq.",
        ],
        "dod": "`dotnet test MatchmakingService.Tests/MatchmakingService.Tests.csproj --filter CompatibilityControllerTests` shows ≥12 passing. Full suite still green.",
        "refs": [
            "Spec: specs/005-core-differentiation/tasks.md line 123",
            "Controller: Controllers/CompatibilityController.cs",
            "Existing test pattern: MatchmakingService.Tests/Controllers/ProfilesControllerTests.cs",
            "Scorer interface: Services/ICompatibilityScorer.cs",
        ],
        "notes": "TESTS ONLY — do not modify the controller implementation. If you discover a bug, file a follow-up issue and add a `// TODO` test marked `Skip = \"...\"`.",
    },
    {
        "tid": "T530", "spec": "005",
        "repo": "best-koder-org/MatchmakingService",
        "title": "Add compatibility score to AdvancedMatchingService.ScoreCandidateAsync (30% weight)",
        "estimate": "~4h",
        "files": [
            "Services/AdvancedMatchingService.cs",
            "Services/ScoringConfiguration.cs (or similar weight config)",
            "MatchmakingService.Tests/Services/AdvancedMatchingServiceTests.cs",
        ],
        "spec_quote": "T530 [P0] [Core] Add compatibility score to AdvancedMatchingService.ScoreCandidateAsync() — inject CompatibilityScorer, look up cached score, include as weighted component (30% weight). Fall back gracefully if either user has no answers (use average).",
        "ac": [
            "Constructor of `AdvancedMatchingService` takes `ICompatibilityScorer` (DI already registered in Program.cs).",
            "`ScoreCandidateAsync` calls scorer for the (caller, candidate) pair.",
            "Compatibility component contributes 30% to the final score; existing components rebalanced so weights sum to 1.0.",
            "Graceful fallback: if either user has no answers, compatibility component is treated as the neutral score (0.5) — no exception.",
            "Cache hit path: if `CompatibilityScore` row exists for the pair, use it; otherwise compute (scorer handles caching internally per its current contract).",
            "New unit tests cover: both users answered (score reflected), one user empty (neutral fallback), both empty (neutral fallback), weight sums to 1.0.",
        ],
        "dod": "`dotnet test MatchmakingService.Tests` full suite green, including new tests. No behaviour change for users without compatibility answers other than the (small) weight rebalancing.",
        "refs": [
            "Spec: specs/005-core-differentiation/tasks.md line 189",
            "Scorer: Services/CompatibilityScorer.cs",
            "Scorer interface: Services/ICompatibilityScorer.cs",
            "Target service: Services/AdvancedMatchingService.cs (method ScoreCandidateAsync)",
        ],
        "notes": "Do not modify CompatibilityController or the scorer itself. Keep the change scoped to AdvancedMatchingService + its weight config + tests.",
    },
    {
        "tid": "T363", "spec": "003",
        "repo": "best-koder-org/bot-service",
        "title": "Expand bot persona library from 12 to 50 (Swedish, diverse)",
        "estimate": "~4h",
        "files": [
            "BotService/Personas/*.json (add ~38 new persona files)",
        ],
        "spec_quote": "T363 [P1] [Content] Expand from 12 to 50 personas — cover wider age range (20-55), diverse occupations, suburban/rural personas (not just Stockholm), different chattiness levels, varied relationship goals.",
        "ac": [
            "Total persona files in `BotService/Personas/` is exactly 50 (existing 12 retained).",
            "Age distribution covers 20–55 with at least 5 personas per decade.",
            "Geographic diversity: at least 30% of new personas live outside Stockholm (Göteborg, Malmö, Uppsala, Umeå, smaller towns).",
            "Occupation diversity: tradespeople, healthcare, education, arts, tech, retail, retired/student all represented.",
            "Each new persona JSON validates against the same schema as existing ones (use `astrid.json` and `elsa.json` as reference).",
            "All Swedish content sounds natural — no machine-translation tells, no English idioms calqued into Swedish.",
            "Each persona file passes JSON validity check.",
        ],
        "dod": "Add a script or test that loads every persona JSON and asserts schema compliance. Run `dotnet test` (existing bot-service tests) — all green.",
        "refs": [
            "Spec: specs/003-bot-swarm/tasks.md line 286",
            "Schema reference: BotService/Personas/astrid.json, elsa.json",
            "Loader: BotService/Services/PersonaLoaderService.cs (or similar — find via grep)",
        ],
        "notes": "Pure content task — do NOT modify any C# code beyond an optional schema-validation test. Use a Swedish LLM (Groq Llama-Swedish or local Ollama) to draft bios; cross-check tone with the existing personas.",
    },
    {
        "tid": "T541", "spec": "005",
        "repo": "best-koder-org/mobile_dejtingapp",
        "title": "Compatibility badge widget (circular gradient % score)",
        "estimate": "~3h",
        "files": [
            "lib/widgets/compatibility_badge.dart (new)",
            "test/widgets/compatibility_badge_test.dart (new)",
        ],
        "spec_quote": "T541 [P0] [Flutter] Create compatibility badge widget — circular gradient badge showing overall % score. Coral→teal gradient. Used on discover card and match list.",
        "ac": [
            "New stateless widget `CompatibilityBadge` taking `score: double` (0.0–1.0) and optional `size: double`.",
            "Renders a circular badge with gradient stroke (coral `#FF7F50` → teal). Score above gradient threshold uses richer teal end; lower scores fade toward coral.",
            "Centre text shows the integer percentage (e.g., '87%').",
            "Default size 56dp; respects `MediaQuery.textScaleFactor` for the centre text.",
            "Accessibility: provides a Semantics label like 'Compatibility 87 percent'.",
            "Pure widget — does NOT call any service or fetch data.",
            "At least 4 widget tests: low score (≤30%), mid (50%), high (≥85%), boundary (0% and 100%).",
        ],
        "dod": "`flutter analyze` clean; `flutter test test/widgets/compatibility_badge_test.dart` green. Do not yet integrate into discover card / matches screen — that's T544/T545.",
        "refs": [
            "Spec: specs/005-core-differentiation/tasks.md line 252",
            "Theme primary colors: lib/theme/app_theme.dart (coral = primaryColor)",
            "Existing widget patterns: lib/widgets/ (any small widget for reference)",
        ],
        "notes": "Standalone widget. No service deps. No screen integration in this PR — keeps merge surface tiny.",
    },
]


# ─────────────────────── Issue body builder ───────────────────────

def build_body(t: dict) -> str:
    files = "\n".join(f"- `{f}`" for f in t["files"])
    ac = "\n".join(f"- [ ] {a}" for a in t["ac"])
    refs = "\n".join(f"- {r}" for r in t["refs"])
    return f"""## {t['title']}

**Spec**: `{t['spec']}-*`  •  **Task**: `{t['tid']}`  •  **Estimate**: {t['estimate']}

> {t['spec_quote']}

### Files in scope
{files}

### Acceptance criteria
{ac}

### Definition of done
{t['dod']}

### Reference material
{refs}

### Notes for the agent
{t['notes']}

---
_This issue was opened by the wave-1 launcher (`scripts/wave1_create_issues.py`). The Copilot coding agent should be auto-assigned by the repo's `auto-assign-copilot.yml` workflow and open a draft PR. Keep the change minimal and tightly scoped to the files above — out-of-scope edits will block the wave-merge step._"""


# ─────────────────────── GH helpers ───────────────────────

def gh(*args: str, check: bool = True, stdin: str | None = None) -> str:
    r = subprocess.run(["gh", *args], capture_output=True, text=True, input=stdin)
    if check and r.returncode != 0:
        sys.stderr.write(f"gh {' '.join(args[:3])}… failed:\n{r.stderr}\n")
        sys.exit(1)
    return r.stdout.strip()


def existing_issue(repo: str, prefix: str) -> dict | None:
    raw = gh("issue", "list", "--repo", repo, "--state", "all",
             "--limit", "200", "--json", "number,title,state,url")
    for it in json.loads(raw):
        if it["title"].startswith(prefix):
            return it
    return None


# ─────────────────────── Main ───────────────────────

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", default=True)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    dry = not args.apply

    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}

    print(f"Wave 1 — {len(TASKS)} tasks across "
          f"{len(set(t['repo'] for t in TASKS))} repos.\n")

    for t in TASKS:
        prefix = f"[{t['tid']} / {t['spec']}]"
        title = f"{prefix} {t['title']}"
        body = build_body(t)
        existing = existing_issue(t["repo"], prefix)

        if existing:
            print(f"  ✓ EXISTS  {t['tid']}  #{existing['number']}  {t['repo']}  ({existing['state']})")
            cache[t["tid"]] = {
                "tid": t["tid"], "repo": t["repo"],
                "number": existing["number"], "url": existing["url"],
                "state": existing["state"],
            }
            continue

        if dry:
            print(f"  + WOULD CREATE  {t['tid']}  {t['repo']}")
            print(f"      title: {title}")
            print(f"      body:  {len(body)} chars, {body.count(chr(10))} lines")
            continue

        print(f"  → CREATE  {t['tid']}  {t['repo']} …")
        url = gh("issue", "create",
                 "--repo", t["repo"],
                 "--title", title,
                 "--body-file", "-",
                 stdin=body).strip().splitlines()[-1]
        num = url.rsplit("/", 1)[-1]
        cache[t["tid"]] = {
            "tid": t["tid"], "repo": t["repo"],
            "number": int(num), "url": url, "state": "OPEN",
        }
        print(f"      → {url}")

    if not dry:
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        CACHE.write_text(json.dumps(cache, indent=2))
        print(f"\nCache: {CACHE}")
        for tid, info in cache.items():
            print(f"  {tid}  #{info['number']}  {info['url']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
