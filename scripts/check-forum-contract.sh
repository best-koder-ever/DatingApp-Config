#!/usr/bin/env bash
# Asserts the Flutter forum client and the forum-service API still agree.
#
# The two sides have drifted twice, in both directions: the Dart models once expected a
# title/body shape no backend served, and the backend once returned fields no client read.
# This check needs no running services, so it belongs in CI.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONTRACTS="$ROOT/forum-service/Contracts/ForumContracts.cs"
LIMITS_C="$ROOT/forum-service/Models/ForumLimits.cs"

# The Flutter client is a sibling workspace root, not a child of this repo: DatingApp has a
# stale, near-empty mobile-apps/ directory that must not be mistaken for it.
DART="${FORUM_DART_CLIENT:-}"
if [[ -z "$DART" ]]; then
  for candidate in \
    "$ROOT/../mobile-apps/flutter/dejtingapp/lib/services/forum_service.dart" \
    "$ROOT/mobile-apps/flutter/dejtingapp/lib/services/forum_service.dart"
  do
    if [[ -f "$candidate" ]]; then DART="$candidate"; break; fi
  done
fi

if [[ -z "$DART" ]]; then
  echo "FAIL: could not locate the Flutter forum client." >&2
  echo "      Set FORUM_DART_CLIENT=/path/to/lib/services/forum_service.dart" >&2
  exit 2
fi

for f in "$CONTRACTS" "$DART" "$LIMITS_C"; do
  if [[ ! -f "$f" ]]; then
    echo "FAIL: expected file not found: $f" >&2
    exit 2
  fi
done

python3 - "$CONTRACTS" "$DART" "$LIMITS_C" << 'PY'
import re
import sys

contracts, dart, limits_c = sys.argv[1], sys.argv[2], sys.argv[3]
c_src = open(contracts, encoding="utf-8").read()
d_src = open(dart, encoding="utf-8").read()
l_src = open(limits_c, encoding="utf-8").read()

failures = []


def record_props(src, name):
    """Property names of a C# positional record, as camelCase."""
    m = re.search(rf"public sealed record {name}\((.*?)\);", src, re.S)
    if not m:
        raise SystemExit(f"FAIL: could not find record {name} in {contracts}")
    props = []
    for part in m.group(1).split(","):
        tokens = re.findall(r"[A-Za-z_][A-Za-z0-9_]*", part)
        if tokens:
            props.append(tokens[-1])
    return {p[0].lower() + p[1:] for p in props}


def dart_keys(src, cls):
    """Keys the Dart model reads out of the JSON payload."""
    try:
        start = src.index(f"factory {cls}.fromJson(")
    except ValueError:
        raise SystemExit(f"FAIL: could not find {cls}.fromJson in {dart}")
    end = src.index(");", start)
    return set(re.findall(r"j\['([A-Za-z0-9_]+)'\]", src[start:end]))


def check(dart_cls, record):
    expected = record_props(c_src, record)
    actual = dart_keys(d_src, dart_cls)
    missing = sorted(actual - expected)
    if missing:
        failures.append(
            f"{dart_cls}.fromJson reads {missing}, which {record} does not expose"
        )
    else:
        print(f"  ok  {dart_cls}.fromJson ⊆ {record} ({len(actual)} fields)")

    # Anonymity: the author's identity must not be part of any response shape.
    for leak in ("keycloakId", "authorId"):
        if leak in expected:
            failures.append(f"{record} exposes '{leak}' — the author must stay server-side")
    return expected, actual


print("Forum contract check")
print(f"  backend : {contracts}")
print(f"  client  : {dart}")
print()

check("ForumTopic", "TopicResponse")
check("ForumAnswer", "AnswerResponse")

# The client must not resurrect the removed request field.
if "isAnonymous" in d_src:
    failures.append("the Dart client still sends 'isAnonymous', which was removed from the contract")

# Limits must agree between the single server source of truth and the Dart mirror.
m = re.search(r"MaxTextLength = (\d+)", l_src)
if not m:
    raise SystemExit("FAIL: ForumLimits.MaxTextLength not found")
server_limit = m.group(1)

m = re.search(r"static const int maxTextLength = (\d+)", d_src)
if not m:
    failures.append("ForumService.maxTextLength is missing")
else:
    if m.group(1) != server_limit:
        failures.append(
            f"text limit drift: server {server_limit} vs client {m.group(1)}"
        )
    else:
        print(f"  ok  text limit {server_limit} on both sides")

if failures:
    print()
    for f in failures:
        print(f"  FAIL  {f}")
    print(f"\n{len(failures)} contract problem(s) found.")
    sys.exit(1)

print("\nContract is consistent.")
PY
