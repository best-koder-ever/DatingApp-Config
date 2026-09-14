#!/usr/bin/env python3
"""Harvest photorealistic portrait photos out of a Google Stitch project.

Background
----------
Stitch is a UI design tool, but it also stores bare-photo screens: screens whose
`screenType` is IMAGE and whose prompt is a photographic description (e.g.
"Photorealistic headshot portrait of a Black woman in her early 60s ...").

Read path (no stitch-mcp needed -- the CLI has a schema bug on some payloads):

    GET https://stitch.googleapis.com/v1/projects/{project}/screens
        X-Goog-Api-Key: $STITCH_API_KEY

Each screen carries:
    .screenshot.downloadUrl  -> image URL; the screen's stated width/height is
                               the native size, but the URL as returned is the
                               512px rendition. Appending "=s<size>" fetches the
                               native resolution (measured: 1024x1024).
    .prompt                  -> the photography prompt, i.e. the subject's
                               described age, ethnicity, hair and clothing.
    .title                   -> short label.

Usage:
    python3 scripts/stitch_portrait_harvest.py --project 11184938783521064059 \
        --out /tmp/portraits

Auth: STITCH_API_KEY must be set (value lives in
~/.config/Code - Insiders/User/mcp.json -> servers.stitch.env.STITCH_API_KEY).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import re
import subprocess
import sys
import urllib.request

API = "https://stitch.googleapis.com/v1"


def api_key() -> str:
    key = os.environ.get("STITCH_API_KEY", "").strip()
    if key:
        return key
    raise SystemExit(
        "STITCH_API_KEY is not set. Export it, e.g.:\n"
        "  export STITCH_API_KEY=$(jq -r '[.servers[]|(.env//{})|to_entries[]|"
        "select(.key==\"STITCH_API_KEY\")|.value]|first' "
        "\"$HOME/.config/Code - Insiders/User/mcp.json\")"
    )


def get_json(url: str, key: str) -> dict:
    req = urllib.request.Request(url, headers={"X-Goog-Api-Key": key})
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.load(resp)


def fetch_bytes(url: str, key: str) -> bytes:
    req = urllib.request.Request(url, headers={"X-Goog-Api-Key": key})
    with urllib.request.urlopen(req, timeout=180) as resp:
        return resp.read()


def image_size(path: pathlib.Path) -> tuple[int, int] | None:
    out = subprocess.run(["identify", "-format", "%w %h", str(path)],
                         capture_output=True, text=True)
    if out.returncode != 0:
        return None
    try:
        w, h = out.stdout.split()
        return int(w), int(h)
    except ValueError:
        return None


def to_png(src: pathlib.Path, dst: pathlib.Path) -> bool:
    out = subprocess.run(["convert", str(src), str(dst)], capture_output=True, text=True)
    if out.returncode != 0:
        print(f"    convert failed: {out.stderr.strip()[:160]}")
        return False
    return True


AGE_RE = re.compile(r"\b(early|mid|late)?\s*(teens|twenties|twenties|thirties|forties|"
                    r"fifties|sixties|twenties|20s|30s|40s|50s|60s|70s)\b", re.I)


def guess_demographics(prompt: str) -> dict:
    """Best-effort read of the prompt so personas can be matched to portraits."""
    p = prompt.lower()
    gender = "unknown"
    if re.search(r"\b(woman|female|lady|girl|she)\b", p):
        gender = "female"
    if re.search(r"\b(man|male|guy|boy|he)\b", p):
        gender = "male" if gender == "unknown" else gender + "+male"
    age = None
    m = re.search(r"(early|mid|late)?\s*(20s|30s|40s|50s|60s|70s)", p)
    if m:
        base = {"20s": 22, "30s": 32, "40s": 42, "50s": 52, "60s": 62, "70s": 72}[m.group(2)]
        age = base + (0 if m.group(1) == "early" else 5 if m.group(1) == "mid" else 9 if m.group(1) == "late" else 5)
    return {"gender_guess": gender, "age_guess": age}


def harvest(project: str, out_dir: pathlib.Path, min_px: int, size: int) -> int:
    key = api_key()
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = out_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    seen = {v["sha256"] for v in manifest.values()}
    added = 0

    screens = get_json(f"{API}/projects/{project}/screens", key).get("screens", [])
    images = [s for s in screens if (s.get("screenType") or "").upper() == "IMAGE"]
    print(f"project {project}: {len(screens)} screens, {len(images)} IMAGE screens")

    for scr in images:
        url = (scr.get("screenshot") or {}).get("downloadUrl")
        if not url:
            continue
        native = max(int(scr.get("width") or 0), int(scr.get("height") or 0))
        if native and native < min_px:
            print(f"  skip {native}px screen {scr.get('title')}")
            continue
        full = f"{url}=s{size}"
        if full in manifest:
            continue
        try:
            blob = fetch_bytes(full, key)
        except Exception as exc:
            print(f"  fetch failed for {scr.get('title')}: {exc}")
            continue
        digest = hashlib.sha256(blob).hexdigest()
        if digest in seen:
            continue

        tmp = out_dir / "_tmp.img"
        tmp.write_bytes(blob)
        dims = image_size(tmp)
        if dims is None:
            tmp.unlink(missing_ok=True)
            continue
        w, h = dims
        if min(w, h) < min_px:
            print(f"  skip {w}x{h} (below {min_px}px)")
            tmp.unlink(missing_ok=True)
            continue

        n = len(manifest) + 1
        final = out_dir / f"portrait_{n:04d}.png"
        if not to_png(tmp, final):
            tmp.unlink(missing_ok=True)
            continue
        tmp.unlink(missing_ok=True)

        prompt = scr.get("prompt") or ""
        manifest[full] = {
            "file": final.name,
            "project": project,
            "screen": scr.get("name"),
            "title": scr.get("title"),
            "prompt": prompt,
            "width": w,
            "height": h,
            "bytes": len(blob),
            "sha256": digest,
            "source_url": full,
            **guess_demographics(prompt),
        }
        seen.add(digest)
        added += 1
        print(f"  + {final.name}  {w}x{h}  {(scr.get('title') or '')[:60]}")

    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True))
    print(f"harvested {added} new portraits -> {out_dir} (total {len(manifest)})")
    return added


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True, action="append", dest="projects")
    ap.add_argument("--out", required=True, type=pathlib.Path)
    ap.add_argument("--min-px", type=int, default=512)
    ap.add_argument("--size", type=int, default=1024)
    args = ap.parse_args()
    for project in args.projects:
        harvest(project, args.out, args.min_px, args.size)
    return 0


if __name__ == "__main__":
    sys.exit(main())
