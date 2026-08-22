#!/usr/bin/env python3
"""
export-feedback.py — dump tester feedback into a ready-to-use "fix the app" prompt.

Pulls all user feedback from bot-service (via the YARP gateway) and writes a
markdown file you can paste straight into Copilot / Claude to fix the app:

    .venv/bin/python scripts/export-feedback.py [--out feedback-prompt.md] [--since 2026-08-01]

The file contains one actionable item per piece of feedback (transcript/note,
screen, app version, timestamp) plus a top instruction line. E2E/automation
rows are skipped so the prompt stays focused on real tester feedback.
"""
from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BASE_URL = os.environ.get("DEJTING_API_BASE", "http://localhost:8080")
DEFAULT_OUT = ROOT / "feedback-prompt.md"


def fetch_all(base_url: str, page_size: int = 200) -> list[dict]:
    items: list[dict] = []
    page = 1
    with httpx.Client(timeout=15) as client:
        while True:
            r = client.get(
                f"{base_url}/api/userfeedback",
                params={"page": page, "pageSize": page_size},
            )
            r.raise_for_status()
            payload = r.json()
            batch = payload.get("items", [])
            items.extend(batch)
            total = int(payload.get("total", 0))
            if not batch or page * page_size >= total:
                break
            page += 1
    return items


def is_e2e_row(item: dict) -> bool:
    tag = " ".join(
        str(item.get(k) or "")
        for k in ("appVersion", "noteText", "screen", "transcript")
    ).lower()
    return "e2e" in tag or "test runner" in tag


def main() -> int:
    ap = argparse.ArgumentParser(description="Export tester feedback as a fix-it prompt.")
    ap.add_argument("--base-url", default=DEFAULT_BASE_URL)
    ap.add_argument(
        "--out",
        default=str(DEFAULT_OUT),
        help="Output markdown path (default: feedback-prompt.md in repo root)",
    )
    ap.add_argument(
        "--since",
        default=None,
        help="Only include feedback received on/after this date (YYYY-MM-DD).",
    )
    args = ap.parse_args()

    items = fetch_all(args.base_url)

    since = None
    if args.since:
        since = datetime.fromisoformat(args.since)

    real: list[dict] = []
    for item in items:
        if is_e2e_row(item):
            continue
        if since:
            try:
                ts = datetime.fromisoformat((item.get("receivedAt") or "")[:19])
            except ValueError:
                ts = None
            if ts is None or ts < since:
                continue
        real.append(item)

    real.sort(key=lambda i: i.get("receivedAt") or "", reverse=True)

    lines: list[str] = []
    lines.append("# DatingApp Tester Feedback — fix-it prompt")
    lines.append("")
    lines.append(
        "Below is tester feedback collected from the DatingApp. For each item, "
        "identify the bug or improvement, note the screen and app version, and "
        "propose a concrete fix with code if applicable. If an item is vague or "
        "looks like a test recording, say so and skip it."
    )
    lines.append("")
    lines.append(
        f"Generated: {datetime.now().isoformat(timespec='minutes')} — "
        f"{len(real)} item(s) from {len(items)} total row(s)"
    )
    lines.append("")
    lines.append("## Feedback items")
    lines.append("")
    for i, item in enumerate(real, 1):
        ts = (item.get("receivedAt") or "")[:16]
        screen = item.get("screen") or "(screen not captured)"
        ver = item.get("appVersion") or "?"
        submitter = item.get("submitterKeycloakId") or "anonymous"
        text = (item.get("transcript") or item.get("noteText") or "").strip()
        if not text:
            text = "(no transcript / note)"
        lines.append(
            f"{i}. **[`{ts}`]** screen: `{screen}` · v`{ver}` · by `{submitter}`"
        )
        lines.append(f"   > {text}")
        lines.append("")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"✅ Wrote {len(real)} feedback item(s) to {out}")
    print(f"   (skipped {len(items) - len(real)} E2E/automation row(s))")
    print("   Paste this file into Copilot/Claude to fix the app.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"❌ export-feedback.py failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
