#!/usr/bin/env python3
"""
Wave 2 — open 6 Copilot agent issues across 4 repos.

Idempotent: skips tasks whose issue already exists in the target repo
(matched by '[T### / NNN]' title prefix).

Lessons from Wave 1 applied:
  * All repos point to canonical `best-koder-org/*` (no stale forks)
  * MM CI now runs on ubuntu-latest with real `dotnet test`
  * Tasks chosen with zero file overlap so PRs cannot collide

Usage:
  python3 scripts/wave2_create_issues.py            # dry-run (default)
  python3 scripts/wave2_create_issues.py --apply    # actually create
"""
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / ".cache" / "wave2-issues.json"

# ─────────────────────── Wave 2 task slate ───────────────────────

TASKS = [
    {
        "tid": "T519", "spec": "005",
        "repo": "best-koder-org/mobile_dejtingapp",
        "title": "Widget tests for compatibility_questions_screen",
        "estimate": "~3h",
        "files": [
            "test/screens/wizard/compatibility_questions_screen_test.dart (new)",
        ],
        "spec_quote": "T519 [P0] [Test] Widget tests for compatibility_questions_screen — test question rendering, slider/option interaction, category grouping, submit flow, skip behavior",
        "ac": [
            "New test file `test/screens/wizard/compatibility_questions_screen_test.dart`.",
            "At least 6 widget tests covering: questions render in category groups; selecting an option records the answer; submit invokes the service; skip advances without recording; loading state shown during fetch; error state shown when fetch fails.",
            "Use `Mockito` (or `mocktail`) for the `CompatibilityService`; do NOT hit the network.",
            "Use the project's standard test wrapper if one exists (e.g. `buildCoreScreenTestApp`); otherwise wrap in a `MaterialApp`.",
            "All new tests pass; full `flutter test` suite remains green.",
        ],
        "dod": "`flutter analyze --no-fatal-infos --no-fatal-warnings` clean; `flutter test` green.",
        "refs": [
            "Spec: specs/005-core-differentiation/tasks.md line 129",
            "Screen under test: lib/screens/wizard/compatibility_questions_screen.dart",
            "Service to mock: lib/services/compatibility_service.dart",
            "Existing test patterns: test/screens/wizard/ (look for nearest sibling)",
        ],
        "notes": "TESTS ONLY. Do not modify the screen or service. If the screen is hard to test, add a TODO and a `Skip` test rather than refactoring the screen in this PR.",
    },
    {
        "tid": "T533", "spec": "005",
        "repo": "best-koder-org/MatchmakingService",
        "title": "MatchInsight entity + EF migration",
        "estimate": "~2h",
        "files": [
            "Models/MatchInsight.cs (new)",
            "Data/MatchmakingDbContext.cs (add DbSet + OnModelCreating config)",
            "Migrations/<timestamp>_AddMatchInsight.cs (generated)",
        ],
        "spec_quote": "T533 [P0] [Infra] Create MatchInsight entity + migration — Id, MatchId (FK), ForKeycloakId (string), ReasonsJson, FrictionJson, GrowthJson, OverallScore, CreatedAt",
        "ac": [
            "New `MatchInsight` entity in `Models/` with: `Id` (int PK), `MatchId` (int FK → Match), `ForKeycloakId` (string, indexed), `ReasonsJson` (string, nullable), `FrictionJson` (string, nullable), `GrowthJson` (string, nullable), `OverallScore` (double), `CreatedAt` (DateTime UTC default).",
            "Asymmetric per user: a single match has TWO insight rows (one per `ForKeycloakId`). Add a unique index on (`MatchId`, `ForKeycloakId`).",
            "Registered as `DbSet<MatchInsight>` in `MatchmakingDbContext` with `OnModelCreating` configuration mirroring nearby entities.",
            "Generated EF migration named `AddMatchInsight`; `dotnet ef database update` succeeds against MySQL.",
            "JSON columns left as `string` (no value converter yet — that's a future task).",
            "No controller, service, or DTO changes in this PR.",
        ],
        "dod": "`dotnet build` clean. `dotnet test MatchmakingService.Tests` full suite green. Migration commit includes Designer.cs + the migration file.",
        "refs": [
            "Spec: specs/005-core-differentiation/tasks.md line 207",
            "Existing entity for reference: Models/CompatibilityScore.cs",
            "DbContext: Data/MatchmakingDbContext.cs",
            "Migrations folder: Migrations/",
        ],
        "notes": "Pure infra. Do not touch AdvancedMatchingService, controllers, or DTOs. Keep migration tightly scoped — single new table.",
    },
    {
        "tid": "T540", "spec": "005",
        "repo": "best-koder-org/mobile_dejtingapp",
        "title": "MatchInsightService API client",
        "estimate": "~2h",
        "files": [
            "lib/services/match_insight_service.dart (new)",
            "lib/models/match_insight.dart (new)",
            "test/services/match_insight_service_test.dart (new)",
        ],
        "spec_quote": "T540 [P0] [Flutter] Create MatchInsightService — API client for /api/matchmaking/matches/{matchId}/insight. Caches insight data locally.",
        "ac": [
            "New model `MatchInsight` (data class) with fields: `matchId` (int), `overallScore` (double), `reasons` (List<String>), `friction` (List<String>), `growth` (List<String>?). `fromJson` / `toJson` pair.",
            "New `MatchInsightService` with single public method `Future<MatchInsight?> fetchInsight(int matchId)` that GETs `/api/matchmaking/matches/{matchId}/insight` with the bearer token from the existing auth session manager.",
            "In-memory LRU cache (size ~50) keyed on matchId; TTL ~5 min. Cache hit short-circuits the HTTP call.",
            "404 returns `null` (insight not yet generated). Other non-2xx throw an `ApiException` (or whatever the project's standard pattern is).",
            "At least 4 unit tests with a mocked `http.Client`: success path, 404 → null, cache hit avoids second request, TTL expiry triggers refetch.",
        ],
        "dod": "`flutter analyze` clean; `flutter test` green.",
        "refs": [
            "Spec: specs/005-core-differentiation/tasks.md line 246",
            "Pattern reference: lib/services/compatibility_service.dart (or another small API service)",
            "Auth session: lib/services/auth_session_manager.dart",
            "Base URL helper: lib/services/api_service.dart",
        ],
        "notes": "Service layer only. Do NOT integrate into any screen yet — that's T545. Do NOT modify the backend.",
    },
    {
        "tid": "T542", "spec": "005",
        "repo": "best-koder-org/mobile_dejtingapp",
        "title": "Compatibility bar comparison widget",
        "estimate": "~3h",
        "files": [
            "lib/widgets/compatibility_bar_comparison.dart (new)",
            "test/widgets/compatibility_bar_comparison_test.dart (new)",
        ],
        "spec_quote": "T542 [P0] [Flutter] Create compatibility bar comparison widget — horizontal bars comparing user vs match on Big Five, Attachment, Values dimensions. Used on profile preview.",
        "ac": [
            "New stateless widget `CompatibilityBarComparison` taking `dimensions: List<DimensionScore>` where `DimensionScore { String label; double userScore (0-1); double matchScore (0-1); }`.",
            "Renders one row per dimension: label on the left, two horizontal bars stacked (user above, match below) with a small gap.",
            "Bar colours come from `Theme.of(context).colorScheme` — no hard-coded hex outside the existing theme.",
            "Bars animate from 0 to their target on first build (≤300ms, single AnimationController).",
            "Accessibility: each row exposes a `Semantics` label like 'Openness — you 80 percent, match 60 percent'.",
            "Pure widget — does NOT call any service or fetch data.",
            "At least 5 widget tests: renders all dimensions, handles empty list, clamps out-of-range, semantics labels present, custom theme colours respected.",
        ],
        "dod": "`flutter analyze` clean; `flutter test test/widgets/compatibility_bar_comparison_test.dart` green. No screen integration in this PR.",
        "refs": [
            "Spec: specs/005-core-differentiation/tasks.md line 257",
            "Theme: lib/theme/app_theme.dart",
            "Companion widget already shipped: lib/widgets/compatibility_badge.dart (PR #18)",
        ],
        "notes": "Standalone widget. No service deps. Keep in the same `lib/widgets/` folder as `compatibility_badge.dart` for cohesion.",
    },
    {
        "tid": "T366", "spec": "003",
        "repo": "best-koder-org/bot-service",
        "title": "Swedish naturalness benchmark suite",
        "estimate": "~4h",
        "files": [
            "BotService.Tests/NaturalnessBenchmark/SwedishNaturalnessTests.cs (new)",
            "BotService.Tests/NaturalnessBenchmark/fixtures/messages.json (new)",
            "BotService.Tests/NaturalnessBenchmark/Judge/LlmJudge.cs (new)",
        ],
        "spec_quote": "T366 [P1] [Test] Swedish naturalness benchmark — create evaluation suite: 100 generated messages scored 1-5 by LLM-judge for naturalness, grammar, persona consistency. Run as part of CI. Fail if avg <3.5.",
        "ac": [
            "Fixture file `messages.json` with at least 100 representative bot-generated Swedish messages (covering openers, replies, follow-ups across multiple personas).",
            "`LlmJudge` class scores a message on three axes (naturalness, grammar, persona-consistency) 1-5 via configurable LLM provider (Groq / Gemini / Ollama). Uses the same provider abstraction as the existing bot LLM clients.",
            "`SwedishNaturalnessTests` runs the full fixture through the judge in a single test marked `[Trait(\"Category\",\"Benchmark\")]` and asserts mean score ≥ 3.5 on each axis.",
            "When LLM API key is missing, the test is `Skip = \"Requires LLM API key\"` (does NOT fail CI). Use the same env-var pattern as existing bot LLM code.",
            "Add a CI job (or instructions in README) showing how to run only the benchmark trait: `dotnet test --filter Category=Benchmark`.",
        ],
        "dod": "`dotnet test BotService.Tests` green (benchmark either runs and passes ≥3.5, or skips when no key). Fixture file is valid JSON. Judge respects circuit-breaker if the LLM provider is down.",
        "refs": [
            "Spec: specs/003-bot-swarm/tasks.md line 302",
            "Existing LLM client pattern: BotService/Services/ (find the LLM provider abstraction)",
            "Existing personas: BotService/Personas/*.json",
        ],
        "notes": "Benchmark must NOT block normal CI runs. Default `dotnet test` (no filter) should still pass when the key is unset by skipping the benchmark.",
    },
    {
        "tid": "T550", "spec": "005",
        "repo": "best-koder-org/UserService",
        "title": "PsykologSession entity + DbContext + migration",
        "estimate": "~2h",
        "files": [
            "Models/PsykologSession.cs (new)",
            "Models/PsykologMessage.cs (new)",
            "Data/ApplicationDbContext.cs (add DbSets + OnModelCreating)",
            "Migrations/<timestamp>_AddPsykologSession.cs (generated)",
        ],
        "spec_quote": "T550 [P0] [Infra] Create PsykologSession entity in UserService — Id, KeycloakId, StartedAt, EndedAt, ThemeCount (int), Status (enum: Active, Completed, Expired), SessionNumber (int, per user). T551 PsykologMessage — Id, SessionId (FK), Role (enum: User, Assistant), Content (string), CreatedAt.",
        "ac": [
            "New `PsykologSession` entity with: `Id` (int PK), `KeycloakId` (string, indexed), `StartedAt` (DateTime UTC), `EndedAt` (DateTime?), `ThemeCount` (int default 0), `Status` (enum `PsykologSessionStatus { Active, Completed, Expired }`), `SessionNumber` (int).",
            "New `PsykologMessage` entity with: `Id` (int PK), `SessionId` (int FK → PsykologSession with cascade delete), `Role` (enum `PsykologRole { User, Assistant }`), `Content` (string), `CreatedAt` (DateTime UTC).",
            "Both entities registered as DbSets in `ApplicationDbContext`; configure relationships and indexes in `OnModelCreating`.",
            "Single EF migration named `AddPsykologSession` covers both tables; applies cleanly to MySQL.",
            "Enums stored as `int` (default EF behaviour) — no string converters needed.",
            "No service, controller, or DTO changes in this PR.",
        ],
        "dod": "`dotnet build` clean. `dotnet test UserService.Tests` full suite green. `dotnet ef database update` succeeds.",
        "refs": [
            "Spec: specs/005-core-differentiation/tasks.md lines 302-307",
            "DbContext: Data/ApplicationDbContext.cs (or wherever the project keeps it)",
            "Existing entity for reference: any UserService/Models/*.cs",
            "Migrations: Migrations/",
        ],
        "notes": "Combines T550 + T551 + T552 into one tightly scoped PR (all are entity/migration only). Do NOT add the PsykologService — that's T553.",
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
_This issue was opened by the wave-2 launcher (`scripts/wave2_create_issues.py`). The Copilot coding agent should be auto-assigned by the repo's `auto-assign-copilot.yml` workflow and open a draft PR. Keep the change minimal and tightly scoped to the files above — out-of-scope edits will block the wave-merge step._"""


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

    print(f"Wave 2 — {len(TASKS)} tasks across "
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
