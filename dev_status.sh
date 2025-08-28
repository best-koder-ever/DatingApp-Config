#!/bin/bash

# 🤖 AI AGENT: DEVELOPMENT ENVIRONMENT STATUS CHECKER
# ===================================================

echo "🤖 AI AGENT: DEVELOPMENT ENVIRONMENT STATUS"
echo "==========================================="
echo ""

echo "🐳 BACKEND SERVICES:"
echo "==================="
docker-compose ps

echo ""
echo "📱 ANDROID DEVICES:"
echo "=================="
adb devices

echo ""
echo "🔍 EMULATOR DETAILS:"
echo "==================="
if adb devices | grep -q "emulator"; then
    echo "✅ Emulator detected!"
    
    # Wait for device to be fully ready
    adb wait-for-device
    
    echo "📱 Device Model: $(adb shell getprop ro.product.model 2>/dev/null || echo 'Loading...')"
    echo "🤖 Android Version: $(adb shell getprop ro.build.version.release 2>/dev/null || echo 'Loading...')"
    echo "🎯 API Level: $(adb shell getprop ro.build.version.sdk 2>/dev/null || echo 'Loading...')"
    echo "🧠 RAM: $(adb shell getprop ro.config.total_ram 2>/dev/null || echo 'Loading...')"
else
    echo "❌ No emulator detected"
    echo "💡 Start with: ./start_dating_emulator.sh"
fi

echo ""
echo "🦋 FLUTTER STATUS:"
echo "=================="
cd ../mobile-apps/flutter/dejtingapp 2>/dev/null && pwd && echo "✅ Flutter app found" || echo "❌ Flutter app not found"

echo ""
echo "🎯 QUICK COMMANDS:"
echo "=================="
echo "🚀 Start emulator: ./start_dating_emulator.sh"
echo "🐳 Start backend: ./start_backend.sh"
echo "🔥 Run Flutter app: cd ../mobile-apps/flutter/dejtingapp && flutter run"
echo "📊 Check this status: ./dev_status.sh"
echo ""

if adb devices | grep -q "device$"; then
    echo "✅ READY FOR DEVELOPMENT!"
    echo "========================="
    echo "Your ThinkPad P1 Android development environment is ready!"
    echo "Navigate to the Flutter app and run: flutter run"
else
    echo "⏳ EMULATOR STARTING..."
    echo "======================"
    echo "Wait 1-2 minutes for emulator to fully boot, then check again."
fi
