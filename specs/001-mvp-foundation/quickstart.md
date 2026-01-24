# Quickstart: DatingApp MVP Foundation

## Prerequisites
- Docker + Docker Compose
- .NET 8 SDK
- Flutter 3.32.1 with web/desktop tooling
- Python 3.12 + `requests`
- Configured `.env` files (see `environments/`)

## Environment Defaults
- **Keycloak admin**: `admin` / `admin` (exposed on http://localhost:8090 via `infrastructure/start.sh`)
- **Database users**: each service container seeds MySQL users matching `<Service>_user` / `<Service>_user_password` (see `docker-compose.yml`)
- **Demo mode flag**: set `DEMO_MODE=true` when running services locally to enable seeded flows (`dev-start.sh` handles this automatically)
- **Realm export**: `config/keycloak/realms/datingapp-realm.json` is the source of truth; refresh with `./infrastructure/start.sh` if changes land in Keycloak

## Setup Steps
1. **Bootstrap shared infrastructure**
   ```bash
   cd /home/m/development/DatingApp
   ./infrastructure/start.sh
   ```
2. **Launch backend services + demo data**
   ```bash
   ./dev-start.sh
   ```
       - Verifies Keycloak & MySQL
       - Use Keycloak admin console or forthcoming automation (T029) to provision demo users; TestDataGenerator is retired
3. **Start Flutter demo client**
   ```bash
   cd mobile-apps/flutter/dejtingapp
   flutter run -d chrome --web-port 3000
   ```
4. **Run smoke tests**
   ```bash
   cd /home/m/development/DatingApp
   python3 api_tests.py
   ```
5. **(Optional) Tail logs**
   ```bash
   tail -f logs/*.log
   ```

## Validating MVP Loop
1. Register or log in with demo credentials listed in `DEMO_USERS_REFERENCE.md`.
2. Complete the profile wizard ensuring at least one photo uploads successfully.
3. Perform swipe actions until you create a mutual match.
4. Open messaging tab and exchange messages between demo accounts.
5. Exercise safety controls: toggle privacy, report a user, and confirm logs.

## Troubleshooting
- If `dev-start.sh` stalls, run `./dev-status.sh` to identify unhealthy services.
- For photo moderation failures, check `photo-service` logs and ensure ML model assets downloaded.
- If Flutter cannot authenticate, verify Keycloak realm import by inspecting `infrastructure/start.sh` output.
