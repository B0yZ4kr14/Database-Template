#!/bin/bash

# =============================================================================
# Database - Script de Validação
# =============================================================================
# Valida a instalação e configuração do Database
# =============================================================================

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Contadores
TESTS_PASSED=0
TESTS_FAILED=0

# Funções
print_header() {
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║           Database - Validação de Instalação                   ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
    ((TESTS_PASSED++))
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
    ((TESTS_FAILED++))
}

print_info() {
    echo -e "${YELLOW}→ $1${NC}"
}

print_section() {
    echo ""
    echo -e "${BLUE}$1${NC}"
    echo "────────────────────────────────────────────────────────────────"
}

# =============================================================================
# TESTES
# =============================================================================

print_header

# Diretórios
print_section "📁 Verificando Diretórios"

if [ -d "/opt/database" ]; then
    print_success "Diretório /opt/database existe"
else
    print_error "Diretório /opt/database não encontrado"
fi

if [ -d "/opt/database/backend" ]; then
    print_success "Diretório /opt/database/backend existe"
else
    print_error "Diretório /opt/database/backend não encontrado"
fi

if [ -d "/opt/database/frontend" ]; then
    print_success "Diretório /opt/database/frontend existe"
else
    print_error "Diretório /opt/database/frontend não encontrado"
fi

if [ -d "/opt/database/data" ]; then
    print_success "Diretório /opt/database/data existe"
else
    print_error "Diretório /opt/database/data não encontrado"
fi

if [ -d "/opt/database/backups" ]; then
    print_success "Diretório /opt/database/backups existe"
else
    print_error "Diretório /opt/database/backups não encontrado"
fi

# Arquivos do Backend
print_section "🔧 Verificando Arquivos do Backend"

if [ -f "/opt/database/backend/main.py" ]; then
    print_success "main.py existe"
else
    print_error "main.py não encontrado"
fi

if [ -f "/opt/database/backend/requirements.txt" ]; then
    print_success "requirements.txt existe"
else
    print_error "requirements.txt não encontrado"
fi

if [ -f "/opt/database/backend/wsgi.py" ]; then
    print_success "wsgi.py existe"
else
    print_error "wsgi.py não encontrado"
fi

if [ -d "/opt/database/backend/venv" ]; then
    print_success "Ambiente virtual existe"
else
    print_error "Ambiente virtual não encontrado"
fi

# Arquivos do Frontend
print_section "🎨 Verificando Arquivos do Frontend"

if [ -f "/opt/database/frontend/package.json" ]; then
    print_success "package.json existe"
else
    print_error "package.json não encontrado"
fi

if [ -d "/opt/database/frontend/dist" ]; then
    print_success "Build do frontend existe"
else
    print_error "Build do frontend não encontrado (execute 'make build')"
fi

# Configuração Nginx
print_section "🌐 Verificando Configuração Nginx"

if [ -f "/etc/nginx/sites-available/database.conf" ]; then
    print_success "Configuração Nginx existe"
else
    print_error "Configuração Nginx não encontrada"
fi

if [ -L "/etc/nginx/sites-enabled/database.conf" ]; then
    print_success "Configuração Nginx ativada"
else
    print_error "Configuração Nginx não ativada"
fi

# Configuração Systemd
print_section "⚙️ Verificando Configuração Systemd"

if [ -f "/etc/systemd/system/database-backend.service" ]; then
    print_success "Serviço systemd existe"
else
    print_error "Serviço systemd não encontrado"
fi

# Serviços
print_section "🚀 Verificando Serviços"

if systemctl is-active --quiet database-backend 2>/dev/null; then
    print_success "Serviço backend está rodando"
else
    print_error "Serviço backend não está rodando"
fi

if systemctl is-active --quiet nginx 2>/dev/null; then
    print_success "Serviço nginx está rodando"
else
    print_error "Serviço nginx não está rodando"
fi

# Testes de API
print_section "🔌 Testando API"

API_RESPONSE=$(curl -s http://localhost:8000/api/health 2>/dev/null || echo "")
if [ -n "$API_RESPONSE" ]; then
    print_success "API está respondendo"
    echo "    Resposta: $API_RESPONSE"
else
    print_error "API não está respondendo"
fi

# Teste de endpoints
ENDPOINTS=(
    "/api/config"
    "/api/engines"
    "/api/connection-history"
)

for endpoint in "${ENDPOINTS[@]}"; do
    RESPONSE=$(curl -s "http://localhost:8000$endpoint" 2>/dev/null || echo "")
    if [ -n "$RESPONSE" ]; then
        print_success "Endpoint $endpoint respondendo"
    else
        print_error "Endpoint $endpoint não responde"
    fi
done

# Permissões
print_section "🔐 Verificando Permissões"

if [ "$(stat -c '%U' /opt/database/data 2>/dev/null)" = "www-data" ]; then
    print_success "Permissões de /opt/database/data corretas"
else
    print_error "Permissões de /opt/database/data incorretas"
fi

# Logs
print_section "📝 Verificando Logs"

if [ -d "/var/log/database" ]; then
    print_success "Diretório de logs existe"
else
    print_error "Diretório de logs não encontrado"
fi

# Bancos de Dados (Opcional)
print_section "🗄️ Verificando Bancos de Dados (Opcional)"

if command -v psql &> /dev/null; then
    if systemctl is-active --quiet postgresql 2>/dev/null; then
        print_success "PostgreSQL está rodando"
    else
        print_info "PostgreSQL instalado mas não está rodando"
    fi
else
    print_info "PostgreSQL não instalado"
fi

if command -v mysql &> /dev/null; then
    if systemctl is-active --quiet mariadb 2>/dev/null; then
        print_success "MariaDB está rodando"
    else
        print_info "MariaDB instalado mas não está rodando"
    fi
else
    print_info "MariaDB não instalado"
fi

# =============================================================================
# RESUMO
# =============================================================================

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗"
echo "║                      RESUMO                                    ║"
echo "╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}Testes passados: $TESTS_PASSED${NC}"
echo -e "${RED}Testes falhos: $TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ Todos os testes passaram! Instalação válida.${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️ Alguns testes falharam. Verifique os erros acima.${NC}"
    exit 1
fi
