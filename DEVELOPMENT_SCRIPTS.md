# Dating App - Development Scripts

This directory contains convenient scripts to start your dating app development environment.

## 🚀 Quick Start Options

### Option 1: Start Everything (Recommended)
```bash
./start_dating_app.sh
```
- Starts backend services
- Waits for services to be ready
- Tests API endpoints
- Starts Flutter app with hot reload
- Interactive prompts for stopping services

### Option 2: Start Backend Only
```bash
./start_backend.sh
```
- Starts only the backend Docker services
- Use when you want to start Flutter manually later

### Option 3: Start Flutter Only
```bash
cd /home/m/development/mobile-apps/flutter/dejtingapp
./start_flutter.sh
```
- Starts only the Flutter app
- Checks if backend is running first
- Use when backend is already running

### Option 4: Run All Tests (Automated)
```bash
cd /home/m/development/DatingApp/e2e-tests
./run_all_tests.sh
```
- Comprehensive test suite
- Flutter analysis + unit tests
- Backend API health checks
- E2E tests with Playwright
- Flutter integration tests
- No manual clicking required!

## 📋 Manual Commands

### Backend Commands
```bash
# Start backend services
cd /home/m/development/DatingApp
docker-compose up -d

# Stop backend services  
docker-compose down

# View logs
docker-compose logs -f

# Restart a specific service
docker-compose restart auth-service
```

### Flutter Commands
```bash
cd /home/m/development/mobile-apps/flutter/dejtingapp

# Start with hot reload
flutter run --hot

# Start on specific device
flutter run -d chrome
flutter run -d android

# Build for release
flutter build apk
flutter build web
```

## 🌐 Service URLs

| Service | URL | Purpose |
|---------|-----|---------|
| YARP Gateway | http://localhost:8080 | Main API gateway (use this in Flutter) |
| Auth Service | http://localhost:8081 | User authentication |
| User Service | http://localhost:8082 | User profiles and data |
| Matchmaking | http://localhost:8083 | Match algorithms |
| Swipe Service | http://localhost:8084 | Swipe functionality |

## 🔧 Troubleshooting

### Backend Issues
```bash
# Check service status
docker-compose ps

# View specific service logs
docker-compose logs auth-service
docker-compose logs yarp

# Rebuild services
docker-compose build --no-cache
docker-compose up -d
```

### Flutter Issues
```bash
# Clean and get dependencies
flutter clean
flutter pub get

# Check for issues
flutter analyze
flutter doctor
```

### Common Problems

1. **Port already in use**: Stop other instances with `docker-compose down`
2. **Flutter not connecting**: Check that YARP gateway (8080) is responding
3. **Build errors**: Run `flutter clean && flutter pub get`
4. **API errors**: Check backend logs with `docker-compose logs`

## 📱 Testing the App

1. Start with `./start_dating_app.sh`
2. Register a new account
3. Create your profile with photos and interests
4. Start swiping to find matches
5. View your matches in the matches tab

## 🛠 Development Tips

- Use `flutter run --hot` for fast development with hot reload
- Press `r` in the Flutter terminal for hot reload
- Press `R` for hot restart
- Press `q` to quit the Flutter app
- Backend services keep running even after Flutter stops
- Use the Flutter Inspector in your IDE for UI debugging

## 📂 Project Structure

```
DatingApp/
├── start_dating_app.sh     # Full startup script
├── start_backend.sh        # Backend only
├── docker-compose.yml      # Backend services
├── auth-service/           # Authentication microservice
├── user-service/           # User profile microservice  
├── matchmaking-service/    # Matching algorithms
├── swipe-service/          # Swipe functionality
└── dejting-yarp/           # API gateway

mobile-apps/flutter/dejtingapp/
├── start_flutter.sh        # Flutter app only
├── lib/
│   ├── main.dart          # App entry point
│   ├── models.dart        # Data models
│   ├── api_services.dart  # API communication
│   ├── backend_url.dart   # Service URLs
│   └── *_screen.dart      # UI screens
└── pubspec.yaml           # Flutter dependencies
```

Happy coding! 💙
