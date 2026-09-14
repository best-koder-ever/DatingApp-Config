#!/usr/bin/env python3
"""Assign generated portraits to bot personas as lightweight JPEG assets.

Input can be a Stitch harvest directory, a folder of PNG/JPEG portraits, or both.
The script writes bot-service/BotService/Personas/photos/{personaId}.jpg by
default, plus optional -2/-3 slots when enough source images are available.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import random
from dataclasses import dataclass
from typing import Iterable

from PIL import Image, ImageOps


ROOT = pathlib.Path(__file__).resolve().parents[1]
PERSONAS = ROOT / "bot-service" / "BotService" / "Personas"
PHOTOS = PERSONAS / "photos"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}


@dataclass(frozen=True)
class Persona:
    id: str
    gender: str
    age: int


@dataclass(frozen=True)
class SourceImage:
    path: pathlib.Path
    gender: str = "unknown"
    age: int | None = None


def load_personas() -> list[Persona]:
    personas: list[Persona] = []
    for path in sorted(PERSONAS.glob("*.json")):
        if path.name == "demo-user.json":
            continue
        data = json.loads(path.read_text())
        personas.append(Persona(
            id=data["id"],
            gender=str(data.get("gender", "")).lower(),
            age=int(data.get("age", 0) or 0),
        ))
    return personas


def load_manifest_images(source_dir: pathlib.Path) -> list[SourceImage]:
    manifest_path = source_dir / "manifest.json"
    if not manifest_path.exists():
        return []

    manifest = json.loads(manifest_path.read_text())
    images: list[SourceImage] = []
    for entry in manifest.values():
        file_name = entry.get("file")
        if not file_name:
            continue
        path = source_dir / file_name
        if not path.exists():
            continue
        images.append(SourceImage(
            path=path,
            gender=str(entry.get("gender_guess") or "unknown").lower(),
            age=entry.get("age_guess"),
        ))
    return images


def discover_images(source_dirs: Iterable[pathlib.Path]) -> list[SourceImage]:
    images: list[SourceImage] = []
    for source_dir in source_dirs:
        manifest_images = load_manifest_images(source_dir)
        if manifest_images:
            images.extend(manifest_images)
            continue
        for path in sorted(source_dir.rglob("*")):
            if path.is_file() and path.suffix.lower() in IMAGE_EXTS:
                images.append(SourceImage(path=path))
    return images


def age_distance(persona: Persona, image: SourceImage) -> int:
    if image.age is None or persona.age <= 0:
        return 0
    return abs(persona.age - image.age)


def gender_penalty(persona: Persona, image: SourceImage) -> int:
    if image.gender == "unknown" or not persona.gender:
        return 0
    if persona.gender in image.gender or image.gender in persona.gender:
        return 0
    return 20


def assign_images(personas: list[Persona], images: list[SourceImage], slots: int) -> dict[str, list[SourceImage]]:
    rng = random.Random(42)
    pool = images[:]
    rng.shuffle(pool)
    assignments: dict[str, list[SourceImage]] = {}

    for persona in personas:
        scored = sorted(
            pool,
            key=lambda img: (
                gender_penalty(persona, img),
                age_distance(persona, img),
                hashlib.sha256(f"{persona.id}:{img.path}".encode()).hexdigest(),
            ),
        )
        selected = scored[:slots]
        if not selected:
            break
        assignments[persona.id] = selected
        for img in selected:
            if img in pool:
                pool.remove(img)
        if len(pool) < slots:
            pool = images[:]
            rng.shuffle(pool)

    return assignments


def write_jpeg(src: pathlib.Path, dst: pathlib.Path, size: int, quality: int) -> int:
    with Image.open(src) as img:
        img = ImageOps.exif_transpose(img).convert("RGB")
        w, h = img.size
        side = min(w, h)
        left = (w - side) // 2
        top = (h - side) // 2
        img = img.crop((left, top, left + side, top + side))
        img = img.resize((size, size), Image.Resampling.LANCZOS)
        dst.parent.mkdir(parents=True, exist_ok=True)
        img.save(dst, "JPEG", quality=quality, optimize=True, progressive=True)
    return dst.stat().st_size


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", action="append", type=pathlib.Path, required=True,
                    help="Directory containing generated/harvested portraits.")
    ap.add_argument("--out", type=pathlib.Path, default=PHOTOS)
    ap.add_argument("--slots", type=int, default=1, choices=range(1, 7))
    ap.add_argument("--size", type=int, default=640)
    ap.add_argument("--quality", type=int, default=72)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    personas = load_personas()
    images = discover_images(args.source)
    if not images:
        raise SystemExit("No source images found.")

    assignments = assign_images(personas, images, args.slots)
    manifest: dict[str, object] = {
        "format": "jpg",
        "size": args.size,
        "quality": args.quality,
        "personas": {},
    }
    total_bytes = 0
    written = 0

    for persona_id, selected in assignments.items():
        outputs = []
        for slot, image in enumerate(selected, start=1):
            suffix = "" if slot == 1 else f"-{slot}"
            dst = args.out / f"{persona_id}{suffix}.jpg"
            outputs.append(dst.name)
            if dst.exists() and not args.force:
                total_bytes += dst.stat().st_size
                continue
            if args.dry_run:
                continue
            total_bytes += write_jpeg(image.path, dst, args.size, args.quality)
            written += 1
        manifest["personas"][persona_id] = {
            "outputs": outputs,
            "sources": [str(img.path) for img in selected],
        }

    if not args.dry_run:
        (args.out / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True))

    print(f"personas={len(assignments)} sources={len(images)} written={written} approx_size={total_bytes // 1024} KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
