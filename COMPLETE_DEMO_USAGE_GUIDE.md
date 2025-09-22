# Complete Demo System Usage Guide

## Overview
The dating app now includes a comprehensive demo system with both backend API endpoints and frontend UI automation. This allows for easy testing and demonstration without complex setup.

## Quick Start

### 1. Start Demo Services
```bash
cd /home/m/development/DatingApp
./start_demo_services.sh
```

This will:
- Start all microservices with demo endpoints enabled
- AuthService on port 8081
- UserService on port 8082
- MatchmakingService on port 8083
- Check health of all services

### 2. Run Demo System
```bash
cd /home/m/development/mobile-apps/flutter/dejtingapp
python3 accurate_demo.py
```

### 3. Choose Demo Option
The menu provides 10 options:

1. **📝 Registration Demo** - Test user registration with accurate field mapping
2. **🔐 Login Demo** - Test user login with any credentials
3. **🏠 Main App Navigation** - Navigate through all 4 app tabs
4. **💕 Discover Screen Interactions** - Test swipe functionality
5. **🎯 Complete End-to-End Demo** - Full user journey from registration to matching
6. **📸 Visual Debug Test** - Take screenshots for visual verification
7. **🔄 Restart Flutter App** - Restart the Flutter application
8. **🛑 Stop Flutter App** - Stop the Flutter application
9. **🔧 Backend Demo API Testing** - Test all backend demo endpoints
0. **❌ Exit** - Exit the demo system

### 4. Stop Services When Done
```bash
cd /home/m/development/DatingApp
./stop_demo_services.sh
```

## Demo Features

### Backend Demo Endpoints
All services provide demo endpoints that return realistic fake data:

#### AuthService Demo (:8081)

Test endpoint: `http://localhost:8081/api/demo/health`
Full docs: `http://localhost:8081/swagger`

#### UserService Demo (:8082)

Test endpoint: `http://localhost:8082/api/demo/health` 
Full docs: `http://localhost:8082/swagger`

#### MatchmakingService Demo (:8083)

Test endpoint: `http://localhost:8083/api/demo/health`
Full docs: `http://localhost:8083/swagger`

### Frontend UI Automation
- **Safety Protection**: Prevents accidental typing into VS Code windows
- **Accurate Field Mapping**: Based on actual Flutter UI analysis
- **Visual Debug**: Screenshots for verification
- **Error Handling**: Graceful handling of window focus issues
- **Menu-Driven Interface**: Easy selection of specific test scenarios

## Test Data Characteristics

### User Profiles
- **Realistic Names**: Swedish/International names
- **Age Range**: 22-36 years old
- **Cities**: Swedish cities (Stockholm, Gothenburg, etc.)
- **Photos**: High-quality placeholder images
- **Interests**: Common dating app interests
- **Verification**: 33% verified profiles
- **Online Status**: 75% shown as online

### Matching System
- **Match Rate**: 20% mutual match probability
- **Compatibility**: Scores between 70-100%
- **Distance**: Simulated 1-50km range
- **Common Interests**: 1-6 shared interests per potential match

## Predefined Test Accounts
- **alice@demo.com** / password123 (Alice Johnson)
- **bob@demo.com** / password123 (Bob Smith)
- **carol@demo.com** / password123 (Carol Williams)
- **demo@example.com** / demo123 (Demo User)
- **test@test.com** / test123 (Test User)

## Troubleshooting

### Services Not Starting
```bash
# Check if ports are available
netstat -tulpn | grep -E ":500[1-3]"

# Check service logs
tail -f /home/m/development/DatingApp/logs/authservice.log
tail -f /home/m/development/DatingApp/logs/userservice.log
tail -f /home/m/development/DatingApp/logs/matchmakingservice.log
```

### Flutter App Issues
```bash
# Check Flutter installation
flutter doctor

# Clean Flutter project
cd /home/m/development/mobile-apps/flutter/dejtingapp
flutter clean
flutter pub get
```

### Demo Script Issues
```bash
# Check Python dependencies
pip install requests pillow pyautogui

# Check permissions
chmod +x accurate_demo.py
chmod +x backend_demo_tester.py
```

## Advanced Usage

### Standalone Backend Testing
```bash
cd /home/m/development/mobile-apps/flutter/dejtingapp
python3 backend_demo_tester.py
```

### Custom Demo Scenarios
Edit `accurate_demo.py` to add custom test scenarios or modify existing ones.

### CI/CD Integration
The demo system can be integrated into CI/CD pipelines:
```bash
# Start services
./start_demo_services.sh

# Run backend tests
python3 backend_demo_tester.py --automated

# Run UI tests (with virtual display)
python3 accurate_demo.py --automated

# Stop services
./stop_demo_services.sh
```

## Benefits

1. **No Database Setup** - Works without complex database initialization
2. **Consistent Testing** - Predictable, realistic test data
3. **Fast Iteration** - Quick verification during development
4. **Demo Ready** - Perfect for presentations and stakeholder demos
5. **Development Speed** - Faster testing cycles
6. **CI/CD Friendly** - Easy automation integration

## File Structure
```
DatingApp/
├── start_demo_services.sh      # Start all demo services
├── stop_demo_services.sh       # Stop all demo services
├── DEMO_MODE_GUIDE.md         # This guide
├── auth-service/
│   └── Controllers/DemoController.cs
├── UserService/
│   └── Controllers/DemoController.cs
├── matchmaking-service/
│   └── Controllers/DemoController.cs
└── logs/                      # Service logs

mobile-apps/flutter/dejtingapp/
├── accurate_demo.py           # Main demo system
├── backend_demo_tester.py     # Backend API tester
└── flutter_automator.py      # UI automation engine
```

This demo system provides a complete testing and demonstration environment that works reliably without complex setup, making it perfect for development, testing, and stakeholder presentations.
