#!/usr/bin/env python3
"""Seed Vikunja with the DatingApp MVP board (labels, tasks, assign to buckets)."""

import json
import os
import sys
import urllib.request
import urllib.error

API_BASE = "http://localhost:3456/api/v1"
# Allow injecting a token via environment for non-interactive runs
TOKEN = os.environ.get("VIKUNJA_TOKEN") or None

def api(method, path, data=None):
    url = f"{API_BASE}{path}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TOKEN}",
    }
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        text = e.read().decode()
        print(f"  ❌ {method} {path} -> {e.code}: {text}", file=sys.stderr)
        sys.exit(1)

# ── Labels ──────────────────────────────────────────────────────────────────
LABELS = [
    ("001-foundation", "Core MVP — user stories 1-4", "00b4d8"),
    ("002-agentic-ai", "AI agent features", "7b2d8e"),
    ("003-bot-swarm", "Bot swarm + testing", "e07c24"),
    ("004-multi-app", "Multi-app architecture", "2d6a4f"),
    ("005-core-diff", "Compatibility engine + AI psykolog", "1b4332"),
    ("bug", "Known defect", "d62828"),
    ("test", "Test coverage work", "457b9d"),
    ("polish", "UI/UX polish, debug print removal", "a8dadc"),
    ("infra", "Infrastructure, CI/CD, monitoring", "6c757d"),
    ("docs", "Documentation", "8b5cf6"),
    ("P0-blocker", "Blocks tester handoff", "e63946"),
    ("P1-critical", "Must-do before next milestone", "f4a261"),
    ("P2-important", "Should do", "e9c46a"),
    ("P3-nice", "Nice to have", "a0c4ff"),
]

# Known bucket IDs from Kanban view (view_id=8) of project id=2
BUCKET_IDS = {
    "Backlog": 7,
    "Ready": 8,
    "In Progress": 9,
    "Done": 10,
    "Verified": 11,
}
# Project/view created during this session
PROJECT_ID = 2
VIEW_ID = 8

# Each task: (title, bucket_name, [label-titles])
TASKS = [
    # ── Done ──
    ("T022 — Keycloak registration + email verification", "Done", ["001-foundation"]),
    ("T023 — 3-step wizard (basic info, preferences, photos)", "Done", ["001-foundation"]),
    ("T024 — Photo moderation + blur", "Done", ["001-foundation"]),
    ("T025 — Onboarding status persistence", "Done", ["001-foundation"]),
    ("T026 — Flutter wizard UI (16 screens)", "Done", ["001-foundation"]),
    ("T027 — Basic telemetry (funnel tracking)", "Done", ["001-foundation"]),
    ("T030 — Matchmaking unit tests", "Done", ["001-foundation", "test"]),
    ("T032 — Scoring algorithm", "Done", ["001-foundation"]),
    ("T033 — Daily queue limits", "Done", ["001-foundation"]),
    ("T034 — Swipe idempotency", "Done", ["001-foundation"]),
    ("T035 — Flutter Discover UI (card stack)", "Done", ["001-foundation"]),
    ("T036 — Match creation notifications", "Done", ["001-foundation"]),
    ("T037 — Offline swipe cache", "Done", ["001-foundation"]),
    ("T042 — Basic SignalR hub", "Done", ["001-foundation"]),
    ("T043 — Message persistence", "Done", ["001-foundation"]),
    ("T044 — Flutter offline queue", "Done", ["001-foundation"]),
    ("T045 — YARP websocket routing", "Done", ["001-foundation"]),
    ("T052 — Photo privacy enforcement", "Done", ["001-foundation"]),
    ("T054 — Block action (client + API)", "Done", ["001-foundation"]),
    ("T519 — Compatibility questions widget tests", "Done", ["005-core-diff", "test"]),
    ("T530 — AdvancedMatchingService compatibility blend", "Done", ["005-core-diff"]),
    ("T531 — ScoringConfiguration compatibility weight", "Done", ["005-core-diff"]),
    ("T532 — 'Why You Matched' reasons + frictions", "Done", ["005-core-diff"]),
    ("T533 — MatchInsight entity + migration", "Done", ["005-core-diff"]),
    ("T534 — GET /api/matchmaking/matches/{id}/insight", "Done", ["005-core-diff"]),
    ("T535 — DailyPick compatibility integration", "Done", ["005-core-diff"]),
    ("T537 — MatchInsight unit tests", "Done", ["005-core-diff", "test"]),
    ("T540 — MatchInsightService API client", "Done", ["005-core-diff"]),
    ("T541 — CompatibilityBadge widget", "Done", ["005-core-diff"]),
    ("T542 — CompatibilityBarComparison widget", "Done", ["005-core-diff"]),
    ("T543 — MatchInsightScreen", "Done", ["005-core-diff"]),
    ("T544 — Badge in discover deck", "Done", ["005-core-diff"]),
    ("T545 — Matches list badge tap", "Done", ["005-core-diff"]),
    ("T546/T547 — Widget tests", "Done", ["005-core-diff", "test"]),
    ("T524 — CompatibilityPrecomputeService background job", "Done", ["005-core-diff"]),
    ("Tester APK builder script (scripts/build-tester-apk.sh)", "Done", ["infra"]),
    ("Feedback FAB widget + service", "Done", ["001-foundation"]),
    ("Keycloak tunnel support (scripts/start-keycloak-tunnel.sh)", "Done", ["infra"]),
    ("Whisper transcription pump (scripts/process-feedback.py)", "Done", ["infra"]),
    ("Swipe contract fix (2026-05-29)", "Done", ["001-foundation", "bug"]),
    ("T006 — MMP scope definition", "Done", ["infra"]),
    ("T007 — Database strategy consolidation (MySQL)", "Done", ["infra"]),
    ("T008 — AuthService removal (Keycloak migration)", "Done", ["infra"]),
    ("T072 — CI/CD workflow fix", "Done", ["infra"]),
    ("T073 — Skipped tests fix", "Done", ["infra", "test"]),
    ("T074 — API smoke tests in CI", "Done", ["infra", "test"]),
    ("T075 — Test coverage reporting", "Done", ["infra", "test"]),

    # ── Ready ──
    ("T021 — Flutter onboarding integration test", "Ready", ["P0-blocker", "001-foundation", "test"]),
    ("T041 — Flutter messaging widget test", "Ready", ["P0-blocker", "001-foundation", "test"]),
    ("T051 — Flutter privacy screen test", "Ready", ["P0-blocker", "001-foundation", "test"]),
    ("Remove debug prints from Flutter (ENRICH logs, debugPrint)", "Ready", ["P1-critical", "polish", "001-foundation"]),
    ("Fix bot-to-bot message flooding (MaxConversationsPerBot)", "Ready", ["P1-critical", "bug", "003-bot-swarm"]),
    ("MatchmakingService test coverage (18→40+ tests)", "Ready", ["P1-critical", "test", "001-foundation"]),
    ("Fix geo-location timeout (emulator GPS graceful handling)", "Ready", ["P2-important", "bug", "polish"]),
    ("T004 — Fix CI/CD coverage gate (80% threshold)", "Ready", ["P2-important", "infra"]),
    ("T002 — Add Mermaid dependency graphs to tasks.md", "Ready", ["P2-important", "docs"]),

    # ── Backlog ──
    ("T028/T029 — Webhook/automation (deferred)", "Backlog", ["001-foundation"]),
    ("T046 — Moderation hooks (deferred)", "Backlog", ["001-foundation"]),
    ("T053 — Report workflow (deferred)", "Backlog", ["001-foundation"]),
    ("T055 — Account recovery (deferred)", "Backlog", ["001-foundation"]),
    ("T056 — Ops playbook (deferred)", "Backlog", ["001-foundation"]),
    ("T009-T015 — Full test automation platform (post-MVP)", "Backlog", ["001-foundation", "test"]),
    ("AI Psykolog (LLM reflection coach)", "Backlog", ["005-core-diff"]),
    ("Vector matching", "Backlog", ["005-core-diff"]),
    ("Radar chart", "Backlog", ["005-core-diff"]),
    ("Anonymous forum", "Backlog", ["005-core-diff"]),
    ("Post-date feedback", "Backlog", ["005-core-diff"]),
    ("Safety agent", "Backlog", ["002-agentic-ai"]),
    ("Photo coach", "Backlog", ["002-agentic-ai"]),
    ("Conversation starter", "Backlog", ["002-agentic-ai"]),
    ("Smart match", "Backlog", ["002-agentic-ai"]),
    ("Bot photo generation", "Backlog", ["003-bot-swarm"]),
    ("Multi-language bot support", "Backlog", ["003-bot-swarm"]),
    ("Bot admin UI", "Backlog", ["003-bot-swarm"]),
    ("Shared Flutter packages (multi-app blueprint)", "Backlog", ["004-multi-app"]),
    ("Flavor config (multi-app blueprint)", "Backlog", ["004-multi-app"]),
    ("Audio retention policy — delete old feedback .m4a files", "Backlog", ["polish", "003-bot-swarm"]),
    ("Crash/error capture — attach logs to voice memos", "Backlog", ["polish"]),
    ("Persist Keycloak hostname overrides in docker-compose", "Backlog", ["infra"]),
]

def main():
    global TOKEN

    print("🔐 Logging in as admin…")
    resp = api("POST", "/login", {"username": "admin", "password": "adminadmin"})
    TOKEN = resp["token"]
    print("  ✅ Token obtained")

    # ── 1. Create labels ──
    print("\n📋 Creating labels…")
    label_map = {}
    for title, desc, color in LABELS:
        lbl = api("PUT", "/labels", {"title": title, "description": desc, "hex_color": color})
        label_map[title] = lbl["id"]
        print(f"  ✅ Label '{title}' -> id={lbl['id']}")

    # ── 2. Delete existing project (2) and recreate? No, use existing ──
    # Project id=2 "DatingApp MVP" already exists.

    # ── 3. Create tasks ──
    print("\n📝 Creating tasks…")
    created = 0
    for title, bucket_name, labels in TASKS:
        # Create task
        task = api("PUT", f"/projects/{PROJECT_ID}/tasks", {"title": title})
        tid = task["id"]

        # Set bucket_id directly on task
        bucket_id = BUCKET_IDS[bucket_name]
        api("POST", f"/tasks/{tid}", {"bucket_id": bucket_id})

        # Also register in Kanban view bucket
        api("POST", f"/projects/{PROJECT_ID}/views/{VIEW_ID}/buckets/{bucket_id}/tasks", {"task_id": tid})

        # Assign labels
        label_ids = [label_map[l] for l in labels if l in label_map]
        for lid in label_ids:
            api("PUT", f"/tasks/{tid}/labels", {"label_id": lid})

        print(f"  ✅ [{bucket_name}] {title[:70]}… (id={tid})")
        created += 1

    print(f"\n🎉 Done! {created} tasks created across 5 buckets.")
    print("   Open http://localhost:3456 → DatingApp MVP project → Kanban view")

if __name__ == "__main__":
    main()
