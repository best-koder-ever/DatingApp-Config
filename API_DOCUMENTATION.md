# 📚 DatingApp API Documentation

## 🔐 Authentication Service (Port 8081)

### Base URL: `http://localhost:8081`

#### POST `/api/auth/register`
Register a new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "userName": "JohnDoe"
}
```

**Response (200):**
```json
{
  "message": "User registered successfully",
  "userId": "b47ac10b-58cc-4372-a567-0e02b2c3d479"
}
```

**Response (400):**
```json
{
  "error": "Email already exists."
}
```

#### POST `/api/auth/login`
Authenticate user and receive JWT token.

**Request:**
```json
{
  "email": "erik.astrom@demo.com",
  "password": "Demo123!"
}
```

**Response (200):**
```json
{
  "token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expiration": "2025-09-23T14:30:00Z",
  "user": {
    "id": "b47ac10b-58cc-4372-a567-0e02b2c3d479",
    "email": "erik.astrom@demo.com",
    "userName": "Erik"
  }
}
```

**Response (401):**
```json
{
  "error": "Demo user not found or password incorrect."
}
```

#### GET `/health`
Check service health.

**Response (200):**
```text
Healthy
```

## 👤 User Service (Port 8082)

### Base URL: `http://localhost:8082`
### Authentication: Bearer Token Required

#### GET `/api/userprofiles`
Get current user's profile.

**Headers:**
```
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

**Response (200):**
```json
{
  "id": "b47ac10b-58cc-4372-a567-0e02b2c3d479",
  "email": "erik.astrom@demo.com",
  "userName": "Erik",
  "bio": "Software developer from Stockholm",
  "age": 28,
  "location": "Stockholm, Sweden",
  "interests": ["Technology", "Travel", "Photography"],
  "photos": [
    {
      "id": 1,
      "url": "http://localhost:8085/api/photos/1/image",
      "isPrimary": true
    }
  ]
}
```

#### PUT `/api/userprofiles`
Update user profile.

**Request:**
```json
{
  "bio": "Updated bio text",
  "location": "Gothenburg, Sweden",
  "interests": ["Music", "Sports", "Cooking"]
}
```

#### GET `/api/userprofiles/{userId}`
Get another user's public profile.

**Response (200):**
```json
{
  "id": "user-id",
  "userName": "Anna",
  "bio": "Designer from Stockholm",
  "age": 26,
  "location": "Stockholm, Sweden",
  "photos": [...]
}
```

## 📸 Photo Service (Port 8085)

### Base URL: `http://localhost:8085`
### Authentication: Bearer Token Required

#### POST `/api/photos`
Upload a new photo.

**Content-Type:** `multipart/form-data`

**Form Data:**
- `file`: Image file (JPEG, PNG, WebP)
- `isPrimary`: boolean (optional, default: false)
- `displayOrder`: integer (optional, default: 1)
- `description`: string (optional)

**Headers:**
```
Authorization: Bearer <JWT_TOKEN>
```

**Response (201):**
```json
{
  "success": true,
  "errorMessage": null,
  "warnings": [],
  "photo": {
    "id": 1,
    "userId": 1218659562,
    "originalFileName": "photo.jpg",
    "displayOrder": 1,
    "isPrimary": true,
    "createdAt": "2025-09-22T12:23:44.2943859Z",
    "width": 800,
    "height": 600,
    "fileSizeBytes": 9081,
    "moderationStatus": "AUTO_APPROVED",
    "qualityScore": 75,
    "urls": {
      "full": "http://localhost:8085/api/photos/1/image",
      "medium": "http://localhost:8085/api/photos/1/medium", 
      "thumbnail": "http://localhost:8085/api/photos/1/thumbnail"
    },
    "fileSizeFormatted": "8.9 KB"
  },
  "processingInfo": {
    "wasResized": false,
    "originalWidth": 800,
    "originalHeight": 600,
    "finalWidth": 800,
    "finalHeight": 600,
    "formatConverted": false,
    "originalFormat": "JPEG",
    "finalFormat": "JPEG",
    "processingTimeMs": 178
  }
}
```

#### GET `/api/photos`
Get all photos for current user.

**Response (200):**
```json
{
  "userId": 1218659562,
  "totalPhotos": 3,
  "hasPrimaryPhoto": true,
  "primaryPhoto": {
    "id": 1,
    "userId": 1218659562,
    "originalFileName": "photo.jpg",
    "displayOrder": 1,
    "isPrimary": true,
    "urls": {
      "full": "http://localhost:8085/api/photos/1/image",
      "medium": "http://localhost:8085/api/photos/1/medium",
      "thumbnail": "http://localhost:8085/api/photos/1/thumbnail"
    }
  },
  "photos": [...],
  "totalStorageBytes": 47064,
  "remainingPhotoSlots": 3,
  "hasReachedPhotoLimit": false
}
```

#### GET `/api/photos/{photoId}/image`
Get full-size photo image.

**Response:** Binary image data

#### GET `/api/photos/{photoId}/thumbnail`
Get thumbnail version of photo.

**Response:** Binary image data (150x150px max)

#### GET `/api/photos/{photoId}/medium`
Get medium-size version of photo.

**Response:** Binary image data (800x800px max)

#### DELETE `/api/photos/{photoId}`
Delete a photo.

**Response (200):**
```json
{
  "success": true,
  "message": "Photo deleted successfully"
}
```

#### PUT `/api/photos/{photoId}/primary`
Set photo as primary.

**Response (200):**
```json
{
  "success": true,
  "message": "Primary photo updated"
}
```

## 💕 Matchmaking Service (Port 8083)

### Base URL: `http://localhost:8083`
### Authentication: Bearer Token Required

#### GET `/api/matchmaking/potential-matches`
Get potential matches for current user.

**Query Parameters:**
- `maxAge`: integer (optional)
- `minAge`: integer (optional)
- `maxDistance`: integer (optional, km)
- `limit`: integer (optional, default: 10)

**Response (200):**
```json
{
  "matches": [
    {
      "userId": "match-user-id",
      "userName": "Anna",
      "age": 26,
      "location": "Stockholm",
      "distance": 5.2,
      "compatibilityScore": 87,
      "primaryPhoto": "http://localhost:8085/api/photos/5/thumbnail",
      "bio": "Designer who loves travel",
      "commonInterests": ["Photography", "Travel"]
    }
  ],
  "totalMatches": 15,
  "hasMore": true
}
```

#### POST `/api/matchmaking/preferences`
Update matching preferences.

**Request:**
```json
{
  "ageRange": {
    "min": 22,
    "max": 35
  },
  "maxDistance": 50,
  "interests": ["Technology", "Travel", "Sports"],
  "showOnlyVerified": false
}
```

## 👆 Swipe Service (Port 8087)

### Base URL: `http://localhost:8087`
### Authentication: Bearer Token Required

#### POST `/api/swipes`
Record a swipe action.

**Request:**
```json
{
  "targetUserId": "target-user-id",
  "action": "LIKE" // or "PASS"
}
```

**Response (200):**
```json
{
  "success": true,
  "isMatch": true,
  "matchId": "match-id-if-mutual-like"
}
```

#### GET `/api/swipes/history`
Get swipe history for current user.

**Response (200):**
```json
{
  "swipes": [
    {
      "id": 1,
      "targetUserId": "user-id",
      "action": "LIKE",
      "swipedAt": "2025-09-22T12:00:00Z"
    }
  ]
}
```

## 💬 Messaging Service (Port 8086)

### Base URL: `http://localhost:8086`
### Authentication: Bearer Token Required

#### GET `/api/messages/conversations`
Get all conversations for current user.

**Response (200):**
```json
{
  "conversations": [
    {
      "id": "conversation-id",
      "participantId": "other-user-id",
      "participantName": "Anna",
      "lastMessage": {
        "text": "Hello there!",
        "sentAt": "2025-09-22T12:00:00Z",
        "senderId": "other-user-id"
      },
      "unreadCount": 2
    }
  ]
}
```

#### GET `/api/messages/conversation/{conversationId}`
Get messages from a specific conversation.

**Response (200):**
```json
{
  "messages": [
    {
      "id": "message-id",
      "text": "Hello there!",
      "senderId": "sender-user-id",
      "sentAt": "2025-09-22T12:00:00Z",
      "readAt": "2025-09-22T12:01:00Z"
    }
  ]
}
```

#### POST `/api/messages`
Send a new message.

**Request:**
```json
{
  "conversationId": "conversation-id",
  "text": "Hello! How are you?"
}
```

### SignalR Hub: `/messagingHub`
Real-time messaging connection.

**Connection:** 
```javascript
// JavaScript example
const connection = new signalR.HubConnectionBuilder()
    .withUrl("http://localhost:8086/messagingHub", {
        accessTokenFactory: () => authToken
    })
    .build();
```

**Events:**
- `ReceiveMessage`: New message received
- `UserOnline`: User came online
- `UserOffline`: User went offline
- `MessageRead`: Message was read

## 🌐 YARP Gateway (Port 8080)

### Base URL: `http://localhost:8080`

The YARP Gateway routes requests to appropriate microservices:

- `/auth/**` → AuthService (8081)
- `/users/**` → UserService (8082)
- `/matching/**` → MatchmakingService (8083)
- `/photos/**` → PhotoService (8085)
- `/messages/**` → MessagingService (8086)
- `/swipes/**` → SwipeService (8087)

## 🔧 Error Response Format

All services return consistent error responses:

**4xx/5xx Response:**
```json
{
  "error": "Error message description",
  "code": "ERROR_CODE",
  "timestamp": "2025-09-22T12:00:00Z",
  "path": "/api/endpoint"
}
```

## 🔑 Authentication

All protected endpoints require JWT Bearer token:

**Header:**
```
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
```

**JWT Claims:**
- `sub`: User ID
- `aud`: "DatingApp-Audience"
- `iss`: "DatingApp-Issuer"
- `exp`: Token expiration
- `jti`: Unique token ID

## 📊 Rate Limiting

Default rate limits (when implemented):
- Auth endpoints: 5 requests/minute
- Photo upload: 10 photos/hour
- Messaging: 100 messages/hour
- Swipes: 200 swipes/day

## 🧪 Testing Endpoints

### Quick API Test Script
```bash
#!/bin/bash
# Test all endpoints with demo user

# 1. Login
TOKEN=$(curl -s -X POST http://localhost:8081/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"erik.astrom@demo.com","password":"Demo123!"}' \
  | jq -r '.token')

echo "Token: $TOKEN"

# 2. Get user profile
curl -H "Authorization: Bearer $TOKEN" http://localhost:8082/api/userprofiles

# 3. Get photos
curl -H "Authorization: Bearer $TOKEN" http://localhost:8085/api/photos

# 4. Get potential matches
curl -H "Authorization: Bearer $TOKEN" http://localhost:8083/api/matchmaking/potential-matches
```
