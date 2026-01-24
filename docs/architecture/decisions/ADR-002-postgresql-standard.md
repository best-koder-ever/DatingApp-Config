# ADR-002: Standardize Database Engine

**Status**: Proposed
**Date**: 2026-01-24

## Context
Currently mixing PostgreSQL (photo, swipe, matchmaking) and MySQL 
(user, messaging, auth) without clear strategy.

## Decision
Standardize on **PostgreSQL** for all services.

## Rationale
- Better JSON support (for future flexible schemas)
- Single DB engine to maintain
- Superior full-text search (for future search features)
- Open source with excellent EF Core support

## Consequences
**Positive**:
- Simplified ops (one DB to backup, monitor)
- Consistent migration patterns

**Negative**:
- Migration effort for 3 services
- Team must learn PostgreSQL (already know MySQL)

## Implementation
See T007 in tasks.md (4h estimate)
