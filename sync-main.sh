#!/usr/bin/env bash
# sync-main.sh — short-trunk helper for this multi-repo workspace.
#
# For every repo below it:
#   1. ensures you are on `main` with an `origin`
#   2. fetches, then rebases local commits onto origin/main (linear history)
#   3. pushes to origin/main
#
# SAFETY: never force-pushes; never switches branches; stops a repo with a clear
# message on rebase conflict or rejected push (another writer raced us) — resolve
# manually, then re-run. Run from the DatingApp root:  ./sync-main.sh
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

REPOS=(
  "$ROOT"
  "$ROOT/photo-service"
  "$ROOT/MatchmakingService"
  "$ROOT/bot-service"
  "$ROOT/UserService"
  "$ROOT/../mobile-apps/flutter/dejtingapp"
)

fail=0

for repo in "${REPOS[@]}"; do
  name="$(basename "$repo")"
  if [ ! -e "$repo/.git" ]; then
    echo "⚠️  skip $name (not a git checkout: $repo)"
    continue
  fi

  echo "=== $name ==="
  (
    cd "$repo" || exit 1

    branch="$(git rev-parse --abbrev-ref HEAD 2>/dev/null)"
    if [ "$branch" != "main" ]; then
      echo "  skip: not on 'main' (on '$branch')"
      exit 2
    fi

    if ! git remote get-url origin >/dev/null 2>&1; then
      echo "  skip: no 'origin' remote"
      exit 2
    fi

    if ! git fetch origin main --quiet 2>/dev/null; then
      echo "  ❌ fetch failed (network/auth?)"
      exit 1
    fi

    ahead="$(git rev-list --count origin/main..HEAD 2>/dev/null || echo 0)"
    behind="$(git rev-list --count HEAD..origin/main 2>/dev/null || echo 0)"
    echo "  ahead=$ahead  behind=$behind"

    if [ "$behind" -gt 0 ]; then
      echo "  → rebasing local commits onto origin/main"
      if ! GIT_EDITOR=true git pull --rebase origin main; then
        echo "  ❌ rebase has conflicts — resolve manually, then run: git push origin main"
        exit 1
      fi
    fi

    if [ "$ahead" -gt 0 ] || [ "$behind" -gt 0 ]; then
      if ! git push origin main; then
        echo "  ❌ push rejected (another writer pushed) — re-run this script to rebase & retry"
        exit 1
      fi
      echo "  ✅ pushed origin/main"
    else
      echo "  ✔ already in sync"
    fi
  )
  rc=$?
  [ "$rc" -eq 1 ] && fail=1
done

if [ "$fail" -eq 1 ]; then
  echo "Finished with failures — fix the repos above, then re-run."
  exit 1
fi
echo "All repos in sync with origin/main."
