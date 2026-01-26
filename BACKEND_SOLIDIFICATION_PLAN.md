# Backend Solidification Plan
**Date**: 2026-01-26  
**Current Phase**: Phase 5-6 (Messaging & Safety)  
**Progress**: 27/83 tasks complete (33%)

## Current Status Assessment

### ✅ What's Solid (Production-Ready)
1. **Authentication**: Keycloak OIDC fully operational
2. **User Profiles**: Complete CRUD with photo upload pipeline
3. **Matchmaking Core**: Advanced scoring algorithm (location, age, interests, lifestyle)
4. **Swipe Service**: Idempotency, retry logic, daily limits
5. **SignalR Hubs**: Real-time match notifications + messaging infrastructure
6. **Safety Service**: Report/block endpoints with database persistence
7. **YARP Gateway**: WebSocket passthrough, JWT auth, rate limiting
8. **Messaging**: Message persistence, conversation history, match-based messaging

### ⚠️ What Needs Hardening (Technical Debt)

#### **Critical Path Blockers** (Must Fix Before Launch)
1. **T007 [DB Consolidation]**: Mixed PostgreSQL/MySQL without clear strategy
   - **Impact**: Operational complexity, migration risks
   - **Fix**: Standardize on MySQL (already used by User/Messaging/Auth)
   - **Estimate**: 4h

2. **T008 [Remove AuthService]**: Dual auth systems causing confusion
   - **Impact**: Security risk, maintenance burden
   - **Fix**: Delete AuthService, update YARP routes
   - **Estimate**: 3h

3. **T004 [CI/CD Green Builds]**: Tests exist but not gated
   - **Impact**: Regression bugs, breaking changes unnoticed
   - **Fix**: Enable comprehensive-ci-cd.yml, add coverage badges
   - **Estimate**: 3h

#### **Performance & Scalability**
4. **T062 [EF Core Query Optimization]**: N+1 queries, missing indexes
   - **Services**: MatchmakingService (candidate queries), UserService (profile lookups)
   - **Fix**: Add composite indexes, use compiled queries, eager loading
   - **Estimate**: 3-4h

5. **Missing Service-to-Service Auth**: Services trust internal calls without validation
   - **Risk**: If YARP is bypassed, no auth layer
   - **Fix**: Add internal API keys or mutual TLS
   - **Estimate**: 4-5h

#### **Observability & Monitoring**
6. **T068-T071 [Metrics Instrumentation]**: No telemetry for success criteria
   - **Missing**: Onboarding funnel, match conversion, message latency, safety SLA
   - **Fix**: Add OpenTelemetry spans, Prometheus metrics
   - **Estimate**: 8-10h (2-3h each)

7. **No Centralized Logging**: Scattered logs across 8 services
   - **Fix**: Configure Serilog → Seq/Loki aggregation
   - **Estimate**: 3-4h

#### **Data Integrity & Safety**
8. **T052 [PhotoService Privacy]**: Photos visible to non-matches
   - **Impact**: Privacy violation, MMP requirement
   - **Fix**: Check match status before serving photos, blur enforcement
   - **Estimate**: 3-4h

9. **No Photo Cleanup**: Orphaned photos when users delete profiles
   - **Fix**: Add cascade delete, scheduled cleanup job
   - **Estimate**: 2-3h

10. **Missing Rate Limit Enforcement**: YARP routes defined but not enforced
    - **Risk**: Spam, resource exhaustion
    - **Fix**: Enable rate limiter middleware in YARP
    - **Estimate**: 2h

---

## Proposed Backend Solidification Roadmap

### **Week 1: Critical Infrastructure** (20-25h)
**Goal**: Fix architectural blockers, make system production-deployable

#### Day 1-2: Database & Auth Cleanup (7h)
- [ ] **T007**: Migrate PostgreSQL services to MySQL (4h)
  - PhotoService, SwipeService, MatchmakingService
  - Update docker-compose, connection strings
  - Test migration scripts
- [ ] **T008**: Remove AuthService (3h)
  - Delete directory, update YARP routes
  - Remove from dev-start.sh, docker-compose

#### Day 3: CI/CD & Testing (6h)
- [ ] **T004**: Enable green CI/CD builds (3h)
  - Fix failing tests, enable coverage gates
  - Add badges to README
- [ ] **Add Integration Test Suite** (3h)
  - End-to-end user journey (signup → match → message)
  - Safety scenario (report → block → verify enforcement)

#### Day 4-5: Security & Privacy (7-9h)
- [ ] **T052**: PhotoService privacy enforcement (3-4h)
  - Match verification before photo serving
  - Blur non-matched photos
- [ ] **Service-to-Service Auth** (4-5h)
  - Add internal API keys for cross-service calls
  - Update HttpClient configurations

### **Week 2: Performance & Observability** (18-22h)
**Goal**: Optimize queries, add monitoring, prevent scaling issues

#### Day 1-2: Query Optimization (6-8h)
- [ ] **T062**: EF Core performance tuning (6-8h)
  - Add indexes to MatchmakingService (userId, preferences, location)
  - Add indexes to UserService (email, city, age)
  - Use compiled queries for hot paths
  - Add AsNoTracking() for read-only queries
  - Test with 10k user dataset

#### Day 3-4: Observability (8-10h)
- [ ] **T068-T071**: Metrics instrumentation (8-10h)
  - Add OpenTelemetry to all services
  - Track: onboarding completion %, match conversion rate, message latency P95, safety report SLA
  - Configure Prometheus + Grafana dashboards
  - Add structured logging with correlation IDs

#### Day 5: Operational Hardening (4h)
- [ ] **Rate Limiting Enforcement** (2h)
  - Enable YARP rate limiter middleware
  - Test with load testing scripts
- [ ] **Photo Cleanup Job** (2h)
  - Add scheduled job to delete orphaned photos
  - Add cascade delete for profile deletions

### **Week 3: Polish & Launch Prep** (15-18h)
**Goal**: Final testing, documentation, deployment automation

#### Day 1-2: Load Testing (6-8h)
- [ ] **K6 Performance Tests** (4-5h)
  - Simulate 100 concurrent users
  - Test matchmaking under load (1k profiles)
  - Verify rate limits hold under stress
- [ ] **Fix Performance Bottlenecks** (2-3h)
  - Address any issues found in load tests

#### Day 3: Documentation (4-5h)
- [ ] **Operations Runbook** (2-3h)
  - Deployment procedures
  - Monitoring & alerting guide
  - Incident response playbook
- [ ] **API Documentation** (2h)
  - Swagger/OpenAPI complete for all services
  - Usage examples for key endpoints

#### Day 4-5: Deployment Automation (5h)
- [ ] **Docker Compose Production Config** (3h)
  - Separate dev/prod configurations
  - Health checks, restart policies
  - Resource limits
- [ ] **Deployment Scripts** (2h)
  - One-command deployment
  - Database migration automation
  - Rollback procedures

---

## Success Metrics
At the end of 3 weeks, backend should achieve:

### **Reliability**
- ✅ 95%+ test coverage on critical paths
- ✅ Green CI/CD pipeline with no skipped tests
- ✅ All services restart automatically on failure
- ✅ Load tested to 100 concurrent users

### **Security**
- ✅ No dual auth systems (Keycloak only)
- ✅ Service-to-service authentication enforced
- ✅ Photo privacy enforcement active
- ✅ Rate limiting prevents abuse

### **Performance**
- ✅ Database queries optimized with indexes
- ✅ P95 latency < 500ms for all API calls
- ✅ Matchmaking handles 10k user dataset

### **Observability**
- ✅ Centralized logging with correlation IDs
- ✅ Metrics dashboard tracking all success criteria
- ✅ Alerting configured for critical failures

### **Operations**
- ✅ One-command deployment
- ✅ Automated database migrations
- ✅ Runbook with incident procedures
- ✅ Rollback tested and documented

---

## Deferred to Post-MVP (Phase 2)
- Message read receipts UI
- Typing indicators
- Presence/online status
- Advanced photo moderation (ML-based)
- Message reactions/emojis
- Voice/video calling
- Premium features (unlimited swipes, etc.)

---

## Immediate Next Steps (This Week)
**Priority Order**:
1. **T052**: PhotoService privacy (3-4h) - MMP blocker
2. **T007**: Database consolidation (4h) - Operational risk
3. **T008**: Remove AuthService (3h) - Security cleanup
4. **T004**: CI/CD green builds (3h) - Quality gate

**Total**: ~13-15h of focused backend work to reach "shippable" state.

