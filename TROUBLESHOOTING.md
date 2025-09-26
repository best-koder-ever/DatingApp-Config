# 🔧 DatingApp Troubleshooting Guide

## 🚨 Common Error Patterns & Solutions

### Authentication Issues

#### "Demo user not found or password incorrect"
**Symptoms:**
- HTTP 401 on login
- Login API returns error message

**Solutions:**
1. Restart services to reset in-memory databases:
   ```bash
   cd /home/m/development/DatingApp
   ./dev-restart.sh
   ```

2. Check if AuthService is running:
   ```bash
   curl -s http://localhost:8081/health
   ```

3. Register demo user manually:
   ```bash
   curl -X POST http://localhost:8081/api/auth/register \
     -H "Content-Type: application/json" \
     -d '{
       "email": "erik.astrom@demo.com",
       "password": "Demo123!",
       "userName": "Erik"
     }'
   ```

#### "401 Unauthorized" on API calls
**Symptoms:**
- Photo upload fails with 401
- API endpoints reject authenticated requests

**Root Causes:**
- JWT Issuer/Audience mismatch
- Missing or incorrect public key
- Token expired

**Solutions:**
1. Verify JWT configuration consistency:
   ```bash
   # Check all appsettings.json files have:
   grep -r "DatingApp-Issuer" /home/m/development/DatingApp/*/appsettings.json
   ```

2. Ensure public key files exist:
   ```bash
   find /home/m/development/DatingApp -name "public.key" -type f
   ```

3. Copy public key to all services:
   ```bash
   cd /home/m/development/DatingApp
   cp AuthService/public.key UserService/
   cp AuthService/public.key photo-service/
   cp AuthService/public.key messaging-service/
   cp AuthService/public.key MatchmakingService/
   cp AuthService/public.key swipe-service/
   ```

### Service Startup Issues

#### "Port already in use"
**Error:** `Only one usage of each socket address`

**Solutions:**
1. Kill existing processes:
   ```bash
   pkill -f "dotnet.*Service"
   pkill -f photo-service
   ```

2. Check port usage:
   ```bash
   netstat -tlpn | grep :808
   ```

3. Kill specific port processes:
   ```bash
   sudo lsof -ti:8081 | xargs kill -9
   ```

#### Service fails to start
**Check logs:**
```bash
cd /home/m/development/DatingApp
tail -f logs/[service-name].log
```

**Common fixes:**
- Missing appsettings.json
- Invalid connection strings
- Missing NuGet packages
- Port conflicts

### Database Issues

#### Entity Framework migrations
**Error:** `Pending model changes`

**Solutions:**
```bash
# Add migration
cd /home/m/development/DatingApp/AuthService
dotnet ef migrations add UpdateSchema

# Update database
dotnet ef database update
```

#### In-memory database issues
**Problem:** Data not persisting between requests

**Solution:** Ensure `DEMO_MODE=true` is set:
```bash
export DEMO_MODE=true
dotnet run
```

### Flutter Integration Issues

#### file_picker warnings on Linux
**Warning:** `file_picker:linux references file_picker:linux`

**Status:** Normal - plugin works despite warnings

#### Flutter test failures
**Error:** `No Material widget found`

**Solutions:**
1. Wrap test widgets in MaterialApp
2. Use `tester.pumpWidget()` properly
3. Check widget tree structure

#### Web debugging issues
**Problem:** DevTools not connecting

**Solutions:**
```bash
# Restart with explicit renderer
flutter run -d chrome --web-renderer html --debug

# Check if Chrome is in debug mode
ps aux | grep chrome | grep debug
```

### Photo Upload Issues

#### "Unable to determine user identity"
**Error:** JWT claims not parsing correctly

**Solutions:**
1. Check PhotoService user ID mapping
2. Verify JWT token format
3. Update GetCurrentUserId() method

#### File upload size limits
**Error:** `Request too large`

**Solutions:**
1. Update Kestrel limits in appsettings.json:
   ```json
   {
     "Kestrel": {
       "Limits": {
         "MaxRequestBodySize": 52428800
       }
     }
   }
   ```

### Network & CORS Issues

#### CORS blocked in browser
**Error:** `Access-Control-Allow-Origin`

**Solutions:**
1. Add CORS policy to Program.cs:
   ```csharp
   builder.Services.AddCors(options =>
   {
       options.AddDefaultPolicy(policy =>
       {
           policy.AllowAnyOrigin()
                 .AllowAnyMethod()
                 .AllowAnyHeader();
       });
   });
   ```

2. Use CORS middleware:
   ```csharp
   app.UseCors();
   ```

#### Connection refused
**Error:** `Connection refused` or `ECONNREFUSED`

**Check:**
1. Service is running: `curl http://localhost:8081/health`
2. Correct port numbers
3. Firewall settings
4. Service binding to correct interface

## 🔍 Debugging Workflows

### Quick Health Check All Services
```bash
#!/bin/bash
services=(
  "8081:AuthService"
  "8082:UserService" 
  "8083:MatchmakingService"
  "8085:PhotoService"
  "8086:MessagingService"
  "8087:SwipeService"
  "8080:YARP Gateway"
)

for service in "${services[@]}"; do
  port="${service%%:*}"
  name="${service##*:}"
  
  if curl -s -f "http://localhost:$port/health" > /dev/null; then
    echo "✅ $name ($port)"
  else
    echo "❌ $name ($port)"
  fi
done
```

### Service Restart Sequence
```bash
# 1. Stop all services
./dev-stop.sh

# 2. Clean ports
pkill -f "dotnet.*Service"

# 3. Wait for clean shutdown
sleep 2

# 4. Start in dependency order
cd AuthService && DEMO_MODE=true dotnet run --urls=http://localhost:8081 &
sleep 3

cd ../UserService && DEMO_MODE=true dotnet run --urls=http://localhost:8082 &
sleep 2

cd ../photo-service && DEMO_MODE=true dotnet run --urls=http://localhost:8085 &
# ... continue for other services
```

### Log Analysis
```bash
# Find errors in all logs
grep -r "ERROR\|FATAL\|Exception" logs/

# Monitor all logs simultaneously
tail -f logs/*.log

# Filter for specific issues
grep -r "401\|Unauthorized" logs/
grep -r "500\|Internal Server Error" logs/
```

### Performance Monitoring
```bash
# Check memory usage
ps aux | grep dotnet | awk '{print $4, $11}'

# Check CPU usage
top -p $(pgrep -f "dotnet.*Service" | tr '\n' ',' | sed 's/,$//')

# Monitor file handles
lsof -p $(pgrep -f photo-service)
```

## 🧪 Testing Strategies

### Photo Upload Testing Pyramid
1. **Unit Tests**: PhotoService methods
2. **Integration Tests**: API endpoints with auth
3. **E2E Tests**: Flutter widget to backend
4. **Visual Tests**: Browser automation

### Environment Testing Matrix
- **Demo Mode**: In-memory DB, relaxed validation
- **Development**: Local MySQL, full auth
- **Staging**: Remote DB, production-like
- **Production**: Full security, monitoring

### Common Test Data
```json
{
  "demoUsers": [
    {"email": "erik.astrom@demo.com", "password": "Demo123!"},
    {"email": "anna.lindberg@demo.com", "password": "Demo123!"},
    {"email": "oskar.kallstrom@demo.com", "password": "Demo123!"}
  ],
  "testImages": [
    {"size": "800x600", "format": "JPEG", "sizeKB": 45},
    {"size": "1200x800", "format": "PNG", "sizeKB": 234},
    {"size": "500x500", "format": "WebP", "sizeKB": 67}
  ]
}
```
