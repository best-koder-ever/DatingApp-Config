#!/usr/bin/env bash
# install-web-boot-service.sh — make the Flutter web container (+ shared
# infra) start on boot via systemd.
#
# Run ONCE on the machine that hosts the stack (the "little machine"):
#   sudo ./infra/install-web-boot-service.sh
#
# This:
#   1. Writes /etc/systemd/system/dejting-web.service using this repo path.
#   2. Enables + starts it, so `docker compose up -d` for the web+infra
#      containers runs on every boot.
#   3. Relies on the `restart: unless-stopped` policies in docker-compose.yml
#      as the second layer of resilience.

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

if [ "$(id -u)" -ne 0 ]; then
  echo "❌ Please run as root (sudo)."
  exit 1
fi

if [ ! -f "${REPO_DIR}/docker-compose.yml" ]; then
  echo "❌ docker-compose.yml not found at ${REPO_DIR}"
  exit 1
fi

UNIT=/etc/systemd/system/dejting-web.service

echo "🚀 Generating systemd unit for repo at: ${REPO_DIR}"
sed "s|__REPO_DIR__|${REPO_DIR}|" "${SCRIPT_DIR}/dejting-web.service" > "${UNIT}"

echo "🔄 daemon-reload + enable + start..."
systemctl daemon-reload
systemctl enable dejting-web.service
systemctl start dejting-web.service

echo ""
echo "✅ Boot service installed. Verify with:"
echo "   systemctl status dejting-web.service"
echo "   systemctl is-enabled dejting-web.service"
echo ""
echo "   The Flutter web app will now be served on http://<this-host>:9000"
echo "   after every reboot. To remove later:"
echo "   sudo systemctl disable --now dejting-web.service"
