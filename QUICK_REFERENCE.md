# ⚡ DatingApp Quick Reference

## 🚀 One-Command Actions

```bash
# Start everything in demo mode
cd /home/m/development/DatingApp && ./dev-start.sh

# Test photo upload end-to-end
cd /home/m/development/mobile-apps/flutter/dejtingapp && python3 test_photo_upload_direct.py

# Launch visual Flutter demo
cd /home/m/development/mobile-apps/flutter/dejtingapp && ./run_visual_photo_upload_demo.sh

# Check all services health
curl -s http://localhost:8081/health && curl -s http://localhost:8085/health
```

## 🎯 Essential URLs

- **Flutter App**: http://localhost:3000
- **AuthService**: http://localhost:8081/health
- **PhotoService**: http://localhost:8085/health
- **API Gateway**: http://localhost:8080/health

## 👤 Demo Credentials

```
Email: erik.astrom@demo.com
Password: Demo123!
```

## 🔧 Emergency Fixes

```bash
# Kill everything and restart
pkill -f "dotnet.*Service" && sleep 2 && cd /home/m/development/DatingApp && ./dev-start.sh

# Fix JWT keys
cd /home/m/development/DatingApp && find . -name "public.key" -delete && cp AuthService/public.key */

# Reset demo data
export DEMO_MODE=true && ./dev-restart.sh
```

## 📱 Flutter Commands

```bash
# Run on web
flutter run -d chrome --web-port 3000

# Run integration test
flutter test integration_test/visual_photo_upload_test.dart

# Clean and rebuild
flutter clean && flutter pub get
```

## 🧪 Test Photo Upload

```bash
# Quick test
curl -X POST http://localhost:8085/api/photos \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test.jpg"

# Full test with login
cd /home/m/development/mobile-apps/flutter/dejtingapp && python3 test_photo_upload_direct.py
```
