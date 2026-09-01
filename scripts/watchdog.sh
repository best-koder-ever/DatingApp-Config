#!/usr/bin/env bash
# datingapp-watchdog.sh — self-heal for the little machine (100.86.173.9).
#
# Prevents recurrence of "can't connect to the little machine":
#   - Tailscale/funnel lost sync with the coordination server -> the phone
#     can't reach https://a.tail45c6a7.ts.net. We detect it and restart
#     tailscaled automatically.
#   - A service (or the gateway) crashes -> we re-run docker compose up -d.
#
# Live copy runs on the little machine at
#   /home/a/datingapp/scripts/watchdog.sh
# via systemd timer: datingapp-watchdog.timer (every 5 min, +2 min after boot).
# Logs to /var/log/datingapp-watchdog.log.
#
# Install on the little machine:
#   sudo systemctl daemon-reload && sudo systemctl enable --now datingapp-watchdog.timer
set -u

LOG=/var/log/datingapp-watchdog.log
APP_DIR=/home/a/datingapp
FUNNEL_URL=https://a.tail45c6a7.ts.net/health
GW_PORT=8080
# All 12 app service ports (parity with laptop)
SERVICE_PORTS='8080 8082 8083 8085 8086 8087 8088 8089 8091 8092 8093 8094'

log() { echo "$(date '+%Y-%m-%d %H:%M:%S') $*" >> "$LOG"; }

# ── 1. Local gateway health ──
gw_ok=0
if curl -sf --max-time 5 "http://localhost:${GW_PORT}/health" >/dev/null 2>&1; then
  gw_ok=1
else
  log "WARN gateway down on :${GW_PORT} — re-running docker compose up"
  (cd "$APP_DIR" && docker compose up -d --remove-orphans >>"$LOG" 2>&1)
  sleep 12
  if curl -sf --max-time 5 "http://localhost:${GW_PORT}/health" >/dev/null 2>&1; then
    log "OK gateway recovered after compose up"
    gw_ok=1
  else
    log "ERR gateway still down after compose up"
  fi
fi

# ── 2. Funnel reachability (what the phone uses) ──
funnel_ok=0
if curl -sf --max-time 8 "$FUNNEL_URL" >/dev/null 2>&1; then
  funnel_ok=1
else
  log "WARN funnel unreachable ($FUNNEL_URL)"
fi

# ── 3. Tailscale coordination health ──
ts_bad=0
if tailscale status 2>&1 | grep -qiE 'unable to connect to the tailscale coordination|offline'; then
  ts_bad=1
  log "WARN tailscale reports degraded state"
fi

# Restart tailscaled if the funnel is down (gateway up) OR tailscale degraded.
if { [ "$funnel_ok" -eq 0 ] && [ "$gw_ok" -eq 1 ]; } || [ "$ts_bad" -eq 1 ]; then
  log "INFO restarting tailscaled"
  sudo systemctl restart tailscaled
  sleep 20
  if curl -sf --max-time 8 "$FUNNEL_URL" >/dev/null 2>&1; then
    log "OK funnel recovered after tailscaled restart"
  else
    log "ERR funnel still down after tailscaled restart — manual check needed"
  fi
fi

# ── 4. All 12 app services up (parity) ──
down=''
for p in $SERVICE_PORTS; do
  if ! (echo > /dev/tcp/127.0.0.1/$p) 2>/dev/null; then
    down="$down $p"
  fi
done
if [ -n "$down" ]; then
  log "WARN service port(s) down:$down — re-running docker compose up"
  (cd "$APP_DIR" && docker compose up -d --remove-orphans >>"$LOG" 2>&1)
  sleep 15
fi

# ── 5. Re-check all 12 ports after recovery attempt ──
down2=''
for p in $SERVICE_PORTS; do
  if ! (echo > /dev/tcp/127.0.0.1/$p) 2>/dev/null; then
    down2="$down2 $p"
  fi
done
if [ -n "$down2" ]; then
  log "ERR still down after recovery:$down2"
else
  log "OK all 12 service ports up"
fi
