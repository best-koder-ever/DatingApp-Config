#!/usr/bin/env python3
"""
Wave 1 status monitor — one-screen table of issue → PR → CI status.

Reads .cache/wave1-issues.json and prints a refreshable summary table.

Usage:
  python3 scripts/wave_status.py           # once
  python3 scripts/wave_status.py --watch   # refresh every 60s until Ctrl-C
"""
from __future__ import annotations
import argparse, json, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path

CACHE = Path(__file__).resolve().parents[1] / ".cache" / "wave1-issues.json"


def gh(*args: str) -> dict | list | None:
    r = subprocess.run(["gh", *args], capture_output=True, text=True)
    if r.returncode != 0:
        return None
    out = r.stdout.strip()
    if not out:
        return None
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return None


def issue_state(repo: str, num: int) -> dict:
    d = gh("issue", "view", str(num), "--repo", repo,
           "--json", "state,assignees,closedAt,updatedAt") or {}
    return {
        "state": d.get("state", "?"),
        "assigned": ",".join(a["login"] for a in d.get("assignees", [])) or "-",
        "updated": d.get("updatedAt", ""),
    }


def linked_pr(repo: str, issue_num: int, tid: str) -> dict | None:
    """Find the Copilot agent PR for this T-ID by branch name pattern 'copilot/t###-...'."""
    prs = gh("pr", "list", "--repo", repo, "--state", "all", "--limit", "30",
             "--author", "app/copilot-swe-agent",
             "--json", "number,state,isDraft,title,statusCheckRollup,headRefName,updatedAt") or []
    tid_low = tid.lower()
    pr = next((p for p in prs if tid_low in (p.get("headRefName") or "").lower()), None)
    if pr is None:
        return None
    rolls = pr.get("statusCheckRollup") or []
    fails = sum(1 for c in rolls if c.get("conclusion") == "FAILURE")
    pending = sum(1 for c in rolls if c.get("status") == "IN_PROGRESS" or c.get("conclusion") is None)
    passes = sum(1 for c in rolls if c.get("conclusion") == "SUCCESS")
    if fails:
        ci = f"FAIL {fails}/{len(rolls)}"
    elif pending:
        ci = f"RUN  {pending}/{len(rolls)}"
    elif passes and passes == len(rolls):
        ci = f"PASS {passes}/{len(rolls)}"
    else:
        ci = "—"
    return {
        "number": pr["number"],
        "state": pr["state"],
        "draft": pr.get("isDraft", False),
        "title": (pr.get("title") or "")[:50],
        "ci": ci,
        "updated": pr.get("updatedAt", ""),
    }


def fmt_age(iso: str) -> str:
    if not iso:
        return "-"
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    except ValueError:
        return "-"
    delta = datetime.now(timezone.utc) - dt
    s = int(delta.total_seconds())
    if s < 60: return f"{s}s"
    if s < 3600: return f"{s//60}m"
    if s < 86400: return f"{s//3600}h"
    return f"{s//86400}d"


def render(cache: dict) -> None:
    print(f"\n=== Wave 1 status @ {datetime.now().strftime('%H:%M:%S')} ===")
    print(f"{'TID':<6}{'#':<6}{'STATE':<10}{'AGENT':<28}{'PR':<8}{'PR_STATE':<14}{'CI':<14}{'AGE':<6}{'REPO'}")
    print("-" * 120)
    for tid, info in cache.items():
        s = issue_state(info["repo"], info["number"])
        pr = linked_pr(info["repo"], info["number"], tid)
        if pr:
            pr_num = f"#{pr['number']}"
            pr_state = ("draft " if pr["draft"] else "") + pr["state"]
            ci = pr["ci"]
            age = fmt_age(pr["updated"])
        else:
            pr_num = "-"
            pr_state = "no PR"
            ci = "-"
            age = fmt_age(s["updated"])
        repo_short = info["repo"].split("/")[-1][:28]
        print(f"{tid:<6}{'#'+str(info['number']):<6}{s['state']:<10}"
              f"{s['assigned'][:27]:<28}{pr_num:<8}{pr_state:<14}{ci:<14}{age:<6}{repo_short}")
    print("\nProject board: https://github.com/users/best-koder-ever/projects/3\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--watch", action="store_true",
                    help="Refresh every 60s until Ctrl-C")
    ap.add_argument("--interval", type=int, default=60)
    args = ap.parse_args()

    if not CACHE.exists():
        sys.exit(f"missing {CACHE}; run wave1_create_issues.py first")
    cache = json.loads(CACHE.read_text())

    if not args.watch:
        render(cache)
        return 0

    try:
        while True:
            render(cache)
            time.sleep(args.interval)
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    sys.exit(main())
