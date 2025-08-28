#!/bin/bash

# 🤖 AI AGENT: AUTOMATED ANDROID EMULATOR SETUP
# ===============================================
# Target: High-Performance Dating App Development
# Hardware: ThinkPad P1 (12 cores, 64GB RAM, NVIDIA GPU)

set -e

echo "🤖 AI AGENT: SETTING UP OPTIMAL ANDROID EMULATOR"
echo "================================================"
echo "Target: Dating App Development Optimization"
echo ""

# Load system analysis
if [ -f "/tmp/thinkpad_analysis.env" ]; then
    source /tmp/thinkpad_analysis.env
fi

# Configuration based on ThinkPad P1 specs
EMULATOR_NAME="DatingApp_Pixel6Pro_API33"
API_LEVEL="33"
SYSTEM_IMAGE="system-images;android-33;google_apis_playstore;x86_64"
DEVICE_PROFILE="pixel_6_pro"
RAM_SIZE="8192"
HEAP_SIZE="1024"
CORES="6"
INTERNAL_STORAGE="8192"
SD_CARD_SIZE="2048M"

echo "📱 EMULATOR SPECIFICATIONS:"
echo "   Name: $EMULATOR_NAME"
echo "   API Level: $API_LEVEL"
echo "   RAM: ${RAM_SIZE}MB"
echo "   CPU Cores: $CORES"
echo "   Device: Pixel 6 Pro"
echo "   Hardware Acceleration: YES"
echo ""

# Accept Android licenses
echo "📋 Accepting Android licenses..."
yes | sdkmanager --licenses > /dev/null 2>&1

# Install/update required components
echo "📦 Installing/updating Android components..."
sdkmanager "platforms;android-${API_LEVEL}" > /dev/null 2>&1
sdkmanager "$SYSTEM_IMAGE" > /dev/null 2>&1
sdkmanager "build-tools;34.0.0" > /dev/null 2>&1
sdkmanager "platform-tools" > /dev/null 2>&1
sdkmanager "emulator" > /dev/null 2>&1

# Delete existing emulator if it exists
if avdmanager list avd | grep -q "$EMULATOR_NAME"; then
    echo "🗑️  Removing existing $EMULATOR_NAME..."
    avdmanager delete avd -n "$EMULATOR_NAME"
fi

# Create optimized AVD
echo "🏗️  Creating optimized AVD: $EMULATOR_NAME..."
avdmanager create avd \
    -n "$EMULATOR_NAME" \
    -k "$SYSTEM_IMAGE" \
    -d "$DEVICE_PROFILE" \
    --force

# Configure AVD for optimal performance
AVD_PATH="$HOME/.android/avd/${EMULATOR_NAME}.avd"
CONFIG_FILE="$AVD_PATH/config.ini"

echo "⚙️  Optimizing AVD configuration..."

# Performance optimizations for ThinkPad P1
cat > "$CONFIG_FILE" << EOF
PlayStore.enabled = true
abi.type = x86_64
avd.ini.displayname = $EMULATOR_NAME
avd.ini.encoding = UTF-8
hw.accelerometer = yes
hw.arc = false
hw.audioInput = yes
hw.audioOutput = yes
hw.battery = yes
hw.camera.back = virtualscene
hw.camera.front = emulated
hw.cpu.arch = x86_64
hw.cpu.ncore = $CORES
hw.device.hash2 = MD5:8304da6a6ccd59ab240c745c3b8bfded
hw.device.manufacturer = Google
hw.device.name = pixel_6_pro
hw.dPad = no
hw.gpu.enabled = yes
hw.gpu.mode = host
hw.gsmModem = yes
hw.initialOrientation = Portrait
hw.keyboard = yes
hw.keyboard.lid = no
hw.lcd.density = 512
hw.lcd.height = 3120
hw.lcd.width = 1440
hw.mainKeys = no
hw.ramSize = $RAM_SIZE
hw.sdCard = yes
hw.sensors.orientation = yes
hw.sensors.proximity = yes
hw.trackBall = no
hw.useext4 = true
image.sysdir.1 = system-images/android-$API_LEVEL/google_apis_playstore/x86_64/
runtime.network.latency = none
runtime.network.speed = full
showDeviceFrame = yes
skin.dynamic = yes
skin.name = pixel_6_pro
tag.display = Google Play
tag.id = google_apis_playstore
vm.heapSize = $HEAP_SIZE
disk.dataPartition.size = ${INTERNAL_STORAGE}M
hw.sdCard.path = $AVD_PATH/sdcard.img
EOF

# Create SD card
echo "💾 Creating SD card ($SD_CARD_SIZE)..."
mksdcard "$SD_CARD_SIZE" "$AVD_PATH/sdcard.img"

# Create optimized emulator start script
echo "🚀 Creating emulator start script..."
cat > "/home/m/development/DatingApp/start_emulator.sh" << 'EOF'
#!/bin/bash

# 🤖 AI AGENT: OPTIMIZED EMULATOR LAUNCHER
# ========================================
# Target: Maximum Performance Dating App Development

EMULATOR_NAME="DatingApp_Pixel6Pro_API33"

echo "🚀 Starting optimized Android emulator..."
echo "📱 Device: $EMULATOR_NAME"
echo "⚡ Hardware acceleration: ENABLED"
echo ""

# Kill any existing emulator instances
pkill -f emulator64-x86 2>/dev/null || true
pkill -f qemu-system 2>/dev/null || true

# Wait a moment for cleanup
sleep 2

# Start emulator with performance optimizations
emulator -avd "$EMULATOR_NAME" \
    -gpu host \
    -no-snapshot-save \
    -no-snapshot-load \
    -no-snapshot \
    -wipe-data \
    -partition-size 8192 \
    -memory 8192 \
    -cores 6 \
    -accel on \
    -netfast \
    -no-audio \
    -camera-back virtualscene \
    -camera-front emulated \
    -skin pixel_6_pro \
    -show-kernel \
    -verbose &

EMULATOR_PID=$!

echo "🎯 Emulator starting (PID: $EMULATOR_PID)..."
echo "⏳ This may take 1-2 minutes for first boot..."
echo ""
echo "📱 While waiting, you can:"
echo "   • Start the backend services: ./start_backend.sh"
echo "   • Prepare Flutter for hot reload"
echo "   • Monitor emulator status with: adb devices"
echo ""

# Wait for emulator to be ready
echo "⏳ Waiting for emulator to boot..."
timeout 300 adb wait-for-device

if [ $? -eq 0 ]; then
    echo "✅ Emulator ready for development!"
    echo "📱 Device: $(adb shell getprop ro.product.model)"
    echo "🤖 Android version: $(adb shell getprop ro.build.version.release)"
    echo ""
    echo "🔥 Ready for dating app development!"
else
    echo "❌ Emulator boot timeout. Check for issues."
fi
EOF

chmod +x "/home/m/development/DatingApp/start_emulator.sh"

# Create complete development environment script
echo "🔧 Creating complete development environment starter..."
cat > "/home/m/development/DatingApp/start_mobile_dev.sh" << 'EOF'
#!/bin/bash

# 🤖 AI AGENT: COMPLETE MOBILE DEVELOPMENT ENVIRONMENT
# ====================================================
# Target: Full-Stack Dating App Development

echo "🤖 AI AGENT: STARTING MOBILE DEVELOPMENT ENVIRONMENT"
echo "===================================================="
echo "Target: Complete Dating App Development Stack"
echo ""

# Function to check if process is running
check_process() {
    pgrep -f "$1" > /dev/null
}

echo "🐳 Starting backend services..."
if ! check_process "docker-compose"; then
    docker-compose up -d
    sleep 10
    echo "✅ Backend services started"
else
    echo "✅ Backend services already running"
fi

echo ""
echo "📱 Starting Android emulator..."
if ! check_process "emulator64-x86"; then
    ./start_emulator.sh &
    echo "⏳ Emulator starting in background..."
else
    echo "✅ Emulator already running"
fi

echo ""
echo "🦋 Preparing Flutter development..."
cd dejtingapp

# Check Flutter doctor
echo "🏥 Flutter health check..."
flutter doctor --android-licenses > /dev/null 2>&1
flutter doctor -v

echo ""
echo "📦 Getting Flutter dependencies..."
flutter pub get

echo ""
echo "🎯 DEVELOPMENT ENVIRONMENT STATUS:"
echo "=================================="
echo "📊 Backend Services:"
docker-compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "📱 Android Devices:"
adb devices

echo ""
echo "🔥 READY FOR MOBILE DEVELOPMENT!"
echo "================================"
echo ""
echo "💡 Next steps:"
echo "   1. Wait for emulator to fully boot (check: adb devices)"
echo "   2. Run: flutter run"
echo "   3. Enable hot reload for rapid development"
echo ""
echo "🚀 Happy coding!"
EOF

chmod +x "/home/m/development/DatingApp/start_mobile_dev.sh"

echo ""
echo "✅ ANDROID EMULATOR SETUP COMPLETE!"
echo "==================================="
echo ""
echo "📁 Created files:"
echo "   • DatingApp_Pixel6Pro_API33 AVD (optimized for ThinkPad P1)"
echo "   • start_emulator.sh (performance launcher)"
echo "   • start_mobile_dev.sh (complete environment)"
echo ""
echo "🚀 To start development:"
echo "   ./start_mobile_dev.sh"
echo ""
echo "📱 To start just the emulator:"
echo "   ./start_emulator.sh"
echo ""
echo "⚡ Performance features enabled:"
echo "   • Hardware GPU acceleration"
echo "   • 6 CPU cores allocated"
echo "   • 8GB RAM (optimal for 64GB system)"
echo "   • KVM acceleration"
echo "   • Host graphics mode"
echo ""
echo "🎯 Ready for high-performance dating app development!"
