# P0 Features Documentation

This directory contains comprehensive documentation for all P0 (Priority 0) features implemented in the MVP foundation. Each feature follows the 4-layer SpecKit documentation approach with Mermaid diagrams for visual understanding.

## Documentation Layers

1. **Feature Specification** - User stories, acceptance criteria, business context
2. **Implementation Plan** - Technical approach, architecture diagrams, component design
3. **API Contracts** - REST endpoints, request/response formats, data models
4. **Architecture Decisions** - ADRs (Architecture Decision Records) for significant technical choices

## System Overview

- **[System Architecture](./system-architecture.md)** - High-level overview of microservices architecture, communication patterns, data flows, security model, and deployment architecture

## Completed P0 Features

### Core Functionality
- **[Account Deletion](./account-deletion.md)** - GDPR-compliant cascade deletion across 6 services with soft/hard delete modes
- **[Unmatch Functionality](./unmatch.md)** - Users can unmatch with optional reason tracking and state management
- **[Consolidated Match List](./match-list.md)** - Single endpoint for user matches with batch profile fetching

### Safety & Privacy
- **[User Blocking](./user-blocking.md)** - ✅ **PRODUCTION READY** - Complete blocking system with Flutter UI, safety-service backend, and cross-service enforcement (Jan 2026)

## Proposed Week 3 Features (Launch Prep)

### User Experience & Support
- **[Account Pause / Snooze Mode](./account-pause.md)** - ⚠️ **HIGH PRIORITY** - Table stakes feature allowing users to temporarily hide profile from discovery (~15h)
- **[Feedback & Customer Support](./feedback-support.md)** - Essential for beta launch, provides in-app support and bug reporting (~10h)

## Mermaid Diagram Index

### Architecture Diagrams
- **System Components**: Full microservices topology ([system-architecture.md](./system-architecture.md))
- **Account Deletion Cascade**: Service orchestration pattern ([account-deletion.md](./account-deletion.md))
- **Match List Aggregation**: Data consolidation flow ([match-list.md](./match-list.md))

### Sequence Diagrams
- **User Registration Flow**: Keycloak integration ([system-architecture.md](./system-architecture.md))
- **Match Creation Flow**: Swipe to match pipeline ([system-architecture.md](./system-architecture.md))
- **Account Deletion Sequence**: Cascade deletion steps ([account-deletion.md](./account-deletion.md))
- **Unmatch Request Flow**: State transitions ([unmatch.md](./unmatch.md))
- **Consolidated Match List**: Batch fetching sequence ([match-list.md](./match-list.md))

### State Diagrams
- **Match Lifecycle**: Active → Unmatched transitions ([unmatch.md](./unmatch.md))

### ER Diagrams
- **Complete Database Schema**: All entities and relationships ([system-architecture.md](./system-architecture.md))
- **Account Deletion Model**: Cascade relationships ([account-deletion.md](./account-deletion.md))
- **Unmatch Data Model**: Match entity fields ([unmatch.md](./unmatch.md))
- **Match List Data Model**: Aggregation sources ([match-list.md](./match-list.md))

## How to Use This Documentation

### For Developers
1. Start with [system-architecture.md](./system-architecture.md) to understand overall system design
2. Review feature-specific docs for implementation details
3. Check ADRs (Layer 4) to understand architectural constraints and decisions
4. Use Mermaid diagrams for visual understanding of flows

### For Product Managers
- Focus on **Layer 1** (Feature Specification) for user stories and business context
- Review **Layer 3** (API Contracts) for integration planning and external API documentation

### For AI Agents
- Scan this README for feature index and documentation structure
- Read full 4-layer docs for complete implementation context
- Use Mermaid diagrams to understand request flows and data relationships
- Check ADRs for architectural constraints before proposing changes

### For QA/Testing
- Use Acceptance Criteria (Layer 1) as basis for test cases
- Reference API contracts (Layer 3) for integration test scenarios
- Check "Testing Status" sections in each doc for coverage gaps

## P1 Roadmap & Priorities

**Complete P1 Review**: [P1_ROADMAP_REVIEW.md](../../../P1_ROADMAP_REVIEW.md)

### P1 Feature Documentation (In Progress)
- **[P1-008: OpenAPI/Swagger](./p1-swagger-openapi.md)** - Complete API documentation for all services (Phase 1, Week 1)
- **P1-006: Rate Limiting** - Security and abuse prevention (Planned)
- **P1-001: Health Metrics** - Matchmaking operational visibility (Planned)
- **P1-003: Push Notifications** - Mobile engagement via APNS/FCM (Planned)
- **P1-009: Integration Tests** - Critical path coverage (Planned)

### Validation Summary
- ❌ **Message REST Fallback**: Already implemented (REST endpoints exist)
- ⚠️ **Queue Stats**: Refined into P1-001 (Health Metrics)
- ✅ **Notification Service**: Scoped to P1-003 (Mobile Push)

## Future Documentation Needs

The following features have been implemented but lack comprehensive SpecKit documentation:

- Safety reporting & moderation queue (blocks documented, reports deferred to Phase 2)
- Preferences CRUD operations
- Photo upload and blur pipeline
- SignalR messaging implementation
- Swipe ingestion and processing
- Match scoring algorithms (ML.NET integration)

## Related Documentation

- [RUNBOOK.md](../../../RUNBOOK.md) - Operational commands and development workflows
- [API Specification](../contracts/api-spec.md) - Complete REST API reference
- [SignalR Specification](../contracts/signalr-spec.md) - Real-time messaging protocol
- [Data Model](../data-model.md) - Entity definitions and relationships
- [Implementation Plan](../plan.md) - MVP implementation roadmap
- [Feature Backlog](../FEATURE_BACKLOG.md) - Future enhancements and competitive gaps ⭐ NEW
- [Industry Research Guide](../INDUSTRY_RESEARCH_GUIDE.md) - How to identify table stakes features and research dating app standards ⭐ NEW
