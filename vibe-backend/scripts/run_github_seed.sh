#!/bin/sh
# 定时抓取 GitHub 作品：插入新条目，并更新本脚本作者名下的已有条目。
set -eu

ENV_FILE="${VIBE_CRON_ENV:-/etc/vibecoding.env}"
if [ -f "$ENV_FILE" ]; then
  # shellcheck disable=SC1090
  . "$ENV_FILE"
fi

ROOT="${VIBE_BACKEND_ROOT:-/vibecoding}"
cd "$ROOT"

LOCK="${GITHUB_SEED_LOCK:-/tmp/github-seed.lock}"
LOG="${GITHUB_SEED_LOG:-/var/log/vibecoding-github-seed.log}"
LIMIT="${GITHUB_SEED_LIMIT:-40}"
AUTHOR="${GITHUB_SEED_AUTHOR:-admin}"
MIN_STARS="${GITHUB_SEED_MIN_STARS:-100}"

if command -v flock >/dev/null 2>&1; then
  exec flock -n "$LOCK" python3 scripts/seed_github_projects.py \
    --limit "$LIMIT" \
    --author "$AUTHOR" \
    --min-stars "$MIN_STARS" \
    >>"$LOG" 2>&1
fi

python3 scripts/seed_github_projects.py \
  --limit "$LIMIT" \
  --author "$AUTHOR" \
  --min-stars "$MIN_STARS" \
  >>"$LOG" 2>&1
