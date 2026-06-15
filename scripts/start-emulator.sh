#!/bin/bash
# Emulator startup script that works with swiftshader software rendering
# Use: ./scripts/start-emulator.sh [avd_name]
# Default AVD: DatingApp_Pixel6_API33

AVD="${1:-DatingApp_Pixel6_API33}"
MEMORY="${2:-8192}"

echo "🚀 Starting emulator: $AVD ($MEMORY MB, swiftshader_indirect)"

pkill -f "qemu.*avd" 2>/dev/null
sleep 1

VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/lvp_icd.json \
  emulator -avd "$AVD" \
  -gpu swiftshader_indirect \
  -no-snapshot \
  -memory "$MEMORY" \
  -netdelay none \
  -netspeed full \
  -no-audio &

EMU_PID=$!

echo "⏳ Waiting for emulator to boot..."
for i in $(seq 1 30); do
    sleep 5
    STATE=$(adb get-state 2>/dev/null)
    if [ "$STATE" = "device" ]; then
        BOOT=$(adb shell getprop sys.boot_completed 2>/dev/null | tr -d '\r')
        if [ "$BOOT" = "1" ]; then
            echo "✅ Emulator ready after $((i*5))s (PID=$EMU_PID)"
            echo "📱 Window should be visible now"
            exit 0
        fi
    fi
    echo "   waiting... ($((i*5))s)"
done

echo "⚠️  Emulator started but may still be booting (PID=$EMU_PID)"
