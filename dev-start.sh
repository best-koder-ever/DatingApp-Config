#!/bin/bash

# Local Development Startup Script
# Starts all services for local development
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🚀 Starting Local Development Environment..."

# Source environment files (API keys, shared config)
if [ -f .env.local ]; then
    set -a; source .env.local; set +a
    echo "📋 Loaded .env.local"
fi
if [ -f .env ]; then
    set -a; source .env; set +a
    echo "📋 Loaded .env (API keys)"
fi

check_port() {
    local host="$1"
    local port="$2"
    if command -v timeout >/dev/null 2>&1; then
        if timeout 1 bash -c "cat < /dev/null > /dev/tcp/${host}/${port}" >/dev/null 2>&1; then
            return 0
        fi
    else
        if bash -c "cat < /dev/null > /dev/tcp/${host}/${port}" >/dev/null 2>&1; then
            return 0
        fi
    fi
    return 1
}

ensure_infrastructure() {
    local missing=0

    if ! check_port localhost 8090; then
        echo "❌ Keycloak (localhost:8090) is not reachable."
        missing=1
    fi

    if ! check_port localhost 3309; then
        echo "❌ Matchmaking MySQL (localhost:3309) is not reachable."
        missing=1
    fi

    if [ "$missing" -eq 1 ]; then
        echo "💡 Infrastructure is not running — starting it now (./infrastructure/start.sh)..."
        echo "   (Data persists in Docker volumes across reboots.)"
        if ! bash "${SCRIPT_DIR}/infrastructure/start.sh"; then
            echo "❌ Failed to start infrastructure. Check Docker is running, then try ./infrastructure/start.sh manually."
            exit 1
        fi
        # Re-check after infra starts
        if ! check_port localhost 8090 || ! check_port localhost 3309; then
            echo "❌ Infrastructure started but Keycloak/MySQL are still not reachable."
            exit 1
        fi
        echo "✅ Infrastructure up (Keycloak + DBs)."
    else
        echo "✅ Infrastructure already running (Keycloak + DBs)."
    fi
}

ensure_infrastructure

# Kill any existing processes
echo "🧹 Cleaning up existing processes..."
pkill -f "dotnet" 2>/dev/null || true

# Wait a moment for processes to clean up
sleep 2

# Check if ports are available
echo "🔍 Checking port availability..."
PORTS=(8080 8082 8083 8085 8086 8087 8088 8089)
for port in "${PORTS[@]}"; do
    if lsof -i :$port >/dev/null 2>&1; then
        echo "❌ Port $port is busy - killing processes..."
        pkill -f "$port" 2>/dev/null || true
        sleep 1
    fi
done

# Start UserService
echo "👤 Starting UserService on port 8082..."
cd ${SCRIPT_DIR}/UserService
ASPNETCORE_ENVIRONMENT=Development ASPNETCORE_URLS=http://+:8082 dotnet run > ../logs/user-service.log 2>&1 &
USER_PID=$!
sleep 2

# Start MatchmakingService
echo "� Starting MatchmakingService on port 8083..."
cd ${SCRIPT_DIR}/MatchmakingService
ASPNETCORE_ENVIRONMENT=Development ASPNETCORE_URLS=http://+:8083 dotnet run > ../logs/matchmaking-service.log 2>&1 &
MATCHMAKING_PID=$!
sleep 2

# Start PhotoService  
echo "📸 Starting PhotoService on port 8085..."
cd ${SCRIPT_DIR}/photo-service
ASPNETCORE_ENVIRONMENT=Development ASPNETCORE_URLS=http://+:8085 dotnet run > ../logs/photo-service.log 2>&1 &
PHOTO_PID=$!
sleep 2

# Start MessagingService
echo "💬 Starting MessagingService on port 8086..."
cd ${SCRIPT_DIR}/messaging-service
ASPNETCORE_ENVIRONMENT=Development ASPNETCORE_URLS=http://+:8086 dotnet run > ../logs/messaging-service.log 2>&1 &
MESSAGING_PID=$!
sleep 2

# Start SwipeService
echo "👆 Starting SwipeService on port 8087..."
cd ${SCRIPT_DIR}/swipe-service
ASPNETCORE_ENVIRONMENT=Development ASPNETCORE_URLS=http://+:8087 dotnet run --project SwipeService.csproj > ../logs/swipe-service.log 2>&1 &
SWIPE_PID=$!
sleep 2

# Start SafetyService
echo "🛡️ Starting SafetyService on port 8088..."
cd ${SCRIPT_DIR}/safety-service/SafetyService
ASPNETCORE_ENVIRONMENT=Development ASPNETCORE_URLS=http://+:8088 dotnet run > ../../logs/safety-service.log 2>&1 &
SAFETY_PID=$!
sleep 2

# Start YARP Gateway
echo "🌐 Starting YARP Gateway on port 8080..."
cd ${SCRIPT_DIR}/dejting-yarp/src/dejting-yarp
ASPNETCORE_ENVIRONMENT=Development ASPNETCORE_URLS=http://+:8080 dotnet run > ../../../logs/yarp-gateway.log 2>&1 &
YARP_PID=$!

# Create logs directory if it doesn't exist
mkdir -p ${SCRIPT_DIR}/logs


# Wait for services to start
echo "⏳ Waiting for services to initialize..."
sleep 8


# Health checks
echo "🏥 Performing health checks..."
USER_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8082/health 2>/dev/null || echo "000")
MATCHMAKING_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8083/health 2>/dev/null || echo "000")
PHOTO_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8085/health 2>/dev/null || echo "000")
MESSAGING_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8086/health 2>/dev/null || echo "000")
MESSAGING_READINESS=$(curl -s http://localhost:8086/health 2>/dev/null || echo "")
SWIPE_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8087/health 2>/dev/null || echo "000")
SAFETY_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8088/health 2>/dev/null || echo "000")
YARP_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/health 2>/dev/null || echo "000")

echo ""
echo "📊 Service Status:"
if [ "$USER_HEALTH" = "200" ]; then
    echo "✅ UserService: Running (PID: $USER_PID)"
else
    echo "❌ UserService: Failed to start (HTTP: $USER_HEALTH)"
fi

if [ "$MATCHMAKING_HEALTH" = "200" ]; then
    echo "✅ MatchmakingService: Running (PID: $MATCHMAKING_PID)"
else
    echo "❌ MatchmakingService: Failed to start (HTTP: $MATCHMAKING_HEALTH)"
fi

if [ "$PHOTO_HEALTH" = "200" ]; then
    echo "✅ PhotoService: Running (PID: $PHOTO_PID)"
else
    echo "❌ PhotoService: Failed to start (HTTP: $PHOTO_HEALTH)"
fi

if [ "$MESSAGING_HEALTH" = "200" ]; then
    READY_MSG="$(echo "$MESSAGING_READINESS" | sed -n 's/.*"status"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1)"
    if [ -z "$READY_MSG" ]; then
        READY_MSG=$(echo "$MESSAGING_READINESS" | tr -d '\n' | cut -c1-120)
    fi
    if [ -n "$READY_MSG" ]; then
        echo "✅ MessagingService: Running (PID: $MESSAGING_PID) – readiness: $READY_MSG"
    else
        echo "✅ MessagingService: Running (PID: $MESSAGING_PID)"
    fi
else
    echo "❌ MessagingService: Failed to start (HTTP: $MESSAGING_HEALTH)"
fi

if [ "$SWIPE_HEALTH" = "200" ]; then
    echo "✅ SwipeService: Running (PID: $SWIPE_PID)"
else
    echo "❌ SwipeService: Failed to start (HTTP: $SWIPE_HEALTH)"
fi

if [ "$SAFETY_HEALTH" = "200" ]; then
    echo "✅ SafetyService: Running (PID: $SAFETY_PID)"
else
    echo "❌ SafetyService: Failed to start (HTTP: $SAFETY_HEALTH)"
fi

if [ "$YARP_HEALTH" = "200" ]; then
    echo "✅ YARP Gateway: Running (PID: $YARP_PID)"
else
    echo "❌ YARP Gateway: Failed to start (HTTP: $YARP_HEALTH)"
fi

echo ""
echo "📝 Logs:"
echo "   UserService: tail -f logs/user-service.log"
echo "   MatchmakingService: tail -f logs/matchmaking-service.log"
echo "   PhotoService: tail -f logs/photo-service.log"
echo "   MessagingService: tail -f logs/messaging-service.log"
echo "   SwipeService: tail -f logs/swipe-service.log"
echo "   SafetyService: tail -f logs/safety-service.log"
echo "   YARP Gateway: tail -f logs/yarp-gateway.log"
echo ""
echo "🛑 To stop: ./dev-stop.sh"
echo "🔄 To restart: ./dev-restart.sh"
echo "📊 To check status: ./dev-status.sh"
echo ""
echo "🎯 Complete Dating App Backend Running!"

# Refresh AI context (injects live state into .github/copilot-instructions.md)
if [ -f scripts/generate-ai-context.sh ]; then
    bash scripts/generate-ai-context.sh 2>/dev/null &
fi

echo "💡 All services: 8080(Gateway), 8082(User), 8083(Matchmaking), 8085(Photo), 8086(Messaging), 8087(Swipe), 8088(Safety), 8089(Bot*)"


# Start BotService (on by default, disable with BOT_MODE=false)
if [ "${BOT_MODE:-true}" = "true" ]; then
    echo "🤖 Starting BotService on port 8089..."
    cd ${SCRIPT_DIR}/bot-service/BotService
    # Source .env for API keys (GEMINI_API_KEY etc)
    set -a; source ${SCRIPT_DIR}/.env 2>/dev/null; set +a
    ASPNETCORE_ENVIRONMENT=Development ASPNETCORE_URLS=http://+:8089 dotnet run > ../../logs/bot-service.log 2>&1 &
    BOT_PID=$!
    sleep 3
    BOT_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8089/health 2>/dev/null || echo "000")
    if [ "$BOT_HEALTH" = "200" ]; then
        echo "✅ BotService: Running (PID: $BOT_PID)"
    else
        echo "⚠️  BotService: Starting (HTTP: $BOT_HEALTH) — check logs/bot-service.log"
    fi
else
    echo "🤖 BotService: Skipped (set BOT_MODE=true to enable)"
fi

# Start Whisper feedback transcription watcher (laptop-dev fallback).
# In the full Docker stack the server-side bot-service transcribes voice memos
# itself (WhisperTranscriptionService -> whisper-service). This laptop watcher
# only matters for local dotnet-run dev, where no whisper-service container runs.
if [ "${WHISPER_WATCHER:-true}" = "true" ]; then
    echo "🎤 Starting Whisper feedback watcher (laptop-dev fallback)..."
    if [ -x "$SCRIPT_DIR/.venv/bin/python" ] && [ -f "$SCRIPT_DIR/scripts/process-feedback.py" ]; then
        nohup "$SCRIPT_DIR/.venv/bin/python" "$SCRIPT_DIR/scripts/process-feedback.py" --watch 600 > "$SCRIPT_DIR/logs/whisper-feedback.log" 2>&1 &
        WHISPER_PID=$!
        sleep 2
        if kill -0 "$WHISPER_PID" 2>/dev/null; then
            echo "✅ Whisper watcher: Running (PID: $WHISPER_PID) — logs/whisper-feedback.log"
        else
            echo "⚠️  Whisper watcher exited early — check logs/whisper-feedback.log"
        fi
    else
        echo "⚠️  Whisper watcher skipped: missing .venv/bin/python or scripts/process-feedback.py"
    fi
else
    echo "🎤 Whisper watcher: Skipped (set WHISPER_WATCHER=true to enable the laptop fallback)"
fi
