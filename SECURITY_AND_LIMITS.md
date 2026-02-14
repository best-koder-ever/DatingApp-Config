# DatingApp — Security, Rate Limits & Monitoring Reference

> Single source of truth for all security policies, rate limits, and observability config.
> Last updated: 2026-02-13

---

## 📋 Table of Contents

- [Service Map](#service-map)
- [Rate Limits](#rate-limits)
- [Authentication & Authorization](#authentication--authorization)
- [Input Validation & Security Headers](#input-validation--security-headers)
- [Monitoring & Observability](#monitoring--observability)
- [Alerting](#alerting)
- [Logging](#logging)
- [Known Gaps & TODOs](#known-gaps--todos)
- [Load Testing & Performance Benchmarks](#-load-testing--performance-benchmarks)

---

## 🗺️ Service Map

| Service              | Port  | Health Endpoint | Metrics Endpoint  |
|----------------------|-------|-----------------|-------------------|
| Keycloak (OIDC/Auth) | 8090  | `/realms/master`| —                 |
| YARP Gateway         | 8080  | `/health`       | `/metrics`        |
| UserService          | 8082  | `/health`       | `/metrics`        |
| MatchmakingService   | 8083  | `/health`       | `/metrics`        |
| PhotoService         | 8085  | `/health`       | `/metrics`        |
| MessagingService     | 8086  | `/health`       | `/metrics`        |
| SwipeService         | 8087  | `/health`       | `/metrics`        |
| Bot Dashboard        | 9091  | `/`             | —                 |
| Prometheus           | 9090  | `/-/healthy`    | `/metrics`        |
| Grafana              | 3000  | `/api/health`   | —                 |

### Databases

| Database              | Port  | User/Pass          | DB Name                  |
|-----------------------|-------|--------------------|--------------------------|
| MatchmakingService DB | 3309  | root / root_password | matchmaking_service_db  |
| SwipeService DB       | 3310  | root / root_password | SwipeServiceDb          |

---

## 🚦 Rate Limits

### Layer 1: YARP Gateway (all requests pass through here)

Per-user sliding window rate limits, partitioned by JWT `sub` claim.
Configured in: `dejting-yarp/src/dejting-yarp/Program.cs`

| Endpoint Pattern       | Limit         | Window   | Queue | Response when exceeded          |
|------------------------|---------------|----------|-------|---------------------------------|
| `/api/messages/*`      | 10 requests   | 1 minute | 0     | 429 + `Retry-After` header      |
| `/api/photos/*`        | 20 requests   | 1 day    | 0     | 429 + `Retry-After` header      |
| `/api/userprofiles/*`  | 60 requests   | 1 minute | 0     | 429 + `Retry-After` header      |
| `/api/swipes/*`        | 60 requests   | 1 minute | 0     | 429 + `Retry-After` header      |
| `/api/matchmaking/*`   | 20 requests   | 1 minute | 0     | 429 + `Retry-After` header      |
| `/api/safety/*`        | 5 requests    | 1 day    | 0     | 429 + `Retry-After` header      |
| `/health/*`            | **exempt**    | —        | —     | Always allowed                  |
| `/api/auth/*`          | **exempt**    | —        | —     | Always allowed                  |
| All other paths        | **no limit**  | —        | —     | —                               |

**Response format** (429):
```json
{
  "error": "Rate limit exceeded",
  "message": "Too many requests. Please try again later.",
  "retryAfterSeconds": 60
}
```
**Headers**: `Retry-After`, `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`

### Layer 2: Service-Level Business Limits

#### SwipeService
Configured in: `swipe-service/appsettings.json` → `SwipeLimits`

| Limit                 | Value | Scope     | Enforcement         |
|-----------------------|-------|-----------|---------------------|
| Daily swipes total    | 100   | Per user  | `IRateLimitService`  |
| Daily right-swipes    | 50    | Per user  | `IRateLimitService`  |

#### MessagingService
Configured in: `messaging-service/Program.cs`

| Protection              | Details                                |
|-------------------------|----------------------------------------|
| Rate limiting           | `IRateLimitingService` + middleware     |
| Spam detection          | `ISpamDetectionService`                |
| Content moderation      | `IContentModerationService`            |
| Personal info detection | `IPersonalInfoDetectionService`        |

### Layer 3: Request Size Limits

| Location              | Max Size | Configured In                              |
|-----------------------|----------|--------------------------------------------|
| YARP Gateway          | 50 MB    | `InputValidationMiddleware.cs` (L102)      |
| PhotoService uploads  | 10 MB    | `VerificationController.cs` `[RequestSizeLimit]` |

---

## 🔐 Authentication & Authorization

### Keycloak OIDC / JWT

- **Realm**: `DatingApp`
- **Client ID**: `dejtingapp-flutter`
- **Token endpoint**: `http://localhost:8090/realms/DatingApp/protocol/openid-connect/token`
- **JWKS**: Auto-discovered via OpenID Connect metadata

**JWT validation** (all services):
- ✅ `ValidateIssuer = true`
- ✅ `ValidateIssuerSigningKey = true`
- ✅ `ValidateLifetime = true`
- ✅ `ValidateAudience` (when audiences configured)
- ✅ `NameClaimType = "preferred_username"`
- ✅ `RoleClaimType = "roles"`
- ⚠️ `ClockSkew = TimeSpan.Zero` only in UserService + MessagingService (others use 5-min default)

### Service-to-Service Authentication (Internal APIs)

API key authentication via `InternalApiKeyAuthFilter` + `InternalApiKeyAuthHandler`:

| Service            | Dev API Key                                          |
|--------------------|------------------------------------------------------|
| SwipeService       | `swipe-service-internal-key-dev-only`                |
| MatchmakingService | `matchmaking-service-internal-key-dev-only`          |
| PhotoService       | `photo-service-internal-key-dev-only`                |
| MessagingService   | `messaging-service-internal-key-dev-only`            |

⚠️ **Production**: These must be rotated to strong random secrets and stored in a vault.

### CORS Policies

| Service            | Policy           | Origins                              |
|--------------------|------------------|---------------------------------------|
| YARP Gateway       | `AllowAll`       | `*` (any origin, method, header)      |
| UserService        | `AllowAll`       | `*`                                   |
| PhotoService       | `AllowAll`       | `*`                                   |
| MessagingService   | Restricted       | `localhost:3000`, `localhost:8080`     |
| MatchmakingService | None             | Relies on gateway                     |
| SwipeService       | None             | Relies on gateway                     |

⚠️ **Production**: Gateway CORS must be locked down to actual frontend domains.

---

## 🛡️ Input Validation & Security Headers

### Gateway-Level Input Validation (`InputValidationMiddleware`)

Blocks requests containing:
- SQL injection patterns (`SELECT`, `DROP`, `UNION`, `INSERT`, etc.)
- XSS patterns (`<script>`, `javascript:`, `onerror=`, etc.)
- Path traversal (`../`, `..\\`)
- Dangerous headers (`X-Forwarded-For` spoofing — stripped)

### Security Headers (`SecurityHeadersMiddleware`)

Applied to every response via YARP gateway:

| Header                       | Value                                           |
|------------------------------|-------------------------------------------------|
| `X-Content-Type-Options`     | `nosniff`                                       |
| `X-Frame-Options`            | `DENY`                                          |
| `X-XSS-Protection`           | `1; mode=block`                                 |
| `Referrer-Policy`            | `strict-origin-when-cross-origin`               |
| `Content-Security-Policy`    | `default-src 'self'; frame-ancestors 'none'; ...`|
| `Permissions-Policy`         | Disables geolocation, camera, microphone, etc.  |
| `Strict-Transport-Security`  | When HTTPS: `max-age=31536000; includeSubDomains`|

### FluentValidation (per service)

All services register `AddValidatorsFromAssembly` — validators for:
- `CreateUserProfileValidator` (UserService)
- `RecordSwipeValidator` (SwipeService)
- Plus validators in MessagingService, PhotoService, MatchmakingService

---

## 📊 Monitoring & Observability

### Prometheus Metrics (scraped every 15s)

| Service            | Custom Meters                                                              |
|--------------------|----------------------------------------------------------------------------|
| YARP Gateway       | `gateway_requests_forwarded_total`, `gateway_requests_blocked_total`, ASP.NET Core rate limiting metrics |
| UserService        | `user_profiles_created_total`, `user_profiles_updated_total`, `user_profiles_deleted_total`, `user_search_duration_ms` |
| MatchmakingService | `matches_created_total`, `candidates_evaluated_total`, `match_score_value`, `match_algorithm_duration_ms` |
| SwipeService       | `swipes_processed_total`, `likes_total`, `passes_total`, `mutual_matches_total`, `swipes_rate_limited_total` |
| PhotoService       | `photos_uploaded_total`, `photos_deleted_total`, `photo_processing_duration_ms`, `photo_moderation_score` |
| MessagingService   | `messages_sent_total`, `messages_moderated_total`, `message_delivery_duration_ms`, `spam_detection_score` |

### Grafana Dashboards

- **URL**: http://localhost:3000
- **Login**: admin / `dating_app_2025`
- **Pre-built dashboards**: `mvp-overview.json`, `system-overview.json`
- **Datasource**: Prometheus (auto-provisioned)

### Useful Prometheus Queries

```promql
# Swipes per second
rate(swipes_processed_total[5m])

# Match rate (mutual matches / total likes)
rate(mutual_matches_total[5m]) / rate(likes_total[5m])

# 95th percentile matchmaking latency
histogram_quantile(0.95, rate(match_algorithm_duration_ms_bucket[5m]))

# Messages per minute
rate(messages_sent_total[5m]) * 60

# Rate-limited requests (gateway)
rate(aspnetcore_ratelimiting_queued_requests_total[5m])

# Service error rate
rate(http_server_request_duration_seconds_count{http_response_status_code=~"5.."}[5m])
/ rate(http_server_request_duration_seconds_count[5m])

# Photo upload latency
histogram_quantile(0.95, rate(photo_processing_duration_ms_bucket[5m]))
```

### Starting/Stopping Monitoring

```bash
# Start Prometheus + Grafana
cd /path/to/DatingApp
docker compose -f docker-compose.monitoring.yml up -d

# Hot-reload Prometheus config (no restart needed)
curl -X POST http://localhost:9090/-/reload

# Stop monitoring
docker compose -f docker-compose.monitoring.yml down
```

---

## 🚨 Alerting

Alert rules defined in `monitoring/prometheus/alert_rules.yml`:

| Alert                     | Condition                                 | Severity | For    |
|---------------------------|-------------------------------------------|----------|--------|
| `ServiceDown`             | `up == 0`                                 | critical | 30s    |
| `HighResponseTime`        | p95 latency > 2s                          | warning  | 2 min  |
| `HighErrorRate`           | 5xx rate > 10%                            | critical | 2 min  |
| `DatabaseConnectionFailure` | `mysql_up == 0`                         | critical | 1 min  |
| `HighMemoryUsage`         | Container memory > 80%                    | warning  | 5 min  |
| `FlutterAppDown`          | `probe_success == 0`                      | warning  | 1 min  |

⚠️ **Alertmanager not yet configured** — alerts fire in Prometheus but no notification channel (Slack/email/PagerDuty) is wired up.

---

## 📝 Logging

### Serilog (all services)

Every service uses structured Serilog logging with:
- **Console sink**: Human-readable, colored output
- **File sink**: Rolling daily in `<service>/logs/`, 7-day retention
- **Enrichment**: `CorrelationId`, `ServiceName`, `EnvironmentName`, `MachineName`
- **Format**: `[{Timestamp:HH:mm:ss} {Level:u3}] [{ServiceName}] [{CorrelationId}] {Message:lj}`

### Cross-Service Tracing

All services propagate `X-Correlation-Id` headers via `DatingApp.Shared.Middleware`:
- Incoming request gets a correlation ID (generated if missing)
- All downstream HTTP calls include the correlation ID
- All log entries include `[{CorrelationId}]`
- Enables tracing a request across Gateway → Service → Database

### Log Locations

| Service            | Log Files                               |
|--------------------|-----------------------------------------|
| YARP Gateway       | `dejting-yarp/src/dejting-yarp/logs/`   |
| UserService        | `UserService/logs/`                     |
| MatchmakingService | `MatchmakingService/logs/`              |
| SwipeService       | `swipe-service/logs/`                   |
| PhotoService       | `photo-service/logs/`                   |
| MessagingService   | `messaging-service/logs/`               |

### Centralized Log Aggregation

- **Loki**: Configured in `infrastructure/docker-compose.yml` (port 3100)
- **Promtail**: Collects and ships logs to Loki
- MatchmakingService pushes directly to Loki via `Serilog.Sinks.Grafana.Loki`
- Other services rely on Promtail to ingest their file logs

---

## ⚠️ Known Gaps & TODOs

### Security
- [ ] CORS too permissive in dev — lock down to real frontend domains for production
- [ ] Internal API keys are hardcoded dev-only values — use vault/secrets manager in prod
- [ ] `RequireHttpsMetadata: false` in dev configs — already `true` in prod appsettings
- [ ] `ClockSkew` inconsistent — standardize to `TimeSpan.Zero` across all services
- [ ] No protection if services are accessed directly bypassing gateway (firewall/network policy needed in prod)

### Rate Limiting
- [ ] All rate limiters are in-memory — won't work across multiple instances; Redis backend needed for horizontal scaling
- [ ] No per-IP rate limiting for unauthenticated endpoints (login, token)
- [ ] Consider adding CAPTCHA or proof-of-work for account creation endpoint

### Monitoring
- [ ] Alertmanager not deployed — alerts fire but nobody gets notified
- [ ] Only MatchmakingService pushes logs to Loki directly; other services need Promtail configured
- [ ] No Serilog file size limit — a bad day of logging could produce very large files; add `fileSizeLimitBytes`
- [ ] No distributed tracing (OpenTelemetry traces) — only metrics are exported

### Bot/Spam Defense (Production)
- [ ] Add device fingerprinting for bot detection
- [ ] Add velocity checks on account creation (X accounts from same IP/device in Y minutes)
- [ ] Add progressive CAPTCHA — show CAPTCHA after unusual swipe patterns
- [ ] Add photo hash deduplication to detect mass-created fake profiles
- [ ] Rate-limit failed login attempts (currently only Keycloak brute-force protection)

---

## 🔥 Load Testing & Performance Benchmarks

### What is a "Locust User"?

**Locust users ≠ real app users.** A Locust user is a virtual client that sends
requests as fast as a configured wait time allows (1-5 seconds between requests).
A real human user opens the app, scrolls photos for 30+ seconds, maybe swipes,
checks messages once, and goes idle. The difference:

| Locust Users | ≈ Real-World Equivalent | Why |
|---|---|---|
| 1 | 30-50 real users | Real users have 30-60s think time; Locust has 1-5s |
| 20 | 500-1,000 | Each Locust user sends ~15 req/min vs ~1 req/min for humans |
| 200 | 5,000-10,000 | |
| 500 | 15,000-25,000 | |
| 1,000 | 30,000-50,000 | |
| 2,000+ | 100,000+ | Expect to hit infrastructure limits here |

**Rule of thumb:** 1 Locust user ≈ 30-50 real mobile app users.

### Test Hardware (dev machine baseline)

```
CPU:  12 cores
RAM:  31 GB
Disk: NVMe SSD (468 GB)
OS:   Linux

Running simultaneously on this ONE machine:
  - 6 .NET 8 services (YARP, UserService, MatchmakingService, PhotoService, MessagingService, SwipeService)
  - Keycloak (JVM)
  - 2 MySQL instances
  - Prometheus + Grafana (Docker)
  - VS Code
```

### Benchmark Results (February 2026)

| Locust Users | ≈ Real Users | Avg Latency | P95 Latency | Verdict |
|---|---|---|---|---|
| 20 | ~1,000 | 5 ms | 12 ms | 🟢 Effortless |
| 200 | ~10,000 | 5 ms | 11 ms | 🟢 Still effortless |
| 500 | ~25,000 | 16 ms | 130 ms | 🟢 Totally fine |
| 1,000 | ~50,000 | 68 ms | 480 ms | 🟡 Starting to feel it |

**Interpretation:** On a single dev machine running everything, P95 stays
under 500ms even at ~50,000 real-user-equivalent load. In production with
dedicated servers, expect 2-3x better numbers.

### Expected Production Bottlenecks (in order)

1. **MySQL connection pool** — first thing to saturate; default pool is small
2. **Keycloak token validation** — JWT verification on every request is CPU-bound
3. **MatchmakingService memory** — candidate scoring grows with user count (500 MB at idle with 50 users)
4. **Network bandwidth** — photo uploads/downloads; not relevant for API-only tests

### Running Load Tests

```bash
cd bot-service

# Quick smoke test (30s, 10 users ≈ 500 real users)
PYTHONPATH=. .venv/bin/python -m bot_service.load_test

# Medium (60s, 50 users ≈ 2,500 real users)
PYTHONPATH=. .venv/bin/python -m bot_service.load_test --users 50 --time 60

# Stress test (120s, 500 users ≈ 25,000 real users)
PYTHONPATH=. .venv/bin/python -m bot_service.load_test --users 500 --time 120 --spawn-rate 50

# Find the breaking point (60s, 2000 users ≈ 100,000 real users)
PYTHONPATH=. .venv/bin/python -m bot_service.load_test --users 2000 --time 60 --spawn-rate 200
```

The load test:
1. Verifies services are healthy
2. Runs Locust headless with realistic user behavior (browse candidates, swipe, view matches, send messages)
3. Produces per-endpoint latency + error breakdown
4. Waits for Prometheus scrape
5. Runs bottleneck analysis (P95s, error rates, memory, DB connections, rate-limiter rejections)
6. Prints hardware context so results are reproducible

### Bottleneck Checker (no load test, just current state)

```bash
# One-shot report
PYTHONPATH=. .venv/bin/python -m bot_service.perf_checker

# Watch mode (refreshes every 30s)
PYTHONPATH=. .venv/bin/python -m bot_service.perf_checker --watch
```

Checks 10 things:
- Service health (Prometheus `up` metric)
- P95 latency per endpoint (threshold: >200ms warn, >1s crit)
- Average latency per endpoint (threshold: >100ms)
- 5xx error rate (threshold: >1% warn, >5% crit)
- Rate limiter rejections
- Kestrel active connections (threshold: >50)
- Outbound HTTP latency (service-to-service calls)
- .NET process memory (threshold: >500MB warn, >1GB crit)
- MySQL connection count (threshold: >50)
- Hot endpoint ranking (highest req/s)

### Locust Web UI (interactive mode)

For exploring behavior interactively, run Locust with its web UI:

```bash
cd bot-service
.venv/bin/locust -f bot_service/locust_tests/locustfile.py --host http://localhost:8080
# Open http://localhost:8089 in browser
# Set users + spawn rate, watch live charts
```

### Scaling Guidelines

| Real Users | Infra Needed |
|---|---|
| < 10,000 | Single server (4 CPU / 16 GB) — all services |
| 10,000-50,000 | 2-3 servers: separate DB, separate Keycloak |
| 50,000-200,000 | Kubernetes / container orchestration; DB replicas |
| 200,000+ | Horizontal scaling, Redis for rate limiting, CDN for photos |
