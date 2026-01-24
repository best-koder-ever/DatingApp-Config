# ADR-001: Migrate Authentication to Keycloak

**Status**: Accepted (Implemented 2025-10-22)
**Deciders**: Solo dev

## Context
Dual auth system (AuthService + Keycloak) caused confusion.
Keycloak provides enterprise-grade OIDC with better security.

## Decision
- Retire AuthService
- All auth flows through Keycloak
- Services validate JWT tokens from Keycloak

## Consequences
**Positive**:
- Standard OIDC protocol
- Email verification built-in
- SSO-ready for future integrations

**Negative**:
- Learning curve for Keycloak admin
- More complex local dev setup

## Implementation
- Completed: October 22, 2025
- See: T008 in tasks.md for cleanup
