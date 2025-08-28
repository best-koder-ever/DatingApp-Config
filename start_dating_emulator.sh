#!/bin/bash

# 🤖 AI AGENT: DATING APP EMULATOR LAUNCHER
# =========================================
# Optimized for ThinkPad P1 + Dating App Development

export ANDROID_HOME=/home/m/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest-2/bin:$ANDROID_HOME/platform-tools:$ANDROID_HOME/emulator

EMULATOR_NAME="DatingApp_Pixel6_API33"

echo "🚀 STARTING DATING APP EMULATOR"
echo "=============================="
echo "📱 Device: $EMULATOR_NAME"
echo "⚡ Hardware: ThinkPad P1 optimized"
echo ""

# Kill existing emulators
pkill -f emulator 2>/dev/null || true
sleep 2

echo "⏳ Starting emulator (this may take 1-2 minutes)..."

# Start with performance optimizations
emulator -avd "$EMULATOR_NAME" \
    -gpu host \
    -memory 4096 \
    -cores 4 \
    -accel on \
    -netfast \
    -camera-back virtualscene \
    -camera-front emulated \
    -no-snapshot-save \
    -no-snapshot-load \
    -partition-size 4096 &

EMULATOR_PID=$!
echo "🎯 Emulator PID: $EMULATOR_PID"

# Wait for device
echo "⏳ Waiting for device to be ready..."
timeout 300 adb wait-for-device

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ EMULATOR READY!"
    echo "=================="
    echo "📱 Device: $(adb shell getprop ro.product.model 2>/dev/null || echo 'Android Device')"
    echo "🤖 Android: $(adb shell getprop ro.build.version.release 2>/dev/null || echo 'API 33')"
    echo ""
    echo "🔥 Ready for dating app development!"
    echo ""
    echo "💡 Next steps:"
    echo "   1. cd dejtingapp"
    echo "   2. flutter run"
    echo "   3. Start hot reload development"
else
    echo "❌ Emulator startup timeout"
    echo "💡 Try: adb devices to check status"
fi
