#!/bin/bash

# =============================================================================
# Database - Exemplos de Uso da API
# =============================================================================
# Script com exemplos práticos de uso da API
# =============================================================================

API_URL="${API_URL:-http://localhost:8000/api}"

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Função para imprimir seção
print_section() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
}

# Função para executar e mostrar comando
run_cmd() {
    echo ""
    echo -e "${YELLOW}$ $1${NC}"
    eval "$1" | jq . 2>/dev/null || eval "$1"
}

# =============================================================================
# EXEMPLOS
# =============================================================================

echo -e "${GREEN}"
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║           Database - Exemplos de API                           ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""
echo "API URL: $API_URL"
echo ""

# Health Check
print_section "1. Health Check"
run_cmd "curl -s $API_URL/health"

# Listar motores
print_section "2. Listar Motores Disponíveis"
run_cmd "curl -s $API_URL/engines"

# Obter configuração atual
print_section "3. Obter Configuração Atual"
run_cmd "curl -s $API_URL/config"

# Salvar configuração PostgreSQL
print_section "4. Salvar Configuração PostgreSQL"
run_cmd "curl -s -X POST $API_URL/config -H 'Content-Type: application/json' -d '{\"engine\":\"postgresql\",\"host\":\"localhost\",\"port\":5432,\"database\":\"orthoplus\",\"username\":\"postgres\",\"password\":\"\",\"ssl_mode\":\"prefer\"}'"

# Testar conexão
print_section "5. Testar Conexão"
run_cmd "curl -s -X POST $API_URL/test-connection -H 'Content-Type: application/json' -d '{\"engine\":\"postgresql\",\"host\":\"localhost\",\"port\":5432,\"database\":\"orthoplus\",\"username\":\"postgres\",\"password\":\"\"}'"

# Obter histórico
print_section "6. Obter Histórico de Conexões"
run_cmd "curl -s $API_URL/connection-history"

# Listar ferramentas de manutenção
print_section "7. Ferramentas de Manutenção (PostgreSQL)"
run_cmd "curl -s $API_URL/maintenance/tools/postgresql"

# Obter documentação
print_section "8. Documentação do PostgreSQL"
run_cmd "curl -s $API_URL/docs/postgresql"

# Obter configuração de backup
print_section "9. Configuração de Backup"
run_cmd "curl -s $API_URL/backup/config"

# Salvar configuração de backup
print_section "10. Salvar Configuração de Backup"
run_cmd "curl -s -X POST $API_URL/backup/config -H 'Content-Type: application/json' -d '{\"auto_backup\":true,\"interval\":\"daily\",\"retention_days\":7,\"compression\":true,\"encryption\":false}'"

# Obter histórico de backups
print_section "11. Histórico de Backups"
run_cmd "curl -s $API_URL/backup/history"

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Exemplos concluídos!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo "Para mais exemplos, consulte: docs/API_EXAMPLES.md"
