#!/usr/bin/env python3
"""Query Claude with DatingApp context cached for 90% input token savings.

Usage:
    ./scripts/cached-query.py "What services handle swipe processing?"
    ./scripts/cached-query.py --model claude-3-5-haiku-20241022 "Summarize the architecture"
    echo "Review my test coverage" | ./scripts/cached-query.py

Requires: pip install anthropic
          export ANTHROPIC_API_KEY=sk-ant-...  (or set in .env)
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_env() -> None:
    """Load .env and .env.local into os.environ."""
    for name in (".env.local", ".env"):
        env_file = ROOT / name
        if not env_file.exists():
            continue
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


def main() -> None:
    parser = argparse.ArgumentParser(description="Cached Claude query for DatingApp")
    parser.add_argument("query", nargs="?", help="The question to ask")
    parser.add_argument("--model", default="claude-sonnet-4-20250514",
                        help="Model (claude-sonnet-4-20250514, claude-4-opus-20250514, claude-3-5-haiku-20241022)")
    parser.add_argument("--max-tokens", type=int, default=2000, help="Max output tokens")
    parser.add_argument("--no-cache", action="store_true", help="Disable prompt caching")
    args = parser.parse_args()

    # Load env
    load_env()

    try:
        import anthropic
    except ImportError:
        print("pip install anthropic", file=sys.stderr)
        sys.exit(1)

    # Read query from arg or stdin
    query = args.query
    if not query:
        if not sys.stdin.isatty():
            query = sys.stdin.read().strip()
        if not query:
            print("Usage: cached-query.py 'your question here'", file=sys.stderr)
            sys.exit(1)

    # Load system prompt
    sys_file = ROOT / ".ai-system-prompt.md"
    if not sys_file.exists():
        sys_file = ROOT / ".github" / "copilot-instructions.md"
    if sys_file.exists():
        system_text = sys_file.read_text(errors="replace")
    else:
        system_text = "You are an expert .NET 8 / Flutter architect for DatingApp."

    # Build system block
    if args.no_cache:
        system_block = [{"type": "text", "text": system_text}]
    else:
        system_block = [{"type": "text", "text": system_text, "cache_control": {"type": "ephemeral"}}]

    client = anthropic.Anthropic()
    response = client.messages.create(
        model=args.model,
        max_tokens=args.max_tokens,
        system=system_block,
        messages=[{"role": "user", "content": query}],
    )

    # Print response
    for block in response.content:
        if hasattr(block, "text"):
            print(block.text)

    # Print token usage to stderr
    u = response.usage
    cache_write = getattr(u, "cache_creation_input_tokens", 0)
    cache_read = getattr(u, "cache_read_input_tokens", 0)
    print(f"\n--- tokens: in={u.input_tokens} out={u.output_tokens} "
          f"cache_write={cache_write} cache_read={cache_read} "
          f"{'(HIT 90% saved!)' if cache_read > 0 else '(MISS - next call hits)'} ---",
          file=sys.stderr)


if __name__ == "__main__":
    main()
