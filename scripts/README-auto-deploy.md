# DatingApp Service Auto-Deploy & Discovery

Keeps the little machine (100.86.173.9) in sync with the laptop/workspace,
including automatic detection of **brand-new services**.

## How a new service is discovered

A directory in `DatingApp/` is treated as a service when it has:
- a `Dockerfile`
- a `Program.cs` at its root
- exactly one non-`.Tests` `*.csproj`

Its port is read from `appsettings.json` → `"Urls": "http://0.0.0.0:PORT"`.
If absent, a port is auto-assigned from 8096+ and persisted in
`scripts/.auto-ports` (gitignored, stable across runs).

Its database is detected from `GetConnectionString("X")` in `Program.cs`:
- fallback `?? "Server=..."` → MySQL (a `<name>-db` container is created)
- fallback `?? "Data Source=..."` or `UseSqlite` → SQLite (no extra container)

## Commands

```bash
# List all workspace services and whether they're on the remote
bash scripts/discover-services.sh                # table
bash scripts/discover-services.sh --json         # tsv: name port dbkey dbtype on_remote

# Deploy any NEW services found (generate compose entry + rsync + build + up)
bash scripts/auto-deploy.sh                      # only new services
bash scripts/auto-deploy.sh --dry-run            # preview, no changes
bash scripts/auto-deploy.sh --only my-service    # deploy just one
bash scripts/auto-deploy.sh --sync-all           # new services + full sync-to-remote

# Full sync: auto-discovers new services, rsyncs all source, rebuilds images,
# restarts the stack, health-checks 8080-8094
bash sync-to-remote.sh
```

## Notes / gotchas
- Remote compose has `image:`-only entries (no `build:`), so `sync-to-remote.sh`
  builds each image explicitly with `docker build` from the synced source.
- `docker build` on the remote **hangs on apt/network-heavy images** (e.g.
  video-service with ffmpeg). For those, build on the laptop and transfer:
  `docker save <img> | gzip > /tmp/x.tgz` → `scp` → `docker load -i` → `up -d`.
- The dashboard CI/CD panel health-checks all 12 services + whisper; the
  "Services Up" counter counts real app containers only.
