#!/bin/bash

# =============================================================================
# Database - Health Check Script
# =============================================================================
# Verifica a saúde do sistema Database
# Uso: ./health-check.sh [--json]
# =============================================================================

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Flags
JSON_OUTPUT=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --json)
            JSON_OUTPUT=true
            shift
            ;;
        *)
            echo "Uso: $0 [--json]"
            exit 1
            ;;
    esac
done

# Resultados
declare -A CHECKS
OVERALL_STATUS="healthy"

# Funções
check_service() {
    local name=$1
    local service=$2
    
    if systemctl is-active --quiet "$service" 2>/dev/null; then
        CHECKS[$name]="healthy"
        return 0
    else
        CHECKS[$name]="unhealthy"
        OVERALL_STATUS="unhealthy"
        return 1
    fi
}

check_api() {
    local response
    response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/health 2>/dev/null || echo "000")
    
    if [ "$response" = "200" ]; then
        CHECKS["api"]="healthy"
        return 0
    else
        CHECKS["api"]="unhealthy (HTTP $response)"
        OVERALL_STATUS="unhealthy"
        return 1
    fi
}

check_disk() {
    local usage
    usage=$(df -h /opt/database | awk 'NR==2 {print $5}' | sed 's/%//')
    
    if [ "$usage" -lt 80 ]; then
        CHECKS["disk"]="healthy (${usage}%)"
        return 0
    elif [ "$usage" -lt 90 ]; then
        CHECKS["disk"]="warning (${usage}%)"
        [ "$OVERALL_STATUS" = "healthy" ] && OVERALL_STATUS="warning"
        return 0
    else
        CHECKS["disk"]="critical (${usage}%)"
        OVERALL_STATUS="unhealthy"
        return 1
    fi
}

check_memory() {
    local usage
    usage=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
    
    if [ "$usage" -lt 80 ]; then
        CHECKS["memory"]="healthy (${usage}%)"
        return 0
    elif [ "$usage" -lt 90 ]; then
        CHECKS["memory"]="warning (${usage}%)"
        [ "$OVERALL_STATUS" = "healthy" ] && OVERALL_STATUS="warning"
        return 0
    else
        CHECKS["memory"]="critical (${usage}%)"
        OVERALL_STATUS="unhealthy"
        return 1
    fi
}

# Executar verificações
check_service "backend" "database-backend"
check_service "nginx" "nginx"
check_api
check_disk
check_memory

# Timestamp
TIMESTAMP=$(date -Iseconds)

# Output
if [ "$JSON_OUTPUT" = true ]; then
    # JSON output
    echo "{"
    echo "  \"status\": \"$OVERALL_STATUS\","
    echo "  \"timestamp\": \"$TIMESTAMP\","
    echo "  \"checks\": {"
    first=true
    for key in "${!CHECKS[@]}"; do
        if [ "$first" = true ]; then
            first=false
        else
            echo ","
        fi
        printf '    "%s": "%s"' "$key" "${CHECKS[$key]}"
    done
    echo ""
    echo "  }"
    echo "}"
else
    # Pretty output
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗"
    echo -e "║           Database - Health Check                              ║"
    echo -e "╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Timestamp: $TIMESTAMP"
    echo ""
    
    # Status geral
    if [ "$OVERALL_STATUS" = "healthy" ]; then
        echo -e "Status Geral: ${GREEN}✓ HEALTHY${NC}"
    elif [ "$OVERALL_STATUS" = "warning" ]; then
        echo -e "Status Geral: ${YELLOW}⚠ WARNING${NC}"
    else
        echo -e "Status Geral: ${RED}✗ UNHEALTHY${NC}"
    fi
    echo ""
    
    # Checks individuais
    echo "Verificações:"
    for key in "${!CHECKS[@]}"; do
        value="${CHECKS[$key]}"
        if [[ "$value" == healthy* ]]; then
            echo -e "  ${GREEN}✓${NC} $key: $value"
        elif [[ "$value" == warning* ]]; then
            echo -e "  ${YELLOW}⚠${NC} $key: $value"
        elif [[ "$value" == critical* ]] || [[ "$value" == unhealthy* ]]; then
            echo -e "  ${RED}✗${NC} $key: $value"
        fi
    done
    echo ""
fi

# Exit code
if [ "$OVERALL_STATUS" = "healthy" ]; then
    exit 0
elif [ "$OVERALL_STATUS" = "warning" ]; then
    exit 1
else
    exit 2
fi
