#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/home/haolun/.openclaw/workspace/mission-control"
LOG_DIR="$APP_DIR/logs"
LOCK_FILE="$APP_DIR/.keepalive.lock"
WATCHDOG_LOG="$LOG_DIR/keepalive.log"
APP_LOG="$LOG_DIR/dev.log"
APP_PORT="${MISSION_CONTROL_PORT:-4180}"

mkdir -p "$LOG_DIR"
exec 9>"$LOCK_FILE"
flock -n 9 || exit 0

check_up() {
  curl -fsS "http://127.0.0.1:${APP_PORT}" >/dev/null 2>&1 && \
  curl -fsS "http://127.0.0.1:${APP_PORT}/api/health" >/dev/null 2>&1
}

restart_app() {
  echo "[$(date -Is)] mission-control down; rebuilding + restarting" >> "$WATCHDOG_LOG"
  pkill -f '/home/haolun/.openclaw/workspace/mission-control/server.js' || true
  pkill -f 'HOST=0.0.0.0 PORT=4180 node server.js' || true
  pkill -f 'mission-control@0.0.1 start' || true
  sleep 1
  cd "$APP_DIR"
  npm run build >> "$APP_LOG" 2>&1
  (
    exec 9>&-
    nohup npm run start >> "$APP_LOG" 2>&1 &
  )
}

if ! check_up; then
  restart_app
fi

while true; do
  if ! check_up; then
    restart_app
  fi
  sleep 60
done
