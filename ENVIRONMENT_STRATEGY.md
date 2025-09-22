# 🌍 Dating App Environment Strategy & Port Management

## 📋 **Current Problems Analysis**

### **Port Configuration Chaos:**
- Services have mixed internal ports (8081, 8082, 8083)
- Docker containers trying to override with port 80
- ASPNETCORE_URLS conflicts with appsettings.json
- Different docker-compose files use different schemes
- No consistent service discovery

### **Environment Confusion:**
- Demo and development environments overlap
- No clear separation of configurations
- Hard to switch between environments
- Production strategy undefined

---

## 🎯 **Long-Term Strategy: Standardized Environment Management**

### **1. Port Allocation Schema**

#### **External Port Ranges (Host Machine):**
```
Development:   8000-8099  (Direct service access)
Demo:          8080-8099  (Presentation/client access)  
Staging:       6000-6099  (Pre-production testing)
Production:    443/80     (Load balancer only)
```

#### **Internal Port Standards (Container):**
```
All services:  80         (Standardized internal port)
Database:      3306       (MySQL standard)
Gateway:       80         (YARP standard)
```

### **2. Environment-Specific Configurations**

#### **Development Environment**
```yaml
# For active coding and debugging
External Ports: 8001-8010
Purpose: Local development, debugging, hot reload
Database: Local MySQL on 3306 or Docker on 3308
Gateway: Optional (direct service access)
SSL: No
Logging: Verbose
```

#### **Demo Environment** 
```yaml
# For presentations and client demos
External Ports: 8081-8090  
Purpose: Stable demos, client presentations
Database: Demo MySQL with curated data on 3320
Gateway: Required (professional URLs)
SSL: Optional
Logging: Minimal
```

#### **Staging Environment**
```yaml
# For pre-production testing
External Ports: 6001-6010
Purpose: Production-like testing, QA validation
Database: Staging MySQL with production-like data
Gateway: Required
SSL: Yes
Logging: Production-level
```

#### **Production Environment**
```yaml
# For live users
External Ports: 80/443 only (via load balancer)
Purpose: Live user traffic
Database: Production MySQL cluster
Gateway: Required with SSL termination
SSL: Required
Logging: Structured, minimal
```

---

## 🏗️ **Implementation Strategy**

### **Phase 1: Standardize Internal Configuration (This Week)**

#### **Service Configuration Standard:**
```csharp
// appsettings.json - NO HARDCODED PORTS
{
  "Kestrel": {
    "Endpoints": {
      "Http": {
        "Url": "http://*:80"  // Always port 80 internally
      }
    }
  }
}

// Environment-specific overrides via environment variables only
```

#### **Docker-Compose Standard:**
```yaml
# All services follow this pattern:
service-name:
  build: ../../ServiceName
  environment:
    - ASPNETCORE_ENVIRONMENT=${ENV_NAME}
    - ASPNETCORE_URLS=http://+:80
    - ConnectionStrings__DefaultConnection=${DB_CONNECTION}
  ports:
    - "${EXTERNAL_PORT}:80"  # External port from environment
  networks:
    - app-network
```

### **Phase 2: Environment Separation (Next Week)**

#### **Directory Structure:**
```
environments/
├── development/
│   ├── docker-compose.dev.yml
│   ├── .env.dev
│   └── appsettings.Development.json
├── demo/
│   ├── docker-compose.demo.yml  
│   ├── .env.demo
│   └── appsettings.Demo.json
├── staging/
│   ├── docker-compose.staging.yml
│   ├── .env.staging
│   └── appsettings.Staging.json
└── production/
    ├── docker-compose.prod.yml
    ├── .env.prod
    └── appsettings.Production.json
```

#### **Environment Files:**
```bash
# .env.demo
ENV_NAME=Demo
AUTH_PORT=8081
USER_PORT=8082
MATCHMAKING_PORT=8083
GATEWAY_PORT=8080
DB_PORT=3320
DB_CONNECTION=Server=mysql-demo;Database=dating_app_demo;Uid=root;Pwd=demo_root_password;

# .env.dev  
ENV_NAME=Development
AUTH_PORT=8001
USER_PORT=8002
MATCHMAKING_PORT=8003
GATEWAY_PORT=8000
DB_PORT=3308
DB_CONNECTION=Server=mysql-dev;Database=dating_app_dev;Uid=root;Pwd=dev_password;
```

### **Phase 3: Service Discovery & Networking (Month 2)**

#### **Internal Service Communication:**
```yaml
# Services communicate via Docker network names
networks:
  app-network:
    name: dating-app-${ENV_NAME}
    driver: bridge

# Service URLs become:
# http://auth-service/api/auth/...
# http://user-service/api/users/...
# http://matchmaking-service/api/matchmaking/...
```

#### **Configuration Management:**
```csharp
// Centralized configuration
public class ServiceConfiguration
{
    public string AuthServiceUrl { get; set; } = "http://auth-service";
    public string UserServiceUrl { get; set; } = "http://user-service";
    public string MatchmakingServiceUrl { get; set; } = "http://matchmaking-service";
}
```

---

## 🛠️ **Tools & Scripts for Environment Management**

### **Environment Switcher Script:**
```bash
#!/bin/bash
# switch-env.sh
ENV=$1

case $ENV in
  "dev"|"development")
    export COMPOSE_FILE=environments/development/docker-compose.dev.yml
    export COMPOSE_ENV_FILE=environments/development/.env.dev
    ;;
  "demo")
    export COMPOSE_FILE=environments/demo/docker-compose.demo.yml  
    export COMPOSE_ENV_FILE=environments/demo/.env.demo
    ;;
  "staging")
    export COMPOSE_FILE=environments/staging/docker-compose.staging.yml
    export COMPOSE_ENV_FILE=environments/staging/.env.staging
    ;;
  *)
    echo "Usage: ./switch-env.sh [dev|demo|staging]"
    exit 1
    ;;
esac

echo "🌍 Switched to $ENV environment"
echo "📄 Using: $COMPOSE_FILE"
docker-compose --env-file $COMPOSE_ENV_FILE -f $COMPOSE_FILE $@
```

### **Health Check Script:**
```bash
#!/bin/bash
# health-check.sh
source environments/$1/.env.$1

echo "🔍 Checking $ENV_NAME environment health..."
curl -s http://localhost:$AUTH_PORT/health || echo "❌ Auth service down"
curl -s http://localhost:$USER_PORT/health || echo "❌ User service down"  
curl -s http://localhost:$MATCHMAKING_PORT/api/matchmaking/health || echo "❌ Matchmaking service down"
curl -s http://localhost:$GATEWAY_PORT/health || echo "❌ Gateway down"
```

### **Port Validation Script:**
```bash
#!/bin/bash
# check-ports.sh
ENV=$1
source environments/$ENV/.env.$ENV

echo "🔍 Checking port availability for $ENV_NAME..."
netstat -tuln | grep :$AUTH_PORT && echo "⚠️ Port $AUTH_PORT in use"
netstat -tuln | grep :$USER_PORT && echo "⚠️ Port $USER_PORT in use"
netstat -tuln | grep :$MATCHMAKING_PORT && echo "⚠️ Port $MATCHMAKING_PORT in use"
```

---

## 📚 **Documentation Strategy**

### **Environment Quick Reference:**
```
🔧 Development (8001-8010): Active coding, debugging
🎬 Demo (8081-8090): Client presentations, stable demos  
🧪 Staging (6001-6010): Pre-production testing
🚀 Production (80/443): Live user traffic
```

### **Port Assignment Matrix:**
```
Service          | Dev  | Demo | Staging | Production
-----------------|------|------|---------|------------
Auth Service     | 8001 | 8081 | 6001    | LB:443
User Service     | 8002 | 8082 | 6002    | LB:443  
Matchmaking      | 8003 | 8083 | 6003    | LB:443
Gateway (YARP)   | 8000 | 8080 | 6000    | 443/80
MySQL DB         | 3308 | 3320 | 3330    | Internal
```

---

## 🎯 **Benefits of This Strategy**

### **For Development:**
- ✅ No port conflicts between environments
- ✅ Easy environment switching
- ✅ Clear service discovery
- ✅ Consistent configuration management

### **For Demo/Presentation:**
- ✅ Stable, predictable ports (8000 series)
- ✅ Professional URLs via gateway
- ✅ Isolated from development changes
- ✅ Curated demo data

### **For Production:**
- ✅ Security through load balancer
- ✅ Scalable architecture
- ✅ Environment isolation
- ✅ Professional deployment

### **For Team:**
- ✅ Clear documentation
- ✅ Automated tooling
- ✅ Consistent patterns
- ✅ Future-proof architecture

---

## 🚀 **Implementation Timeline**

### **Week 1: Fix Current Issues**
- Standardize all services to port 80 internally
- Fix docker-compose configurations
- Create environment-specific .env files
- Get demo working reliably

### **Week 2: Environment Separation**  
- Complete environment directory structure
- Create switching scripts
- Document port assignments
- Test all environments

### **Week 3: Service Discovery**
- Implement internal networking
- Update service configurations
- Create health check automation
- Performance testing

### **Week 4: Production Planning**
- Design production architecture
- Security and SSL planning
- Monitoring and logging strategy
- Deployment automation

---

## 💡 **Immediate Action Plan**

1. **Fix Demo Environment** (Today)
   - Standardize to port 80 internal
   - Create proper .env.demo file
   - Test complete user journey

2. **Create Development Environment** (Tomorrow)
   - Port 8000 series
   - Local development optimized
   - Hot reload support

3. **Document Everything** (This Week)
   - Port assignment matrix
   - Environment switching guide
   - Troubleshooting guide

This strategy eliminates confusion, provides clear separation, and scales from development to production! 🎯
