# Matchmaking Load Tests

K6 performance testing suite for the matchmaking service, measuring candidate generation, swipe processing, and match retrieval under realistic load.

## Prerequisites

Install K6:
```bash
# macOS
brew install k6

# Linux (Debian/Ubuntu)
sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update
sudo apt-get install k6

# Docker
docker pull grafana/k6:latest
```

## Test Scenarios

### 1. Baseline Load (2 minutes)
- **Virtual Users**: 20 constant
- **Purpose**: Establish performance baseline under normal traffic
- **Metrics**: Response times, throughput, error rates

### 2. Ramp-Up Test (5 minutes)
- **Virtual Users**: 0 → 50 → 100 → 0
- **Purpose**: Test scalability and identify breaking points
- **Metrics**: Performance degradation, resource utilization

### 3. Spike Test (50 seconds)
- **Virtual Users**: 0 → 200 → 0 (rapid spike)
- **Purpose**: Test system resilience under sudden traffic bursts
- **Metrics**: Recovery time, error handling, queue management

## Running Tests

### Local Development
```bash
# Ensure MatchmakingService is running on port 8083
cd load-tests/k6

# Run all scenarios (8 minute full test)
k6 run matchmaking-load-test.js

# Run with custom base URL
k6 run --env BASE_URL=http://localhost:8083 matchmaking-load-test.js

# Run through YARP gateway
k6 run --env YARP_URL=http://localhost:8080 matchmaking-load-test.js

# Generate HTML report
k6 run --out json=results.json matchmaking-load-test.js
```

### With Docker
```bash
docker run --rm -i --network host grafana/k6:latest run - <matchmaking-load-test.js
```

### CI/CD Integration
```bash
# Run with pass/fail thresholds
k6 run --no-color --quiet matchmaking-load-test.js

# Exit code 0 = all thresholds passed
# Exit code 99 = thresholds failed
```

## Performance Thresholds

From MVP constitution and [MATCHMAKING.md](../../specs/001-mvp-foundation/MATCHMAKING.md):

| Metric | Threshold | Rationale |
|--------|-----------|-----------|
| Candidate generation (p95) | <2000ms | Cache miss scenario |
| Candidate generation (cache hit) | <200ms | Cached score retrieval |
| Swipe processing (p95) | <200ms | Quick user interaction |
| Match retrieval (p95) | <500ms | Acceptable for non-critical path |
| Error rate | <1% | High reliability requirement |
| Cache hit rate | >90% | Algorithm efficiency |
| HTTP failures | <5% | Tolerate transient errors |

## Metrics Collected

### Standard HTTP Metrics
- `http_req_duration`: Request latency (p50, p95, p99)
- `http_req_failed`: Failed request rate
- `http_reqs`: Requests per second (RPS)
- `vus`: Active virtual users

### Custom Application Metrics
- `candidate_generation_time`: End-to-end candidate generation
- `swipe_processing_time`: Swipe endpoint response time
- `matches_retrieval_time`: Match list retrieval time
- `error_rate`: Application-level error rate
- `cache_hit_rate`: Percentage of cached responses

## Analyzing Results

### Console Output
K6 displays real-time metrics during test execution and a summary at the end:
```
✓ status is 200
✓ has candidates array
✓ response time <2s

checks.........................: 95.23% ✓ 9523      ✗ 477
data_received..................: 2.4 MB 300 kB/s
data_sent......................: 1.1 MB 138 kB/s
http_req_duration..............: avg=180ms min=45ms med=165ms max=2.1s p(95)=350ms p(99)=890ms
http_reqs......................: 10234  1279/s
vus............................: 20     min=0       max=200
```

### Export to JSON
```bash
k6 run --out json=results.json matchmaking-load-test.js

# Analyze with jq
jq '.metrics.http_req_duration' results.json
```

### Integration with Grafana
```bash
# Run with InfluxDB output
k6 run --out influxdb=http://localhost:8086/k6 matchmaking-load-test.js

# Or Prometheus Remote Write
k6 run --out experimental-prometheus-rw matchmaking-load-test.js
```

## Baseline Results

**Date**: 2026-01-30  
**Environment**: Local development (MacBook Pro, 12 cores)  
**Service Version**: MVP v1.0  
**Test Duration**: 8 minutes (all scenarios)

See [BASELINE_RESULTS.md](./BASELINE_RESULTS.md) for detailed metrics.

## Troubleshooting

### Service Not Healthy
```
Error: Service not healthy: 503
```
**Solution**: Ensure MatchmakingService is running and health endpoint responds:
```bash
curl http://localhost:8083/health
```

### High Error Rate
**Symptom**: `error_rate` threshold fails  
**Causes**:
- Database connection pool exhausted
- External service (UserService, SafetyService) down
- Insufficient CPU/memory

**Solution**: Check service logs, increase resource limits, scale horizontally

### Low Cache Hit Rate
**Symptom**: `cache_hit_rate` < 90%  
**Causes**:
- Test data spread across too many users (cache dilution)
- Cache invalidation too aggressive
- 24-hour cache window not honored

**Solution**: Review cache implementation, adjust test user pool

### Response Time Degradation
**Symptom**: p95 latency increases during ramp-up  
**Causes**:
- Database query N+1 problem
- Insufficient connection pooling
- Lock contention on shared resources

**Solution**: Database query profiling, add indexes, optimize scoring algorithm

## Next Steps

1. **Establish Baseline**: Run tests in clean environment, capture metrics
2. **Set Alerts**: Configure Prometheus alerts for threshold violations
3. **Continuous Testing**: Add to CI/CD pipeline (nightly runs)
4. **Expand Coverage**: Create load tests for other services (PhotoService, MessagingService)
5. **Stress Testing**: Find breaking point (increase VUs until failure)

## Related Documentation

- [MATCHMAKING.md](../../specs/001-mvp-foundation/MATCHMAKING.md) - Algorithm details
- [logs/README.md](../../logs/README.md) - Observability setup
- [api-spec.md](../../specs/001-mvp-foundation/contracts/api-spec.md) - API contracts
