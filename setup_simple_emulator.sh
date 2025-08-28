#!/bin/bash

# 🤖 AI AGENT: SIMPLIFIED ANDROID EMULATOR SETUP
# ==============================================
# Target: High-Performance Dating App Development
# Hardware: ThinkPad P1 optimized

set -e

echo "🤖 AI AGENT: CREATING OPTIMIZED ANDROID EMULATOR"
echo "==============================================="
echo "Target: Dating App Development on ThinkPad P1"
echo ""

# Set Android environment
export ANDROID_HOME=/home/m/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest-2/bin:$ANDROID_HOME/platform-tools:$ANDROID_HOME/emulator

# Configuration optimized for ThinkPad P1
EMULATOR_NAME="DatingApp_Pixel6_API33"
API_LEVEL="33"
PACKAGE="system-images;android-33;google_apis_playstore;x86_64"

echo "📱 EMULATOR CONFIGURATION:"
echo "   Name: $EMULATOR_NAME"
echo "   API Level: $API_LEVEL"
echo "   Device: Pixel 6 (optimized for dating apps)"
echo "   RAM: 4GB (optimal for basic app)"
echo "   CPU Cores: 4 (perfect balance)"
echo ""

# Install required components
echo "📦 Installing Android API 33 and system images..."
sdkmanager "platforms;android-${API_LEVEL}" 2>/dev/null
sdkmanager "$PACKAGE" 2>/dev/null
sdkmanager "build-tools;34.0.0" 2>/dev/null

# Delete existing AVD if it exists
if avdmanager list avd | grep -q "$EMULATOR_NAME"; then
    echo "🗑️  Removing existing $EMULATOR_NAME..."
    avdmanager delete avd -n "$EMULATOR_NAME"
fi

# Create AVD
echo "🏗️  Creating AVD: $EMULATOR_NAME..."
echo "no" | avdmanager create avd \
    -n "$EMULATOR_NAME" \
    -k "$PACKAGE" \
    -d "pixel_6"

# Configure for high performance
AVD_PATH="$HOME/.android/avd/${EMULATOR_NAME}.avd"
CONFIG_FILE="$AVD_PATH/config.ini"

echo "⚙️  Optimizing for ThinkPad P1 performance..."

# Add performance optimizations to config
cat >> "$CONFIG_FILE" << EOF

# ThinkPad P1 Performance Optimizations (Optimal for Basic Dating App)
hw.cpu.ncore = 4
hw.ramSize = 4096
vm.heapSize = 512
hw.gpu.enabled = yes
hw.gpu.mode = host
runtime.network.latency = none
runtime.network.speed = full
hw.keyboard = yes
hw.sensors.orientation = yes
hw.sensors.proximity = yes
hw.camera.back = virtualscene
hw.camera.front = emulated
disk.dataPartition.size = 4096M
EOF

echo "🚀 Creating optimized launcher script..."
cat > "/home/m/development/DatingApp/start_dating_emulator.sh" << 'EOF'
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
EOF

chmod +x "/home/m/development/DatingApp/start_dating_emulator.sh"

echo "🔧 Creating complete development starter..."
cat > "/home/m/development/DatingApp/start_full_dev.sh" << 'EOF'
#!/bin/bash

# 🤖 AI AGENT: COMPLETE DATING APP DEVELOPMENT ENVIRONMENT
# ========================================================

echo "🤖 AI AGENT: STARTING COMPLETE DEVELOPMENT ENVIRONMENT"
echo "======================================================"
echo "🎯 Target: Full-Stack Dating App Development"
echo ""

# Start backend services
echo "🐳 Starting backend services..."
docker-compose up -d
sleep 5

# Show backend status
echo "📊 Backend Status:"
docker-compose ps

echo ""

# Start emulator
echo "📱 Starting Android emulator..."
./start_dating_emulator.sh &

echo ""
echo "🦋 Flutter Environment:"
cd dejtingapp
flutter doctor

echo ""
echo "🎯 DEVELOPMENT ENVIRONMENT READY!"
echo "================================="
echo ""
echo "📱 Check emulator: adb devices"
echo "🚀 Start app: cd dejtingapp && flutter run"
echo "🔥 Enable hot reload for rapid development"
echo ""
echo "Happy coding! 💕"
EOF

chmod +x "/home/m/development/DatingApp/start_full_dev.sh"

echo ""
echo "✅ ANDROID EMULATOR SETUP COMPLETE!"
echo "==================================="
echo ""
echo "🎯 Created:"
echo "   • $EMULATOR_NAME (optimized for ThinkPad P1)"
echo "   • start_dating_emulator.sh (high-performance launcher)"
echo "   • start_full_dev.sh (complete environment)"
echo ""
echo "🚀 Quick start:"
echo "   ./start_full_dev.sh"
echo ""
echo "📱 Just emulator:"
echo "   ./start_dating_emulator.sh"
echo ""
echo "⚡ Performance features:"
echo "   • 4 CPU cores (optimal for basic app + Android OS)"
echo "   • 4GB RAM allocation (perfect for dating app)"
echo "   • Hardware GPU acceleration"
echo "   • KVM acceleration enabled"
echo "   • Network optimization"
echo "   • Leaves 8 cores + 60GB RAM free for development tools"
echo ""
echo "🔥 Ready for efficient dating app development!"
