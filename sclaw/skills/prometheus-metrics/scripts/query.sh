#!/bin/bash
# Prometheus Metrics Query Script
# Usage: ./query.sh <query_type> [options]

set -e

PROM_URL="${PROMETHEUS_URL:-http://localhost:9090}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

print_metric() {
    printf "${GREEN}%-30s${NC} %s\n" "$1" "$2"
}

# URL encode function
url_encode() {
    python3 -c "import urllib.parse; print(urllib.parse.quote('''$1'''))"
}

# Query Prometheus API
query() {
    local promql="$1"
    local encoded=$(url_encode "$promql")
    curl -s "$PROM_URL/api/v1/query?query=$encoded" | jq -r '.data.result[]? | .value[1]'
}

query_with_labels() {
    local promql="$1"
    local encoded=$(url_encode "$promql")
    curl -s "$PROM_URL/api/v1/query?query=$encoded" | jq -r '.data.result[]? | "\(.metric.instance): \(.value[1])"'
}

case "${1:-help}" in
    status)
        print_header "Prometheus Server Status"
        curl -s "$PROM_URL/api/v1/query?query=up" | jq -r '.data.result[] | select(.value[1] == "1") | "\(.metric.instance) ✅ UP"'
        ;;
    
    cpu)
        print_header "CPU Usage (5m avg)"
        query_with_labels '100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m]))) * 100' | while read line; do
            value=$(echo "$line" | awk -F': ' '{print $2}')
            instance=$(echo "$line" | awk -F': ' '{print $1}')
            if (( $(echo "$value > 80" | bc -l 2>/dev/null || echo 0) )); then
                print_metric "$instance" "${RED}${value%.*}% 🔴${NC}"
            elif (( $(echo "$value > 50" | bc -l 2>/dev/null || echo 0) )); then
                print_metric "$instance" "${YELLOW}${value%.*}% 🟡${NC}"
            else
                print_metric "$instance" "${GREEN}${value%.*}% 🟢${NC}"
            fi
        done
        ;;
    
    memory)
        print_header "Memory Usage"
        query_with_labels '(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100' | while read line; do
            value=$(echo "$line" | awk -F': ' '{print $2}')
            instance=$(echo "$line" | awk -F': ' '{print $1}')
            print_metric "$instance" "${value%.*}%"
        done
        ;;
    
    disk)
        print_header "Disk Usage (/)"
        query_with_labels '(1 - (node_filesystem_avail_bytes / node_filesystem_size_bytes)) * 100' | grep -v "boot\|snap" | while read line; do
            value=$(echo "$line" | awk -F': ' '{print $2}')
            instance=$(echo "$line" | awk -F': ' '{print $1}')
            print_metric "$instance" "${value%.*}%"
        done
        ;;
    
    network)
        print_header "Network Traffic (5m avg)"
        print_header "  Receive"
        query_with_labels 'rate(node_network_receive_bytes_total{device!="lo"}[5m])' | head -5 | while read line; do
            echo "  $line"
        done
        print_header "  Transmit"
        query_with_labels 'rate(node_network_transmit_bytes_total{device!="lo"}[5m])' | head -5 | while read line; do
            echo "  $line"
        done
        ;;
    
    targets)
        print_header "Target Status"
        curl -s "$PROM_URL/api/v1/targets" | jq -r '.data.activeTargets[] | "\(.labels.job)/\(.labels.instance): \(.health)"'
        ;;
    
    alerts)
        print_header "Active Alerts"
        curl -s "$PROM_URL/api/v1/rules" | jq -r '.data.groups[].rules[]? | select(.type == "alerting" and .health == "ok") | "\(.name): \(.labels.severity // "none")"'
        ;;
    
    all|health)
        print_header "📊 Server Health Overview"
        echo ""
        $0 status
        echo ""
        $0 cpu
        echo ""
        $0 memory
        echo ""
        $0 disk
        ;;
    
    custom)
        if [ -z "$2" ]; then
            echo "Usage: $0 custom <promql>"
            exit 1
        fi
        shift
        promql="$*"
        echo "Query: $promql"
        echo "---"
        encoded=$(url_encode "$promql")
        curl -s "$PROM_URL/api/v1/query?query=$encoded" | jq '.'
        ;;
    
    help|*)
        echo "Prometheus Metrics Query Tool"
        echo ""
        echo "Usage: $0 <command> [options]"
        echo ""
        echo "Commands:"
        echo "  status    - Show server status (up/down)"
        echo "  cpu       - CPU usage by instance"
        echo "  memory    - Memory usage by instance"
        echo "  disk      - Disk usage by instance"
        echo "  network   - Network traffic"
        echo "  targets   - All target status"
        echo "  alerts    - Active alerts"
        echo "  all       - Full health overview"
        echo "  custom    - Custom PromQL query"
        echo "  help      - Show this help"
        echo ""
        echo "Environment:"
        echo "  PROMETHEUS_URL - Prometheus server URL (default: http://localhost:9090)"
        echo ""
        echo "Examples:"
        echo "  $0 all"
        echo "  $0 cpu"
        echo "  $0 custom 'up{job=\"node\"}'"
        ;;
esac
