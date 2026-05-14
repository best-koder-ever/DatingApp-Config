#!/usr/bin/env python3
"""
Sync all specs/*/tasks.md → GitHub Issues + Projects v2 board.

Source of truth: the markdown files. Script is one-way (md → GH) and idempotent.

Modes:
    --dry-run         (default) Print what would change, no API writes.
    --apply           Actually push changes.
    --create-project  Create the GH Projects v2 board + custom fields, print id.
    --spec=NNN        Limit to a single spec (e.g. --spec=005).

Issue title format:    "[T### / NNN] <task title>"
Project custom fields: Spec, Phase, Wave, Priority, Category, Status (built-in)

Requires: `gh` CLI authenticated with `project` scope.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# ───────────────────────── Config ─────────────────────────

REPO_ROOT = Path(__file__).resolve().parent.parent
SPECS_DIR = REPO_ROOT / "specs"

OWNER = "best-koder-ever"
HUB_REPO = f"{OWNER}/DatingApp-Config"
PROJECT_TITLE = "DatingApp Roadmap"

# Filled in lazily after --create-project (or read from env / cache file).
CACHE_FILE = REPO_ROOT / ".cache" / "sync_specs.json"

CUSTOM_FIELDS = {
    # name: (data_type, options-or-None)
    "Spec":     ("SINGLE_SELECT", ["001-mvp-foundation", "002-agentic-ai", "003-bot-swarm",
                                   "004-multi-app", "005-core-differentiation"]),
    "Phase":    ("SINGLE_SELECT", [f"Phase {i}" for i in range(0, 21)]),
    "Wave":     ("SINGLE_SELECT", ["—"] + [f"Wave {i}" for i in range(0, 8)]),
    "Priority": ("SINGLE_SELECT", ["P0", "P1", "P2", "P3", "DEFERRED"]),
    "Category": ("SINGLE_SELECT", ["Infra", "API", "Core", "AI", "Data", "Flutter",
                                   "Test", "Planning", "Testing", "DevOps", "Other"]),
}

# ───────────────────────── Parser ─────────────────────────

# Matches: - [x] T123 [P0] [Infra] description
TASK_RE = re.compile(
    r"^- \[(?P<status>[ xX])\] (?P<tid>T\d{3})\s+"
    r"(?:\[(?P<prio>[^\]]+)\]\s+)?"
    r"(?:\[(?P<cat>[^\]]+)\]\s+)?"
    r"(?P<title>.+?)\s*$"
)
PHASE_RE = re.compile(r"^##+\s+Phase\s+(\d+)\b", re.IGNORECASE)
WAVE_RE  = re.compile(r"^##+\s+Wave\s+(\d+)\b", re.IGNORECASE)


@dataclass
class Task:
    spec: str            # "005-core-differentiation"
    tid: str             # "T520"
    title: str
    done: bool
    phase: Optional[str] = None
    wave: Optional[str] = None
    priority: Optional[str] = None
    category: Optional[str] = None

    @property
    def issue_title(self) -> str:
        spec_short = self.spec.split("-", 1)[0]   # "005"
        # Trim very long titles (GH limit is 256, keep room for prefix).
        body = self.title.strip()
        if len(body) > 200:
            body = body[:197] + "..."
        return f"[{self.tid} / {spec_short}] {body}"

    @property
    def issue_body(self) -> str:
        return (
            f"**Spec**: `{self.spec}`  \n"
            f"**Task**: `{self.tid}`  \n"
            f"**Phase**: {self.phase or '-'}  \n"
            f"**Wave**: {self.wave or '-'}  \n"
            f"**Priority**: {self.priority or '-'}  \n"
            f"**Category**: {self.category or '-'}  \n\n"
            f"_Auto-synced from `specs/{self.spec}/tasks.md`. "
            f"Edit the markdown file, do not edit this issue body manually._"
        )

    def normalize_priority(self) -> Optional[str]:
        if not self.priority:
            return None
        p = self.priority.strip().upper()
        if "DEFERRED" in p:
            return "DEFERRED"
        m = re.match(r"P[0-3]", p)
        return m.group(0) if m else None

    def normalize_category(self) -> Optional[str]:
        if not self.category:
            return None
        c = self.category.strip()
        # Map known synonyms to enum values.
        return {
            "infra": "Infra", "api": "API", "core": "Core", "ai": "AI",
            "data": "Data", "flutter": "Flutter", "test": "Test",
            "testing": "Testing", "planning": "Planning", "devops": "DevOps",
        }.get(c.lower(), "Other")


def parse_spec(path: Path) -> list[Task]:
    spec_id = path.parent.name
    tasks: list[Task] = []
    phase: Optional[str] = None
    wave: Optional[str] = None

    for line in path.read_text(encoding="utf-8").splitlines():
        if (m := PHASE_RE.match(line)):
            phase = f"Phase {int(m.group(1))}"
            continue
        if (m := WAVE_RE.match(line)):
            wave = f"Wave {int(m.group(1))}"
            continue
        if (m := TASK_RE.match(line)):
            t = Task(
                spec=spec_id,
                tid=m.group("tid"),
                title=m.group("title").strip(),
                done=m.group("status").strip().lower() == "x",
                phase=phase, wave=wave,
                priority=m.group("prio"),
                category=m.group("cat"),
            )
            t.priority = t.normalize_priority()
            t.category = t.normalize_category()
            tasks.append(t)
    return tasks


def parse_all_specs(only_spec: Optional[str] = None) -> list[Task]:
    out: list[Task] = []
    for tasks_md in sorted(SPECS_DIR.glob("*/tasks.md")):
        if only_spec and tasks_md.parent.name.split("-", 1)[0] != only_spec:
            continue
        out.extend(parse_spec(tasks_md))
    # Dedupe (same T-ID can appear in multiple phases of one spec — keep first
    # occurrence for metadata, but mark done if any instance is done).
    by_key: dict[tuple[str, str], Task] = {}
    for t in out:
        key = (t.spec, t.tid)
        if key not in by_key:
            by_key[key] = t
        else:
            by_key[key].done = by_key[key].done or t.done
    return list(by_key.values())


# ───────────────────────── GH helpers ─────────────────────────

class GhError(RuntimeError):
    pass


def gh(*args: str, check: bool = True) -> str:
    r = subprocess.run(["gh", *args], capture_output=True, text=True)
    if r.returncode != 0:
        if check:
            sys.stderr.write(f"gh {' '.join(args)} failed:\n{r.stderr}\n")
            sys.exit(1)
        raise GhError(r.stderr.strip() or "gh failed")
    return r.stdout.strip()


def graphql(query: str, check: bool = True, **variables) -> dict:
    # Use -f (force string) for ALL vars: GraphQL ID! and String! both accept
    # strings, but -F auto-coerces numeric-looking values to ints which breaks
    # singleSelectOptionId (always a string, sometimes all-digits).
    args = ["api", "graphql", "-f", f"query={query}"]
    for k, v in variables.items():
        args += ["-f", f"{k}={v}"]
    return json.loads(gh(*args, check=check))


def load_cache() -> dict:
    if CACHE_FILE.exists():
        return json.loads(CACHE_FILE.read_text())
    return {}


def save_cache(data: dict) -> None:
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps(data, indent=2))


# ───────────────────────── Project bootstrap ─────────────────────────

def find_or_create_project(create: bool, dry: bool) -> dict:
    cache = load_cache()
    if "project_id" in cache and not create:
        return cache

    raw = gh("project", "list", "--owner", OWNER, "--format", "json")
    proj = next(
        (p for p in json.loads(raw)["projects"] if p["title"] == PROJECT_TITLE),
        None,
    )

    if proj is None:
        if dry:
            print(f"[dry-run] Would create project '{PROJECT_TITLE}' under {OWNER}")
            return {}
        if not create:
            sys.exit(f"Project '{PROJECT_TITLE}' not found. Run with --create-project.")
        out = gh("project", "create", "--owner", OWNER, "--title", PROJECT_TITLE,
                 "--format", "json")
        proj = json.loads(out)
        print(f"Created project #{proj['number']} ({proj['id']})")

    cache["project_id"] = proj["id"]
    cache["project_number"] = proj["number"]
    cache["project_url"] = proj.get("url")

    # Ensure custom fields exist.
    fields_raw = gh("project", "field-list", str(proj["number"]),
                    "--owner", OWNER, "--format", "json")
    existing = {f["name"]: f for f in json.loads(fields_raw)["fields"]}
    cache.setdefault("fields", {})

    for name, (dtype, options) in CUSTOM_FIELDS.items():
        if name in existing:
            cache["fields"][name] = existing[name]
            continue
        if dry:
            print(f"[dry-run] Would create field '{name}' ({dtype})")
            continue
        if dtype == "SINGLE_SELECT":
            args = ["project", "field-create", str(proj["number"]),
                    "--owner", OWNER, "--name", name,
                    "--data-type", "SINGLE_SELECT",
                    "--single-select-options", ",".join(options or []),
                    "--format", "json"]
        else:
            args = ["project", "field-create", str(proj["number"]),
                    "--owner", OWNER, "--name", name,
                    "--data-type", dtype, "--format", "json"]
        out = gh(*args)
        cache["fields"][name] = json.loads(out)
        print(f"Created field '{name}'")

    if not dry:
        save_cache(cache)
    return cache


# ───────────────────────── Issue + project ops ─────────────────────────

def fetch_existing_issues() -> dict[str, dict]:
    """Map issue title-prefix '[T### / NNN]' → {number, state, node_id, title}.

    GitHub search ignores '[' so we list ALL issues and filter in Python.
    """
    raw = gh("issue", "list", "--repo", HUB_REPO, "--state", "all",
             "--limit", "2000",
             "--json", "number,title,state,id")
    by_prefix: dict[str, dict] = {}
    for it in json.loads(raw):
        m = re.match(r"^(\[T\d{3} / \d{3}\])", it["title"])
        if m:
            by_prefix[m.group(1)] = it
    return by_prefix


def project_items_by_issue(project_id: str) -> dict[str, str]:
    """Map issue node_id → project item id for items already in the project."""
    out: dict[str, str] = {}
    cursor = None
    query = """
    query($pid:ID!,$after:String) {
      node(id:$pid) {
        ... on ProjectV2 {
          items(first:100, after:$after) {
            pageInfo { hasNextPage endCursor }
            nodes {
              id
              content {
                ... on Issue { id }
              }
            }
          }
        }
      }
    }
    """
    while True:
        vars_ = {"pid": project_id}
        if cursor:
            vars_["after"] = cursor
        result = graphql(query, **vars_)
        page = result["data"]["node"]["items"]
        for n in page["nodes"]:
            c = n.get("content")
            if c and "id" in c:
                out[c["id"]] = n["id"]
        if not page["pageInfo"]["hasNextPage"]:
            break
        cursor = page["pageInfo"]["endCursor"]
    return out


def add_issue_to_project(project_id: str, issue_node_id: str) -> str:
    q = """
    mutation($pid:ID!,$iid:ID!) {
      addProjectV2ItemById(input:{projectId:$pid,contentId:$iid}) { item { id } }
    }
    """
    r = graphql(q, pid=project_id, iid=issue_node_id)
    return r["data"]["addProjectV2ItemById"]["item"]["id"]


def set_select_field(project_id: str, item_id: str, field_id: str, option_id: str) -> None:
    q = """
    mutation($pid:ID!,$iid:ID!,$fid:ID!,$oid:String!) {
      updateProjectV2ItemFieldValue(input:{
        projectId:$pid, itemId:$iid, fieldId:$fid,
        value:{ singleSelectOptionId:$oid }
      }) { projectV2Item { id } }
    }
    """
    graphql(q, check=False, pid=project_id, iid=item_id, fid=field_id, oid=option_id)


def field_option_id(field: dict, option_name: str) -> Optional[str]:
    for o in field.get("options", []):
        if o["name"] == option_name:
            return o["id"]
    return None


def create_issue(t: Task) -> dict:
    out = gh("issue", "create",
             "--repo", HUB_REPO,
             "--title", t.issue_title,
             "--body", t.issue_body)
    # `gh issue create` prints the URL. Resolve number via API.
    url = out.strip().splitlines()[-1]
    num = url.rsplit("/", 1)[-1]
    raw = gh("issue", "view", num, "--repo", HUB_REPO,
             "--json", "number,title,state,id")
    return json.loads(raw)


def close_issue(num: int) -> None:
    gh("issue", "close", str(num), "--repo", HUB_REPO, "--reason", "completed")


def reopen_issue(num: int) -> None:
    gh("issue", "reopen", str(num), "--repo", HUB_REPO)


# ───────────────────────── Main sync ─────────────────────────

def sync(only_spec: Optional[str], dry: bool, create_project: bool) -> int:
    tasks = parse_all_specs(only_spec)
    print(f"Parsed {len(tasks)} tasks from specs/")
    by_spec: dict[str, list[Task]] = {}
    for t in tasks:
        by_spec.setdefault(t.spec, []).append(t)
    for spec, items in sorted(by_spec.items()):
        done = sum(1 for t in items if t.done)
        print(f"  {spec}: {len(items)} tasks ({done} done, {len(items)-done} pending)")

    cache = find_or_create_project(create=create_project, dry=dry)
    if not cache.get("project_id"):
        # Pure dry-run with no project yet — bail after summary.
        print("\n(no project_id available; skipping issue sync — run --create-project first)")
        return 0

    project_id = cache["project_id"]
    fields = cache["fields"]

    print("\nFetching existing issues + project items …")
    by_prefix = fetch_existing_issues()
    issue_to_item = project_items_by_issue(project_id) if not dry else {}
    print(f"  {len(by_prefix)} issues already exist with [T### / NNN] prefix")
    print(f"  {len(issue_to_item)} project items already linked")

    created = closed = reopened = added_to_project = field_writes = 0

    for idx, t in enumerate(tasks, 1):
        spec_short = t.spec.split("-", 1)[0]
        prefix = f"[{t.tid} / {spec_short}]"
        existing = by_prefix.get(prefix)

        if idx % 25 == 0 and not dry:
            print(f"  [{idx}/{len(tasks)}] created={created} closed={closed} "
                  f"linked={added_to_project} fields={field_writes}")

        if not existing:
            if dry:
                print(f"  + CREATE {t.issue_title}")
            else:
                existing = create_issue(t)
                by_prefix[prefix] = existing
            created += 1
            new_issue = True
        else:
            new_issue = False

        if not existing:
            continue

        target_state = "CLOSED" if t.done else "OPEN"
        if existing["state"] != target_state:
            if dry:
                print(f"  ~ {existing['state']} → {target_state}  #{existing['number']} {prefix}")
            else:
                if t.done:
                    close_issue(existing["number"])
                    closed += 1
                else:
                    reopen_issue(existing["number"])
                    reopened += 1
            existing["state"] = target_state

        if dry:
            continue

        # Ensure linked to project.
        item_id = issue_to_item.get(existing["id"])
        if item_id is None:
            item_id = add_issue_to_project(project_id, existing["id"])
            issue_to_item[existing["id"]] = item_id
            added_to_project += 1

        # Push custom field values.
        spec_label = t.spec
        for fname, value in [
            ("Spec", spec_label),
            ("Phase", t.phase),
            ("Wave", t.wave or "—"),
            ("Priority", t.priority),
            ("Category", t.category),
        ]:
            if not value:
                continue
            f = fields.get(fname)
            if not f:
                continue
            oid = field_option_id(f, value)
            if not oid:
                continue
            try:
                set_select_field(project_id, item_id, f["id"], oid)
                field_writes += 1
            except (GhError, SystemExit) as e:
                # Non-fatal: log and continue.
                sys.stderr.write(f"  ! field-write {fname}={value} on #{existing['number']}: {e}\n")

    print("\nSummary:")
    print(f"  Created issues:       {created}")
    print(f"  Closed (newly done):  {closed}")
    print(f"  Reopened:             {reopened}")
    print(f"  Added to project:     {added_to_project}")
    print(f"  Field updates:        {field_writes}")
    if cache.get("project_url"):
        print(f"\n  → {cache['project_url']}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true", default=True,
                    help="(default) Print what would change.")
    ap.add_argument("--apply", action="store_true",
                    help="Actually push changes to GitHub.")
    ap.add_argument("--create-project", action="store_true",
                    help="Create the GH project + custom fields if missing.")
    ap.add_argument("--spec", default=None,
                    help="Sync only the given spec id (e.g. --spec=005)")
    args = ap.parse_args()
    dry = not args.apply
    return sync(only_spec=args.spec, dry=dry, create_project=args.create_project)


if __name__ == "__main__":
    sys.exit(main())
