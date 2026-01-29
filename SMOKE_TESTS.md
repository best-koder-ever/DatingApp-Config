# Smoke Tests

Automated smoke tests for the DatingApp microservices architecture.

## Overview

The smoke tests verify that all core services are healthy and responding correctly. These tests run:
- In CI/CD pipeline (GitHub Actions) after build
- Locally for development verification

## Services Tested

| Service | Port | Health Endpoint |
|---------|------|----------------|
| UserService | 8082 | `/health` |
| MatchmakingService | 8083 | `/health` |
| SwipeService | 8084 | `/health` |
| PhotoService | 8085 | `/health` |
| MessagingService | 8086 | `/health` |

## Running Locally

### Prerequisites
```bash
# Install Python dependencies
pip install httpx

# Or activate the project venv
source .venv/bin/activate
```

### Start Services
```bash
# Use the dev-start script
./dev-start.sh

# Or start services individually
cd UserService && dotnet run --urls="http://localhost:8082" &
cd MatchmakingService && dotnet run --urls="http://localhost:8083" &
# ... etc
```

### Run Smoke Tests
```bash
# Run the test script
python3 smoke-tests.py

# Expected output:
# 🧪 Starting DatingApp API Smoke Tests
# ⏳ Waiting up to 30s for services to start...
# ✅ First service (UserService) is ready
# 📋 Testing Health Endpoints:
#   ✅ UserService health check passed
#   ✅ MatchmakingService health check passed
#   ...
# ✅ All smoke tests passed!
```

## CI/CD Integration

The smoke tests are integrated into `.github/workflows/comprehensive-ci-cd.yml`:

1. **Build Phase**: All services are compiled
2. **Service Startup**: Services start in background on their designated ports
3. **Smoke Tests**: Python script validates all health endpoints
4. **Cleanup**: Services are stopped, logs captured on failure

### Workflow Steps
```yaml
- name: Start services (background)
  # Starts all 5 microservices on ports 8082-8086

- name: Run smoke tests
  run: python3 smoke-tests.py

- name: Display service logs on failure
  if: failure()
  # Shows last 50 lines of each service log for debugging

- name: Cleanup services
  if: always()
  # Kills all background processes
```

## Test Structure

### Health Check Test
Each service is tested with:
- HTTP GET to `/health` endpoint
- 5-second timeout
- JSON response validation
- Status field verification

### Exit Codes
- `0`: All tests passed
- `1`: At least one test failed

## Troubleshooting

### Service Not Reachable
```
⚠️  {ServiceName} not reachable (connection refused)
```
**Solution**: Ensure service is running on the correct port

### Connection Timeout
```
❌ {ServiceName} health check error: timeout
```
**Solution**: Service may be starting slowly, increase wait time in `wait_for_services()`

### View Service Logs (CI)
Check the "Display service logs on failure" step in GitHub Actions for detailed error messages.

### View Service Logs (Local)
```bash
# If using dev-start.sh, check logs in terminal
# If running manually, redirect to files:
dotnet run > service.log 2>&1 &
tail -f service.log
```

## Extending Tests

To add functional tests beyond health checks:

1. Edit `smoke-tests.py`
2. Add test functions (e.g., `test_user_creation()`)
3. Update `SERVICES` dict with `"functional"` endpoint
4. Call test functions in `run_smoke_tests()`

Example:
```python
SERVICES = {
    "UserService": {
        "port": 8082,
        "health": "/health",
        "functional": "/api/users/stats",  # Unauthenticated endpoint
    },
}

def test_functional_endpoint(service_name: str, config: Dict) -> Tuple[bool, str]:
    if "functional" not in config:
        return True, f"⏭️  {service_name} has no functional test"
    
    url = f"http://localhost:{config['port']}{config['functional']}"
    response = httpx.get(url, timeout=5.0)
    if response.status_code == 200:
        return True, f"✅ {service_name} functional test passed"
    return False, f"❌ {service_name} functional test failed"
```

## Related Files

- `smoke-tests.py` - Main test script
- `.github/workflows/comprehensive-ci-cd.yml` - CI/CD integration
- `dev-start.sh` - Local development environment startup
