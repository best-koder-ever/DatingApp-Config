# DatingApp System Architecture Overview

## Purpose

This document provides a high-level overview of the DatingApp microservices architecture, showing how services communicate, data flows, and key integration points. This serves as the foundation for understanding individual feature implementations.

---

## System Components

### Microservices Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        MobileApp[Flutter Mobile App<br/>iOS + Android]
        WebApp[Flutter Web App]
    end
    
    subgraph "Gateway Layer"
        YARP[YARP Gateway<br/>:8080<br/>Routing + CORS]
    end
    
    subgraph "Backend Services"
        User[UserService<br/>:5002<br/>Profiles + Preferences<br/>Account Deletion]
        Matchmaking[MatchmakingService<br/>:5003<br/>Swipe scoring<br/>Match management]
        Photo[photo-service<br/>:5004<br/>Upload + Blur<br/>Storage + Privacy]
        Swipe[swipe-service<br/>:5005<br/>Swipe ingestion]
        Messaging[messaging-service<br/>:5006<br/>SignalR hub<br/>Message persistence]
        Safety[safety-service<br/>:5007<br/>Reports + Blocks]
    end
    
    subgraph "External Services"
        Keycloak[Keycloak<br/>:9090<br/>OIDC Identity Provider]
    end
    
    subgraph "Data Layer"
        UserDB[(UserDB<br/>MySQL 8.0)]
        MatchDB[(MatchmakingDB<br/>MySQL 8.0)]
        PhotoDB[(PhotoDB<br/>MySQL 8.0)]
        SwipeDB[(SwipeDB<br/>MySQL 8.0)]
        MessagingDB[(MessagingDB<br/>MySQL 8.0)]
        SafetyDB[(SafetyDB<br/>MySQL 8.0)]
        KeycloakDB[(KeycloakDB<br/>PostgreSQL)]
        PhotoStorage[("Photo Files<br/>/app/photos")]
    end
    
    MobileApp -->|HTTPS| YARP
    WebApp -->|HTTPS| YARP
    
    YARP -->|/api/userprofiles/**<br/>/api/preferences/**| User
    YARP -->|/api/matchmaking/**| Matchmaking
    YARP -->|/api/photos/**| Photo
    YARP -->|/api/swipes/**| Swipe
    YARP -->|/hub/chat<br/>/api/messages/**| Messaging
    YARP -->|/api/safety/**| Safety
    
    User -->|Keycloak admin API| Keycloak
    
    User -->|HTTP + API Key| Photo
    User -->|HTTP + API Key| Matchmaking
    User -->|HTTP + API Key| Messaging
    User -->|HTTP + API Key| Swipe
    User -->|HTTP + API Key| Safety
    
    Matchmaking -->|HTTP + API Key| User
    Photo -->|HTTP + API Key| Matchmaking
    Swipe -->|HTTP + API Key| Matchmaking
    Messaging -->|HTTP + API Key| Matchmaking
    
    User --> UserDB
    Matchmaking --> MatchDB
    Photo --> PhotoDB
    Photo --> PhotoStorage
    Swipe --> SwipeDB
    Messaging --> MessagingDB
    Safety --> SafetyDB
    Keycloak --> KeycloakDB
    
    style YARP fill:#f9f,stroke:#333,stroke-width:4px
    style Keycloak fill:#fc9,stroke:#333,stroke-width:2px
    style User fill:#9cf,stroke:#333,stroke-width:2px
```

---

## Service Responsibilities

| Service | Port | Primary Responsibilities | Key Entities |
|---------|------|-------------------------|--------------|
| **YARP** | 8080 | API gateway, routing, CORS, load balancing | N/A (stateless) |
| **Keycloak** | 9090 | OpenID Connect provider, user authentication, JWT issuance | Users, Clients, Realms |
| **UserService** | 5002 | User profiles, match preferences, account deletion orchestration | UserProfile, MatchPreferences |
| **MatchmakingService** | 5003 | Match creation, unmatch, consolidated match list | Match, Swipe |
| **photo-service** | 5004 | Photo upload, blur processing, privacy controls | Photo (metadata), file storage |
| **swipe-service** | 5005 | Swipe ingestion, matchmaking hooks | Swipe |
| **messaging-service** | 5006 | Real-time messaging (SignalR), message persistence | Message, Conversation |
| **safety-service** | 5007 | User reports, blocking, content moderation | SafetyReport, BlockedUser |

---

## Communication Patterns

### HTTP REST Communication

```mermaid
sequenceDiagram
    participant Client
    participant YARP
    participant ServiceA as Service A
    participant ServiceB as Service B
    participant DB
    
    Client->>YARP: HTTPS Request<br/>(Bearer token)
    YARP->>ServiceA: Forward with routing
    
    Note over ServiceA: Validate JWT<br/>Parse claims
    
    ServiceA->>ServiceB: Internal HTTP call<br/>via YARP (X-Internal-API-Key)
    Note over ServiceB: Validate API Key<br/>Log service call
    ServiceB->>DB: Query data
    DB-->>ServiceB: Return data
    ServiceB-->>ServiceA: Return result
    
    ServiceA->>DB: Update data
    ServiceA-->>YARP: JSON response
    YARP-->>Client: Return to client
```

**Key Principles:**
- All external requests go through YARP gateway
- Service-to-service calls route through YARP (e.g., `http://dejting-yarp:8080`)
- Internal endpoints protected with `[RequireInternalApiKey]` attribute (API key validation)
- Authorization via JWT claims (Keycloak-issued tokens) for client requests
- Service-to-service auth via internal API keys (X-Internal-API-Key header)

### SignalR Real-Time Communication

```mermaid
sequenceDiagram
    participant ClientA as User A Client
    participant YARP
    participant MessagingHub as messaging-service<br/>SignalR Hub
    participant DB as MessagingDB
    participant ClientB as User B Client
    
    ClientA->>YARP: WebSocket connect<br/>/hub/chat
    YARP->>MessagingHub: Establish connection
    MessagingHub-->>ClientA: Connected
    
    ClientB->>YARP: WebSocket connect
    YARP->>MessagingHub: Establish connection
    MessagingHub-->>ClientB: Connected
    
    ClientA->>MessagingHub: SendMessage(userId, content)
    MessagingHub->>DB: INSERT Message
    MessagingHub-->>ClientB: ReceiveMessage(from, content)
    MessagingHub-->>ClientA: MessageSent confirmation
```

**Key Principles:**
- SignalR hub hosted in messaging-service
- WebSocket connections through YARP (`/hub/chat`)
- Messages persisted to database for offline users
- Connection groups by userId for targeted delivery

---

## Data Flow Examples

### User Registration Flow

```mermaid
sequenceDiagram
    participant Client
    participant YARP
    participant Keycloak
    participant UserService
    
    Client->>Keycloak: Register (email, password)
    Keycloak-->>Client: User created (Guid userId)
    
    Client->>Keycloak: Login (username, password)
    Keycloak-->>Client: JWT access token + refresh token
    
    Client->>YARP: POST /api/userprofiles<br/>(Bearer token, profile data)
    YARP->>UserService: Forward
    UserService->>UserService: Create UserProfile<br/>(extract userId from JWT)
    UserService-->>Client: Profile created
```

### Match Creation Flow

```mermaid
sequenceDiagram
    participant ClientA as User A Client
    participant YARP
    participant SwipeService
    participant MatchmakingService
    participant ClientB as User B Client
    participant MessagingHub
    
    ClientA->>YARP: POST /api/swipes<br/>{targetId: B, isLike: true}
    YARP->>SwipeService: Store swipe
    SwipeService->>MatchmakingService: Check for mutual swipe
    
    alt Mutual swipe exists
        MatchmakingService->>MatchmakingService: Create Match entity
        MatchmakingService-->>ClientA: Match notification
        
        MatchmakingService->>MessagingHub: Notify User B via SignalR
        MessagingHub-->>ClientB: Match notification
    else No mutual swipe yet
        SwipeService-->>ClientA: Swipe recorded
    end
```

### Account Deletion Cascade Flow

```mermaid
graph LR
    Client[Client DELETE request]
    Controller[UserProfilesController]
    ADS[AccountDeletionService]
    
    Client --> Controller
    Controller -->|Authorize| Controller
    Controller --> ADS
    
    ADS -->|1. DELETE photos| PhotoService[photo-service]
    ADS -->|2. DELETE matches| MatchService[MatchmakingService]
    ADS -->|3. DELETE messages| MessageService[messaging-service]
    ADS -->|4. DELETE swipes| SwipeService[swipe-service]
    ADS -->|5. DELETE safety data| SafetyService[safety-service]
    ADS -->|6. DELETE preferences| UserDB[(UserDB)]
    ADS -->|7. Soft delete profile| UserDB
    
    ADS -->|Aggregated summary| Controller
    Controller -->|AccountDeletionResult| Client
    
    style ADS fill:#f96,stroke:#333,stroke-width:4px
```

---

## ID Strategy

### Dual ID System

The system uses two types of user identifiers:

| ID Type | Services Using It | Format | Source | Example |
|---------|------------------|--------|--------|---------|
| **UserProfile.Id** | photo-service, MatchmakingService, swipe-service | `int` (auto-increment) | UserService database | `123` |
| **UserId** | messaging-service, safety-service, AuthService | `Guid` (string) | Keycloak | `"a7f3e8c2-4b1a-..."` |

**Why Two IDs?**
- Legacy services (photo, matchmaking, swipe) built before Keycloak integration used auto-increment IDs
- Newer services (messaging, safety) built with Keycloak from start use standard OIDC `sub` claim (Guid)
- Migration to single ID strategy deferred to avoid breaking changes

**How Services Map Between Them:**
- UserProfile entity stores both: `Id` (int, PK) and `UserId` (Guid, indexed)
- AccountDeletionService retrieves both and uses appropriate ID per service

---

## Security Model

```mermaid
graph TB
    User[User Login]
    Keycloak[Keycloak OIDC]
    JWT[JWT Token<br/>Claims: userId, email, roles]
    
    User -->|1. Authenticate| Keycloak
    Keycloak -->|2. Issue token| JWT
    
    JWT -->|3. Attach to requests| APIGateway[YARP Gateway]
    APIGateway -->|4. Forward| Services[Backend Services]
    
    Services -->|5a. Validate signature| Services
    Services -->|5b. Parse claims| Services
    Services -->|5c. Authorize action| Services
    
    subgraph "Authorization Patterns"
        ClaimCheck["JWT Claim Check<br/>(User owns resource)"]
        RoleCheck["Role-Based Check<br/>(Admin, Moderator)"]
        ResourceOwnership["Resource Ownership<br/>(Match participant)"]
    end
    
    Services --> ClaimCheck
    Services --> RoleCheck
    Services --> ResourceOwnership
    
    style Keycloak fill:#fc9,stroke:#333,stroke-width:2px
    style JWT fill:#9f9,stroke:#333,stroke-width:2px
```

**Key Security Principles:**
1. **All client requests require JWT** (except anonymized public endpoints)
2. **Service-to-service calls use internal API keys** (X-Internal-API-Key header)
3. **UserId extracted from claims** (`ClaimTypes.NameIdentifier`)
4. **Resource ownership checks** (e.g., user can only delete own account)
5. **Keycloak as single source of truth** for authentication

### Service-to-Service Authentication

**Internal API Key System** (implemented 2026-01-26):

All microservices now use internal API key authentication to secure cross-service HTTP communication. This prevents unauthorized access to internal endpoints and provides audit trails for service-to-service calls.

**Architecture Components:**

```mermaid
graph LR
    ServiceA[Service A<br/>PhotoService]
    Handler[InternalApiKeyAuthHandler]
    YARP[YARP Gateway]
    Filter[InternalApiKeyAuthFilter]
    ServiceB[Service B<br/>MatchmakingService]
    
    ServiceA -->|Outgoing Request| Handler
    Handler -->|Add X-Internal-API-Key| YARP
    YARP -->|Route to Service B| Filter
    Filter -->|Validate API Key| ServiceB
    
    style Handler fill:#9f9,stroke:#333,stroke-width:2px
    style Filter fill:#f99,stroke:#333,stroke-width:2px
```

**Components:**
- **InternalApiKeyAuthHandler** (`Common/InternalApiKeyAuthHandler.cs`): DelegatingHandler that adds `X-Internal-API-Key` header to outgoing HttpClient requests
- **InternalApiKeyAuthFilter** (`Common/InternalApiKeyAuthFilter.cs`): Authorization filter that validates incoming internal API requests
- **[RequireInternalApiKey]** Attribute: Apply to controllers/actions that should only accept service-to-service calls

**Security Model:**
- **Each service has unique API key for outgoing requests** (`InternalAuth:ApiKey` in appsettings)
- **Each service validates comma-separated trusted keys** (`InternalAuth:ValidApiKeys` from other services)
- **DEV mode**: Allows requests if `ValidApiKeys` empty (gradual rollout, logs warnings)
- **PROD mode** (TODO): Strict validation, environment variables, key rotation

**Service Communication Matrix:**

| Service | Outgoing Calls (adds API key to) | Incoming Calls (validates API key from) |
|---------|-----------------------------------|------------------------------------------|
| PhotoService | MatchmakingService, SafetyService | MessagingService, UserService |
| MatchmakingService | UserService, SafetyService | PhotoService, MessagingService, SwipeService |
| MessagingService | SafetyService, MatchmakingService | PhotoService |
| SwipeService | MatchmakingService | None currently |
| UserService | None currently | MatchmakingService |

**Configuration Example** (appsettings.Development.json - gitignored):
```json
{
  "InternalAuth": {
    "ApiKey": "photo-service-internal-key-dev-only",
    "ValidApiKeys": "matchmaking-service-internal-key-dev-only,safety-service-internal-key-dev-only,user-service-internal-key-dev-only"
  }
}
```

**Usage:**
```csharp
// Protecting an internal endpoint
[ApiController]
[Route("api/internal/matches")]
public class InternalMatchesController : ControllerBase
{
    [HttpGet("check/{userId1}/{userId2}")]
    [RequireInternalApiKey]  // Only services with valid API keys can call
    public async Task<ActionResult<bool>> CheckMatch(string userId1, string userId2)
    {
        // Match verification logic
    }
}
```

**See Also:** [SERVICE_TO_SERVICE_AUTH.md](../../../SERVICE_TO_SERVICE_AUTH.md) for complete implementation details, troubleshooting, and migration guide.

---

## Database Schema Relationships

```mermaid
erDiagram
    UserProfile ||--o{ Photo : has
    UserProfile ||--o{ Match : participates_as_user1
    UserProfile ||--o{ Match : participates_as_user2
    UserProfile ||--o{ Swipe : creates
    UserProfile ||--o{ Message : sends
    UserProfile ||--o{ SafetyReport : files
    UserProfile ||--o{ BlockedUser : blocks
    UserProfile ||--|| MatchPreferences : configures
    
    Match ||--o{ Message : contains
    
    UserProfile {
        int Id PK
        Guid UserId "Keycloak"
        string Email
        string Name
        int Age
        string Gender
        string City
        string Bio
        bool IsActive
        DateTime CreatedAt
        DateTime UpdatedAt
    }
    
    MatchPreferences {
        int Id PK
        int UserProfileId FK
        int MinAge
        int MaxAge
        string PreferredGender
        int MaxDistance
    }
    
    Photo {
        int Id PK
        int UserId FK
        string StoredFileName
        string BlurredFileName
        bool IsPrimary
        bool IsVerified
    }
    
    Match {
        int Id PK
        int User1Id FK
        int User2Id FK
        DateTime MatchedAt
        bool IsActive
        DateTime UnmatchedAt
        string UnmatchReason
    }
    
    Swipe {
        int Id PK
        int UserId FK
        int TargetUserId FK
        bool IsLike
        DateTime SwipedAt
    }
    
    Message {
        int Id PK
        string SenderId FK "Keycloak Guid"
        string ReceiverId FK "Keycloak Guid"
        int MatchId FK
        string Content
        DateTime SentAt
        bool IsRead
    }
    
    SafetyReport {
        int Id PK
        string ReporterId FK
        string ReportedUserId FK
        string Reason
        DateTime ReportedAt
    }
    
    BlockedUser {
        int Id PK
        string BlockerId FK
        string BlockedUserId FK
        DateTime BlockedAt
    }
```

---

## Technology Stack

### Backend
- **.NET 8**: All microservices use ASP.NET Core 8
- **Entity Framework Core 8**: ORM for database access with Pomelo MySQL provider
- **MySQL 8.0**: Primary database for all backend services (UserService, MatchmakingService, photo-service, swipe-service, messaging-service, safety-service)
- **PostgreSQL**: Identity database for Keycloak only
- **SignalR**: Real-time WebSocket communication
- **YARP**: Reverse proxy and API gateway
- **Keycloak**: OpenID Connect identity provider

### Frontend
- **Flutter 3.32.1**: Cross-platform mobile + web client
- **Dart 3.5**: Programming language
- **Riverpod**: State management (lite pattern)

### Infrastructure
- **Docker Compose**: Local development orchestration
- **Bash scripts**: dev-start.sh, dev-stop.sh automation

### Image Processing
- **ImageSharp**: Photo processing and blur
- **OpenCvSharp**: Advanced blur algorithms (future)

### Machine Learning
- **ML.NET**: Match scoring algorithms (planned)

---

## Deployment Architecture

```mermaid
graph TB
    subgraph "Development Environment"
        Dev[Developer Workstation]
        DevCompose[Docker Compose<br/>infrastructure + services]
    end
    
    subgraph "Docker Network: dating-app-network"
        YARP_Dev[dejting-yarp]
        KC_Dev[keycloak]
        MySQL_Dev[mysql-shared<br/>+ per-service DBs]
        Postgres_Dev[postgres<br/>Keycloak only]
        User_Dev[UserService]
        Match_Dev[MatchmakingService]
        Photo_Dev[photo-service]
        Swipe_Dev[swipe-service]
        Msg_Dev[messaging-service]
        Safety_Dev[safety-service]
    end
    
    Dev -->|docker-compose up| DevCompose
    DevCompose --> YARP_Dev
    DevCompose --> KC_Dev
    DevCompose --> MySQL_Dev
    DevCompose --> Postgres_Dev
    
    YARP_Dev --> User_Dev
    YARP_Dev --> Match_Dev
    YARP_Dev --> Photo_Dev
    YARP_Dev --> Swipe_Dev
    YARP_Dev --> Msg_Dev
    YARP_Dev --> Safety_Dev
    
    User_Dev --> MySQL_Dev
    Match_Dev --> MySQL_Dev
    Photo_Dev --> MySQL_Dev
    Swipe_Dev --> MySQL_Dev
    Msg_Dev --> MySQL_Dev
    Safety_Dev --> MySQL_Dev
    KC_Dev --> Postgres_Dev
    
    style YARP_Dev fill:#f9f,stroke:#333,stroke-width:2px
    style KC_Dev fill:#fc9,stroke:#333,stroke-width:2px
```

**Container Ports:**
- YARP: 8080 (external), internal routing
- Keycloak: 9090 (external), 8080 (internal)
- Services: 5002-5007 (internal only, accessed via YARP)
- MySQL: 3306 (internal only), per-service databases on ports 3311-3315
- PostgreSQL: 5432 (internal only, Keycloak)

**Database Port Mapping:**
- 3311: photo-service-db
- 3312: matchmaking-service-db
- 3313: messaging-service-db
- 3314: swipe-service-db
- 3315: user-service-db

---

## Future Architecture Enhancements

### Planned Improvements
1. **Message Queue (RabbitMQ/Kafka)**: Async event-driven architecture for swipes, matches, notifications
2. **Redis Cache**: Cache UserProfiles, match lists, swipe history
3. **Elasticsearch**: Full-text search for profiles, messages
4. **CDN**: Offload photo delivery to Cloudflare/AWS CloudFront
5. **Kubernetes**: Replace Docker Compose for production
6. **API Versioning**: Support /v1/, /v2/ endpoints for breaking changes
7. **Circuit Breaker**: Polly policies for resilient service-to-service calls
8. **Distributed Tracing**: OpenTelemetry for request tracking across services

### Scalability Considerations
- **Horizontal Scaling**: All services stateless (except SignalR, needs sticky sessions)
- **Database Sharding**: Partition UserProfiles by geographic region
- **Read Replicas**: Offload read-heavy operations (match list, profiles)
- **CQRS**: Separate read/write models for high-traffic features

---

## Related Documentation

- [Account Deletion Feature](./account-deletion.md) - Cascade deletion across 6 services
- [Unmatch Feature](./unmatch.md) - Match lifecycle and soft delete
- [Consolidated Match List](./match-list.md) - Data aggregation pattern
- [API Specification](../contracts/api-spec.md) - Complete REST API reference
- [SignalR Specification](../contracts/signalr-spec.md) - Real-time messaging protocol
- [RUNBOOK.md](../../../RUNBOOK.md) - Operational commands and workflows

---

**Last Updated:** 2026-01-20  
**Version:** 1.0 - MVP Foundation  
**Maintainers:** Backend Team, Architecture Group
