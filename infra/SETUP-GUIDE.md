# DatingApp Server Setup Guide

Run these steps on each stationary machine. Each step is self-contained and
can be executed by an AI coding agent or a human.

## Machine Requirements

- Ubuntu 22.04 or 24.04 LTS
- Minimum 8 GB RAM, 4 CPU cores
- 50 GB free disk space
- Static LAN IP (set in router DHCP reservation)

---

## Phase A: Docker Installation (both machines)

```bash
# Run on BOTH stationary machines
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
sudo apt install -y docker-compose-v2 git curl jq
# Log out and back in for group membership
```

---

## Phase B: Machine #1 — Dev & Test Server

### B1. Clone repository
```bash
mkdir -p ~/datingapp
cd ~/datingapp
git clone https://github.com/YOUR_ORG/DatingApp.git .
```

### B2. Create dev environment file
```bash
cp infra/.env.template infra/.env.dev
# Edit infra/.env.dev with your values:
#   KC_DB_PASSWORD, KEYCLOAK_ADMIN_PASSWORD, MYSQL_ROOT_PASSWORD
#   Set DEMO_MODE=true for dev
```

### B3. Create test environment file
```bash
cp infra/.env.template infra/.env.test
# Edit infra/.env.test:
#   Set DEMO_MODE=false
#   Set TUNNEL_HOST=test.datingapp.example.com
```

### B4. Start dev environment
```bash
chmod +x scripts/deploy-env.sh
./scripts/deploy-env.sh dev latest
# Wait ~2 minutes for all services to start
```

### B5. Start test environment
```bash
./scripts/deploy-env.sh test latest
```

### B6. Verify
```bash
./scripts/health-check.sh http://localhost 10
```

---

## Phase C: Machine #2 — Production Server

### C1. Clone repository
```bash
mkdir -p ~/datingapp
cd ~/datingapp
git clone https://github.com/YOUR_ORG/DatingApp.git .
```

### C2. Install Cloudflare Tunnel
```bash
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o cloudflared
chmod +x cloudflared
sudo mv cloudflared /usr/local/bin/
```

### C3. Authenticate Cloudflare Tunnel
```bash
# Run on a machine with a browser (SSH port forward or use laptop)
cloudflared tunnel login
# This opens a browser. Authorize your Cloudflare account.
```

### C4. Create Tunnel
```bash
cloudflared tunnel create datingapp-prod
# Copy the tunnel ID and credentials file to ~/.cloudflared/<id>.json
```

### C5. Configure DNS
```bash
# Point these subdomains to the tunnel (via Cloudflare dashboard):
#   prod.datingapp.example.com  → tunnel
#   api.datingapp.example.com   → tunnel
```

### C6. Create production env file
```bash
cp infra/.env.template infra/.env.prod
# Edit infra/.env.prod:
#   Set DEMO_MODE=false
#   Set TUNNEL_HOST=prod.datingapp.example.com
#   Set CLOUDFLARE_TUNNEL_TOKEN=<your tunnel token>
```

### C7. Start production
```bash
./scripts/deploy-env.sh prod stable
```

### C8. Verify external access
```bash
# From any internet-connected device:
curl https://prod.datingapp.example.com/health
# Should return 200
```

---

## Phase D: Self-Hosted GitHub Runner (Machine #2)

### D1. Add runner to repo
```bash
# Go to GitHub repo → Settings → Actions → Runners → New self-hosted runner
# Choose Linux x64, follow the instructions shown.

# Summary:
mkdir ~/actions-runner && cd ~/actions-runner
curl -o actions-runner-linux-x64.tar.gz -L <URL_FROM_GITHUB>
tar xzf actions-runner-linux-x64.tar.gz
./config.sh --url https://github.com/YOUR_ORG/DatingApp --token <TOKEN_FROM_GITHUB>
sudo ./svc.sh install
sudo ./svc.sh start
```

### D2. Verify runner
```bash
# In GitHub repo → Settings → Actions → Runners
# Should show "Idle" status
```

---

## Phase E: Portainer (both machines)

```bash
docker run -d -p 9443:9443 --name portainer --restart=always \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v portainer_data:/data portainer/portainer-ce:latest

# Access at https://<machine-ip>:9443
```

---

## Phase F: Database Backups (Machine #1)

```bash
# Add to crontab (crontab -e):
0 3 * * * ~/datingapp/scripts/backup-db.sh

# Backup script at scripts/backup-db.sh:
cat > ~/datingapp/scripts/backup-db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR=~/datingapp-backups/$(date +%Y-%m-%d)
mkdir -p "$BACKUP_DIR"
for DB in UserServiceDb MatchmakingServiceDb SwipeServiceDb PhotoServiceDb MessagingServiceDb; do
  docker exec ${DB}-db mysqldump -u root -p"${MYSQL_ROOT_PASSWORD}" "$DB" > "$BACKUP_DIR/${DB}.sql"
done
# Keep last 14 days
find ~/datingapp-backups -maxdepth 1 -type d -mtime +14 -exec rm -rf {} \;
echo "Backup complete: $BACKUP_DIR"
EOF
chmod +x ~/datingapp/scripts/backup-db.sh
```

---

## Phase G: Flutter APK Build (Optional, on Machine #2)

```bash
# Install Flutter SDK
sudo snap install flutter --classic
flutter doctor

# The APK build will run via GitHub Actions. Local test:
cd mobile-apps/flutter/dejtingapp
flutter pub get
flutter build apk --release
```

---

## Quick Reference: Deploy Commands

```bash
# Deploy to dev (from machine #1)
cd ~/datingapp && ./scripts/deploy-env.sh dev

# Deploy to test (from machine #1)
cd ~/datingapp && ./scripts/deploy-env.sh test

# Deploy to prod (from machine #2)
cd ~/datingapp && ./scripts/deploy-env.sh prod stable

# Health check
./scripts/health-check.sh

# View logs
docker compose -f docker-compose.yml logs -f --tail=50 yarp
```

---

## Troubleshooting

| Problem | Check |
|---|---|
| Service won't start | `docker compose logs <service-name>` |
| Keycloak unreachable | `curl http://localhost:8090/health/ready` |
| Database connection refused | `docker exec <db-container> mysqladmin ping -h localhost` |
| Port already in use | `ss -ltnp \| grep <port>` then `docker compose down` |
| Cloudflare tunnel not connecting | `cloudflared tunnel list` and check token |
| Images not pulling | Check `docker login ghcr.io` and PAT permissions |
