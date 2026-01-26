# Dating App Observability Stack

This directory contains the Prometheus + Grafana monitoring stack for the Dating App MVP.

## Components

- **Prometheus**: Metrics collection and storage
- **Grafana**: Dashboards and visualization
- **Health Dashboard**: Custom health check dashboard (port 8090)

## Quick Start

### Start the observability stack:
```bash
cd /home/m/development/DatingApp
docker-compose -f docker-compose.monitoring.yml up -d
```

### Access the dashboards:
- **Grafana**: http://localhost:3000
  - Username: `admin`
  - Password: `dating_app_2025`
- **Prometheus**: http://localhost:9090
- **Health Dashboard**: http://localhost:8090

### Stop the stack:
```bash
docker-compose -f docker-compose.monitoring.yml down
```

## Grafana Dashboards

Dashboards are automatically provisioned on startup:

1. **System Overview** (`dating-app-system-overview`)
   - Request rates across all services
   - Service health (up/down status)
   - Response time P95 percentiles
   - Error rates (5xx responses)

More dashboards can be created via Grafana UI and will be saved in the database.

## Metrics

All 6 backend services expose `/metrics` endpoints with OpenTelemetry instrumentation:

- **user-service** (port 8082) - Profile operations, search queries
- **matchmaking-service** (port 8083) - Match creation, algorithm performance
- **swipe-service** (port 8084) - Swipe processing, rate limiting
- **photo-service** (port 8085) - Photo uploads, moderation scores
- **messaging-service** (port 8086) - Message delivery, spam detection
- **auth-service** (port 8081) - Authentication, JWT issuance

## Custom Business Metrics

Each service exposes service-specific custom meters:

### User Service
- `user_profiles_created_total` - Profile creation counter
- `user_profiles_updated_total` - Profile update counter
- `user_profiles_deleted_total` - Profile deletion counter
- `user_search_duration_ms` - Search query duration histogram

### Matchmaking Service
- `matches_created_total` - Match creation counter
- `candidates_evaluated_total` - Candidate evaluation counter
- `match_score_value` - Compatibility score distribution
- `match_algorithm_duration_ms` - Algorithm performance histogram

### Swipe Service
- `swipes_processed_total` - Total swipe counter
- `likes_total` - Right swipe counter
- `passes_total` - Left swipe counter
- `mutual_matches_total` - Mutual match counter
- `swipes_rate_limited_total` - Rate limit enforcement counter

### Photo Service
- `photos_uploaded_total` - Photo upload counter
- `photos_deleted_total` - Photo deletion counter
- `photo_processing_duration_ms` - Processing time histogram
- `photo_moderation_score` - Safety score distribution

### Messaging Service
- `messages_sent_total` - Message counter
- `messages_moderated_total` - Moderation event counter
- `message_delivery_duration_ms` - SignalR delivery latency
- `spam_detection_score` - Spam score distribution

## Prometheus Configuration

See `prometheus/prometheus.yml` for scraping configuration.

- **Scrape Interval**: 15s
- **Evaluation Interval**: 15s
- **Retention**: 200h (~8 days)

## Alert Rules

Alert rules are defined in `prometheus/alert_rules.yml`:

- **ServiceDown**: Service unavailable for >30s
- **HighResponseTime**: P95 >2s for >2m
- **HighErrorRate**: Error rate >10% for >2m
- **DatabaseConnectionFailure**: Database unreachable for >1m
- **HighMemoryUsage**: Container memory >80% for >5m

## Adding New Dashboards

1. Create dashboard in Grafana UI
2. Export dashboard JSON (Settings > JSON Model)
3. Save to `dashboards/` directory
4. Dashboard will auto-load on next Grafana restart

OR

Create dashboard JSON directly in `dashboards/` and restart Grafana:
```bash
docker-compose -f docker-compose.monitoring.yml restart grafana
```

## Troubleshooting

### Prometheus not scraping services
- Ensure backend services are running (`./dev-start.sh`)
- Check Prometheus targets: http://localhost:9090/targets
- Verify `/metrics` endpoints are accessible (e.g., `curl http://localhost:8082/metrics`)

### Grafana shows "No Data"
- Check Prometheus datasource connection (Configuration > Data Sources)
- Verify Prometheus is collecting metrics: http://localhost:9090/graph
- Check time range in Grafana (top-right time picker)

### Dashboards not appearing
- Check Grafana logs: `docker logs dating-app-grafana`
- Verify provisioning files exist in `grafana/provisioning/`
- Restart Grafana: `docker-compose -f docker-compose.monitoring.yml restart grafana`

## Development

- Edit Prometheus config: `prometheus/prometheus.yml`
- Edit alert rules: `prometheus/alert_rules.yml`
- Reload Prometheus config: `curl -X POST http://localhost:9090/-/reload`
