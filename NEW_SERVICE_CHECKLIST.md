# 📝 New Service Creation Checklist

## BEFORE you start coding a new service:

### 1. Port Assignment (CRITICAL - Update this list)
```
NEXT AVAILABLE PORTS:
- Development: 8084 (next service should use this)
- Demo External: 5004 (next service should use this)
- Internal Docker: 80 (ALWAYS use this for Docker)
```

### 2. Copy Template Files From Existing Service
```bash
# Copy from AuthService or UserService
cp -r AuthService/DTOs NewService/DTOs
cp AuthService/appsettings.*.json NewService/
cp AuthService/Dockerfile NewService/
# Edit NewService.csproj to include Demo.json files
```

### 3. Required Files Checklist
- [ ] `appsettings.json` (with development port 80XX)
- [ ] `appsettings.Demo.json` (with port 80 and correct DB)
- [ ] `NewService.csproj` includes Demo.json with CopyToOutputDirectory
- [ ] `/health` endpoint controller
- [ ] Dockerfile based on existing pattern
- [ ] Database migration setup

### 4. Docker-Compose Integration
```yaml
# Add to environments/demo/docker-compose.demo.yml
  newservice-demo:
    build: ../../NewService
    container_name: dating-newservice-demo
    environment:
      - ASPNETCORE_ENVIRONMENT=Demo
      - ASPNETCORE_URLS=http://+:80
      - ConnectionStrings__DefaultConnection=Server=mysql-demo;Database=newservice_demo;Uid=root;Pwd=demo_root_password;
    ports:
      - "5004:80"  # UPDATE with next available port
    depends_on:
      - mysql-demo
    networks:
      - dating-demo-network
```

### 5. Database Setup
- [ ] Add database creation to `init-demo-databases.sql`
- [ ] Test database connection from service
- [ ] Run migrations successfully

### 6. Integration Testing
- [ ] Service starts without errors
- [ ] Health endpoint responds
- [ ] Database connectivity works
- [ ] Port mapping is correct (external->80)
- [ ] Configuration files copied to container

## Auto-Validation Commands (Use VS Code Tasks)
1. **Ctrl+Shift+P** → "Tasks: Run Task" → "🔍 Validate Demo Environment"
2. **Ctrl+Shift+P** → "Tasks: Run Task" → "🏥 Quick Health Check"

## Port Strategy Reference
```
Service         | Dev Port | Demo External | Docker Internal
----------------|----------|---------------|----------------
Auth            | 8081     | 5001         | 80
User            | 8082     | 5002         | 80  
Matchmaking     | 8083     | 5003         | 80
YARP Gateway    | 8080     | 5000         | 80
MySQL           | 3306     | 3307         | 3306
Next Service    | 8084     | 5004         | 80 ⭐
```

**Remember**: Docker internal port is ALWAYS 80 for .NET services!
