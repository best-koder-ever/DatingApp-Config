# DatingApp AI Context File

> **Add this file to AI conversations to provide complete project context**

## 🏗️ Project Architecture

### Core Services (Microservices)
- **AuthService** (Port 8081) - User authentication & JWT token generation
- **UserService** (Port 8082) - User profiles & management  
- **MatchmakingService** (Port 8083) - Matching algorithms & preferences
- **PhotoService** (Port 8085) - Photo upload, storage & processing
- **MessagingService** (Port 8086) - Chat & real-time messaging (SignalR)
- **SwipeService** (Port 8087) - Swipe mechanics & interactions
- **YARP Gateway** (Port 8080) - API Gateway & reverse proxy

### Technology Stack
- **Backend**: .NET 8, Entity Framework Core, MySQL/In-Memory DB
- **Authentication**: JWT with RSA keys (DatingApp-Issuer/DatingApp-Audience)
- **Frontend**: Flutter 3.32.1 (Web + Mobile)
- **Testing**: Python scripts, Flutter integration tests
- **Logging**: Serilog with Loki/Grafana integration
- **Image Processing**: ImageSharp for resizing, format conversion
- **Real-time**: SignalR for messaging
- **API Gateway**: YARP for routing and load balancing

## 🔐 JWT Authentication Configuration

**Standard Configuration (ALL services must use):**
```json
{
  "Jwt": {
    "Issuer": "DatingApp-Issuer",
    "Audience": "DatingApp-Audience"
  }
}
```

**Key Management:**
- AuthService: Uses `private.key` for token signing (RSA-2048)
- All other services: Use `public.key` for token validation
- Key files are RSA 2048-bit format in PEM encoding
- **CRITICAL**: All services must have identical public key copies

**User ID Handling:**
- AuthService generates tokens with string user IDs (IdentityUser.Id)
- PhotoService maps string IDs to integers using hash code
- Other services handle string IDs natively

## 📁 Complete File Structure

```
DatingApp/                              # Main backend project
├── AuthService/                        # JWT token generation & user auth
│   ├── Controllers/
│   │   ├── AuthController.cs           # Login, register endpoints
│   │   └── TestController.cs           # Demo/health endpoints
│   ├── Services/
│   │   ├── AuthService.cs              # JWT token generation logic
│   │   ├── IAuthService.cs             # Service interface
│   │   └── RsaKeyProvider.cs           # RSA key management
│   ├── Models/
│   │   ├── User.cs                     # IdentityUser extension
│   │   └── LoginRequest.cs             # DTOs
│   ├── Data/
│   │   └── ApplicationDbContext.cs     # Entity Framework context
│   ├── appsettings.json                # JWT config, DB connection
│   ├── appsettings.Development.json    # Dev-specific settings
│   ├── public.key                      # RSA public key (master copy)
│   ├── private.key                     # RSA private key (DO NOT COPY)
│   ├── Program.cs                      # Service configuration
│   └── AuthService.csproj              # Project file
├── UserService/                        # User profile management
│   ├── Controllers/
│   │   ├── UserProfilesController.cs   # Profile CRUD operations
│   │   └── DemoController.cs           # Demo data endpoints
│   ├── Models/
│   │   ├── UserProfile.cs              # User profile entity
│   │   └── Interest.cs                 # User interests
│   ├── Services/
│   │   ├── IPhotoService.cs            # Photo service integration
│   │   └── IVerificationService.cs     # Profile verification
│   ├── DTOs/                           # Data transfer objects
│   ├── Data/ApplicationDbContext.cs    # EF context
│   ├── appsettings.json                # JWT + DB config
│   ├── public.key                      # RSA public key copy
│   └── Program.cs                      # JWT validation setup
├── MatchmakingService/                 # Matching algorithms
│   ├── Controllers/
│   │   └── MatchmakingController.cs    # Match finding endpoints
│   ├── Services/
│   │   ├── MatchmakingService.cs       # Core matching logic
│   │   ├── IAdvancedMatchingService.cs # Advanced algorithms
│   │   ├── NotificationService.cs      # Match notifications
│   │   └── IUserServiceClient.cs       # External service calls
│   ├── Models/
│   │   ├── Match.cs                    # Match entity
│   │   └── MatchingPreference.cs       # User preferences
│   ├── DTOs/                           # Request/response models
│   ├── Data/MatchmakingDbContext.cs    # EF context
│   ├── appsettings.json                # JWT + DB config
│   ├── public.key                      # RSA public key copy
│   └── Program.cs                      # JWT validation + services
├── photo-service/                      # Photo upload & processing
│   ├── Controllers/
│   │   └── PhotosController.cs         # Photo CRUD + upload
│   ├── Services/
│   │   ├── IStorageService.cs          # Photo storage interface
│   │   ├── LocalStorageService.cs      # Local file storage
│   │   ├── ImageProcessingService.cs   # Resize, format conversion
│   │   └── ModerationService.cs        # Content moderation
│   ├── Models/
│   │   └── Photo.cs                    # Photo entity
│   ├── DTOs/
│   │   ├── PhotoUploadDto.cs           # Upload request
│   │   └── PhotoResponseDto.cs         # API response
│   ├── Data/PhotoContext.cs            # EF context
│   ├── appsettings.json                # JWT + storage config
│   ├── public.key                      # RSA public key copy
│   ├── Program.cs                      # JWT validation + ImageSharp
│   └── wwwroot/uploads/photos/         # Local photo storage
├── messaging-service/                  # Chat & real-time messaging
│   ├── Controllers/
│   │   └── MessagesController.cs       # Message CRUD endpoints
│   ├── Hubs/
│   │   └── MessagingHub.cs             # SignalR real-time hub
│   ├── Services/
│   │   └── MessageService.cs           # Message business logic
│   ├── Models/
│   │   ├── Message.cs                  # Message entity
│   │   └── Conversation.cs             # Conversation entity
│   ├── Middleware/
│   │   └── JwtAuthenticationMiddleware.cs # JWT for SignalR
│   ├── Data/MessagingContext.cs        # EF context
│   ├── appsettings.json                # JWT + SignalR config
│   ├── public.key                      # RSA public key copy
│   └── Program.cs                      # JWT + SignalR setup
├── swipe-service/                      # Swipe mechanics
│   ├── Controllers/
│   │   ├── SwipesController.cs         # Swipe recording endpoints
│   │   └── HealthController.cs         # Health check
│   ├── Services/
│   │   ├── SwipeService.cs             # Swipe logic
│   │   └── MatchmakingNotifier.cs      # Match notifications
│   ├── Models/
│   │   └── Swipe.cs                    # Swipe entity
│   ├── Data/SwipeContext.cs            # EF context
│   ├── appsettings.json                # JWT + DB config
│   ├── public.key                      # RSA public key copy
│   └── Program.cs                      # JWT validation
├── dejting-yarp/                       # API Gateway
│   └── src/dejting-yarp/
│       ├── Program.cs                  # YARP routing configuration
│       ├── appsettings.json            # Route definitions
│       └── Controllers/HealthController.cs
├── TestDataGenerator/                  # Demo data seeding
│   ├── Program.cs                      # Demo user creation
│   └── TestDataGenerator.csproj
├── logs/                               # Service logs (auto-generated)
│   ├── auth-service.log                # AuthService output
│   ├── photo-service.log               # PhotoService output
│   ├── user-service.log                # UserService output
│   ├── matchmaking-service.log         # MatchmakingService output
│   ├── messaging-service.log           # MessagingService output
│   ├── swipe-service.log               # SwipeService output
│   └── yarp-gateway.log                # YARP Gateway output
├── docker-compose.yml                  # Container orchestration
├── dev-start.sh                        # 🚀 Start all services script
├── dev-stop.sh                         # 🛑 Stop all services script  
├── dev-restart.sh                      # 🔄 Restart all services script
├── dev-status.sh                       # 📊 Check service status script
├── commit_and_push_all.sh              # Git operations script
├── TROUBLESHOOTING.md                  # 🔧 Debugging guide
├── API_DOCUMENTATION.md                # 📚 Complete API reference
├── QUICK_REFERENCE.md                  # ⚡ Essential commands
└── AI_CONTEXT.md                       # 🤖 This file

mobile-apps/flutter/dejtingapp/         # Flutter frontend application
├── lib/
│   ├── main.dart                       # Flutter app entry point
│   ├── services/
│   │   ├── auth_service.dart           # Authentication API calls
│   │   ├── api_service.dart            # Base API service
│   │   ├── photo_service.dart          # Photo upload/management
│   │   ├── user_service.dart           # User profile operations
│   │   └── messaging_service.dart      # Chat/messaging
│   ├── screens/
│   │   ├── login_screen.dart           # Login/register UI
│   │   ├── profile_screen.dart         # User profile management
│   │   ├── photo_upload_screen.dart    # Photo management UI
│   │   ├── matching_screen.dart        # Swipe interface
│   │   └── chat_screen.dart            # Messaging interface
│   ├── widgets/                        # Reusable UI components
│   ├── models/                         # Data models/DTOs
│   └── utils/                          # Helper functions
├── integration_test/
│   ├── visual_photo_upload_test.dart   # 📸 Photo upload E2E test
│   └── complete_profile_photo_flow_test.dart # Full profile flow
├── test/                               # Unit tests
├── test_photo_upload_direct.py         # 🧪 Python API testing script
├── run_visual_photo_upload_demo.sh     # 🎬 Visual testing launcher
├── pubspec.yaml                        # Flutter dependencies
├── analysis_options.yaml               # Code analysis rules
├── .venv/                              # Python virtual environment
└── README.md                           # Flutter app documentation
```

## 🚀 Essential Scripts & Commands

### Service Management Scripts
```bash
# 🚀 Start all services in demo mode (auto-restart on crash)
cd /home/m/development/DatingApp
./dev-start.sh

# 🛑 Stop all services gracefully
./dev-stop.sh

# 🔄 Restart all services (stop + start)
./dev-restart.sh

# 📊 Check service status and health
./dev_status.sh

# 🔧 Manual individual service start (demo mode)
cd /home/m/development/DatingApp/AuthService
DEMO_MODE=true dotnet run --urls=http://localhost:8081 > ../logs/auth-service.log 2>&1 &

cd /home/m/development/DatingApp/photo-service  
DEMO_MODE=true dotnet run --urls=http://localhost:8085 > ../logs/photo-service.log 2>&1 &

# 🔪 Emergency kill all services
pkill -f "dotnet.*Service"
pkill -f "dotnet run"
```

### Health Check Commands
```bash
# 🏥 Quick health check all services (returns JSON or "Healthy")
curl -s http://localhost:8081/health  # AuthService
curl -s http://localhost:8082/health  # UserService  
curl -s http://localhost:8083/health  # MatchmakingService
curl -s http://localhost:8085/health  # PhotoService (returns JSON)
curl -s http://localhost:8086/health  # MessagingService
curl -s http://localhost:8087/health  # SwipeService
curl -s http://localhost:8080/health  # YARP Gateway

# 🔍 Automated health check script
for port in 8081 8082 8083 8085 8086 8087 8080; do
  echo -n "Port $port: "
  curl -s -f "http://localhost:$port/health" >/dev/null && echo "✅ OK" || echo "❌ FAIL"
done
```

### Flutter Testing Commands
```bash
cd /home/m/development/mobile-apps/flutter/dejtingapp

# 🎬 Run comprehensive visual photo upload demo (with browser)
./run_visual_photo_upload_demo.sh

# 🧪 Direct API testing with Python (requires all services running)
python3 test_photo_upload_direct.py

# 🧪 Flutter integration tests (visual photo upload workflow)
flutter test integration_test/visual_photo_upload_test.dart

# 🌐 Start Flutter web app for manual testing
flutter run -d chrome --web-port 3000 --web-renderer html

# 🔧 Flutter clean and rebuild
flutter clean && flutter pub get && flutter run -d chrome

# 📱 Run on mobile (requires device/emulator)
flutter run -d android
flutter run -d ios
```

### Database & Migration Commands
```bash
# 📊 Entity Framework migrations (per service)
cd /home/m/development/DatingApp/AuthService
dotnet ef migrations add AddNewFeature
dotnet ef database update

# 🗑️ Reset in-memory databases (restart services in demo mode)
export DEMO_MODE=true
./dev-restart.sh

# 🔍 Check database connections (production mode)
cd /home/m/development/DatingApp/AuthService
dotnet ef database can-connect
```

### Log Management
```bash
cd /home/m/development/DatingApp

# 📜 View real-time logs
tail -f logs/auth-service.log
tail -f logs/photo-service.log
tail -f logs/user-service.log

# 📜 View all logs simultaneously
tail -f logs/*.log

# 🔍 Search for errors across all logs
grep -r "ERROR\|Exception\|FATAL" logs/

# 🔍 Find authentication issues
grep -r "401\|Unauthorized\|JWT" logs/

# 🔍 Find photo upload issues
grep -r "photo\|upload\|image" logs/photo-service.log

# 🧹 Clear old logs
rm logs/*.log
```

### Git & Development
```bash
cd /home/m/development/DatingApp

# 📦 Commit and push all services
./commit_and_push_all.sh

# 📊 Check git status across all projects
git status
cd ../mobile-apps/flutter/dejtingapp && git status

# 🔄 Pull latest changes
git pull
cd ../mobile-apps/flutter/dejtingapp && git pull
```

## 👥 Demo Users & Test Data

**Standard demo credentials (auto-created in demo mode):**
```json
{
  "demoUsers": [
    {
      "email": "erik.astrom@demo.com",
      "password": "Demo123!",
      "name": "Erik Astrom",
      "age": 28,
      "location": "Stockholm, Sweden",
      "bio": "Software developer passionate about technology",
      "interests": ["Technology", "Travel", "Photography"]
    },
    {
      "email": "anna.lindberg@demo.com", 
      "password": "Demo123!",
      "name": "Anna Lindberg",
      "age": 26,
      "location": "Stockholm, Sweden",
      "bio": "Graphic designer who loves art and nature",
      "interests": ["Design", "Art", "Nature"]
    },
    {
      "email": "oskar.kallstrom@demo.com",
      "password": "Demo123!", 
      "name": "Oskar Kallstrom",
      "age": 30,
      "location": "Gothenburg, Sweden",
      "bio": "Marketing manager and outdoor enthusiast",
      "interests": ["Marketing", "Hiking", "Music"]
    },
    {
      "email": "sara.blomqvist@demo.com",
      "password": "Demo123!",
      "name": "Sara Blomqvist", 
      "age": 24,
      "location": "Malmö, Sweden",
      "bio": "Student studying psychology and wellness",
      "interests": ["Psychology", "Wellness", "Reading"]
    },
    {
      "email": "magnus.ohman@demo.com",
      "password": "Demo123!",
      "name": "Magnus Ohman",
      "age": 32,
      "location": "Uppsala, Sweden", 
      "bio": "Engineer who enjoys cooking and sports",
      "interests": ["Engineering", "Cooking", "Sports"]
    }
  ]
}
```

**Test API Credentials:**
- **Primary Test User**: erik.astrom@demo.com / Demo123!
- **Secondary Test User**: anna.lindberg@demo.com / Demo123!

**Quick Login Test:**
```bash
# Get JWT token for testing
TOKEN=$(curl -s -X POST http://localhost:8081/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"erik.astrom@demo.com","password":"Demo123!"}' \
  | jq -r '.token')

echo "Auth Token: $TOKEN"
```

## 🔧 Advanced Debugging & Troubleshooting

### Process Management
```bash
# 🔍 Check what services are running
ps aux | grep -E "dotnet.*Service" | grep -v grep

# 🔍 Check specific service process
ps aux | grep photo-service

# 🔍 Find process using specific port
sudo lsof -i :8085
sudo netstat -tlpn | grep :808

# 🔪 Kill stuck services by name
pkill -f photo-service
pkill -f "dotnet.*AuthService"

# 🔪 Kill services by port
sudo fuser -k 8085/tcp
```

### Service Logs Deep Dive
```bash
cd /home/m/development/DatingApp

# 🔍 Real-time error monitoring
tail -f logs/*.log | grep -E "ERROR|Exception|FATAL|401|500"

# 🔍 Find JWT/Authentication issues
grep -r "JWT\|Token\|Unauthorized\|401" logs/

# 🔍 Find photo upload issues specifically
grep -r "photo\|upload\|multipart\|image" logs/photo-service.log

# 🔍 Find startup issues
grep -r "Starting\|Listening\|Application started" logs/

# 🔍 Database connection issues
grep -r "Connection\|Database\|Entity" logs/

# 📊 Service performance analysis
grep -r "Request finished" logs/ | head -20
```

### Network & Port Debugging
```bash
# 🌐 Test service connectivity
nc -zv localhost 8081  # Test if port is open
telnet localhost 8085  # Interactive port test

# 🌐 Check service response headers
curl -I http://localhost:8085/health

# 🌐 Test with verbose output
curl -v http://localhost:8081/health

# 🌐 Test through YARP gateway
curl -v http://localhost:8080/health
```

### Database Debugging
```bash
# 📊 Check Entity Framework configuration
cd /home/m/development/DatingApp/AuthService
dotnet ef migrations list
dotnet ef database can-connect

# 📊 Verify database schema
dotnet ef migrations script

# 🗑️ Reset database (development)
dotnet ef database drop --force
dotnet ef database update
```

### Memory & Performance
```bash
# 📊 Check memory usage by service
ps aux | grep dotnet | awk '{print $4, $11}' | sort -nr

# 📊 Monitor CPU usage
top -p $(pgrep -f "dotnet.*Service" | tr '\n' ',' | sed 's/,$//')

# 📊 Check file handles
lsof -p $(pgrep -f photo-service) | wc -l
```

## 🎯 Current Development Status & Recent Changes

### ✅ Completed Features & Fixes

#### JWT Authentication Standardization (Latest)
- **Status**: ✅ COMPLETED
- **Changes Made**:
  - Updated all services to use `"DatingApp-Issuer"` and `"DatingApp-Audience"`
  - Migrated MessagingService from symmetric to RSA key validation
  - Added JWT authentication to MatchmakingService and SwipeService
  - Fixed PhotoService user ID mapping (string to int conversion)
  - Ensured all services have identical `public.key` files

#### Photo Upload System (Recently Fixed)
- **Status**: ✅ WORKING END-TO-END
- **Features**:
  - Multi-format support (JPEG, PNG, WebP)
  - Automatic image resizing and thumbnail generation
  - Photo metadata (dimensions, file size, quality score)
  - Primary photo designation
  - User photo galleries with display order
  - Photo moderation status tracking
- **Recent Fixes**:
  - JWT validation between AuthService and PhotoService
  - User ID mapping for IdentityUser compatibility
  - File upload size limits and error handling

#### Visual Testing Infrastructure
- **Status**: ✅ IMPLEMENTED
- **Components**:
  - `visual_photo_upload_test.dart` - Comprehensive Flutter integration test
  - `test_photo_upload_direct.py` - Python API testing script
  - `run_visual_photo_upload_demo.sh` - Automated demo environment
  - Browser-based visual testing with step-by-step feedback

### 🔧 Service Authentication Status

| Service | Port | JWT Auth | Status | Notes |
|---------|------|----------|--------|-------|
| AuthService | 8081 | Token Generation | ✅ Working | Uses private.key for signing |
| UserService | 8082 | Token Validation | ✅ Working | RSA public key validation |
| MatchmakingService | 8083 | Token Validation | ✅ Added | Recently added JWT support |
| PhotoService | 8085 | Token Validation | ✅ Working | Fixed user ID mapping |
| MessagingService | 8086 | Token Validation | ✅ Fixed | Migrated from symmetric to RSA |
| SwipeService | 8087 | Token Validation | ✅ Added | Recently added JWT support |
| YARP Gateway | 8080 | Proxy Only | ⚠️ No Auth | Acts as reverse proxy |

### 🧪 Testing Status

#### Photo Upload Testing
- **API Level**: ✅ 3/3 test images upload successfully
- **Flutter Integration**: ✅ Visual testing framework ready
- **End-to-End**: ✅ Login → Upload → Display workflow working
- **Performance**: ✅ Processing times under 200ms

#### Demo Environment
- **Services**: ✅ All 7 services running in demo mode
- **Demo Users**: ✅ 5 Swedish demo users with realistic profiles
- **Database**: ✅ In-memory databases for rapid testing
- **Health Checks**: ✅ All endpoints responding correctly

### 🔄 Known Limitations & Future Work

#### Current Limitations
1. **File Picker Web Support**: Works but shows warnings on Linux
2. **Real-time Messaging**: SignalR configured but needs frontend integration
3. **Photo Storage**: Currently local filesystem (not cloud storage)
4. **User Verification**: Profile verification system placeholder
5. **Matching Algorithm**: Basic compatibility scoring implemented

#### Planned Improvements
1. **Cloud Storage**: AWS S3 or Azure Blob integration for photos
2. **Advanced Matching**: ML-based compatibility algorithms
3. **Real-time Notifications**: Push notifications for matches/messages
4. **Profile Verification**: Photo verification and identity checks
5. **Performance Optimization**: Caching and database optimization

### 🏗️ Architecture Decisions Made

#### Microservices Communication
- **Service-to-Service**: HTTP REST APIs through YARP gateway
- **Authentication**: Shared RSA public key validation
- **Data Consistency**: Each service owns its domain data
- **Real-time**: SignalR hubs for messaging, WebSockets for notifications

#### Technology Choices
- **.NET 8**: Latest LTS version with performance improvements
- **Entity Framework Core**: Code-first approach with migrations
- **ImageSharp**: Cross-platform image processing
- **Serilog**: Structured logging with multiple sinks
- **YARP**: Microsoft's reverse proxy for .NET

#### Security Implementation
- **JWT Tokens**: RSA-256 signed, 1-hour expiration
- **Password Security**: ASP.NET Identity with hashing
- **API Security**: All endpoints require authentication except auth/health
- **File Upload Security**: Type validation, size limits, virus scanning placeholder

### 🎯 Next Development Priorities

1. **Real-time Features**: Complete SignalR integration in Flutter
2. **Matching Enhancement**: Improve algorithm accuracy and performance
3. **Photo Management**: Advanced editing, filters, album organization
4. **User Experience**: Onboarding flow, tutorial system
5. **Performance**: Database indexing, caching strategies, load testing

## 🐛 Comprehensive Issue Resolution Guide

### Authentication & JWT Issues

#### Problem: "Demo user not found" (HTTP 401)
**Root Causes:**
- Services restarted, in-memory databases reset
- Demo users not seeded properly
- AuthService not running

**Solutions:**
```bash
# 1. Restart services to reset in-memory DB
cd /home/m/development/DatingApp && ./dev-restart.sh

# 2. Manual user registration
curl -X POST http://localhost:8081/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"erik.astrom@demo.com","password":"Demo123!","userName":"Erik"}'

# 3. Verify AuthService health
curl -s http://localhost:8081/health
```

#### Problem: "401 Unauthorized" on authenticated endpoints
**Root Causes:**
- JWT Issuer/Audience mismatch between services
- Missing or corrupted public key files
- Token format issues

**Diagnostic Steps:**
```bash
# 1. Check JWT configuration consistency
grep -r "DatingApp-Issuer" /home/m/development/DatingApp/*/appsettings.json

# 2. Verify public key files exist and are identical
find /home/m/development/DatingApp -name "public.key" -exec md5sum {} \;

# 3. Test token generation
TOKEN=$(curl -s -X POST http://localhost:8081/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"erik.astrom@demo.com","password":"Demo123!"}' \
  | jq -r '.token')
echo $TOKEN | cut -d'.' -f2 | base64 -d | jq  # Decode JWT payload
```

**Fixes:**
```bash
# Copy master public key to all services
cd /home/m/development/DatingApp
for service in UserService photo-service messaging-service MatchmakingService swipe-service; do
  cp AuthService/public.key $service/public.key
done

# Restart services to reload keys
./dev-restart.sh
```

### Service Startup & Communication Issues

#### Problem: "Port already in use"
**Solutions:**
```bash
# Kill all .NET services
pkill -f "dotnet.*Service"

# Kill specific port processes
sudo lsof -ti:8085 | xargs kill -9

# Check what's using ports
netstat -tlpn | grep :808
```

#### Problem: Services fail to start
**Diagnostic Steps:**
```bash
# Check startup logs
cd /home/m/development/DatingApp
tail -20 logs/photo-service.log

# Check for missing dependencies
cd photo-service && dotnet restore

# Verify configuration files
cat appsettings.json | jq .
```

#### Problem: Service-to-service communication failures
**Solutions:**
```bash
# Test direct service connectivity
curl -v http://localhost:8085/health

# Test through YARP gateway
curl -v http://localhost:8080/health

# Check YARP routing configuration
cat dejting-yarp/src/dejting-yarp/appsettings.json | jq .ReverseProxy
```

### Photo Upload Specific Issues

#### Problem: "Unable to determine user identity" (500 error)
**Root Cause:** JWT claims parsing issues in PhotoService

**Solution:**
Check PhotoService `GetCurrentUserId()` method handles string user IDs:
```csharp
// This should be in PhotosController.cs
private int GetCurrentUserId()
{
    var userIdClaim = User.FindFirst(ClaimTypes.NameIdentifier)?.Value ??
                     User.FindFirst("sub")?.Value ??
                     User.FindFirst("userId")?.Value;

    if (string.IsNullOrEmpty(userIdClaim))
    {
        throw new UnauthorizedAccessException("Unable to determine user identity");
    }

    // Handle both int and string user IDs
    if (int.TryParse(userIdClaim, out var userId))
    {
        return userId;
    }

    // Map string ID to integer (for IdentityUser compatibility)
    return Math.Abs(userIdClaim.GetHashCode());
}
```

#### Problem: File upload size limits
**Error:** Request entity too large

**Solution:**
Update `appsettings.json` in PhotoService:
```json
{
  "Kestrel": {
    "Limits": {
      "MaxRequestBodySize": 52428800,
      "MultipartBodyLengthLimit": 52428800
    }
  }
}
```

### Database & Entity Framework Issues

#### Problem: Migration errors
**Solutions:**
```bash
# Check current migration status
cd /home/m/development/DatingApp/AuthService
dotnet ef migrations list

# Add new migration
dotnet ef migrations add FixUserSchema

# Update database
dotnet ef database update

# Reset database (development only)
dotnet ef database drop --force && dotnet ef database update
```

#### Problem: Connection string issues
**Check configuration:**
```bash
# Verify connection strings in appsettings.json
grep -r "ConnectionStrings" /home/m/development/DatingApp/*/appsettings.json

# Test database connectivity
cd AuthService && dotnet ef database can-connect
```

### Flutter Integration Issues

#### Problem: File picker warnings on Linux
**Status:** Normal behavior - plugin works despite warnings

**Example Warning:**
```
Package file_picker:linux references file_picker:linux as the default plugin
```

#### Problem: Integration test failures
**Common Fixes:**
```bash
# Clean Flutter cache
cd /home/m/development/mobile-apps/flutter/dejtingapp
flutter clean && flutter pub get

# Run with specific renderer
flutter test integration_test/visual_photo_upload_test.dart --web-renderer html

# Check test dependencies
flutter doctor
```

#### Problem: CORS issues in web browser
**Solution:** Add CORS policy to services that need browser access:
```csharp
// In Program.cs
builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(policy =>
    {
        policy.AllowAnyOrigin()
              .AllowAnyMethod()
              .AllowAnyHeader();
    });
});

// Before app.UseRouting()
app.UseCors();
```

### Performance & Monitoring Issues

#### Problem: High memory usage
**Diagnostic:**
```bash
# Check memory per service
ps aux | grep dotnet | awk '{print $4, $11}' | sort -nr

# Monitor garbage collection
dotnet-counters monitor --name photo-service --counters System.Runtime
```

#### Problem: Slow response times
**Analysis:**
```bash
# Check request timing in logs
grep -r "Request finished" logs/ | grep -E "[0-9]{3,}ms"

# Monitor active connections
ss -tlpn | grep :808
```

### Emergency Recovery Procedures

#### Complete System Reset
```bash
# 1. Kill everything
cd /home/m/development/DatingApp
pkill -f "dotnet"
pkill -f "flutter"

# 2. Clean build artifacts
find . -name "bin" -type d -exec rm -rf {} + 2>/dev/null
find . -name "obj" -type d -exec rm -rf {} + 2>/dev/null

# 3. Restore dependencies
for service in AuthService UserService MatchmakingService photo-service messaging-service swipe-service; do
  cd $service && dotnet restore && cd ..
done

# 4. Start fresh
export DEMO_MODE=true
./dev-start.sh
```

#### Database Reset (Development)
```bash
# Reset all in-memory databases
export DEMO_MODE=true
./dev-restart.sh

# Reset Entity Framework (if using persistent DB)
for service in AuthService UserService MatchmakingService photo-service messaging-service swipe-service; do
  cd $service
  dotnet ef database drop --force 2>/dev/null || true
  dotnet ef database update 2>/dev/null || true
  cd ..
done
```

## 📝 Development Notes & Best Practices

### Demo Mode vs Production Mode

#### Demo Mode (`DEMO_MODE=true`)
- **Database**: In-memory databases (data resets on restart)
- **Authentication**: More permissive validation for testing
- **Demo Users**: Auto-created Swedish demo users with realistic profiles
- **Photos**: Local storage in `wwwroot/uploads/photos/`
- **Logging**: Console + file logging enabled
- **Performance**: Optimized for rapid testing and development

**Enable Demo Mode:**
```bash
export DEMO_MODE=true
cd /home/m/development/DatingApp && ./dev-start.sh
```

#### Production Mode (Default)
- **Database**: MySQL databases with persistent storage
- **Authentication**: Full JWT validation and security
- **Users**: Real user registration required
- **Photos**: Cloud storage integration (when implemented)
- **Logging**: Structured logging to Loki/Grafana
- **Performance**: Production optimizations enabled

### RSA Key Management

#### Key File Locations & Purpose
```
AuthService/
├── private.key          # 🔑 MASTER - Used for JWT signing (NEVER COPY)
└── public.key           # 🔓 MASTER - Used for JWT validation (COPY TO ALL)

[All Other Services]/
└── public.key           # 🔓 COPY - Must be identical to AuthService version
```

#### Key Rotation Process (Future)
1. Generate new RSA key pair in AuthService
2. Deploy new public key to all services
3. Update AuthService to use new private key
4. Verify all services can validate new tokens
5. Remove old key files

#### Security Notes
- Private key must NEVER leave AuthService directory
- Public key must be identical across all services
- Keys are RSA-2048 in PEM format
- Key rotation should be automated in production

### Database Schema Design

#### User Identity Architecture
- **AuthService**: Uses ASP.NET Identity with string user IDs
- **Other Services**: Reference users by mapped integer IDs
- **Mapping Strategy**: Hash-based consistent mapping (string → int)
- **Benefits**: Maintains referential integrity while supporting Identity framework

#### Photo Storage Schema
```sql
-- Photo entity structure
Photos {
  Id: int (Primary Key)
  UserId: int (Foreign Key, mapped from string)
  OriginalFileName: string
  DisplayOrder: int
  IsPrimary: boolean
  CreatedAt: datetime
  Width: int
  Height: int
  FileSizeBytes: long
  ModerationStatus: enum (AUTO_APPROVED, PENDING, APPROVED, REJECTED)
  QualityScore: int (0-100)
}
```

### API Design Patterns

#### Response Format Standardization
```csharp
// Success Response Pattern
{
  "success": true,
  "data": { /* actual data */ },
  "meta": { /* pagination, counts, etc. */ }
}

// Error Response Pattern  
{
  "success": false,
  "error": "Human-readable error message",
  "code": "ERROR_CODE",
  "details": { /* additional error context */ }
}
```

#### Authentication Header Pattern
```
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
```

### Testing Strategy

#### Testing Pyramid
1. **Unit Tests**: Service methods, business logic validation
2. **Integration Tests**: API endpoints with database interaction
3. **Contract Tests**: Service-to-service communication
4. **E2E Tests**: Full user workflows through Flutter UI
5. **Performance Tests**: Load testing, stress testing

#### Test Data Management
```json
// Standard test data structure
{
  "testUsers": [
    {
      "profile": "primary_tester",
      "email": "erik.astrom@demo.com",
      "hasPhotos": true,
      "photoCount": 3,
      "hasMatches": true
    },
    {
      "profile": "secondary_tester", 
      "email": "anna.lindberg@demo.com",
      "hasPhotos": true,
      "photoCount": 2,
      "hasMatches": false
    }
  ],
  "testPhotos": [
    {
      "size": "800x600",
      "format": "JPEG",
      "sizeKB": 45,
      "purpose": "primary_photo"
    }
  ]
}
```

### Performance Considerations

#### Service Startup Optimization
- **Dependency Order**: AuthService → UserService → Others
- **Health Check Strategy**: Exponential backoff for dependent services
- **Graceful Degradation**: Services continue operating if others are down

#### Database Performance
- **Indexes**: User lookups, photo queries, matching algorithms
- **Connection Pooling**: Configured for high concurrent users
- **Query Optimization**: EF Core query analysis enabled

#### Image Processing Performance
- **Async Processing**: Non-blocking image operations
- **Multiple Formats**: WebP for modern browsers, JPEG fallback
- **Thumbnail Generation**: Multiple sizes (150px, 400px, 800px)
- **CDN Ready**: URLs structured for CDN integration

### Monitoring & Observability

#### Log Levels & Categories
```
TRACE: Detailed execution flow
DEBUG: Development debugging information  
INFO: General application flow
WARN: Potentially harmful situations
ERROR: Error events that allow application to continue
FATAL: Critical errors that may cause application termination
```

#### Key Metrics to Monitor
- **Authentication**: Login success/failure rates, token validation errors
- **Photo Upload**: Upload success rates, processing times, file sizes
- **API Performance**: Response times, error rates, throughput
- **Resource Usage**: Memory, CPU, disk I/O, network I/O

#### Health Check Endpoints
Each service provides detailed health information:
```json
{
  "status": "Healthy",
  "service": "PhotoService",
  "timestamp": "2025-09-22T12:00:00Z",
  "dependencies": {
    "database": "Healthy",
    "storage": "Healthy", 
    "authService": "Healthy"
  },
  "metrics": {
    "requestsPerMinute": 45,
    "averageResponseTime": "125ms",
    "errorRate": "0.2%"
  }
}
```

### Security Best Practices

#### JWT Token Security
- **Expiration**: 1-hour token lifetime
- **Refresh Strategy**: Sliding refresh tokens (future implementation)
- **Validation**: Strict issuer/audience validation
- **Algorithm**: RSA-256 (asymmetric, secure)

#### File Upload Security
- **Type Validation**: Whitelist of allowed image formats
- **Size Limits**: 50MB max file size
- **Content Scanning**: Virus scanning placeholder
- **Storage Isolation**: User photos isolated by user ID

#### API Security
- **Rate Limiting**: Planned for production deployment
- **CORS**: Configured for web application domains
- **HTTPS**: Required in production environments
- **Input Validation**: Comprehensive request validation

---

**🎯 Key Files for AI Context:**
- `AI_CONTEXT.md` - This comprehensive context file
- `TROUBLESHOOTING.md` - Detailed debugging guide
- `API_DOCUMENTATION.md` - Complete API reference
- `QUICK_REFERENCE.md` - Essential commands cheat sheet

**💡 Usage Tip**: Always include this AI_CONTEXT.md file in conversations to provide complete project understanding and prevent knowledge gaps!
