# AI Collaboration Strategy for Full-Stack Dating App

## 🎯 Context Management Strategies

### 1. **Architectural Overview First** (For big decisions)
```
PROVIDE:
- Backend: Service architecture diagram/docs 
- Frontend: App structure and main screens
- Integration: API service layer files
- Infrastructure: docker-compose, routing config

ASK: "Should I redesign X to better integrate with Y?"
```

### 2. **Domain-Specific Deep Dives** (For feature work)
```
PROVIDE:
- Single backend service + related frontend code
- Specific use case flows (e.g., photo upload)
- Related test files and configurations

ASK: "How do I improve photo upload UX while maintaining good API design?"
```

### 3. **Problem-Focused Context** (For debugging)
```
PROVIDE:
- Error logs and specific failing components
- Related configuration files
- Minimal reproducible examples

ASK: "Why isn't X working when Y service returns Z?"
```

## 📋 Your Current Architecture Analysis

### ✅ **What's Working Well:**
- Clean microservices separation
- YARP gateway for routing
- JWT authentication across services
- Demo/production environment flexibility
- RESTful API design principles

### 🔧 **Minor Improvements Needed:**
- API service layer needs better error handling
- Some UI/API mismatches (like photo upload routing)
- Integration test coverage could be better

### ❌ **Major Redesign NOT Needed:**
- Your service boundaries are logical
- API endpoints follow REST conventions
- Flutter app structure is appropriate
- Authentication flow is solid

## 🚀 **Recommended AI Collaboration Workflow:**

1. **For Architecture Questions:**
   - Attach: `docker-compose.yml`, `Program.cs` files, `api_services.dart`
   - Ask: Strategic/design questions

2. **For Feature Development:**
   - Attach: Specific service + related Flutter screens
   - Ask: Implementation questions

3. **For Debugging:**
   - Attach: Error logs + minimal failing code
   - Ask: "Why is this failing?"

4. **For Testing:**
   - Attach: Existing test files + components being tested
   - Ask: "How do I improve test coverage for X?"

## 💡 **Current Priority:**
Your architecture is good. Focus on:
- Improving UX flows (like auto-save photos)
- Better error handling in Flutter
- More comprehensive testing
- Performance optimization

Don't redesign the API structure - it's well-architected!
