#!/bin/bash
# DejTing Dev Tools — single entry point for all dev operations

set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FLUTTER_DIR="/home/m/development/mobile-apps/flutter/dejtingapp"

GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; BOLD='\033[1m'; DIM='\033[2m'; NC='\033[0m'

check_port() { curl -sf -o /dev/null -w "%{http_code}" "http://localhost:$1/health" 2>/dev/null; }

show_status() {
    echo ""
    printf "  ${BOLD}%-22s %-6s %s${NC}\n" "SERVICE" "PORT" "STATUS"
    echo "  ──────────────────────────────────────"
    declare -A services=(
        [YARP Gateway]=8080
        [UserService]=8082
        [MatchmakingService]=8083
        [PhotoService]=8085
        [MessagingService]=8086
        [SwipeService]=8087
        [SafetyService]=8088
    )
    local order=("YARP Gateway" "UserService" "MatchmakingService" "PhotoService" "MessagingService" "SwipeService" "SafetyService")
    for name in "${order[@]}"; do
        port=${services[$name]}
        code=$(check_port "$port")
        if [[ "$code" =~ ^(200|404)$ ]]; then
            printf "  %-22s %-6s ${GREEN}● UP${NC}\n" "$name" "$port"
        else
            printf "  %-22s %-6s ${RED}● DOWN${NC}\n" "$name" "$port"
        fi
    done
    kc=$(curl -sf -o /dev/null -w "%{http_code}" "http://localhost:8090/realms/master" 2>/dev/null)
    if [[ "$kc" =~ ^(200|302)$ ]]; then
        printf "  %-22s %-6s ${GREEN}● UP${NC}\n" "Keycloak" "8090"
    else
        printf "  %-22s %-6s ${RED}● DOWN${NC}\n" "Keycloak" "8090"
    fi
    local dbs_running=$(docker ps --format '{{.Names}}' 2>/dev/null | grep -c -E 'db|keycloak' || echo 0)
    printf "  %-22s %-6s ${CYAN}${dbs_running} containers${NC}\n" "Docker DBs" ""
    if pgrep -f "flutter.*run" >/dev/null 2>&1; then
        printf "  %-22s %-6s ${GREEN}● RUNNING${NC}\n" "Flutter App" ""
    else
        printf "  %-22s %-6s ${YELLOW}● NOT RUNNING${NC}\n" "Flutter App" ""
    fi
    echo ""
}

show_menu() {
    echo ""
    echo -e "  ${BOLD}${CYAN}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "  ${BOLD}${CYAN}║              DejTing Dev Tools                           ║${NC}"
    echo -e "  ${BOLD}${CYAN}╚══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "  ${BOLD}${GREEN}★  1) Launch everything${NC}"
    echo -e "     ${DIM}Start infra → start services → wait for health → seed data → launch Flutter${NC}"
    echo -e "     ${DIM}This is what you want on a fresh boot. Takes ~30s.${NC}"
    echo ""
    echo -e "  ${BOLD}── Backend ──${NC}"
    echo -e "  ${BOLD}2${NC}) Start backend       ${DIM}Start Docker DBs + Keycloak, then all 7 .NET services${NC}"
    echo -e "  ${BOLD}3${NC}) Stop backend        ${DIM}Kill all .NET services, then stop Docker containers${NC}"
    echo -e "  ${BOLD}4${NC}) Restart backend     ${DIM}Stop + start (useful after code changes)${NC}"
    echo -e "  ${BOLD}5${NC}) Status              ${DIM}Show health of all services, DBs, Flutter${NC}"
    echo ""
    echo -e "  ${BOLD}── Data ──${NC}"
    echo -e "  ${BOLD}6${NC}) Seed data           ${DIM}Create test users (alice/bob/charlie/diana/erik) + swipes + matches${NC}"
    echo -e "  ${BOLD}7${NC}) Reset + re-seed     ${DIM}Truncate all tables, re-create everything from scratch${NC}"
    echo ""
    echo -e "  ${BOLD}── App & Testing ──${NC}"
    echo -e "  ${BOLD}8${NC}) Run Flutter         ${DIM}Launch the Flutter app on Linux desktop${NC}"
    echo -e "  ${BOLD}9${NC}) API smoke tests     ${DIM}Run api_tests.py — auth, profiles, matching, messaging${NC}"
    echo ""
    echo -e "  ${BOLD}── Other ──${NC}"
    echo -e "  ${BOLD}l${NC}) Logs               ${DIM}Tail service logs (pick which service)${NC}"
    echo -e "  ${BOLD}0${NC}) Exit"
    echo ""
    echo -e "  ${DIM}──────────────────────────────────────────────────────────${NC}"
    echo -e "  ${DIM}Typical workflow: 1 (first time) → make changes → 4 (restart) → 8 (flutter)${NC}"
    echo -e "  ${DIM}Test users: alice/bob/charlie/diana/erik @test.se  password: Test123!${NC}"
    echo -e "  ${DIM}Matches: alice↔bob, bob↔charlie  |  Messages: bob↔charlie${NC}"
    echo ""
}

wait_for_health() {
    echo -e "  ${CYAN}Waiting for services to be healthy...${NC}"
    local ports=(8080 8082 8083 8085 8086 8087 8088)
    local names=("YARP" "UserService" "Matchmaking" "PhotoService" "Messaging" "SwipeService" "SafetyService")
    local max_wait=60
    local elapsed=0
    while [ $elapsed -lt $max_wait ]; do
        local all_up=true
        for port in "${ports[@]}"; do
            code=$(check_port "$port")
            if ! [[ "$code" =~ ^(200|404)$ ]]; then
                all_up=false
                break
            fi
        done
        if $all_up; then
            echo -e "  ${GREEN}All services healthy ✓${NC}"
            return 0
        fi
        sleep 2
        elapsed=$((elapsed + 2))
        printf "\r  ${DIM}  ...waiting (%ds / %ds)${NC}" "$elapsed" "$max_wait"
    done
    echo ""
    echo -e "  ${YELLOW}⚠ Some services didn't come up in ${max_wait}s — check with option 5${NC}"
    return 1
}

do_start() {
    echo -e "\n  ${CYAN}▶ Starting infrastructure (Docker DBs + Keycloak)...${NC}"
    cd "$ROOT" && bash infrastructure/start.sh
    echo -e "\n  ${CYAN}▶ Starting all .NET services...${NC}"
    bash dev-start.sh
}

do_stop() {
    echo -e "\n  ${CYAN}■ Stopping .NET services...${NC}"
    cd "$ROOT" && bash dev-stop.sh
    echo -e "\n  ${CYAN}■ Stopping Docker containers...${NC}"
    bash infrastructure/stop.sh
}

do_seed() {
    echo -e "\n  ${CYAN}🌱 Seeding minimal test data...${NC}"
    echo -e "  ${DIM}Creates: 5 Keycloak users → 5 profiles → 7 swipes → 2 matches → 2 messages${NC}"
    cd "$ROOT" && bash scripts/seed-test-data.sh minimal
}

do_reset() {
    echo -e "\n  ${CYAN}🔄 Truncating all tables + re-seeding from scratch...${NC}"
    cd "$ROOT" && make quick-reset
}

do_flutter() {
    if ! [ -d "$FLUTTER_DIR" ]; then
        echo -e "  ${RED}Flutter dir not found: $FLUTTER_DIR${NC}"
        return
    fi
    if pgrep -f "flutter.*run" >/dev/null 2>&1; then
        echo -e "  ${YELLOW}Flutter is already running. Kill it first? (y/n)${NC}"
        read -rp "  > " yn
        if [[ "$yn" == "y" ]]; then
            pkill -f "flutter.*run" 2>/dev/null
            sleep 2
        else
            return
        fi
    fi
    echo -e "\n  ${CYAN}📱 Launching Flutter on Linux desktop...${NC}"
    echo -e "  ${DIM}Hot reload: r  |  Hot restart: R  |  Quit: q${NC}"
    cd "$FLUTTER_DIR" && flutter run -d linux &
    echo -e "  ${GREEN}Flutter launching in background.${NC}"
}

do_tests() {
    echo -e "\n  ${CYAN}🧪 Running API smoke tests (auth → profiles → matching → messaging)...${NC}"
    cd "$ROOT" && python3 api_tests.py
}

do_logs() {
    echo ""
    echo "  Pick a service log to tail (Ctrl+C to stop):"
    echo ""
    echo "    a) UserService         e) SwipeService"
    echo "    b) MatchmakingService  f) SafetyService"
    echo "    c) PhotoService        g) YARP Gateway"
    echo "    d) MessagingService    q) Back"
    echo ""
    read -rp "  Log [a-g/q]: " logpick
    local logfile=""
    case "$logpick" in
        a) logfile="logs/user-service.log" ;;
        b) logfile="logs/matchmaking-service.log" ;;
        c) logfile="logs/photo-service.log" ;;
        d) logfile="logs/messaging-service.log" ;;
        e) logfile="logs/swipe-service.log" ;;
        f) logfile="logs/safety-service.log" ;;
        g) logfile="logs/yarp-gateway.log" ;;
        *) return ;;
    esac
    if [ -f "$ROOT/$logfile" ]; then
        echo -e "  ${CYAN}Tailing $logfile (Ctrl+C to stop)...${NC}"
        tail -f "$ROOT/$logfile"
    else
        echo -e "  ${RED}Log file not found: $logfile${NC}"
        echo -e "  ${DIM}Services may not have started yet, or logs dir doesn't exist.${NC}"
    fi
}

do_launch_everything() {
    echo ""
    echo -e "  ${BOLD}${GREEN}★ LAUNCHING EVERYTHING${NC}"
    echo -e "  ${DIM}Step 1/4: Start infrastructure (Docker DBs + Keycloak)${NC}"
    echo -e "  ${DIM}Step 2/4: Start all .NET services + wait for healthy${NC}"
    echo -e "  ${DIM}Step 3/4: Seed test data (users, swipes, matches, messages)${NC}"
    echo -e "  ${DIM}Step 4/4: Launch Flutter app${NC}"
    echo ""

    # Step 1+2: Start backend
    do_start

    # Wait for services
    wait_for_health

    # Step 3: Seed
    do_seed

    # Step 4: Flutter
    do_flutter

    echo ""
    echo -e "  ${BOLD}${GREEN}✅ Everything is up! Open the Flutter app and log in.${NC}"
    echo -e "  ${DIM}Try: alice@test.se / Test123!${NC}"
    echo ""
}

# ── CLI mode (./dev.sh <command>) ──
if [ $# -gt 0 ]; then
    case "$1" in
        all)     do_launch_everything ;;
        start)   do_start ;;
        stop)    do_stop ;;
        status)  show_status ;;
        restart) do_stop; sleep 2; do_start ;;
        seed)    do_seed ;;
        reset)   do_reset ;;
        flutter) do_flutter ;;
        test)    do_tests ;;
        logs)    do_logs ;;
        help|-h|--help)
            echo ""
            echo "  Usage: ./dev.sh [command]"
            echo ""
            echo "  Commands:"
            echo "    all       Launch everything (infra → services → seed → flutter)"
            echo "    start     Start backend (Docker + .NET services)"
            echo "    stop      Stop backend (services + Docker)"
            echo "    restart   Stop + start"
            echo "    status    Show health of all services"
            echo "    seed      Seed test data (5 users, matches, messages)"
            echo "    reset     Truncate all tables + re-seed"
            echo "    flutter   Launch Flutter app on Linux desktop"
            echo "    test      Run API smoke tests"
            echo "    logs      Tail service logs"
            echo ""
            echo "  No command → interactive menu"
            echo ""
            ;;
        *)
            echo "  Unknown command: $1"
            echo "  Run ./dev.sh help for usage"
            ;;
    esac
    exit 0
fi

# ── Interactive menu loop ──
while true; do
    show_menu
    read -rp "  Pick [0-9/l]: " choice
    case "$choice" in
        1) do_launch_everything ;;
        2) do_start ;;
        3) do_stop ;;
        4) do_stop; sleep 2; do_start ;;
        5) show_status ;;
        6) do_seed ;;
        7) do_reset ;;
        8) do_flutter ;;
        9) do_tests ;;
        l|L) do_logs ;;
        0) echo -e "  ${GREEN}Bye!${NC}"; exit 0 ;;
        *) echo -e "  ${RED}Invalid choice${NC}" ;;
    esac
done
