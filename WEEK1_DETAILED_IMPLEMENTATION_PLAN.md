# Week 1: Test Infrastructure - Detailed Implementation Plan

**Date**: January 28, 2026  
**Goal**: Build professional testing foundation that enables all future testing  
**Duration**: 5 days focused work

---

## 🏗️ Architecture Overview: The "Big Boss" Testing System

### The Vision

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         TESTING ARCHITECTURE                              │
└─────────────────────────────────────────────────────────────────────────┘

Production Services:                Test Infrastructure:
├─ UserService/                     tests/
├─ SwipeService/                    ├─── api/              (contract tests)
├─ MatchmakingService/              ├─── integration/      (cross-service)
├─ PhotoService/                    ├─── e2e/              (full journeys)
├─ MessagingService/                ├─── bots/             (load simulation)
└─ dejting-yarp/                    └─── shared/           (test utilities)
                                    
Each service has:                   infrastructure/
├─── Tests/                         ├─── test-fixtures/    (test data)
│    ├─ Unit tests                  │    ├─ minimal/
│    └─ Service integration tests   │    ├─ standard/
                                    │    ├─ load/
                                    │    └─ demo/
                                    └─── test-data-loader/ (CLI tool)

┌─────────────────────────────────────────────────────────────────────────┐
│                    THE "BIG BOSS" = tests/e2e/                           │
│  Orchestrates entire user journeys, used by both CI/CD and bots         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Key Architectural Decisions

**✅ DO**: Create centralized `tests/` directory at repository root
**✅ DO**: Treat test infrastructure as first-class citizen
**✅ DO**: Share test data via `infrastructure/test-fixtures/`
**✅ DO**: Use test orchestrator for E2E journeys
**❌ DON'T**: Make testing a separate microservice (tests are not production)
**❌ DON'T**: Duplicate test data across services

---

## 📊 Testing Layers Explained

### Layer 1: Unit Tests (Already Exists - Per Service)
**Location**: `UserService/Tests/`, `SwipeService.Tests/`, etc.  
**Purpose**: Test individual classes/methods in isolation  
**Runs**: On every commit, very fast (<30s per service)  
**Example**: Test that `UserProfile.Validate()` catches invalid emails

**Status**: ✅ Already have test skeletons (T003 complete)

### Layer 2: Service Integration Tests (Per Service)
**Location**: Same as unit tests but marked `[Integration]`  
**Purpose**: Test service with its database, no external dependencies  
**Runs**: On PR, slower (~2min per service)  
**Example**: Test that creating a profile persists to DB correctly

**Status**: ⚠️ Minimal - need to expand

### Layer 3: Contract Tests (Centralized - NEW Week 1)
**Location**: `tests/api/` ← **THIS IS WEEK 1 DELIVERABLE**  
**Purpose**: Validate all API endpoints match spec, status codes, schemas  
**Runs**: On PR, medium speed (~5min for all services)  
**Example**: `POST /api/userprofiles` returns 201 with valid UserProfile JSON

**Framework**: Pytest + requests + jsonschema  
**This is our "API Big Boss" for backend validation**

### Layer 4: E2E Journey Tests (Centralized - Week 2-3)
**Location**: `tests/e2e/` ← **THE REAL "BIG BOSS"**  
**Purpose**: Full user journeys across all services  
**Runs**: On PR (critical paths), nightly (full suite)  
**Example**: Register → Create profile → Upload photo → Swipe → Match → Message

**Framework**: Pytest + requests (API-level) OR Flutter integration_test (UI-level)  
**This orchestrates everything and is what bots will use**

### Layer 5: Bot Load Testing (Centralized - Week 3)
**Location**: `tests/bots/`  
**Purpose**: Simulate 100-1000 concurrent users running journeys  
**Runs**: On-demand, nightly load tests  
**Example**: Spawn 500 bots doing register → swipe → message simultaneously

**Built on top of Layer 4** - bots run E2E journey tests but with concurrency + metrics

---

## 🎯 Week 1 Focus: Build Foundation (Layers 1-3)

We focus on **infrastructure** that enables all testing:

1. **Test Data Management** (infrastructure/test-fixtures/)
2. **Test Data Loader** (infrastructure/test-data-loader/)
3. **API Contract Tests** (tests/api/)
4. **Test Environment** (docker-compose.test.yml)

**Why this order?** Everything else depends on reliable test data.

---

## 📅 Day-by-Day Implementation Plan

## DAY 1: Architecture Setup + Test Data Design

### Morning (4 hours): Repository Structure

**Create centralized test infrastructure**:

```bash
cd /home/m/development/DatingApp

# Create central test directory
mkdir -p tests/{api,integration,e2e,bots,shared}
mkdir -p tests/api/{userservice,swipeservice,matchmaking,photo,messaging,gateway}
mkdir -p tests/shared/{fixtures,utilities,contracts}

# Create fixture infrastructure
mkdir -p infrastructure/test-fixtures/{minimal,standard,load,demo}
mkdir -p infrastructure/test-fixtures/schemas
mkdir -p infrastructure/test-data-loader

# Create test environment
touch infrastructure/docker-compose.test.yml

# Documentation
cat > tests/README.md << 'TEST_README'
# DatingApp Test Infrastructure

## Architecture

- **tests/api/** - Contract tests validating all API endpoints
- **tests/integration/** - Cross-service integration tests
- **tests/e2e/** - Full user journey tests (THE BIG BOSS)
- **tests/bots/** - Load testing with synthetic users
- **tests/shared/** - Shared utilities, fixtures, contracts

## Running Tests

```bash
# API contract tests (fast, run on every PR)
pytest tests/api/ -v

# Integration tests (slower, cross-service validation)
pytest tests/integration/ -v

# E2E journey tests (full user flows)
pytest tests/e2e/ -v

# Load tests (simulate 1000 users)
python tests/bots/run_load_test.py --users 1000 --duration 60m
```

## Test Data

All tests use centralized fixtures from `infrastructure/test-fixtures/`:
- **minimal**: 5 users, 2 matches - Fast unit tests
- **standard**: 50 users, 20 matches - Integration tests
- **load**: 1000 users, 500 matches - Performance tests
- **demo**: 10 curated personas - Stakeholder demos

Load fixtures: `./infrastructure/test-data-loader/load.py minimal --env test`
TEST_README

echo "✅ Test directory structure created"
```

**Deliverable**: Clean test infrastructure ready for population

### Afternoon (4 hours): Data Model Analysis + Fixture Design

**Analyze all service data models**:

```bash
cd /home/m/development/DatingApp

# Extract all C# models
echo "# Data Models for Test Fixtures" > infrastructure/test-fixtures/schemas/models.md
echo "" >> infrastructure/test-fixtures/schemas/models.md

for service in UserService SwipeService MatchmakingService photo-service messaging-service; do
    echo "## $service" >> infrastructure/test-fixtures/schemas/models.md
    if [ -d "$service/Models" ]; then
        grep -h "public class" "$service/Models/"*.cs 2>/dev/null | \
        sed 's/public class /- /' | sed 's/ .*//' >> infrastructure/test-fixtures/schemas/models.md || true
    fi
    echo "" >> infrastructure/test-fixtures/schemas/models.md
done

# Review the output
cat infrastructure/test-fixtures/schemas/models.md
```

**Design fixture format** (JSON chosen for readability):

```bash
cat > infrastructure/test-fixtures/schemas/fixture-format.md << 'FIXTURE_FORMAT'
# Test Fixture Format Design

## Fixture Structure

Each fixture set contains:
```
fixtures/<set-name>/
├── keycloak_users.json       # Keycloak user definitions
├── user_profiles.json         # UserService profiles
├── swipes.json                # SwipeService swipe history
├── matches.json               # MatchmakingService matches
├── photos.json                # PhotoService photo metadata
├── messages.json              # MessagingService conversations
└── metadata.json              # Fixture metadata (version, description)
```

## JSON Schema Examples

### keycloak_users.json
```json
[
  {
    "username": "alice_test",
    "email": "alice@test.datingapp.com",
    "firstName": "Alice",
    "lastName": "Test",
    "password": "TestPass123!",
    "enabled": true,
    "emailVerified": true
  }
]
```

### user_profiles.json
```json
[
  {
    "userId": "alice_test",  // References Keycloak username
    "name": "Alice Test",
    "bio": "Test user for automated testing",
    "gender": "Female",
    "dateOfBirth": "1995-01-15T00:00:00Z",
    "city": "Stockholm",
    "interests": ["hiking", "coding"],
    "onboardingStatus": "Ready"
  }
]
```

### matches.json
```json
[
  {
    "user1": "alice_test",  // References username
    "user2": "bob_test",
    "compatibilityScore": 87.5,
    "source": "test_fixture",
    "createdAt": "2026-01-20T10:00:00Z"
  }
]
```

## Design Principles

1. **Human-readable**: JSON with clear field names
2. **Referential integrity**: Use usernames as foreign keys
3. **Realistic data**: Mimic production patterns
4. **Deterministic**: Same fixture = same IDs/results
5. **Minimal dependencies**: Load in order (Keycloak → Profiles → Matches)
FIXTURE_FORMAT

cat infrastructure/test-fixtures/schemas/fixture-format.md
```

**Deliverable**: Clear fixture format defined, ready to implement

---

## DAY 2: Minimal Fixture Set + Loader Tool (Part 1)

### Morning (4 hours): Create Minimal Fixture

**Goal**: 2 users who can match

```bash
cd /home/m/development/DatingApp/infrastructure/test-fixtures/minimal

# Keycloak users
cat > keycloak_users.json << 'KEYCLOAK_JSON'
[
  {
    "username": "alice_minimal",
    "email": "alice@minimal.test.datingapp.com",
    "firstName": "Alice",
    "lastName": "Minimal",
    "password": "MinimalTest123!",
    "enabled": true,
    "emailVerified": true,
    "realmRoles": ["user"]
  },
  {
    "username": "bob_minimal",
    "email": "bob@minimal.test.datingapp.com",
    "firstName": "Bob",
    "lastName": "Minimal",
    "password": "MinimalTest123!",
    "enabled": true,
    "emailVerified": true,
    "realmRoles": ["user"]
  }
]
KEYCLOAK_JSON

# User profiles (we'll populate with real schema after analyzing models)
cat > user_profiles.json << 'PROFILES_JSON'
[
  {
    "userId": "alice_minimal",
    "name": "Alice Minimal",
    "email": "alice@minimal.test.datingapp.com",
    "bio": "Test user for minimal fixture set",
    "gender": "Female",
    "preferences": "Male",
    "dateOfBirth": "1995-06-15T00:00:00Z",
    "city": "Stockholm",
    "country": "Sweden",
    "interests": ["hiking", "photography"],
    "languages": ["Swedish", "English"],
    "height": 170,
    "onboardingStatus": "Ready",
    "isActive": true
  },
  {
    "userId": "bob_minimal",
    "name": "Bob Minimal",
    "email": "bob@minimal.test.datingapp.com",
    "bio": "Test user for minimal fixture set",
    "gender": "Male",
    "preferences": "Female",
    "dateOfBirth": "1993-03-20T00:00:00Z",
    "city": "Stockholm",
    "country": "Sweden",
    "interests": ["hiking", "music"],
    "languages": ["Swedish", "English"],
    "height": 180,
    "onboardingStatus": "Ready",
    "isActive": true
  }
]
PROFILES_JSON

# Swipes
cat > swipes.json << 'SWIPES_JSON'
[
  {
    "swiperId": "alice_minimal",
    "swipedUserId": "bob_minimal",
    "direction": "Right",
    "timestamp": "2026-01-20T10:00:00Z"
  },
  {
    "swiperId": "bob_minimal",
    "swipedUserId": "alice_minimal",
    "direction": "Right",
    "timestamp": "2026-01-20T10:05:00Z"
  }
]
SWIPES_JSON

# Matches (created by mutual swipes)
cat > matches.json << 'MATCHES_JSON'
[
  {
    "user1": "alice_minimal",
    "user2": "bob_minimal",
    "compatibilityScore": 85.0,
    "source": "mutual_swipe",
    "createdAt": "2026-01-20T10:05:00Z"
  }
]
MATCHES_JSON

# Photos (minimal - just metadata, no actual images for speed)
cat > photos.json << 'PHOTOS_JSON'
[
  {
    "userId": "alice_minimal",
    "fileName": "alice_profile.jpg",
    "privacyLevel": "Public",
    "isPrimary": true,
    "uploadedAt": "2026-01-20T09:00:00Z"
  },
  {
    "userId": "bob_minimal",
    "fileName": "bob_profile.jpg",
    "privacyLevel": "Public",
    "isPrimary": true,
    "uploadedAt": "2026-01-20T09:00:00Z"
  }
]
PHOTOS_JSON

# Metadata
cat > metadata.json << 'METADATA_JSON'
{
  "name": "minimal",
  "description": "Minimal test fixture with 2 users and 1 match",
  "version": "1.0",
  "userCount": 2,
  "matchCount": 1,
  "createdAt": "2026-01-28",
  "purpose": "Fast unit tests, smoke tests, development"
}
METADATA_JSON

echo "✅ Minimal fixture set created"
ls -lah
```

**Deliverable**: Minimal fixture ready to load

### Afternoon (4 hours): Fixture Loader Tool (Part 1 - Keycloak)

**Build Python CLI tool**:

```python
# infrastructure/test-data-loader/load.py
#!/usr/bin/env python3
"""
Test Data Loader

Loads test fixtures into Keycloak + service databases.
Idempotent - can be run multiple times safely.

Usage:
    ./load.py minimal --env test
    ./load.py standard --env dev
    ./load.py --reset --env test  # Clear all test data first
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any
import requests
from dataclasses import dataclass


@dataclass
class LoaderConfig:
    """Configuration for test data loader"""
    fixtures_dir: Path
    keycloak_url: str
    keycloak_realm: str
    keycloak_admin: str
    keycloak_admin_password: str
    gateway_url: str
    mysql_host: str
    mysql_port: int
    mysql_user: str
    mysql_password: str
    
    @classmethod
    def from_env(cls, env: str) -> 'LoaderConfig':
        """Load config from environment"""
        return cls(
            fixtures_dir=Path(__file__).parent.parent / "test-fixtures",
            keycloak_url=os.getenv("KEYCLOAK_URL", "http://localhost:8090"),
            keycloak_realm=os.getenv("KEYCLOAK_REALM", "DatingApp"),
            keycloak_admin=os.getenv("KEYCLOAK_ADMIN", "admin"),
            keycloak_admin_password=os.getenv("KEYCLOAK_ADMIN_PASSWORD", "admin"),
            gateway_url=os.getenv("GATEWAY_URL", "http://localhost:8080/api"),
            mysql_host=os.getenv(f"MYSQL_HOST_{env.upper()}", "localhost"),
            mysql_port=int(os.getenv(f"MYSQL_PORT_{env.upper()}", "3306")),
            mysql_user=os.getenv(f"MYSQL_USER_{env.upper()}", "root"),
            mysql_password=os.getenv(f"MYSQL_PASSWORD_{env.upper()}", "password"),
        )


class FixtureLoader:
    """Loads test fixtures"""
    
    def __init__(self, config: LoaderConfig):
        self.config = config
        self.session = requests.Session()
        self.admin_token = None
        
    def load_fixture_set(self, name: str) -> bool:
        """Load complete fixture set"""
        fixture_dir = self.config.fixtures_dir / name
        if not fixture_dir.exists():
            print(f"❌ Fixture set '{name}' not found at {fixture_dir}")
            return False
            
        print(f"📦 Loading fixture set: {name}")
        print(f"📂 From: {fixture_dir}")
        
        # Load metadata
        metadata_file = fixture_dir / "metadata.json"
        if metadata_file.exists():
            with open(metadata_file) as f:
                metadata = json.load(f)
                print(f"📋 {metadata.get('description', 'No description')}")
                print(f"👥 Users: {metadata.get('userCount', 'unknown')}")
        
        # Step 1: Load Keycloak users
        print("\n1️⃣ Loading Keycloak users...")
        if not self._load_keycloak_users(fixture_dir / "keycloak_users.json"):
            return False
            
        # Step 2: Load user profiles via API
        print("\n2️⃣ Loading user profiles...")
        if not self._load_user_profiles(fixture_dir / "user_profiles.json"):
            return False
            
        # Step 3: Load swipes
        print("\n3️⃣ Loading swipes...")
        if not self._load_swipes(fixture_dir / "swipes.json"):
            return False
            
        # Step 4: Load matches
        print("\n4️⃣ Loading matches...")
        if not self._load_matches(fixture_dir / "matches.json"):
            return False
            
        # Step 5: Load photos
        print("\n5️⃣ Loading photos...")
        if not self._load_photos(fixture_dir / "photos.json"):
            return False
            
        print("\n✅ Fixture set loaded successfully!")
        return True
    
    def _get_admin_token(self) -> str:
        """Get Keycloak admin token"""
        if self.admin_token:
            return self.admin_token
            
        url = f"{self.config.keycloak_url}/realms/master/protocol/openid-connect/token"
        data = {
            "grant_type": "password",
            "client_id": "admin-cli",
            "username": self.config.keycloak_admin,
            "password": self.config.keycloak_admin_password,
        }
        
        try:
            resp = self.session.post(url, data=data, timeout=10)
            resp.raise_for_status()
            self.admin_token = resp.json()["access_token"]
            return self.admin_token
        except Exception as e:
            print(f"❌ Failed to get admin token: {e}")
            sys.exit(1)
    
    def _load_keycloak_users(self, file_path: Path) -> bool:
        """Load users into Keycloak"""
        if not file_path.exists():
            print(f"⚠️  Skipping - file not found: {file_path}")
            return True
            
        with open(file_path) as f:
            users = json.load(f)
        
        token = self._get_admin_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        users_url = f"{self.config.keycloak_url}/admin/realms/{self.config.keycloak_realm}/users"
        
        for user in users:
            username = user["username"]
            password = user.pop("password")  # Don't send in creation payload
            
            # Create user
            resp = self.session.post(users_url, headers=headers, json=user, timeout=10)
            
            if resp.status_code == 201:
                print(f"   ✅ Created user: {username}")
                
                # Get user ID from Location header
                user_id = resp.headers["Location"].split("/")[-1]
                
                # Set password
                password_url = f"{users_url}/{user_id}/reset-password"
                password_payload = {
                    "type": "password",
                    "value": password,
                    "temporary": False
                }
                self.session.put(password_url, headers=headers, json=password_payload)
                
            elif resp.status_code == 409:
                print(f"   ⚠️  User exists: {username}")
            else:
                print(f"   ❌ Failed to create {username}: {resp.status_code}")
                print(f"      {resp.text}")
                
        return True
    
    def _load_user_profiles(self, file_path: Path) -> bool:
        """Load user profiles via UserService API"""
        # TODO: Implement after Keycloak users exist
        # Get tokens for each user, call POST /api/userprofiles
        print("   ⚠️  TODO: Implement profile loading via API")
        return True
    
    def _load_swipes(self, file_path: Path) -> bool:
        """Load swipes via SwipeService"""
        print("   ⚠️  TODO: Implement swipe loading")
        return True
    
    def _load_matches(self, file_path: Path) -> bool:
        """Load matches via MatchmakingService"""
        print("   ⚠️  TODO: Implement match loading")
        return True
    
    def _load_photos(self, file_path: Path) -> bool:
        """Load photo metadata via PhotoService"""
        print("   ⚠️  TODO: Implement photo loading")
        return True


def main():
    parser = argparse.ArgumentParser(description="Load test fixtures")
    parser.add_argument("fixture", help="Fixture set name (minimal, standard, load, demo)")
    parser.add_argument("--env", default="test", help="Environment (test, dev)")
    parser.add_argument("--reset", action="store_true", help="Clear existing data first")
    
    args = parser.parse_args()
    
    config = LoaderConfig.from_env(args.env)
    loader = FixtureLoader(config)
    
    if args.reset:
        print("⚠️  TODO: Implement reset functionality")
    
    success = loader.load_fixture_set(args.fixture)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
```

Make it executable:
```bash
chmod +x infrastructure/test-data-loader/load.py
```

**Deliverable**: Loader tool can provision Keycloak users (first step working)

---

## DAY 3: Complete Fixture Loader + Standard Fixture Set

### Morning (4 hours): Complete All Loading Functions

Implement the TODO methods:
- `_load_user_profiles()` - Get token, POST to /api/userprofiles
- `_load_swipes()` - POST to /api/swipes  
- `_load_matches()` - POST to /api/matchmaking/matches
- `_load_photos()` - POST to /api/photos with metadata

Add `--reset` functionality to clear databases.

### Afternoon (4 hours): Standard Fixture Set

Create `infrastructure/test-fixtures/standard/` with:
- 50 users (diverse profiles)
- 100 swipes (mix of left/right)
- 20 mutual matches
- 50 photos
- 10 message conversations

Use AI to generate realistic Swedish personas.

**Deliverable**: Can load standard fixture in <10 seconds

---

## DAY 4: Test Environment + Docker Integration

### Morning (4 hours): docker-compose.test.yml

**Create isolated test environment**:

```yaml
# infrastructure/docker-compose.test.yml
version: '3.8'

services:
  # Keycloak for test
  keycloak-test:
    image: quay.io/keycloak/keycloak:23.0
    environment:
      KC_DB: mysql
      KC_DB_URL: jdbc:mysql://mysql-test:3306/keycloak_test
      KC_DB_USERNAME: keycloak
      KC_DB_PASSWORD: keycloak_test_pass
      KEYCLOAK_ADMIN: admin
      KEYCLOAK_ADMIN_PASSWORD: admin_test
    ports:
      - "8091:8080"  # Different port from dev
    networks:
      - test-network
    depends_on:
      - mysql-test

  # MySQL for test (separate from dev)
  mysql-test:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: root_test_pass
      MYSQL_DATABASE: datingapp_test
    ports:
      - "3307:3306"  # Different port from dev
    networks:
      - test-network
    volumes:
      - mysql-test-data:/var/lib/mysql

  # Redis for test (if needed)
  redis-test:
    image: redis:7-alpine
    ports:
      - "6380:6379"  # Different port from dev
    networks:
      - test-network

networks:
  test-network:
    driver: bridge

volumes:
  mysql-test-data:
```

Start test environment:
```bash
docker-compose -f infrastructure/docker-compose.test.yml up -d
```

**Auto-load fixtures on startup**:
Add initialization script that loads minimal fixture.

### Afternoon (4 hours): Integration with Services

**Update service connection strings for test environment**:
- Add `appsettings.Test.json` to each service
- Configure test database connections
- Document in RUNBOOK.md

**Create helper scripts**:
```bash
# scripts/test-env-start.sh
#!/bin/bash
docker-compose -f infrastructure/docker-compose.test.yml up -d
sleep 10  # Wait for services
./infrastructure/test-data-loader/load.py minimal --env test
echo "✅ Test environment ready!"

# scripts/test-env-stop.sh
#!/bin/bash
docker-compose -f infrastructure/docker-compose.test.yml down -v
```

**Deliverable**: Isolated test environment that's separate from dev

---

## DAY 5: API Contract Test Suite (Foundation)

### All Day (8 hours): Build pytest Test Suite

**Install dependencies**:
```bash
cd /home/m/development/DatingApp
python -m venv .venv-tests
source .venv-tests/bin/activate
pip install pytest requests jsonschema pytest-html pytest-xdist
```

**Create test suite structure**:

```python
# tests/api/conftest.py
"""Shared fixtures for API tests"""
import pytest
import requests

@pytest.fixture(scope="session")
def api_base_url():
    return "http://localhost:8080/api"

@pytest.fixture(scope="session")
def test_user_credentials():
    return {
        "username": "alice_minimal",
        "password": "MinimalTest123!"
    }

@pytest.fixture(scope="session")
def auth_token(api_base_url, test_user_credentials):
    """Get auth token for test user"""
    # TODO: Implement Keycloak token fetch
    pass

# tests/api/test_userservice.py
"""UserService API contract tests"""
import pytest

def test_get_profile_requires_auth(api_base_url):
    """Verify GET /userprofiles/{id} requires authentication"""
    resp = requests.get(f"{api_base_url}/userprofiles/1")
    assert resp.status_code == 401

def test_create_profile_success(api_base_url, auth_token):
    """Verify POST /userprofiles creates profile"""
    payload = {
        "name": "Test User",
        "bio": "Test bio",
        # ... full profile
    }
    headers = {"Authorization": f"Bearer {auth_token}"}
    resp = requests.post(f"{api_base_url}/userprofiles", 
                         json=payload, headers=headers)
    assert resp.status_code in [200, 201]
    assert "id" in resp.json()

def test_profile_schema_validation(api_base_url, auth_token):
    """Verify profile response matches schema"""
    # TODO: Use jsonschema to validate
    pass

# tests/api/test_swipeservice.py
# tests/api/test_matchmaking.py
# tests/api/test_photoservice.py
# tests/api/test_messaging.py
# etc.
```

**Run tests**:
```bash
pytest tests/api/ -v --html=test-report.html
```

**Deliverable**: 20+ API contract tests covering critical endpoints

---

## 📊 Week 1 Success Criteria

At end of Week 1, you should have:

✅ **Test Infrastructure**
- `tests/` directory with api/, integration/, e2e/, bots/ structure
- Clear README explaining architecture

✅ **Test Data**
- Minimal fixture (2 users, 1 match) ready
- Standard fixture (50 users, 20 matches) ready
- Fixture loader CLI tool working
- Can load fixtures in <10 seconds

✅ **Test Environment**
- `docker-compose.test.yml` for isolated testing
- Separate from dev environment (different ports/DBs)
- Auto-loads minimal fixture on startup

✅ **API Test Suite**
- 20+ pytest tests for critical endpoints
- Tests run via `pytest tests/api/`
- Validates status codes, schemas, authentication
- Generates HTML test report

✅ **Documentation**
- RUNBOOK.md updated with test workflows
- Fixture format documented
- Test architecture explained

---

## 🔗 How This Connects to Future Weeks

### Week 2: API Tests + Vanilla Harness
**Builds on Week 1**:
- Expand API tests to 80%+ endpoint coverage (uses fixtures from Week 1)
- Build vanilla Flutter harness (uses test environment from Week 1)
- Integration tests between services (uses fixture loader)

### Week 3: Bot Framework
**Builds on Weeks 1-2**:
- Bots use fixture loader to create synthetic users
- Bots run E2E tests from Week 2
- Load testing orchestrates 1000 concurrent users
- Metrics dashboard shows bot performance

### Week 4: Production UI
**Builds on Weeks 1-3**:
- Production UI connects to validated backend (proven by API tests)
- Can run bot tests against production UI
- CI/CD validates every PR with full test suite

---

## 🎯 The "Big Boss" Architecture Revealed

```
┌────────────────────────────────────────────────────────────────────┐
│                     CI/CD Pipeline (GitHub Actions)                 │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  On PR:                                                       │  │
│  │  1. Run unit tests (per service) - 2 min                     │  │
│  │  2. Run API contract tests - 5 min    ← Week 1 deliverable  │  │
│  │  3. Run integration tests - 10 min    ← Week 2 expansion    │  │
│  │  4. Run E2E critical paths - 15 min   ← Week 2-3 deliverable│  │
│  │                                                               │  │
│  │  Nightly:                                                     │  │
│  │  5. Run full E2E suite - 60 min       ← THE BIG BOSS        │  │
│  │  6. Run load tests (1000 bots) - 60min ← Week 3 deliverable │  │
│  │  7. Generate dashboard - 5 min                               │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────┘

All tests use:
├─ infrastructure/test-fixtures/ (Week 1)
├─ infrastructure/test-data-loader/ (Week 1)
└─ tests/e2e/ (THE BIG BOSS - Week 2-3)

Bot framework (Week 3):
└─ Uses tests/e2e/ with concurrency + metrics
```

**The "Big Boss" = tests/e2e/ running in CI/CD with 100%+ coverage**

It's not a separate service - it's a comprehensive test suite that:
1. ✅ Runs all user journeys end-to-end
2. ✅ Used by CI/CD for every PR
3. ✅ Used by bots for load testing
4. ✅ Provides overview dashboard
5. ✅ Can be run locally or in CI

---

## 💡 Key Insights for Your Question

> "should we focus on one thing still it will be done soner or later"

**YES - Focus on Week 1 first**. Here's why:

**Week 1 = Foundation for Everything**:
- Test fixtures enable all other testing
- Fixture loader is reused by unit/integration/E2E/bots
- Test environment isolates testing from dev
- API contract tests validate backend independently

**Without Week 1**: Can't reliably test anything  
**With Week 1**: Can build E2E, bots, CI/CD confidently

**Week 2-4 build incrementally** on this foundation:
- Week 2: More API tests + integration validation
- Week 3: Bots (reuse fixtures + E2E tests with concurrency)
- Week 4: Production UI (validated backend)

**The "Big Boss" emerges over 3 weeks**, not all at once:
- Week 1: Contract tests (API validation)
- Week 2: E2E tests (journey orchestration)
- Week 3: Bot framework (load + metrics)
- Result: Comprehensive testing system

---

## 🚀 Ready to Start?

**OPTION 1: Execute Week 1 Day 1 today**
Say: "Start Day 1" → I'll create directories, analyze models, design fixtures

**OPTION 2: See examples first**
Say: "Show me [specific part]" → I'll demonstrate before building

**OPTION 3: Adjust the plan**
Say: "Change [aspect]" → We refine before starting

**Your move!** 🎯

