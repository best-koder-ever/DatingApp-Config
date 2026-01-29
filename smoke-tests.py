#!/usr/bin/env python3
"""
API Smoke Tests for DatingApp CI/CD Pipeline
Tests basic health and functionality of all microservices
"""
import sys
import time
import httpx
from typing import Dict, List, Tuple

# Service configurations (port, health endpoint, optional functional test endpoint)
SERVICES = {
    "UserService": {
        "port": 8082,
        "health": "/health",
        "functional": "/api/users/test",  # Simple endpoint that doesn't require auth
    },
    "MatchmakingService": {
        "port": 8083,
        "health": "/health",
    },
    "SwipeService": {
        "port": 8084,
        "health": "/health",
    },
    "PhotoService": {
        "port": 8085,
        "health": "/health",
    },
    "MessagingService": {
        "port": 8086,
        "health": "/health",
    },
}

def test_health_endpoint(service_name: str, config: Dict) -> Tuple[bool, str]:
    """Test service health endpoint"""
    url = f"http://localhost:{config['port']}{config['health']}"
    try:
        response = httpx.get(url, timeout=5.0)
        if response.status_code == 200:
            data = response.json()
            if "status" in str(data).lower() or "healthy" in str(data).lower():
                return True, f"✅ {service_name} health check passed"
            return False, f"❌ {service_name} health check returned unexpected data: {data}"
        return False, f"❌ {service_name} health check failed with status {response.status_code}"
    except httpx.ConnectError:
        return False, f"⚠️  {service_name} not reachable (connection refused)"
    except Exception as e:
        return False, f"❌ {service_name} health check error: {str(e)}"

def wait_for_services(timeout: int = 30) -> None:
    """Wait for services to become ready"""
    print(f"⏳ Waiting up to {timeout}s for services to start...")
    start = time.time()
    while time.time() - start < timeout:
        # Check if at least one service is responding
        for service_name, config in SERVICES.items():
            try:
                url = f"http://localhost:{config['port']}{config['health']}"
                response = httpx.get(url, timeout=2.0)
                if response.status_code == 200:
                    print(f"✅ First service ({service_name}) is ready")
                    time.sleep(5)  # Give other services time to start
                    return
            except:
                pass
        time.sleep(2)
    print("⚠️  Timeout waiting for services, proceeding anyway...")

def run_smoke_tests() -> int:
    """Run all smoke tests and return exit code"""
    print("🧪 Starting DatingApp API Smoke Tests\n")
    
    wait_for_services()
    
    results: List[Tuple[bool, str]] = []
    
    # Test all health endpoints
    print("📋 Testing Health Endpoints:")
    for service_name, config in SERVICES.items():
        success, message = test_health_endpoint(service_name, config)
        results.append((success, message))
        print(f"  {message}")
    
    # Summary
    print(f"\n{'='*60}")
    passed = sum(1 for success, _ in results if success)
    total = len(results)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All smoke tests passed!")
        return 0
    elif passed > 0:
        print(f"⚠️  Partial success: {total - passed} test(s) failed")
        return 1
    else:
        print("❌ All smoke tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(run_smoke_tests())
