# YARP Gateway Configuration Guide

## Overview
The YARP (Yet Another Reverse Proxy) Gateway is configured to work seamlessly in both **Local Development** and **Docker** environments using environment-specific configuration files.

## Configuration Files

### 1. `appsettings.json` (Docker/Production)
- **Purpose**: Default configuration for Docker containers
- **Service Addresses**: Uses Docker service names (e.g., `auth-service:8081`)
- **Environment**: Production, Docker Compose

### 2. `appsettings.Development.json` (Local Development - Alternative)
- **Purpose**: Standard development configuration
- **Service Addresses**: Uses localhost addresses (e.g., `localhost:8081`)
- **Environment**: Development

### 3. `appsettings.Local.json` (Local Development - Recommended)
- **Purpose**: Dedicated local development configuration
- **Service Addresses**: Uses localhost addresses with correct ports
- **Environment**: Local (custom environment)
- **Features**: Includes health route with round-robin load balancing

## Environment Configuration

### Local Development Setup
```bash
# Start YARP with Local environment
ASPNETCORE_ENVIRONMENT=Local ASPNETCORE_URLS=http://+:8080 dotnet run
```

### Docker Development Setup
```bash
# Start YARP with Development environment (uses Docker service names)
ASPNETCORE_ENVIRONMENT=Development ASPNETCORE_URLS=http://+:8080 dotnet run
```

## Service Routing

### Local Development (appsettings.Local.json)
| Route | Target Service | Address |
|-------|----------------|---------|
| `/api/auth/**` | AuthService | `http://localhost:8081/` |
| `/api/userprofiles/**` | UserService | `http://localhost:8082/` |
| `/api/matchmaking/**` | MatchmakingService | `http://localhost:8083/` |
| `/api/photos/**` | PhotoService | `http://localhost:8085/` |
| `/api/messages/**` | MessagingService | `http://localhost:8086/` |
| `/api/swipes/**` | SwipeService | `http://localhost:8087/` |
| `/health/**` | Round-robin health checks | Multiple services |

### Docker Development (appsettings.json)
| Route | Target Service | Address |
|-------|----------------|---------|
| `/api/auth/**` | AuthService | `http://auth-service:8081/` |
| `/api/userprofiles/**` | UserService | `http://user-service:8082/` |
| `/api/matchmaking/**` | MatchmakingService | `http://matchmaking-service:8083/` |
| `/api/photos/**` | PhotoService | `http://photo-service:8085/` |
| `/api/messages/**` | MessagingService | `http://messaging-service:8086/` |
| `/api/swipes/**` | SwipeService | `http://swipe-service:8087/` |

## Testing YARP Gateway

### Successful Test Examples
```bash
# Test through YARP Gateway (Local)
curl http://localhost:8080/api/userprofiles/health     # ✅ Returns UserService health
curl http://localhost:8080/api/matchmaking/health      # ✅ Returns MatchmakingService health
curl http://localhost:8080/api/auth/register           # ✅ Returns 405 (POST required)

# Test direct service access
curl http://localhost:8081/health                      # ✅ AuthService health
curl http://localhost:8082/health                      # ✅ UserService health
curl http://localhost:8083/health                      # ✅ MatchmakingService health
```

## Development Scripts Integration

### dev-start.sh
The development startup script automatically:
1. Sets `ASPNETCORE_ENVIRONMENT=Local` for YARP Gateway
2. Starts all services with correct ports
3. Routes traffic through YARP using localhost addresses

### Benefits of This Setup

#### ✅ **Local Development**
- Fast startup (no Docker overhead)
- Direct service debugging
- Hot reload capabilities
- Uses localhost addresses for all inter-service communication

#### ✅ **Docker Development**
- Container-native networking
- Docker service discovery
- Production-like environment
- Uses Docker service names for communication

#### ✅ **Seamless Switching**
- Same codebase, different configurations
- Environment variable-driven
- No code changes required
- Maintains development workflow consistency

## Current Status
- **YARP Gateway**: ✅ Running on port 8080
- **Local Routing**: ✅ Working (UserService, MatchmakingService tested)
- **Docker Routing**: ✅ Ready (configured for Docker service names)
- **Service Discovery**: ✅ Automatic based on environment

This setup allows you to:
1. **Develop locally** with maximum performance and debugging capabilities
2. **Test in Docker** when you need container-specific behavior
3. **Switch environments** easily without code changes
4. **Maintain consistency** across all development modes
