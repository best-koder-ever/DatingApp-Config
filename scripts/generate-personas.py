#!/usr/bin/env python3
"""generate-personas.py — Create DatingApp bot personas at scale.

Writes one BotPersona-schema JSON file per persona, matching the C# model in
bot-service/BotService/Models/BotPersona.cs. Generation is deterministic: the
same --seed always yields the same set of personas, so output is reproducible
and easy to review in git.

Output goes to bot-service/BotService/Personas/generated/ by default. The
BotPersonaEngine loads that subfolder at startup (while still excluding
disabled/).

Usage:
    python3 scripts/generate-personas.py --count 100 --seed 42
    python3 scripts/generate-personas.py --count 25 --out /tmp/personas
    python3 scripts/generate-personas.py --validate
"""
from __future__ import annotations

import argparse
import json
import random
import re
import sys
import unicodedata
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = REPO_ROOT / "bot-service" / "BotService" / "Personas" / "generated"
PERSONAS_ROOT = REPO_ROOT / "bot-service" / "BotService" / "Personas"

# --------------------------------------------------------------------------
# Curated data pools (Swedish-flavored, matching the existing 90 personas)
# --------------------------------------------------------------------------

CITIES = {
    "Stockholm": (59.3293, 18.0686),
    "Göteborg": (57.7010, 11.9672),
    "Malmö": (55.6050, 13.0038),
    "Uppsala": (59.8586, 17.6389),
    "Västerås": (59.6099, 16.5448),
    "Örebro": (59.2753, 15.2134),
    "Linköping": (58.4108, 15.6214),
    "Jönköping": (57.7815, 14.1562),
    "Norrköping": (58.5877, 16.1924),
    "Lund": (55.7047, 13.1910),
    "Helsingborg": (56.0465, 12.6945),
    "Gävle": (60.6749, 17.1413),
    "Umeå": (63.8258, 20.2630),
    "Sundsvall": (62.3908, 17.3069),
    "Borås": (57.7210, 12.9401),
    "Eskilstuna": (59.3666, 16.5077),
    "Karlstad": (59.3793, 13.5036),
    "Halmstad": (56.6744, 12.8570),
    "Växjö": (56.8777, 14.8091),
    "Kalmar": (56.6634, 16.3568),
    "Luleå": (65.5848, 22.1567),
    "Falun": (60.6065, 15.6355),
    "Kristianstad": (56.0294, 14.1568),
    "Trollhättan": (58.2837, 12.2856),
    "Skövde": (58.3914, 13.8451),
    "Östersund": (63.1792, 14.6357),
}

MALE_NAMES = [
    "Adam", "Alexander", "Anders", "Andreas", "Anton", "Arvid", "Axel", "Bengt",
    "Björn", "Carl", "Daniel", "David", "Erik", "Filip", "Fredrik", "Gustav",
    "Hans", "Henrik", "Hugo", "Isak", "Jakob", "Johan", "Johannes", "Jonas",
    "Lars", "Linus", "Lucas", "Magnus", "Marcus", "Martin", "Mattias", "Max",
    "Michael", "Mikael", "Niklas", "Noah", "Olle", "Oscar", "Patrik", "Per",
    "Peter", "Pontus", "Robin", "Rolf", "Simon", "Stefan", "Thomas", "Tobias",
    "Viktor", "William",
]

FEMALE_NAMES = [
    "Alice", "Alva", "Amanda", "Anna", "Astrid", "Beatrice", "Birgitta", "Britta",
    "Caroline", "Elin", "Elsa", "Emma", "Eva", "Frida", "Gun", "Gunilla", "Hanna",
    "Helen", "Helena", "Ida", "Ingrid", "Isabelle", "Julia", "Karin", "Kristina",
    "Lena", "Linnea", "Lova", "Maja", "Margareta", "Maria", "Mia", "Nora", "Pia",
    "Saga", "Sara", "Sofia", "Sofie", "Stina", "Therese", "Vera", "Wilma",
]

UNISEX_NAMES = ["Alex", "Andrea", "Charlie", "Kim", "Robin", "Sam", "Tove", "Billie", "Elias", "Noa"]

LAST_NAMES = [
    "Andersson", "Berg", "Bergman", "Björk", "Eklund", "Engström", "Eriksson",
    "Fransson", "Gustafsson", "Hansen", "Holmgren", "Jansson", "Johansson",
    "Karlsson", "Larsson", "Lindberg", "Lindqvist", "Lindström", "Lundberg",
    "Magnusson", "Martinsson", "Nilsson", "Nordqvist", "Nordström", "Olofsson",
    "Persson", "Pettersson", "Roos", "Rydberg", "Sandberg", "Sjöberg", "Svensson",
    "Söderberg", "Thorsén", "Åberg",
]

INTERESTS = [
    "resor", "musik", "matlagning", "träning", "klättring", "vandring",
    "fotografering", "film", "böcker", "kaffe", "vin", "öl", "djur", "hundar",
    "katter", "dans", "simning", "cykling", "löpning", "yoga", "meditation",
    "trädgård", "bakning", "målning", "teater", "konserter", "spel", "brädspel",
    "padel", "tennis", "golf", "segling", "skidor", "snowboard", "sushi", "fika",
    "teknik", "programmering", "hantverk", "loppis", "design", "mode", "språk",
    "historia", "vetenskap", "natur", "stand-up",
]

OCCUPATIONS = [
    "Software Developer", "Nurse", "Teacher", "Designer", "Engineer",
    "Physiotherapist", "Architect", "Marketing Manager", "Chef", "Psychologist",
    "Journalist", "Veterinarian", "Entrepreneur", "Project Manager", "Data Analyst",
    "Musician", "Personal Trainer", "Social Worker", "Pharmacist", "Pilot",
    "Dentist", "Photographer", "Consultant", "Researcher", "Lärare",
    "Sjuksköterska", "Läkare", "Polis", "Brandman", "Lantbrukare", "Elektriker",
    "Snickare", "Kock", "Barnmorska", "Psykolog", "Ekonom", "Jurist", "Bibliotekarie",
]

EDUCATION = [
    "Stockholms universitet", "KTH Royal Institute of Technology", "Uppsala universitet",
    "Lunds universitet", "Göteborgs universitet", "Chalmers tekniska högskola",
    "Linköpings universitet", "Umeå universitet", "Karolinska institutet",
    "Handelshögskolan i Stockholm", "Linnéuniversitetet", "Malmö högskola",
]

GENDERS = ["female", "male", "female", "male", "female", "male", "non-binary"]
PREFERRED = {"female": "male", "male": "female", "non-binary": "any"}

SMOKING = ["Never", "Never", "Never", "Never", "Socially", "Sometimes"]
DRINKING = ["Socially", "Socially", "Never", "Sometimes", "Often"]
RELATIONSHIPS = [
    "Long-term relationship", "Long-term relationship", "Long-term relationship",
    "Casual dating", "Open to exploring", "Friends first",
]
CHATTINESS = ["low", "medium", "medium", "medium", "high", "high"]

BIO_TEMPLATES = [
    "Älskar {i1} och {i2}. Letar efter någon att dela {i3} med ✨",
    "{occ} som gillar {i1}. Hör av dig om du också älskar {i2} ☕",
    "Ny i {city}! Intresserad av {i1}, {i2} och långa promenader.",
    "Hund- eller kattperson? Jag är för {i1}. {occ} till vardags 🐕",
    "Tränar {i1}, jobbar som {occ} och lagar bättre {i2} än de flesta 🍳",
    "Letar efter äventyr och {i1}. Bonus om du gillar {i2} 💫",
    "Rakt på sak: {occ} som gillar {i1} och hoppas på riktiga möten.",
    "Hälften svensk, helt passionerad för {i1}. Fråga om mitt {i2}-projekt!",
    "Weekend = {i1} + {i2}. Vardag = {occ}. Berätta din bästa historia 🎧",
    "För {i1} och {i2}, men främst för skratt. {city} och lite till 🌍",
]


def slugify(text: str) -> str:
    """Lowercase ASCII-safe id fragment (å->a, ä->a, ö->o, spaces -> -)."""
    norm = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    norm = re.sub(r"[^A-Za-z0-9]+", "-", norm).strip("-")
    return norm.lower()


def load_existing_ids() -> set[str]:
    """Ids already in use (root + disabled), so generated ids never collide."""
    ids: set[str] = set()
    if not PERSONAS_ROOT.exists():
        return ids
    for path in PERSONAS_ROOT.rglob("*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict) and data.get("id"):
                ids.add(str(data["id"]).lower())
        except (json.JSONDecodeError, OSError):
            continue
    return ids


def make_persona(
    rng: random.Random,
    prefix: str,
    existing_ids: set[str],
    photo_source: str,
) -> dict:
    gender = rng.choice(GENDERS)

    if gender == "male":
        first = rng.choice(MALE_NAMES)
    elif gender == "female":
        first = rng.choice(FEMALE_NAMES)
    else:
        first = rng.choice(UNISEX_NAMES)

    last = rng.choice(LAST_NAMES)
    city = rng.choice(list(CITIES.keys()))
    lat, lon = CITIES[city]

    age = min(55, max(20, int(rng.gauss(30, 7))))
    occupation = rng.choice(OCCUPATIONS)
    education = rng.choice(EDUCATION)

    interests = rng.sample(INTERESTS, k=rng.randint(4, 6))
    bio = rng.choice(BIO_TEMPLATES).format(
        i1=interests[0], i2=interests[1], i3=interests[2],
        occ=occupation, city=city,
    )

    if gender == "male":
        height = rng.randint(172, 196)
    elif gender == "female":
        height = rng.randint(158, 182)
    else:
        height = rng.randint(160, 190)

    # Unique, collision-free id in the existing convention: {prefix}_{first}-{initial}
    base = f"{prefix}_{slugify(first)}-{slugify(last)[0]}"
    persona_id = base
    n = 2
    while persona_id.lower() in existing_ids:
        persona_id = f"{base}{n}"
        n += 1
    existing_ids.add(persona_id.lower())

    max_daily_messages = rng.randint(10, 30)
    max_response_delay = rng.randint(max_daily_messages + 60, 600)

    persona = {
        "id": persona_id,
        "firstName": first,
        "lastName": last,
        "age": age,
        "gender": gender,
        "preferredGender": PREFERRED[gender],
        "bio": bio,
        "city": city,
        "latitude": lat,
        "longitude": lon,
        "occupation": occupation,
        "education": education,
        "interests": interests,
        "languages": ["Svenska", "English"],
        "smokingStatus": rng.choice(SMOKING),
        "drinkingStatus": rng.choice(DRINKING),
        "relationshipType": rng.choice(RELATIONSHIPS),
        "height": height,
        "modes": ["synthetic", "warmup"],
        "behavior": {
            "swipeRightProbability": round(rng.uniform(0.30, 0.65), 2),
            "avgActionDelaySec": rng.randint(30, 90),
            "minResponseDelaySec": rng.randint(10, 60),
            "maxResponseDelaySec": max_response_delay,
            "chattiness": rng.choice(CHATTINESS),
            "activeStartHourUtc": rng.randint(6, 9),
            "activeEndHourUtc": rng.randint(21, 24),
            "maxDailySwipes": rng.randint(20, 60),
            "maxDailyMessages": max_daily_messages,
        },
    }

    if photo_source == "pravatar":
        persona["photoUrl"] = f"https://i.pravatar.cc/400?u={persona_id}"

    return persona


def validate_dir(out_dir: Path) -> int:
    """Re-read generated files and report schema/duplicate problems."""
    if not out_dir.exists():
        print(f"No files found in {out_dir}")
        return 1

    required = {"id", "firstName", "age", "gender", "city"}
    ids: set[str] = set()
    problems = 0
    count = 0

    for path in sorted(out_dir.glob("*.json")):
        count += 1
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print(f"  ❌ {path.name}: invalid JSON ({exc})")
            problems += 1
            continue

        missing = required - set(data.keys())
        if missing:
            print(f"  ❌ {path.name}: missing {sorted(missing)}")
            problems += 1
        if not data.get("id"):
            print(f"  ❌ {path.name}: empty id")
            problems += 1
        if str(data.get("id", "")).lower() in ids:
            print(f"  ❌ {path.name}: duplicate id {data.get('id')}")
            problems += 1
        ids.add(str(data.get("id", "")).lower())

    status = "✅" if problems == 0 else "❌"
    print(f"{status} Validated {count} generated personas in {out_dir} ({problems} problems)")
    return 1 if problems else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate DatingApp bot personas at scale.")
    parser.add_argument("--count", type=int, default=100, help="Number of personas to generate (default 100)")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Output directory (default: Personas/generated)")
    parser.add_argument("--seed", type=int, default=None, help="RNG seed for reproducible output (default: random)")
    parser.add_argument("--prefix", default="gen", help="Id prefix for generated personas (default: gen)")
    parser.add_argument("--photo-source", choices=["pravatar", "none"], default="pravatar",
                        help="Attach a remote avatar photoUrl (default: pravatar)")
    parser.add_argument("--force", action="store_true", help="Overwrite existing persona files")
    parser.add_argument("--validate", action="store_true", help="Validate existing generated files and exit")
    args = parser.parse_args()

    if args.validate:
        return validate_dir(args.out)

    if args.count <= 0:
        print("--count must be positive")
        return 1

    seed = args.seed if args.seed is not None else random.randrange(1 << 30)
    rng = random.Random(seed)

    existing_ids = load_existing_ids()
    args.out.mkdir(parents=True, exist_ok=True)

    generated = 0
    skipped = 0
    for _ in range(args.count):
        persona = make_persona(rng, args.prefix, existing_ids, args.photo_source)
        target = args.out / f"{persona['id']}.json"
        if target.exists() and not args.force:
            skipped += 1
            continue
        target.write_text(
            json.dumps(persona, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        generated += 1

    print(f"🧬 Generated {generated} personas (skipped {skipped} existing) → {args.out}")
    print(f"   seed={seed} prefix={args.prefix} photoSource={args.photo_source}")
    print(f"   Run --validate to re-check schema and id uniqueness.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
