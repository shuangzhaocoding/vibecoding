#!/bin/sh
set -eu

APP_HOST="${APP_HOST:-127.0.0.1}"
APP_PORT="${APP_PORT:-8000}"
APP_WORKERS="${APP_WORKERS:-1}"

echo "[entrypoint] dump env for cron"
python3 - <<'PY'
import os, shlex
skip = {"PWD", "OLDPWD", "SHLVL", "_", "LS_COLORS", "TERM"}
with open("/etc/vibecoding.env", "w", encoding="utf-8") as f:
    for k, v in sorted(os.environ.items()):
        if k in skip or k.startswith("BASH_"):
            continue
        f.write(f"export {k}={shlex.quote(v)}\n")
PY

echo "[entrypoint] start cron (GitHub seed 02:00 Asia/Shanghai)"
cron

echo "[entrypoint] start uvicorn ${APP_HOST}:${APP_PORT} workers=${APP_WORKERS}"
cd /vibecoding
uvicorn app.main:app --host "${APP_HOST}" --port "${APP_PORT}" --workers "${APP_WORKERS}" &
UVICORN_PID=$!

cleanup() {
  kill "${UVICORN_PID}" 2>/dev/null || true
  wait "${UVICORN_PID}" 2>/dev/null || true
}
trap cleanup INT TERM EXIT

i=0
while [ "$i" -lt 60 ]; do
  if python3 -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:${APP_PORT}/api/health', timeout=1)" >/dev/null 2>&1; then
    break
  fi
  i=$((i + 1))
  sleep 1
done

echo "[entrypoint] start nginx :80"
exec nginx -g 'daemon off;'
