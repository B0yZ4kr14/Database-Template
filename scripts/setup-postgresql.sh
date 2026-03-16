#!/bin/bash

# =============================================================================
# Database - Configuração do PostgreSQL
# =============================================================================
# Configura PostgreSQL para uso com o Database
# Cria banco, usuário e configura permissões
# =============================================================================

set -e

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configurações padrão
DB_NAME="${DB_NAME:-orthoplus}"
DB_USER="${DB_USER:-dbuser}"
DB_PASS="${DB_PASS:-$(openssl rand -base64 16)}"
PG_VERSION="${PG_VERSION:-14}"

print_header() {
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║           Configuração do PostgreSQL                           ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}→ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Verificar se está rodando como root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        print_error "Este script precisa ser executado como root"
        exit 1
    fi
}

# Instalar PostgreSQL
install_postgresql() {
    print_info "Instalando PostgreSQL..."
    
    apt update
    apt install -y postgresql postgresql-contrib
    
    # Iniciar serviço
    systemctl enable postgresql
    systemctl start postgresql
    
    print_success "PostgreSQL instalado"
}

# Criar banco de dados
create_database() {
    print_info "Criando banco de dados: $DB_NAME"
    
    sudo -u postgres psql -c "CREATE DATABASE $DB_NAME;" 2>/dev/null || {
        print_info "Banco $DB_NAME já existe"
    }
    
    print_success "Banco de dados criado"
}

# Criar usuário
create_user() {
    print_info "Criando usuário: $DB_USER"
    
    # Verificar se usuário existe
    USER_EXISTS=$(sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" 2>/dev/null)
    
    if [ "$USER_EXISTS" = "1" ]; then
        print_info "Usuário $DB_USER já existe, atualizando senha..."
        sudo -u postgres psql -c "ALTER USER $DB_USER WITH PASSWORD '$DB_PASS';"
    else
        sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';"
    fi
    
    print_success "Usuário criado/atualizado"
}

# Configurar permissões
setup_permissions() {
    print_info "Configurando permissões..."
    
    # Conceder permissões no banco
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
    
    # Conceder permissões em schemas
    sudo -u postgres psql -d "$DB_NAME" -c "GRANT ALL ON SCHEMA public TO $DB_USER;"
    sudo -u postgres psql -d "$DB_NAME" -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO $DB_USER;"
    
    print_success "Permissões configuradas"
}

# Configurar acesso local (md5)
configure_access() {
    print_info "Configurando acesso local..."
    
    PG_HBA="/etc/postgresql/$PG_VERSION/main/pg_hba.conf"
    
    # Backup do arquivo original
    if [ ! -f "$PG_HBA.backup" ]; then
        cp "$PG_HBA" "$PG_HBA.backup"
    fi
    
    # Verificar se já existe configuração
    if ! grep -q "database_config" "$PG_HBA" 2>/dev/null; then
        # Adicionar configuração para acesso local
        cat >> "$PG_HBA" << EOF

# Database Configuration
local   $DB_NAME    $DB_USER                            md5
host    $DB_NAME    $DB_USER    127.0.0.1/32            md5
host    $DB_NAME    $DB_USER    ::1/128                 md5
EOF
    fi
    
    # Recarregar configuração
    systemctl reload postgresql
    
    print_success "Acesso configurado"
}

# Configurar postgresql.conf para melhor performance
configure_performance() {
    print_info "Otimizando configurações de performance..."
    
    PG_CONF="/etc/postgresql/$PG_VERSION/main/postgresql.conf"
    
    # Backup
    if [ ! -f "$PG_CONF.backup" ]; then
        cp "$PG_CONF" "$PG_CONF.backup"
    fi
    
    # Configurações recomendadas
    cat >> "$PG_CONF" << 'EOF'

# Database Performance Settings
shared_buffers = 256MB
effective_cache_size = 768MB
maintenance_work_mem = 64MB
work_mem = 4MB
max_connections = 100
EOF
    
    systemctl restart postgresql
    
    print_success "Performance otimizada"
}

# Testar conexão
test_connection() {
    print_info "Testando conexão..."
    
    # Criar arquivo .pgpass para teste
    export PGPASSWORD="$DB_PASS"
    
    if psql -h localhost -U "$DB_USER" -d "$DB_NAME" -c "SELECT version();" > /dev/null 2>&1; then
        print_success "Conexão testada com sucesso!"
    else
        print_error "Falha no teste de conexão"
        print_info "Verifique as configurações em $PG_HBA"
    fi
    
    unset PGPASSWORD
}

# Mostrar informações
show_info() {
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗"
    echo "║              Configuração Concluída!                           ║"
    echo "╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}Credenciais de Acesso:${NC}"
    echo "  Host: localhost"
    echo "  Porta: 5432"
    echo "  Banco: $DB_NAME"
    echo "  Usuário: $DB_USER"
    echo "  Senha: $DB_PASS"
    echo ""
    echo -e "${BLUE}Configuração para Database:${NC}"
    echo "  Engine: PostgreSQL"
    echo "  Host: localhost"
    echo "  Porta: 5432"
    echo "  Banco: $DB_NAME"
    echo "  Usuário: $DB_USER"
    echo "  Senha: $DB_PASS"
    echo ""
    echo -e "${YELLOW}IMPORTANTE: Salve estas informações em um local seguro!${NC}"
    echo ""
    
    # Salvar em arquivo
    CRED_FILE="/opt/database/data/postgresql-credentials.txt"
    mkdir -p "$(dirname "$CRED_FILE")"
    cat > "$CRED_FILE" << EOF
PostgreSQL Credentials - Database
Generated: $(date)

Host: localhost
Port: 5432
Database: $DB_NAME
Username: $DB_USER
Password: $DB_PASS

Connection String:
postgresql://$DB_USER:$DB_PASS@localhost:5432/$DB_NAME
EOF
    chmod 600 "$CRED_FILE"
    
    print_info "Credenciais salvas em: $CRED_FILE"
}

# Menu interativo
interactive_setup() {
    print_header
    
    echo ""
    read -p "Nome do banco de dados [orthoplus]: " input_db_name
    DB_NAME="${input_db_name:-$DB_NAME}"
    
    read -p "Nome do usuário [dbuser]: " input_db_user
    DB_USER="${input_db_user:-$DB_USER}"
    
    read -sp "Senha do usuário (deixe em branco para gerar automático): " input_db_pass
    echo
    DB_PASS="${input_db_pass:-$DB_PASS}"
    
    echo ""
    echo "Resumo da configuração:"
    echo "  Banco: $DB_NAME"
    echo "  Usuário: $DB_USER"
    read -p "Confirmar? (S/n): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        main
    else
        echo "Configuração cancelada."
        exit 0
    fi
}

# Função principal
main() {
    check_root
    
    # Verificar se PostgreSQL está instalado
    if ! command -v psql &> /dev/null; then
        install_postgresql
    else
        print_success "PostgreSQL já instalado"
        PG_VERSION=$(psql --version | awk '{print $3}' | cut -d. -f1)
    fi
    
    create_database
    create_user
    setup_permissions
    configure_access
    
    read -p "Deseja otimizar configurações de performance? (s/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        configure_performance
    fi
    
    test_connection
    show_info
}

# Verificar argumentos
if [ "$1" = "--auto" ]; then
    # Modo automático (não interativo)
    check_root
    install_postgresql
    create_database
    create_user
    setup_permissions
    configure_access
    show_info
elif [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "Uso: $0 [opções]"
    echo ""
    echo "Opções:"
    echo "  --auto     Modo automático (não interativo)"
    echo "  --help     Mostra esta ajuda"
    echo ""
    echo "Variáveis de ambiente:"
    echo "  DB_NAME    Nome do banco (padrão: orthoplus)"
    echo "  DB_USER    Nome do usuário (padrão: dbuser)"
    echo "  DB_PASS    Senha do usuário (padrão: gerado automaticamente)"
    echo ""
    exit 0
else
    # Modo interativo
    interactive_setup
fi
