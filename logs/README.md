# Observability & Monitoring

Comprehensive logging, tracing, and metrics for DatingApp microservices.

## Overview

The DatingApp architecture uses:
- **Serilog** - Structured logging with JSON output
- **OpenTelemetry** - Distributed tracing and metrics
- **ASP.NET Core Logging** - Standard ILogger integration

## Stack

### Logging: Serilog

**Configuration**: All services use Serilog with structured logging

**Log Levels**:
- `Verbose` - Detailed trace information (dev only)
- `Debug` - Diagnostic information
- `Information` - General flow (default minimum)
- `Warning` - Unexpected behavior that doesn't stop execution
- `Error` - Errors and exceptions
- `Fatal` - Critical failures requiring immediate attention

**Output Sinks**:
1. **Console** (Development) - Colored, readable format
2. **File** (Production) - JSON structured logs at `logs/app-.txt`
3. **Seq** (Optional) - Centralized log aggregation

### Tracing: OpenTelemetry

**Enabled Activities**:
- HTTP requests (incoming/outgoing)
- Database operations (Entity Framework)
- Service-to-service calls
- Custom spans for business operations

**Trace Propagation**: W3C Trace Context standard
- `traceparent` header propagated across service boundaries
- Correlation IDs track requests end-to-end

**Exporters**:
- Console (Development)
- OTLP (Production) - OpenTelemetry Protocol to Jaeger/Tempo

### Metrics: OpenTelemetry

**Collected Metrics**:
- HTTP request duration
- Request count by endpoint
- Active request count
- Response status code distribution
- Custom business metrics per service

**Exporters**:
- Console (Development)
- Prometheus (Production) - `/metrics` endpoint

## Service-Specific Logging

### UserService

**Key Events** :
```csharp
Log.Information("User profile created: {UserId}", userId);
Log.Warning("Failed login attempt: {Email}", email);
Log.Error(ex, "Profile update failed: {UserId}", userId);
```

**Metrics**:
- `user.registrations` - New user count
- `user.logins` - Successful logins
- `user.profile.updates` - Profile modification count

**Critical Paths**:
1. User registration → JWT issuance
2. Profile photo upload → S3 storage
3. Profile updates → Database write

### MatchmakingService

**Key Events**:
```csharp
Log.Information("Compatibility score calculated: {UserId1} -> {UserId2} = {Score}", u1, u2, score);
Log.Warning("No candidates found for user: {UserId}", userId);
Log.Error(ex, "Scoring algorithm failure: {UserId}", userId);
```

**Metrics**:
- `matchmaking.candidates.generated` - Candidates produced per request
- `matchmaking.scoring.duration` - Algorithm execution time
- `matchmaking.cache.hits` - Candidate cache effectiveness

**Critical Paths**:
1. Get candidates → Scoring → Cache update
2. Match creation → Mutual like detected
3. Daily queue refresh → Batch scoring

### SwipeService

**Key Events**:
```csharp
Log.Information("Swipe processed: {UserId} -> {TargetId} = {Direction}", userId, targetId, direction);
Log.Information("Match created: {UserId1} <-> {UserId2}", u1, u2);
Log.Warning("Swipe on unavailable candidate: {TargetId}", targetId);
```

**Metrics**:
- `swipe.received` - Total swipes
- `swipe.likes` - Right swipes
- `swipe.passes` - Left swipes
- `swipe.matches` - Mutual matches created

**Critical Paths**:
1. Swipe ingestion → Match check → Notification
2. Match creation → Messaging room creation

### PhotoService

**Key Events**:
```csharp
Log.Information("Photo uploaded: {PhotoId} for user {UserId}", photoId, userId);
Log.Warning("Moderation flagged photo: {PhotoId} - {Reason}", photoId, reason);
Log.Error(ex, "Photo processing failed: {PhotoId}", photoId);
```

**Metrics**:
- `photo.uploads` - Photos uploaded
- `photo.moderation.queue` - Photos awaiting review
- `photo.processing.duration` - Resize/blur time

**Critical Paths**:
1. Upload → Resize/blur → S3 storage → Database
2. Moderation → Safety check → Approval/rejection

### MessagingService

**Key Events**:
```csharp
Log.Information("Message sent: {MessageId} from {SenderId} to {ReceiverId}", msgId, sender, receiver);
Log.Warning("Message to unmatched user blocked: {SenderId} -> {ReceiverId}", sender, receiver);
Log.Error(ex, "SignalR connection failed: {UserId}", userId);
```

**Metrics**:
- `messages.sent` - Total messages
- `messages.delivered` - Successfully delivered
- `signalr.connections` - Active WebSocket connections

**Critical Paths**:
1. Message send → Validation → Delivery → ACK
2. SignalR connection → Room subscription

## Correlation & Tracing

### Correlation IDs

Every request generates a unique correlation ID:
- Captured in `CorrelationId` property
- Propagated via HTTP headers
- Included in all log entries

**Example**:
```
[2026-01-29 14:23:45.123] [Information] [CorrelationId: 7f8e9d3c] User login successful: user@example.com
```

### Distributed Tracing

**Trace Structure**:
```
Trace ID: 4bf92f3577b34da6a3ce929d0e0e4736
└─ Span: POST /api/swipes
   ├─ Span: HTTP GET http://matchmaking:8083/api/candidates/{userId}
   │  └─ Span: SQL SELECT * FROM Candidates
   ├─ Span: SQL INSERT INTO Swipes
   └─ Span: HTTP POST http://messaging:8086/api/rooms (if match)
```

**Span Attributes**:
- `http.method` - HTTP verb
- `http.url` - Full URL
- `http.status_code` - Response code
- `user.id` - Authenticated user
- `db.system` - Database type
- Custom business attributes

## Monitoring Dashboards

### Recommended Dashboards

#### 1. Service Health Dashboard

**Metrics**:
- HTTP request rate (req/sec)
- HTTP error rate (4xx, 5xx %)
- Response time percentiles (p50, p95, p99)
- Active connections
- Memory usage
- CPU usage

**Alerts**:
- Error rate > 5% for 5 minutes
- p99 latency > 3s for 5 minutes
- Service down for 1 minute

#### 2. User Journey Dashboard

**Flows to Monitor**:
1. **Registration→Profile→First Match**
   - Registration count (per hour)
   - Profile completion rate
   - Time to first match (distribution)

2. **Swipe→Match→Message**
   - Swipes per active user
   - Match rate (% of swipes)
   - Messages per match

3. **Photo Upload→Moderation→Approval**
   - Upload success rate
   - Moderation queue length
   - Average moderation time

**Alerts**:
- Registration flow error rate > 10%
- Match creation failure > 5%
- Photo moderation queue > 100 items

#### 3. Business Metrics Dashboard

**KPIs**:
- Daily Active Users (DAU)
- New registrations (daily/weekly)
- Swipes per user per day
- Match rate
- Message response rate
- Photo upload rate

**Cohort Analysis**:
- User retention (D1, D7, D30)
- Match quality (messages per match)
- Engagement distribution

### MVP Flow Observability

#### Critical User Flows

**1. Account Creation & Profile Setup**
```
UserService: POST /api/users/register
  → HTTP 201 Created
  → Log: "User registered: {UserId}"
  → Metric: user.registrations +1

UserService: POST /api/users/profile
  → HTTP 200 OK
  → Log: "Profile updated: {UserId}"
  → Metric: user.profile.completions +1

PhotoService: POST /api/photos
  → HTTP 201 Created
  → Log: "Photo uploaded: {PhotoId}"
  → Metric: photo.uploads +1
```

**Expected Latency**: 
- Registration: <500ms (p95)
- Profile update: <300ms (p95)
- Photo upload: <2s (p95)

**Error Scenarios**:
- Duplicate email → HTTP 409, Log warning
- Invalid photo → HTTP 400, Log validation failure
- Database timeout → HTTP 500, Log error with stack trace

**2. Discovery & Matching**
```
MatchmakingService: GET /api/candidates/{userId}
  → Fetch from cache or generate
  → Log: "Candidates fetched: {Count} for {UserId}"
  → Metric: matchmaking.candidates.generated = {Count}
  → Trace: SQL query + scoring algorithm

SwipeService: POST /api/swipes
  → Check for mutual match
  → Log: "Swipe processed: {Direction}"
  → Log: "Match created: {User1} <-> {User2}" (if match)
  → Metric: swipe.{direction} +1
  → Metric: swipe.matches +1 (if match)
```

**Expected Latency**:
- Get candidates: <1s (p95)
- Process swipe: <200ms (p95)

**Error Scenarios**:
- No candidates available → HTTP 200 with empty array, Log warning
- Swipe on invalid user → HTTP 400, Log validation failure
- Match creation failure → HTTP 500, Log error, retry logic

**3. Messaging**
```
MessagingService: POST /api/messages
  → Validate match exists
  → Deliver via SignalR
  → Log: "Message sent: {MessageId}"
  → Metric: messages.sent +1
  → Trace: HTTP request + DB write + SignalR push

SignalR: OnConnected
  → Subscribe to user's rooms
  → Log: "User connected: {UserId}"
  → Metric: signalr.connections +1
```

**Expected Latency**:
- Send message: <500ms (p95)
- SignalR delivery: <100ms (p95)

**Error Scenarios**:
- Message to non-match → HTTP 403, Log security violation
- SignalR connection drop → Automatic reconnect, Log connection reset

## Log Queries

### Common Queries (Seq/Splunk/Loki)

**Find all logs for a specific user**:
```
UserId = "12345"
```

**Find errors in the last hour**:
```
Level = "Error" AND @Timestamp > Now()-1h
```

**Find slow requests (>2s)**:
```
Elapsed > 2000 AND @Timestamp > Now()-1h
ORDER BY Elapsed DESC
```

**Trace a correlation ID**:
```
CorrelationId = "7f8e9d3c-abc1-def2-9876-543210fedcba"
ORDER BY @Timestamp
```

**Find failed matches**:
```
Message LIKE "%Match creation failed%" AND @Timestamp > Now()-24h
```

## Production Recommendations

### Log Retention

- **Hot storage**: 7 days (fast queries)
- **Warm storage**: 30 days (slower queries)
- **Cold storage**: 1 year (compliance, rare access)

### Sampling

**Trace Sampling**:
- Development: 100% (all requests)
- Staging: 50% (half of requests)
- Production: 10% (representative sample)
- Always trace errors: 100%

**Log Sampling**:
- Error/Fatal: 100% (never sample)
- Warning: 100%
- Information: 50% (sample in high-volume scenarios)
- Debug/Verbose: 10% or off

### Privacy & Security

**PII Handling**:
- ❌ DO NOT log passwords, tokens, credit cards
- ❌ DO NOT log full email addresses in production
- ✅ Log user IDs (obfuscated identifiers)
- ✅ Mask sensitive fields: `email = "u***@example.com"`

**Log Scrubbing**:
```csharp
LoggerConfiguration
    .Destructure.ByTransforming<User>(u => new {
        u.Id,   // OK
        Email = MaskEmail(u.Email),  // Masked
        // Password never logged
    })
```

## Tools Integration

### Seq (Development)

```bash
docker run -d --name seq \
  -e ACCEPT_EULA=Y \
  -p 5341:80 \
  datalust/seq:latest
```

Update `appsettings.Development.json`:
```json
{
  "Serilog": {
    "WriteTo": [
      { "Name": "Seq", "Args": { "serverUrl": "http://localhost:5341" } }
    ]
  }
}
```

### Jaeger (Tracing)

```bash
docker run -d --name jaeger \
  -p 16686:16686 \
  -p 4318:4318 \
  jaegertracing/all-in-one:latest
```

Update `Program.cs` OTLP exporter:
```csharp
.AddOtlpExporter(options => {
    options.Endpoint = new Uri("http://localhost:4318");
})
```

### Prometheus + Grafana (Metrics)

```bash
# Prometheus config
docker run -d --name prometheus \
  -p 9090:9090 \
  -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus

# Grafana
docker run -d --name grafana \
  -p 3000:3000 \
  grafana/grafana
```

Add `/metrics` endpoint to services (already configured).

## Configuration

### appsettings.json Template

```json
{
  "Serilog": {
    "Using": ["Serilog.Sinks.Console", "Serilog.Sinks.File"],
    "MinimumLevel": {
      "Default": "Information",
      "Override": {
        "Microsoft": "Warning",
        "Microsoft.Hosting.Lifetime": "Information",
        "Microsoft.EntityFrameworkCore": "Warning"
      }
    },
    "WriteTo": [
      { 
        "Name": "Console",
        "Args": {
          "outputTemplate": "[{Timestamp:yyyy-MM-dd HH:mm:ss.fff}] [{Level:u3}] [{CorrelationId}] {Message:lj}{NewLine}{Exception}"
        }
      },
      {
        "Name": "File",
        "Args": {
          "path": "logs/app-.txt",
          "rollingInterval": "Day",
          "retainedFileCountLimit": 7,
          "formatter": "Serilog.Formatting.Json.JsonFormatter"
        }
      }
    ],
    "Enrich": ["FromLogContext", "WithMachineName", "WithThreadId"],
    "Properties": {
      "Application": "DatingApp",
      "Service": "UserService"
    }
  },
  "OpenTelemetry": {
    "ServiceName": "UserService",
    "Tracing": {
      "Enabled": true,
      "SamplingRatio": 0.1
    },
    "Metrics": {
      "Enabled": true,
      "ExportInterval": 60
    }
  }
}
```

## Related Files

- Service `Program.cs` files - OpenTelemetry + Serilog configuration
- `.github/workflows/comprehensive-ci-cd.yml` - CI logging
- `smoke-tests.py` - Health check logging
- `collect-coverage.sh` - Test execution logs
