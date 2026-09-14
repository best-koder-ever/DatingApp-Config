#!/usr/bin/env python3
"""Generate unique lightweight bot portraits through Google Stitch contact sheets.

The script writes prompt batches for Stitch: each generated IMAGE screen is a
3x4 grid of distinct dating-app portraits. After generation, screenshots are
downloaded and cropped into BotService/Personas/photos/{personaId}.jpg.

It intentionally keeps only compressed JPEGs in the bot photo folder; the full
Stitch screenshots remain under runs/ and are gitignored.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import pathlib
import subprocess
import textwrap
import urllib.request
from dataclasses import dataclass

from PIL import Image, ImageOps


ROOT = pathlib.Path(__file__).resolve().parents[1]
PERSONAS = ROOT / "bot-service" / "BotService" / "Personas"
PHOTO_DIR = PERSONAS / "photos"
RUNS = ROOT / "runs" / "stitch-bot-portrait-grids"
PROJECT_ID = "11184938783521064059"


@dataclass(frozen=True)
class Persona:
    id: str
    first_name: str
    age: int
    gender: str
    city: str
    occupation: str
    interests: list[str]
    languages: list[str]


def load_personas() -> list[Persona]:
    personas: list[Persona] = []
    for path in sorted(PERSONAS.glob("*.json")):
        data = json.loads(path.read_text())
        if data.get("id") == "demo-user":
            continue
        personas.append(Persona(
            id=data["id"],
            first_name=data.get("firstName", data["id"]),
            age=int(data.get("age", 30)),
            gender=data.get("gender", "person"),
            city=data.get("city", "Stockholm"),
            occupation=data.get("occupation", "creative professional"),
            interests=list(data.get("interests", [])),
            languages=list(data.get("languages", [])),
        ))
    return personas


def ancestry_hint(persona: Persona, index: int) -> str:
    languages = {l.lower() for l in persona.languages}
    if "urdu" in languages:
        return "Swedish-Pakistani"
    if "arabic" in languages:
        return "Swedish-Middle Eastern"
    if "somali" in languages:
        return "Swedish-Somali"
    if "polski" in languages:
        return "Swedish-Polish"
    if "français" in languages:
        return "French-Swedish"
    if "español" in languages:
        return "Latin-Swedish"
    if "português" in languages:
        return "Brazilian-Swedish"
    if "日本語" in languages:
        return "Japanese-Swedish"
    if "hindi" in languages:
        return "Swedish-Indian"
    if "中文" in languages:
        return "Chinese-Swedish"
    if "русский" in languages:
        return "Eastern European-Swedish"
    cycle = [
        "Nordic Swedish", "mixed European Swedish", "Sami-Swedish",
        "Baltic-Swedish", "Mediterranean-Swedish", "Black Swedish",
        "East Asian Swedish", "South Asian Swedish",
    ]
    return cycle[index % len(cycle)]


def gender_words(gender: str) -> str:
    g = gender.lower()
    if g == "female":
        return "woman"
    if g == "male":
        return "man"
    return "non-binary person with androgynous styling"


def archetype(persona: Persona) -> str:
    interests = ", ".join(persona.interests[:3]) or "city walks, coffee, music"
    return (
        f"{persona.first_name}, {persona.age}-year-old {gender_words(persona.gender)}, "
        f"{persona.occupation.lower()} in {persona.city}, dating-app archetype: "
        f"{interests}; authentic personal style tied to that lifestyle"
    )


def build_grid_prompt(batch: list[Persona], batch_index: int) -> str:
    lines = []
    for i, persona in enumerate(batch, start=1):
        hint = ancestry_hint(persona, batch_index * 12 + i)
        lines.append(f"{i}. {archetype(persona)}; appearance heritage: {hint}.")

    return textwrap.dedent(f"""
        Create one pure IMAGE screen: a 3 columns by 4 rows contact sheet of 12 separate square dating app profile portraits.

        Layout rules:
        - Exactly 12 equal square cells, row-major order matching the numbered list.
        - One different person per cell, shoulders-up or upper-body portrait.
        - No text, no numbers, no logos, no UI, no watermarks, no frames, no collage overlaps.
        - Each cell must crop cleanly as its own profile photo.

        Photography style:
        - Photorealistic natural smartphone dating-app photos, not studio headshots.
        - Real skin texture, varied facial features, varied hair, varied body presence, varied outfits.
        - Swedish urban/nature/cafe/home/activity backgrounds with shallow depth of field.
        - Friendly but not identical expressions; avoid model-perfect beauty sameness.

        People, in exact row-major order:
        {chr(10).join(lines)}
    """).strip()


def stitch_key() -> str:
    key = os.environ.get("STITCH_API_KEY", "").strip()
    if key:
        return key
    mcp = pathlib.Path.home() / ".config/Code - Insiders/User/mcp.json"
    if not mcp.exists():
        raise SystemExit("STITCH_API_KEY is not set and MCP config was not found.")
    data = json.loads(mcp.read_text())
    found: list[str] = []

    def walk(value):
        if isinstance(value, dict):
            env = value.get("env")
            if isinstance(env, dict) and env.get("STITCH_API_KEY"):
                found.append(env["STITCH_API_KEY"])
            for child in value.values():
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)

    walk(data)
    if not found:
        raise SystemExit("STITCH_API_KEY not found.")
    return found[0]


def run_node_generator(batch_file: pathlib.Path, project_id: str) -> None:
    node = pathlib.Path(__file__).with_name("stitch_generate_grids.js")
    env = os.environ.copy()
    env["STITCH_API_KEY"] = stitch_key()
    subprocess.run(["node", str(node), "--project", project_id, "--batches", str(batch_file)],
                   check=True, env=env)


def fetch(url: str, dst: pathlib.Path) -> bytes:
    req = urllib.request.Request(url, headers={"X-Goog-Api-Key": stitch_key()})
    with urllib.request.urlopen(req, timeout=180) as resp:
        blob = resp.read()
    dst.write_bytes(blob)
    return blob


def crop_grid(src: pathlib.Path, batch: list[Persona], out_dir: pathlib.Path, size: int, quality: int) -> list[dict]:
    records: list[dict] = []
    with Image.open(src) as raw:
        img = ImageOps.exif_transpose(raw).convert("RGB")
        w, h = img.size
        cell_w = w // 3
        cell_h = h // 4
        for idx, persona in enumerate(batch):
            col = idx % 3
            row = idx // 3
            cell = img.crop((col * cell_w, row * cell_h, (col + 1) * cell_w, (row + 1) * cell_h))
            # Stitch occasionally ignores "no text" and places a small caption at
            # the bottom of a grid cell. Crop a slightly tighter, top-anchored
            # square to keep the face and drop lower-third labels.
            side = int(min(cell.size) * 0.72)
            left = (cell.width - side) // 2
            top = 0
            cell = cell.crop((left, top, left + side, top + side))
            cell = cell.resize((size, size), Image.Resampling.LANCZOS)
            dst = out_dir / f"{persona.id}.jpg"
            cell.save(dst, "JPEG", quality=quality, optimize=True, progressive=True)
            records.append({
                "personaId": persona.id,
                "file": dst.name,
                "sourceGrid": src.name,
                "cell": idx + 1,
                "sha256": hashlib.sha256(dst.read_bytes()).hexdigest(),
                "bytes": dst.stat().st_size,
            })
    return records


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default=PROJECT_ID)
    ap.add_argument("--out", type=pathlib.Path, default=PHOTO_DIR)
    ap.add_argument("--runs", type=pathlib.Path, default=RUNS)
    ap.add_argument("--size", type=int, default=640)
    ap.add_argument("--quality", type=int, default=72)
    ap.add_argument("--generate", action="store_true")
    ap.add_argument("--crop", action="store_true")
    args = ap.parse_args()

    personas = load_personas()
    batches = [personas[i:i + 12] for i in range(0, len(personas), 12)]
    args.runs.mkdir(parents=True, exist_ok=True)
    args.out.mkdir(parents=True, exist_ok=True)

    batch_payload = []
    for i, batch in enumerate(batches, start=1):
        batch_payload.append({
            "index": i,
            "personas": [p.id for p in batch],
            "prompt": build_grid_prompt(batch, i - 1),
        })
    batch_file = args.runs / "batches.json"
    batch_file.write_text(json.dumps(batch_payload, indent=2, ensure_ascii=False))

    if args.generate:
        run_node_generator(batch_file, args.project)

    generated_path = args.runs / "generated.json"
    if args.crop:
        if not generated_path.exists():
            raise SystemExit(f"Missing {generated_path}; run with --generate first.")
        generated = json.loads(generated_path.read_text())
        records: list[dict] = []
        for entry, batch in zip(generated, batches):
            grid_file = args.runs / f"grid_{entry['index']:02d}.png"
            if not grid_file.exists():
                url = entry["downloadUrl"]
                if "=s" not in url:
                    url = f"{url}=s2048"
                fetch(url, grid_file)
            records.extend(crop_grid(grid_file, batch, args.out, args.size, args.quality))
        manifest = {
            "source": "google-stitch-contact-sheets",
            "project": args.project,
            "size": args.size,
            "quality": args.quality,
            "count": len(records),
            "photos": records,
        }
        (args.out / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True))
        print(f"wrote {len(records)} unique persona JPEGs to {args.out}")
    else:
        print(f"wrote {len(batch_payload)} batch prompts to {batch_file}")
        print(f"personas={len(personas)} batches={math.ceil(len(personas) / 12)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
