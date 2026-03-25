#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOCK_FILE="$ROOT/.git-auto-sync.lock"
REMOTE="${GIT_SYNC_REMOTE:-origin}"

exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  echo "RESULT=skipped reason=locked"
  exit 0
fi

cd "$ROOT"

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "RESULT=blocked reason=not_git_repo"
  exit 2
fi

BRANCH="${GIT_SYNC_BRANCH:-$(git branch --show-current 2>/dev/null || true)}"
if [[ -z "$BRANCH" ]]; then
  echo "RESULT=blocked reason=detached_head"
  exit 3
fi

relation() {
  if ! git rev-parse --verify "${REMOTE}/${BRANCH}" >/dev/null 2>&1; then
    echo "no_upstream"
    return
  fi

  local local_sha upstream_sha base_sha
  local_sha="$(git rev-parse HEAD)"
  upstream_sha="$(git rev-parse "${REMOTE}/${BRANCH}")"
  base_sha="$(git merge-base HEAD "${REMOTE}/${BRANCH}")"

  if [[ "$local_sha" == "$upstream_sha" ]]; then
    echo "equal"
  elif [[ "$local_sha" == "$base_sha" ]]; then
    echo "behind"
  elif [[ "$upstream_sha" == "$base_sha" ]]; then
    echo "ahead"
  else
    echo "diverged"
  fi
}

if git remote get-url "$REMOTE" >/dev/null 2>&1; then
  if ! git fetch "$REMOTE" "$BRANCH" --quiet; then
    echo "RESULT=blocked reason=fetch_failed remote=$REMOTE branch=$BRANCH"
    exit 4
  fi
fi

pre_relation="$(relation)"
case "$pre_relation" in
  behind)
    echo "RESULT=blocked reason=remote_ahead remote=$REMOTE branch=$BRANCH"
    exit 5
    ;;
  diverged)
    echo "RESULT=blocked reason=diverged remote=$REMOTE branch=$BRANCH"
    exit 6
    ;;
  *)
    ;;
esac

if [[ -n "$(git status --porcelain)" ]]; then
  git add -A

  if ! git diff --cached --quiet; then
    stamp_utc="$(date -u '+%Y-%m-%d %H:%M UTC')"
    git commit -m "chore: workspace sync (${stamp_utc})" >/dev/null
  fi
fi

post_relation="$(relation)"
case "$post_relation" in
  equal)
    echo "RESULT=no_changes branch=$BRANCH"
    exit 0
    ;;
  ahead)
    if ! git push "$REMOTE" "$BRANCH" >/dev/null 2>&1; then
      echo "RESULT=blocked reason=push_failed remote=$REMOTE branch=$BRANCH"
      exit 7
    fi
    commit="$(git rev-parse --short HEAD)"
    stamp_local="$(TZ=America/New_York date '+%Y-%m-%d %I:%M %p %Z')"
    echo "RESULT=pushed remote=$REMOTE branch=$BRANCH commit=$commit local_time=$stamp_local"
    exit 0
    ;;
  no_upstream)
    if ! git push -u "$REMOTE" "$BRANCH" >/dev/null 2>&1; then
      echo "RESULT=blocked reason=push_failed remote=$REMOTE branch=$BRANCH"
      exit 8
    fi
    commit="$(git rev-parse --short HEAD)"
    stamp_local="$(TZ=America/New_York date '+%Y-%m-%d %I:%M %p %Z')"
    echo "RESULT=pushed remote=$REMOTE branch=$BRANCH commit=$commit local_time=$stamp_local"
    exit 0
    ;;
  behind)
    echo "RESULT=blocked reason=remote_ahead_after_commit remote=$REMOTE branch=$BRANCH"
    exit 9
    ;;
  diverged)
    echo "RESULT=blocked reason=diverged_after_commit remote=$REMOTE branch=$BRANCH"
    exit 10
    ;;
  *)
    echo "RESULT=blocked reason=unknown_state remote=$REMOTE branch=$BRANCH relation=$post_relation"
    exit 11
    ;;
esac
