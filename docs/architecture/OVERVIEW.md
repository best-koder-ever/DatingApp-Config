# Architecture Overview

**Last Updated**: 2026-01-24  
**Status**: As-Built (reflects current implementation)

---

## 🏗️ System Context (C4 Level 1)

```mermaid
C4Context
    title DatingApp - System Context Diagram
    
    Person(user, "Dating App User", "Someone looking for matches")
    System(datingapp, "DatingApp", "Microservices-based dating platform")
    System_Ext(keycloak, "Keycloak", "OIDC authentication")
    System_Ext(email, "Email Service", "Verification emails")
    System_Ext(storage, "Blob Storage", "Photo storage")
    
    Rel(user, datingapp, "Uses", "HTTPS/WSS")
    Rel(datingapp, keycloak, "Authenticates with", "OIDC")
    Rel(datingapp, email, "Sends via", "SMTP")
    Rel(datingapp, storage, "Stores photos", "S3/Azure")
    Rel(keycloak, email, "Sends verification", "SMTP")
```

---

## 🧩 Container Diagram (C4 Level 2)

```mermaid
graph TB
    subgraph "Client Layer"
        Flutter[Flutter Mobile/Web App]
    end
    
    subgraph "API Gateway"
        YARP[YARP Gateway<br/>Port 8080]
    end
    
    subgraph "Microservices"
        User[UserService<br/>Port 8082]
        Match[MatchmakingService<br/>Port 8083]
        Swipe[swipe-service<br/>Port 8084]
        Photo[photo-service<br/>Port 8085]
        Message[messaging-service<br/>Port 8086]
    end
    
    subgraph "Identity"
        Keycloak[Keycloak<br/>Port 8090]
    end
    
    subgraph "Data Layer"
        UserDB[(UserService DB<br/>MySQL:3308)]
        MatchDB[(Matchmaking DB<br/>PostgreSQL)]
        SwipeDB[(Swipe DB<br/>PostgreSQL)]
        PhotoDB[(Photo DB<br/>PostgreSQL:5432)]
        MessageDB[(Message DB<br/>MySQL)]
    end
    
    Flutter -->|HTTPS| YARP
    YARP --> User
    YARP --> Match
    YARP --> Swipe
    YARP --> Photo
    YARP -->|WebSocket| Message
    
    Flutter -->|OIDC| Keycloak
    User --> Keycloak
    
    User --> UserDB
    Match --> MatchDB
    Swipe --> SwipeDB
    Photo --> PhotoDB
    Message --> MessageDB
    
    Match -.queries.-> User
    Swipe -.triggers.-> Match
    
    style Flutter fill:#4FC3F7
    style YARP fill:#FF9800
    style Keycloak fill:#F44336
```

---

## 📡 Service Responsibilities

| Service | Purpose | Database | Key APIs |
|---------|---------|----------|----------|
| **UserService** | Profile CRUD, verification, demographics | MySQL:3308 | GET/POST/PUT `/api/UserProfiles` |
| **MatchmakingService** | Compatibility scoring, candidate selection | PostgreSQL | POST `/api/Matchmaking/find-matches` |
| **swipe-service** | Swipe recording, mutual match detection | PostgreSQL | POST `/api/Swipes`, GET `/api/Swipes/matches` |
| **photo-service** | Upload, moderation, blur, privacy | PostgreSQL:5432 | POST `/api/Photos`, PUT `/api/Photos/{id}/privacy` |
| **messaging-service** | SignalR chat, delivery, moderation | MySQL | SignalR hub `/messagingHub` |
| **dejting-yarp** | API gateway, routing, rate limiting | None | Routes all `/api/*` traffic |
| **Keycloak** | Authentication, OIDC, user management | PostgreSQL | `/realms/dating/protocol/openid-connect` |

---

## 🔄 Key Workflows

### 1. User Registration

```mermaid
sequenceDiagram
    actor User
    participant Flutter
    participant YARP
    participant Keycloak
    participant UserService
    participant Email
    
    User->>Flutter: Enter email/password
    Flutter->>Keycloak: Register user
    Keycloak->>Email: Send verification link
    User->>Email: Click link
    Email->>Keycloak: Verify email
    Keycloak->>Flutter: Redirect with token
    Flutter->>YARP: Create profile (JWT)
    YARP->>UserService: POST /api/UserProfiles
    UserService-->>Flutter: Profile created
```

### 2. Match Discovery (Swipe Loop)

```mermaid
sequenceDiagram
    actor User
    participant Flutter
    participant YARP
    participant Match as Matchmaking
    participant Swipe as SwipeService
    participant User2
    
    User->>Flutter: Open Discover tab
    Flutter->>YARP: GET /api/Matchmaking/find-matches
    YARP->>Match: Find candidates
    Match-->>Flutter: Return 20 scored candidates
    User->>Flutter: Swipe right on User2
    Flutter->>YARP: POST /api/Swipes
    YARP->>Swipe: Record swipe
    Swipe->>Swipe: Check if User2 swiped User
    alt Mutual Match
        Swipe->>Match: Create match
        Match-->>Flutter: Match created
        Flutter->>User: "It's a Match!" 🎉
        Match->>User2: Push notification
    end
```

### 3. Photo Upload with Privacy

```mermaid
sequenceDiagram
    actor User
    participant Flutter
    participant YARP
    participant Photo
    participant ML as ML.NET Moderator
    participant Storage
    
    User->>Flutter: Upload photo
    Flutter->>YARP: POST /api/Photos
    YARP->>Photo: Process upload
    Photo->>ML: Scan for inappropriate content
    ML-->>Photo: Approved/Rejected
    Photo->>Storage: Save original
    Photo->>Photo: Generate blur version
    Photo->>Storage: Save blurred
    Photo-->>Flutter: Photo ID + URLs
    User->>Flutter: Set privacy to "MatchOnly"
    Flutter->>Photo: PUT /api/Photos/{id}/privacy
    Photo-->>Flutter: Privacy updated
```

---

## 🗄️ Data Model (Simplified)

```mermaid
erDiagram
    UserProfile ||--o{ Photo : has
    UserProfile ||--o{ Match : participates_in
    UserProfile ||--o{ Swipe : makes
    Match ||--o{ Message : contains
    
    UserProfile {
        uuid Id PK
        uuid KeycloakUserId FK
        string DisplayName
        int Age
        geography Location
        string OnboardingStatus
    }
    
    Photo {
        uuid Id PK
        uuid UserId FK
        string Url
        string PrivacyLevel
        string ModerationStatus
        boolean IsPrimary
    }
    
    Match {
        uuid Id PK
        uuid User1Id FK
        uuid User2Id FK
        datetime CreatedAt
        string Status
    }
    
    Swipe {
        uuid Id PK
        uuid SwiperId FK
        uuid SwipedUserId FK
        string Action
        datetime CreatedAt
    }
    
    Message {
        uuid Id PK
        uuid MatchId FK
        uuid SenderId FK  
        string Content
        datetime SentAt
        boolean IsRead
    }
```

---

## 🔒 Security Architecture

### Authentication Flow
1. **Keycloak OIDC** - All auth via OpenID Connect
2. **JWT Tokens** - Stateless authentication
3. **YARP Middleware** - Token validation at gateway
4. **Service-to-Service** - No authentication (internal network trust)

### Privacy Controls
- **Photo Privacy Levels**: Public, Private, MatchOnly, VIP
- **Blur Enforcement**: Non-matches see blurred photos
- **Match-Only Messaging**: Can only message mutual matches
- **Block/Report**: (Planned - US4)

---

## 📈 Scalability Considerations

### Current (MVP)
- **Monolithic deployment** via Docker Compose
- **Single instance** per service
- **No caching** (direct DB queries)
- **No message queue** (synchronous processing)

### Future (Post-MVP)
- **Kubernetes** deployment
- **Horizontal scaling** for UserService, Matchmaking
- **Redis cache** for candidate queues
- **RabbitMQ** for async match notifications
- **CDN** for photo delivery

---

## 🔗 Related Documentation

- **[Feature Catalog](../features/README.md)** - What's built
- **[API Reference](../api/README.md)** - Endpoint docs
- **[Data Model](../../specs/001-mvp-foundation/data-model.md)** - Detailed schema
- **[Architecture Decisions](decisions/)** - ADRs

---

*Generated from actual codebase as of 2026-01-24*
