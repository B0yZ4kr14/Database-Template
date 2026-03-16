#!/bin/bash

# =============================================================================
# Database - Monitoramento em Tempo Real
# =============================================================================
# Monitora métricas do sistema Database
# Uso: ./monitor.sh [--interval SEGUNDOS]
# =============================================================================

INTERVAL=5

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --interval)
            INTERVAL="$2"
            shift 2
            ;;
        *)
            echo "Uso: $0 [--interval SEGUNDOS]"
            exit 1
            ;;
    esac
done

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Limpar tela e esconder cursor
clear
tput civis

# Função de limpeza
cleanup() {
    tput cnorm
    clear
    exit 0
}
trap cleanup INT TERM EXIT

# Função para obter métricas
get_metrics() {
    # CPU
    CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    
    # Memória
    MEM_TOTAL=$(free -m | awk 'NR==2{printf "%.0f", $2}')
    MEM_USED=$(free -m | awk 'NR==2{printf "%.0f", $3}')
    MEM_PERCENT=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
    
    # Disco
    DISK_USAGE=$(df -h /opt/database 2>/dev/null | awk 'NR==2 {print $5}' | sed 's/%//' || echo "N/A")
    DISK_AVAIL=$(df -h /opt/database 2>/dev/null | awk 'NR==2 {print $4}' || echo "N/A")
    
    # Conexões API
    API_REQUESTS=$(curl -s http://localhost:8000/api/health 2>/dev/null | wc -c)
    
    # Status serviços
    BACKEND_STATUS=$(systemctl is-active database-backend 2>/dev/null || echo "unknown")
    NGINX_STATUS=$(systemctl is-active nginx 2>/dev/null || echo "unknown")
}

# Função para desenhar barra de progresso
draw_bar() {
    local value=$1
    local max=100
    local width=30
    local filled=$((value * width / max))
    local empty=$((width - filled))
    
    if [ "$value" -lt 50 ]; then
        color="$GREEN"
    elif [ "$value" -lt 80 ]; then
        color="$YELLOW"
    else
        color="$RED"
    fi
    
    printf "${color}"
    printf '['
    printf '%0.s█' $(seq 1 $filled)
    printf '%0.s░' $(seq 1 $empty)
    printf ']${NC} %3d%%' "$value"
}

# Loop principal
while true; do
    get_metrics
    
    # Posicionar cursor no topo
    tput cup 0 0
    
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════════════════╗"
    echo -e "║                    Database - Monitoramento em Tempo Real                    ║"
    echo -e "╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${CYAN}Atualizado: $(date '+%Y-%m-%d %H:%M:%S') | Intervalo: ${INTERVAL}s${NC}"
    echo ""
    
    # Status dos serviços
    echo -e "${YELLOW}Serviços:${NC}"
    if [ "$BACKEND_STATUS" = "active" ]; then
        echo -e "  Backend:  ${GREEN}●${NC} $BACKEND_STATUS"
    else
        echo -e "  Backend:  ${RED}●${NC} $BACKEND_STATUS"
    fi
    
    if [ "$NGINX_STATUS" = "active" ]; then
        echo -e "  Nginx:    ${GREEN}●${NC} $NGINX_STATUS"
    else
        echo -e "  Nginx:    ${RED}●${NC} $NGINX_STATUS"
    fi
    echo ""
    
    # CPU
    echo -e "${YELLOW}CPU:${NC}"
    printf "  Uso: "
    draw_bar ${CPU_USAGE%.*}
    echo ""
    echo ""
    
    # Memória
    echo -e "${YELLOW}Memória:${NC}"
    printf "  Uso: "
    draw_bar $MEM_PERCENT
    echo " (${MEM_USED}MB / ${MEM_TOTAL}MB)"
    echo ""
    
    # Disco
    echo -e "${YELLOW}Disco (/opt/database):${NC}"
    if [ "$DISK_USAGE" != "N/A" ]; then
        printf "  Uso: "
        draw_bar $DISK_USAGE
        echo " (Disponível: $DISK_AVAIL)"
    else
        echo "  Diretório não encontrado"
    fi
    echo ""
    
    # API
    echo -e "${YELLOW}API:${NC}"
    if [ "$API_REQUESTS" -gt 0 ]; then
        echo -e "  Status: ${GREEN}✓${NC} Respondendo"
    else
        echo -e "  Status: ${RED}✗${NC} Não responde"
    fi
    echo ""
    
    # Logs recentes
    echo -e "${YELLOW}Logs Recentes:${NC}"
    journalctl -u database-backend --since "1 minute ago" --no-pager -n 3 2>/dev/null | tail -3 || echo "  Nenhum log recente"
    echo ""
    
    echo -e "${CYAN}Pressione Ctrl+C para sair${NC}"
    
    sleep $INTERVAL
done
