#!/usr/bin/env python3
"""Generate short spoken English "voice prompt" clips for demo bot personas.

Each curated discover bot gets a distinct, benign short quote spoken as audio,
written to bot-service/BotService/Personas/voice/{persona_id}.m4a — the file the
bot-service seeds into photo-service via the normal voice-prompt upload path.

Engines
-------
* default: espeak-ng (offline, always available). Female personas use the
  raised-pitch `+f3` variant; male personas use the default male voice.
* `--engine edge-tts`: nicer Microsoft voices (needs internet). Falls back to
  espeak-ng if edge-tts is not importable.

Only personas that also have a portrait in `Personas/photos/*.png` are generated
(those are the ones that appear in the discover deck). Idempotent — regenerates
every clip on each run.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parents[1]
VOICE_DIR = REPO / "bot-service" / "BotService" / "Personas" / "voice"
PHOTO_DIR = REPO / "bot-service" / "BotService" / "Personas" / "photos"
PERSONA_DIR = REPO / "bot-service" / "BotService" / "Personas"

# Distinct nice, benign quotes — one per discover persona. Kept short
# (~12-18 words) so each clip lands in the 3-30s window the backend enforces.
QUOTES: dict[str, str] = {
    "maja": "My happy place is a sunny terrace with good coffee and even better company.",
    "elsa": "I will absolutely beat you at trivia, but I make a terrible first move at dinner.",
    "linnea": "Ask me about my last spontaneous road trip, I have the photos to prove it.",
    "saga": "I collect sea glass and tiny moments, and I think you would fit right in.",
    "wilma": "Let's get dessert first, and decide what to order after we are friends.",
    "astrid": "I'm equally at home in the forest and the city, and I love a good debate.",
    "axel": "I can build almost anything, but I still need help picking the paint color.",
    "gustav": "Weekends are for long runs, longer brunches, and absolutely zero rush.",
    "noah": "I play guitar badly on purpose, and I sing even worse, so we are safe.",
    "oscar": "My superpower is finding the best taco place in any town we visit.",
    "erik-b": "I'd rather hear about your day than mine, so please, tell me everything.",
}

# Female personas use the raised-pitch variant; everyone else the default male.
VOICE_VARIANTS: dict[str, str] = {
    "female": "en-us+f3",
    "male": "en-us",
}

SAMPLE_RATE = 24000
BITRATE = "48k"
SPEED = 150  # spoken rate; keeps quotes ~4-9s


def _persona_gender(persona_id: str) -> str | None:
    try:
        data = json.loads((PERSONA_DIR / f"{persona_id}.json").read_text(encoding="utf-8"))
        gender = str(data.get("gender", "") or "").strip().lower()
        return gender or None
    except Exception:
        return None


def _espeak_available() -> bool:
    return shutil.which("espeak-ng") is not None


def _generate_espeak(text: str, variant: str, out_wav: pathlib.Path) -> None:
    subprocess.run(
        [
            "espeak-ng", "-v", variant, "-s", str(SPEED), "-p", "45",
            "-w", str(out_wav), text,
        ],
        check=True,
    )


def _generate_edge_tts(text: str, persona_id: str, out_wav: pathlib.Path) -> bool:
    try:
        import asyncio
        import edge_tts

        voice = "en-US-GuyNeural" if _persona_gender(persona_id) == "male" else "en-US-AriaNeural"

        async def _run() -> None:
            communicate = edge_tts.Communicate(text, voice, rate="-8%")
            await communicate.save(str(out_wav))

        asyncio.run(_run())
        return True
    except Exception:
        return False


def _transcode_to_m4a(wav: pathlib.Path, out: pathlib.Path) -> None:
    subprocess.run(
        [
            "ffmpeg", "-y", "-loglevel", "error", "-i", str(wav),
            "-ac", "1", "-ar", str(SAMPLE_RATE),
            "-c:a", "aac", "-b:a", BITRATE, str(out),
        ],
        check=True,
    )


def _duration_seconds(path: pathlib.Path) -> float:
    result = subprocess.run(
        [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", str(path),
        ],
        capture_output=True, text=True, check=True,
    )
    try:
        return float(result.stdout.strip())
    except ValueError:
        return 0.0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--engine", choices=("espeak", "edge-tts", "auto"), default="auto",
        help="TTS engine: auto = edge-tts if importable, else espeak.",
    )
    args = parser.parse_args()

    if not _espeak_available():
        print("espeak-ng is required for offline generation.", file=sys.stderr)
        return 1

    if not PHOTO_DIR.exists():
        print(f"Persona photo directory not found: {PHOTO_DIR}", file=sys.stderr)
        return 1

    persona_ids = sorted(p.stem for p in PHOTO_DIR.glob("*.png"))
    VOICE_DIR.mkdir(parents=True, exist_ok=True)

    generated: list[tuple[str, float, int]] = []
    skipped: list[str] = []

    for persona_id in persona_ids:
        text = QUOTES.get(persona_id)
        if not text:
            skipped.append(f"{persona_id} (no quote defined)")
            continue

        out = VOICE_DIR / f"{persona_id}.m4a"
        with tempfile.TemporaryDirectory() as tmp:
            wav = pathlib.Path(tmp) / f"{persona_id}.wav"

            use_edge = args.engine == "edge-tts" or (
                args.engine == "auto" and shutil.which("edge-tts") is not None
            )
            try:
                if use_edge and _generate_edge_tts(text, persona_id, wav):
                    pass  # wav produced by edge-tts
                else:
                    variant = VOICE_VARIANTS.get(_persona_gender(persona_id) or "", "en-us+f3")
                    _generate_espeak(text, variant, wav)
                _transcode_to_m4a(wav, out)
            except subprocess.CalledProcessError as exc:
                skipped.append(f"{persona_id} (generation failed: {exc})")
                continue

            duration = _duration_seconds(out)
            size = out.stat().st_size
            generated.append((persona_id, duration, size))

    print("Generated voice prompt clips:")
    for persona_id, duration, size in generated:
        flag = "  OK" if 3.0 <= duration <= 30.0 and size < 2 * 1024 * 1024 else "  !CHECK"
        print(f"  {persona_id:8s} {duration:5.1f}s {size // 1024:4d}KB{flag}")
    for item in skipped:
        print(f"  skipped: {item}")

    # Write a sidecar of measured durations so bot-service can send accurate
    # duration metadata when seeding (the upload endpoint otherwise defaults to 15s).
    if generated:
        durations = {persona_id: round(duration, 2) for persona_id, duration, _ in generated}
        (VOICE_DIR / "durations.json").write_text(
            json.dumps(durations, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote durations sidecar: {VOICE_DIR / 'durations.json'}")

    print(f"\n{len(generated)} generated in {VOICE_DIR}")
    return 0 if generated else 1


if __name__ == "__main__":
    raise SystemExit(main())
