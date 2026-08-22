#!/usr/bin/env python3
"""
process-feedback.py — Whisper transcription pump for in-app voice feedback.

LEGACY laptop-dev fallback: the Docker/server stack now transcribes in-process
via bot-service's WhisperTranscriptionService -> whisper-service container.
Keep this script for local dotnet-run dev (no whisper-service) or manual runs.

Pulls unprocessed feedback rows from bot-service, downloads each audio file,
runs Whisper locally, then PATCHes the transcript back. Run from your laptop
on a timer (cron / systemd) — keep API keys off the server.

Usage:
    pip install faster-whisper requests
    python3 scripts/process-feedback.py --once
    python3 scripts/process-feedback.py --watch 600   # loop every 10 minutes

Env / flags:
    --base-url   default http://localhost:8089  (bot-service direct — bypasses
                 the YARP gateway /api/userfeedback rate limit)
    --model      faster-whisper model size (tiny/base/small/medium/large-v3)
    --language   ISO code or 'auto'
    --gh-issue OWNER/REPO  open a GitHub issue per transcribed feedback
                           (requires `gh` CLI authed; needs `repo` scope)
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import requests

DEFAULT_BASE_URL = os.environ.get("DEJTING_API_BASE", "http://localhost:8089")


def fetch_unprocessed(base_url: str) -> list[dict]:
    r = requests.get(
        f"{base_url}/api/userfeedback",
        params={"unprocessed": "true", "pageSize": 50},
        timeout=10,
    )
    r.raise_for_status()
    payload = r.json()
    return payload.get("items", [])


def download_audio(base_url: str, feedback_id: int, dest: Path) -> bool:
    r = requests.get(
        f"{base_url}/api/userfeedback/{feedback_id}/audio",
        stream=True,
        timeout=30,
    )
    if r.status_code == 404:
        return False
    r.raise_for_status()
    with dest.open("wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    return True


def patch_transcript(base_url: str, feedback_id: int, transcript: str) -> None:
    r = requests.patch(
        f"{base_url}/api/userfeedback/{feedback_id}",
        json={"transcript": transcript},
        timeout=15,
    )
    r.raise_for_status()


def open_github_issue(repo: str, item: dict, transcript: str) -> str | None:
    """Open a GitHub issue via `gh` CLI. Returns issue URL or None on failure."""
    fid = item["id"]
    screen = item.get("screen") or "unknown"
    app_version = item.get("appVersion") or "unknown"
    submitter = item.get("submitterKeycloakId") or "anonymous"
    received = item.get("receivedAt") or "?"
    title = f"[tester-feedback #{fid}] {transcript[:60] or '(no transcript)'}"
    body = (
        f"**Feedback id:** {fid}\n"
        f"**Received:** {received}\n"
        f"**Screen:** `{screen}`\n"
        f"**App version:** `{app_version}`\n"
        f"**Submitter:** `{submitter}`\n\n"
        f"### Transcript\n\n{transcript or '_(empty)_'}\n\n"
        f"### Note (typed)\n\n{item.get('noteText') or '_(none)_'}\n"
    )
    try:
        result = subprocess.run(
            [
                "gh", "issue", "create",
                "--repo", repo,
                "--title", title,
                "--body", body,
                "--label", "tester-feedback",
            ],
            capture_output=True, text=True, timeout=30, check=True,
        )
        url = result.stdout.strip().splitlines()[-1] if result.stdout else None
        return url
    except FileNotFoundError:
        print("  WARN: `gh` CLI not installed — skipping issue creation.",
              file=sys.stderr)
        return None
    except subprocess.CalledProcessError as e:
        print(f"  WARN: gh issue create failed: {e.stderr.strip()}",
              file=sys.stderr)
        return None


def transcribe(audio_path: Path, model_name: str, language: str) -> str:
    try:
        from faster_whisper import WhisperModel  # type: ignore
    except ImportError:
        print("ERROR: install faster-whisper first: pip install faster-whisper",
              file=sys.stderr)
        raise

    model = WhisperModel(model_name, device="cpu", compute_type="int8")
    segments, _info = model.transcribe(
        str(audio_path),
        language=None if language == "auto" else language,
        vad_filter=True,
    )
    return " ".join(seg.text.strip() for seg in segments).strip()


def process_once(base_url: str, model_name: str, language: str,
                 gh_repo: str | None = None) -> int:
    items = fetch_unprocessed(base_url)
    if not items:
        print(f"No unprocessed feedback at {base_url}.")
        return 0
    print(f"Found {len(items)} unprocessed item(s).")

    handled = 0
    for item in items:
        fid = item["id"]
        has_audio = item.get("hasAudio", False)
        note = item.get("noteText")

        if not has_audio:
            # Text-only entry — just mark processed with the note as 'transcript'.
            transcript = note or ""
            patch_transcript(base_url, fid, transcript)
            print(f"  #{fid} text-only — marked processed.")
            if gh_repo and transcript:
                url = open_github_issue(gh_repo, item, transcript)
                if url:
                    print(f"  #{fid} issue → {url}")
            handled += 1
            continue

        with tempfile.NamedTemporaryFile(suffix=".m4a", delete=False) as tf:
            tmp_path = Path(tf.name)
        try:
            if not download_audio(base_url, fid, tmp_path):
                print(f"  #{fid} audio missing on server — skipping.")
                continue
            print(f"  #{fid} transcribing ({tmp_path.stat().st_size} bytes)…")
            try:
                transcript = transcribe(tmp_path, model_name, language)
            except Exception as e:
                # Garbage / corrupt audio (e.g. early smoke-test rows containing
                # a few raw bytes). Mark with the note as transcript so it
                # stops re-appearing in the unprocessed queue.
                fallback = note or f"[unreadable audio: {type(e).__name__}]"
                print(f"  #{fid} transcribe failed ({e.__class__.__name__}); "
                      f"marking with fallback: {fallback!r}")
                patch_transcript(base_url, fid, fallback)
                handled += 1
                continue
            print(f"  #{fid} → {transcript!r}")
            patch_transcript(base_url, fid, transcript)
            if gh_repo:
                url = open_github_issue(gh_repo, item, transcript)
                if url:
                    print(f"  #{fid} issue → {url}")
            handled += 1
        finally:
            tmp_path.unlink(missing_ok=True)
    return handled


def main() -> int:
    ap = argparse.ArgumentParser(description="Transcribe pending user feedback.")
    ap.add_argument("--base-url", default=DEFAULT_BASE_URL)
    ap.add_argument("--model", default="base")
    ap.add_argument("--language", default="auto")
    ap.add_argument("--gh-issue", metavar="OWNER/REPO",
                    help="Open a GitHub issue per transcribed feedback "
                         "(requires `gh` CLI authed).")
    grp = ap.add_mutually_exclusive_group()
    grp.add_argument("--once", action="store_true", default=True)
    grp.add_argument("--watch", type=int, metavar="SECONDS",
                     help="Loop every N seconds")
    args = ap.parse_args()

    if args.watch:
        print(f"Watching {args.base_url} every {args.watch}s — Ctrl-C to stop.")
        while True:
            try:
                process_once(args.base_url, args.model, args.language,
                             args.gh_issue)
            except Exception as e:
                print(f"WARN: {e}", file=sys.stderr)
            time.sleep(args.watch)
    else:
        process_once(args.base_url, args.model, args.language, args.gh_issue)
    return 0


if __name__ == "__main__":
    sys.exit(main())
