#!/bin/bash
# AI Agent: ThinkPad P1 System Analysis Script

echo "🤖 AI AGENT: ANALYZING THINKPAD P1 SYSTEM"
echo "========================================="
echo "Target: Optimal Android Emulator Setup"
echo ""

# System Info
echo "💻 HARDWARE ANALYSIS:"
echo "--------------------"
echo "🖥️  CPU Info:"
CPU_INFO=$(lscpu | grep -E "(Model name|CPU\(s\)|Thread|Core|MHz)")
echo "$CPU_INFO"
CPU_CORES=$(nproc)
echo "   📊 Available CPU cores: $CPU_CORES"
echo ""

echo "🧠 Memory Analysis:"
TOTAL_RAM=$(free -h | awk '/^Mem:/ {print $2}')
AVAILABLE_RAM=$(free -h | awk '/^Mem:/ {print $7}')
echo "   Total RAM: $TOTAL_RAM"
echo "   Available RAM: $AVAILABLE_RAM"
echo ""

echo "💾 Storage Analysis:"
df -h / /home | grep -v tmpfs
echo ""

echo "🎮 GPU Detection:"
GPU_INFO=$(lspci | grep -i vga)
echo "   $GPU_INFO"
if command -v nvidia-smi &> /dev/null; then
    echo "   ✅ NVIDIA GPU detected - checking status:"
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits 2>/dev/null || echo "   ⚠️  NVIDIA drivers may need setup"
else
    echo "   ⚠️  NVIDIA tools not detected"
fi
echo ""

# Check existing Android development environment
echo "📱 ANDROID DEVELOPMENT ENVIRONMENT:"
echo "----------------------------------"

# Java check
echo "☕ Java Status:"
if command -v java &> /dev/null; then
    JAVA_VERSION=$(java -version 2>&1 | head -1)
    echo "   ✅ $JAVA_VERSION"
else
    echo "   ❌ Java NOT installed"
fi

# Android SDK check
echo "📱 Android SDK Status:"
if [ -d "$HOME/Android/Sdk" ]; then
    echo "   ✅ Android SDK found: $HOME/Android/Sdk"
    if [ -f "$HOME/Android/Sdk/cmdline-tools/latest/bin/sdkmanager" ]; then
        echo "   ✅ SDK Manager available"
        # Check installed packages
        INSTALLED_PACKAGES=$($HOME/Android/Sdk/cmdline-tools/latest/bin/sdkmanager --list_installed 2>/dev/null | grep -c "system-images")
        echo "   📦 System images installed: $INSTALLED_PACKAGES"
    else
        echo "   ⚠️  SDK Manager not properly configured"
    fi
else
    echo "   ❌ Android SDK NOT found"
fi

# Flutter check
echo "🦋 Flutter Status:"
if command -v flutter &> /dev/null; then
    FLUTTER_VERSION=$(flutter --version | head -1)
    echo "   ✅ $FLUTTER_VERSION"
    
    # Check Flutter doctor for Android
    echo "   🔍 Flutter Android setup:"
    flutter doctor | grep -A 5 "Android toolchain" | sed 's/^/      /'
else
    echo "   ❌ Flutter NOT installed"
fi

# Emulator check
echo "📱 Android Emulator Status:"
if command -v emulator &> /dev/null; then
    echo "   ✅ Emulator command available"
    AVD_COUNT=$(emulator -list-avds 2>/dev/null | wc -l)
    echo "   📊 Existing AVDs: $AVD_COUNT"
    if [ $AVD_COUNT -gt 0 ]; then
        echo "   📱 Available AVDs:"
        emulator -list-avds 2>/dev/null | sed 's/^/      /'
    fi
else
    echo "   ❌ Emulator command NOT available"
fi

# ADB check
echo "🔌 ADB Status:"
if command -v adb &> /dev/null; then
    ADB_VERSION=$(adb version | head -1)
    echo "   ✅ $ADB_VERSION"
    
    # Check for connected devices
    DEVICES=$(adb devices | grep -v "List of devices" | grep -v "^$" | wc -l)
    echo "   📱 Connected devices: $DEVICES"
else
    echo "   ❌ ADB NOT available"
fi

# Hardware acceleration check
echo "⚡ Hardware Acceleration:"
if [ -e /dev/kvm ]; then
    echo "   ✅ KVM available"
    KVM_PERMS=$(ls -la /dev/kvm)
    echo "   🔐 KVM permissions: $KVM_PERMS"
    if groups | grep -q kvm; then
        echo "   ✅ User in KVM group"
    else
        echo "   ⚠️  User NOT in KVM group"
    fi
else
    echo "   ❌ KVM NOT available - emulator will be slow"
fi

# Check your dating app environment
echo "💕 DATING APP ENVIRONMENT:"
echo "-------------------------"
if [ -d "/home/m/development/DatingApp" ]; then
    echo "   ✅ Dating app backend found"
    if [ -f "/home/m/development/DatingApp/docker-compose.yml" ]; then
        echo "   ✅ Docker compose configuration found"
    fi
    
    if [ -d "/home/m/development/mobile-apps/flutter/dejtingapp" ]; then
        echo "   ✅ Flutter app found at: /home/m/development/mobile-apps/flutter/dejtingapp"
        cd /home/m/development/mobile-apps/flutter/dejtingapp
        if [ -f "pubspec.yaml" ]; then
            echo "   ✅ Flutter project valid"
            # Check if it's configured for Android
            if grep -q "android:" pubspec.yaml || [ -d "android" ]; then
                echo "   ✅ Android configuration present"
            else
                echo "   ⚠️  Android configuration may be missing"
            fi
        fi
    else
        echo "   ⚠️  Flutter app directory not found"
    fi
    
    # Check Flutter SDK location
    if [ -d "/home/m/development/tools/flutter" ]; then
        echo "   ✅ Flutter SDK organized in tools directory"
    elif [ -d "/home/m/development/flutter" ]; then
        echo "   ⚠️  Flutter SDK in old location (consider moving to tools/)"
    fi
else
    echo "   ⚠️  Dating app directory not found"
fi

# Docker check (for backend)
echo "🐳 Docker Status:"
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    echo "   ✅ $DOCKER_VERSION"
    if docker ps &> /dev/null; then
        echo "   ✅ Docker daemon running"
        RUNNING_CONTAINERS=$(docker ps --format "table {{.Names}}" | grep -v NAMES | wc -l)
        echo "   📊 Running containers: $RUNNING_CONTAINERS"
    else
        echo "   ⚠️  Docker daemon not running"
    fi
else
    echo "   ❌ Docker NOT installed"
fi

echo ""
echo "🎯 AI ANALYSIS SUMMARY:"
echo "======================"

# Determine optimal emulator configuration for basic dating app
OPTIMAL_RAM=4096
OPTIMAL_CORES=4

# For basic apps, 4 cores is optimal regardless of host CPU count
# This leaves resources for IDE, build tools, and browser
echo "💡 RECOMMENDED EMULATOR SPECS (OPTIMIZED FOR BASIC APP):"
echo "   🧠 RAM: ${OPTIMAL_RAM}MB (4GB - perfect for dating app)"
echo "   🖥️  CPU Cores: $OPTIMAL_CORES (optimal for basic app + Android OS)"
echo "   🎮 GPU: Host acceleration"
echo "   📱 Target: Pixel 6 Pro API 33"
echo ""

# Generate installation plan
echo "📋 INSTALLATION PLAN:"
if ! command -v java &> /dev/null; then
    echo "   1️⃣  Install OpenJDK 11"
fi
if [ ! -d "$HOME/Android/Sdk" ]; then
    echo "   2️⃣  Install Android SDK"
fi
if ! command -v flutter &> /dev/null; then
    echo "   3️⃣  Install Flutter"
fi
if [ ! -e /dev/kvm ]; then
    echo "   4️⃣  Setup KVM acceleration"
fi
if [ $(emulator -list-avds 2>/dev/null | wc -l) -eq 0 ]; then
    echo "   5️⃣  Create optimized AVD"
fi

echo ""
echo "✅ System analysis complete! Ready for automated setup."

# Save analysis to file for other scripts
cat > /tmp/thinkpad_analysis.env << EOF
CPU_CORES=$CPU_CORES
OPTIMAL_RAM=$OPTIMAL_RAM
OPTIMAL_CORES=$OPTIMAL_CORES
TOTAL_RAM=$TOTAL_RAM
HAS_JAVA=$(command -v java &> /dev/null && echo "true" || echo "false")
HAS_ANDROID_SDK=$([ -d "$HOME/Android/Sdk" ] && echo "true" || echo "false")
HAS_FLUTTER=$(command -v flutter &> /dev/null && echo "true" || echo "false")
HAS_KVM=$([ -e /dev/kvm ] && echo "true" || echo "false")
HAS_EMULATOR=$(command -v emulator &> /dev/null && echo "true" || echo "false")
EOF

echo "📊 Analysis data saved to /tmp/thinkpad_analysis.env"
