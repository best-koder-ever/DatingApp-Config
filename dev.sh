#!/bin/bash
# DejTing Dev Tools — single entry point for all dev operations

set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FLUTTER_DIR="/home/m/development/mobile-apps/flutter/dejtingapp"

GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

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
    # Keycloak
    kc=$(curl -sf -o /dev/null -w "%{http_code}" "http://localhost:8090/realms/master" 2>/dev/null)
    if [[ "$kc" =~ ^(200|302)$ ]]; then
        printf "  %-22s %-6s ${GREEN}● UP${NC}\n" "Keycloak" "8090"
    else
        printf "  %-22s %-6s ${RED}● DOWN${NC}\n" "Keycloak" "8090"
    fi
    # Docker DBs
    local dbs_running=$(docker ps --format '{{.Names}}' 2>/dev/null | grep -c -E 'db|keycloak' || echo 0)
    printf "  %-22s %-6s ${CYAN}${dbs_running} containers${NC}\n" "Docker DBs" ""
    # Flutter
    if pgrep -f "flutter.*run" >/dev/null 2>&1; then
        printf "  %-22s %-6s ${GREEN}● RUNNING${NC}\n" "Flutter App" ""
    else
        printf "  %-22s %-6s ${YELLOW}● NOT RUNNING${NC}\n" "Flutter App" ""
    fi
    echo ""
}

show_menu() {
    echo ""
    echo -e "  ${BOLD}${CYAN}DejTing Dev Tools${NC}"
    echo "  ─────────────────────────────────"
    echo -e "  ${BOLD}1${NC}) Start backend      ${BOLD}5${NC}) Seed data"
    echo -e "  ${BOLD}2${NC}) Stop backend       ${BOLD}6${NC}) Reset + re-seed"
    echo -e "  ${BOLD}3${NC}) Status             ${BOLD}7${NC}) Run Flutter (linux)"
    echo -e "  ${BOLD}4${NC}) Restart backend    ${BOLD}8${NC}) API smoke tests"
    echo -e "  ${BOLD}9${NC}) Logs               ${BOLD}0${NC}) Exit"
    echo "  ─────────────────────────────────"
}

do_start() {
    echo -e "\n  ${CYAN}Starting infrastructure...${NC}"
    cd "$ROOT" && bash infrastructure/start.sh
    echo -e "\n  ${CYAN}Starting services...${NC}"
    bash dev-start.sh
}

do_stop() {
    echo -e "\n  ${CYAN}Stopping services...${NC}"
    cd "$ROOT" && bash dev-stop.sh
    echo -e "\n  ${CYAN}Stopping infrastructure...${NC}"
    bash infrastructure/stop.sh
}

do_seed() {
    echo -e "\n  ${CYAN}Seeding minimal test data...${NC}"
    cd "$ROOT" && bash scripts/seed-test-data.sh minimal
}

do_reset() {
    echo -e "\n  ${CYAN}Truncating tables + re-seeding...${NC}"
    cd "$ROOT" && make quick-reset
}

do_flutter() {
    if ! [ -d "$FLUTTER_DIR" ]; then
        echo -e "  ${RED}Flutter dir not found: $FLUTTER_DIR${NC}"
        return
    fi
    echo -e "\n  ${CYAN}Launching Flutter on Linux desktop...${NC}"
    cd "$FLUTTER_DIR" && flutter run -d linux &
    echo -e "  ${GREEN}Flutter launching in background.${NC}"
}

do_tests() {
    echo -e "\n  ${CYAN}Running API smoke tests...${NC}"
    cd "$ROOT" && python3 api_tests.py
}

do_logs() {
    echo ""
    echo "  Pick a service log:"
    echo "    a) UserService       e) SwipeService"
    echo "    b) MatchmakingService f) SafetyService"
    echo "    c) PhotoService      g) YARP Gateway"
    echo "    d) MessagingService  q) Back"
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
    echo -e "  ${CYAN}Tailing $logfile (Ctrl+C to stop)...${NC}"
    tail -f "$ROOT/$logfile"
}

# If argument passed, run directly
if [ $# -gt 0 ]; then
    case "$1" in
        start)   do_start ;;
        stop)    do_stop ;;
        status)  show_status ;;
        restart) do_stop; sleep 2; do_start ;;
        seed)    do_seed ;;
        reset)   do_reset ;;
        flutter) do_flutter ;;
        test)    do_tests ;;
        *)       echo "Usage: $0 {start|stop|status|restart|seed|reset|flutter|test}" ;;
    esac
    exit 0
fi

# Interactive menu loop
while true; do
    show_menu
    read -rp "  Pick [0-9]: " choice
    case "$choice" in
        1) do_start ;;
        2) do_stop ;;
        3) show_status ;;
        4) do_stop; sleep 2; do_start ;;
        5) do_seed ;;
        6) do_reset ;;
        7) do_flutter ;;
        8) do_tests ;;
        9) do_logs ;;
        0) echo -e "  ${GREEN}Bye!${NC}"; exit 0 ;;
        *) echo -e "  ${RED}Invalid choice${NC}" ;;
    esac
done
