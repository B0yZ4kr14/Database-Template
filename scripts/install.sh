#!/bin/bash

# =============================================================================
# Database - Script de Instalação para Ubuntu Server LTS
# =============================================================================
# Autor: Database Team
# Versão: 2.0.2
# Compatibilidade: Ubuntu 22.04 LTS, Ubuntu 24.04 LTS
# =============================================================================

set -e  # Exit on error

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variáveis
INSTALL_DIR="/opt/database"
LOG_DIR="/var/log/database"
BACKUP_DIR="/opt/database/backups"
DATA_DIR="/opt/database/data"
CURRENT_USER=$(whoami)

# Funções de utilidade
print_header() {
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║          Database - Instalação Ubuntu LTS                      ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}→ $1${NC}"
}

print_step() {
    echo -e "${BLUE}[$(date +%H:%M:%S)] $1${NC}"
}

# Verificar root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        print_error "Este script precisa ser executado como root ou com sudo"
        exit 1
    fi
}

# Verificar versão do Ubuntu
check_ubuntu_version() {
    print_step "Verificando versão do Ubuntu..."
    
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        if [[ "$ID" != "ubuntu" ]]; then
            print_error "Este script é projetado para Ubuntu Server LTS"
            exit 1
        fi
        
        VERSION_ID=$(echo "$VERSION_ID" | cut -d. -f1)
        if [[ "$VERSION_ID" != "22" && "$VERSION_ID" != "24" ]]; then
            print_warning "Versão do Ubuntu não testada: $VERSION_ID"
            read -p "Deseja continuar mesmo assim? (s/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Ss]$ ]]; then
                exit 1
            fi
        fi
        
        print_success "Ubuntu $VERSION_ID detectado"
    else
        print_error "Não foi possível detectar a versão do sistema"
        exit 1
    fi
}

# Atualizar sistema
update_system() {
    print_step "Atualizando sistema..."
    apt update && apt upgrade -y
    print_success "Sistema atualizado"
}

# Instalar dependências do sistema
install_system_deps() {
    print_step "Instalando dependências do sistema..."
    
    apt install -y \
        curl \
        wget \
        git \
        build-essential \
        software-properties-common \
        apt-transport-https \
        ca-certificates \
        gnupg \
        lsb-release
    
    print_success "Dependências do sistema instaladas"
}

# Instalar Python
install_python() {
    print_step "Instalando Python..."
    
    apt install -y \
        python3 \
        python3-pip \
        python3-venv \
        python3-dev \
        python3-psycopg2 \
        libpq-dev
    
    # Verificar instalação
    PYTHON_VERSION=$(python3 --version)
    print_success "Python instalado: $PYTHON_VERSION"
}

# Instalar Node.js
install_nodejs() {
    print_step "Instalando Node.js..."
    
    # Adicionar repositório NodeSource
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt install -y nodejs
    
    # Verificar instalação
    NODE_VERSION=$(node --version)
    NPM_VERSION=$(npm --version)
    print_success "Node.js $NODE_VERSION instalado"
    print_success "npm $NPM_VERSION instalado"
}

# Instalar Nginx
install_nginx() {
    print_step "Instalando Nginx..."
    
    apt install -y nginx
    
    # Configurar firewall
    if command -v ufw &> /dev/null; then
        ufw allow 'Nginx Full'
        ufw allow OpenSSH
    fi
    
    print_success "Nginx instalado"
}

# Criar estrutura de diretórios
create_directories() {
    print_step "Criando estrutura de diretórios..."
    
    mkdir -p "$INSTALL_DIR"/{backend,frontend,data,backups,logs}
    mkdir -p "$LOG_DIR"
    mkdir -p "$DATA_DIR"
    mkdir -p "$BACKUP_DIR"
    
    # Definir permissões
    chown -R www-data:www-data "$INSTALL_DIR"
    chmod -R 755 "$INSTALL_DIR"
    
    print_success "Diretórios criados em $INSTALL_DIR"
}

# Configurar backend
setup_backend() {
    print_step "Configurando backend..."
    
    cd "$INSTALL_DIR/backend"
    
    # Criar ambiente virtual
    python3 -m venv venv
    source venv/bin/activate
    
    # Instalar dependências
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Desativar ambiente virtual
    deactivate
    
    print_success "Backend configurado"
}

# Configurar frontend
setup_frontend() {
    print_step "Configurando frontend..."
    
    cd "$INSTALL_DIR/frontend"
    
    # Instalar dependências
    npm install
    
    # Build para produção
    npm run build
    
    print_success "Frontend configurado"
}

# Configurar Nginx
setup_nginx() {
    print_step "Configurando Nginx..."
    
    cat > /etc/nginx/sites-available/database << 'EOF'
server {
    listen 80;
    server_name _;
    
    root /opt/database/frontend/dist;
    index index.html;
    
    # Frontend
    location / {
        try_files $uri $uri/ /index.html;
        add_header Cache-Control "no-cache";
    }
    
    # API Backend
    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 86400;
    }
    
    # Documentação API
    location /docs {
        proxy_pass http://127.0.0.1:8000/docs;
        proxy_set_header Host $host;
    }
    
    location /redoc {
        proxy_pass http://127.0.0.1:8000/redoc;
        proxy_set_header Host $host;
    }
    
    # Logs
    access_log /var/log/nginx/database-access.log;
    error_log /var/log/nginx/database-error.log;
}
EOF
    
    # Ativar site
    ln -sf /etc/nginx/sites-available/database /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default
    
    # Testar configuração
    nginx -t
    
    # Reiniciar Nginx
    systemctl restart nginx
    
    print_success "Nginx configurado"
}

# Configurar systemd
setup_systemd() {
    print_step "Configurando serviço systemd..."
    
    cat > /etc/systemd/system/database-backend.service << EOF
[Unit]
Description=Database Backend API
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=$INSTALL_DIR/backend
Environment=PATH=$INSTALL_DIR/backend/venv/bin
Environment=PYTHONPATH=$INSTALL_DIR/backend
ExecStart=$INSTALL_DIR/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
    
    # Recarregar systemd
    systemctl daemon-reload
    
    # Habilitar e iniciar serviço
    systemctl enable database-backend
    systemctl start database-backend
    
    print_success "Serviço systemd configurado"
}

# Instalar bancos de dados opcionais
install_databases() {
    print_step "Instalando bancos de dados (opcional)..."
    
    read -p "Instalar PostgreSQL? (s/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        apt install -y postgresql postgresql-contrib
        systemctl enable postgresql
        systemctl start postgresql
        print_success "PostgreSQL instalado"
    fi
    
    read -p "Instalar MariaDB? (s/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        apt install -y mariadb-server mariadb-client
        systemctl enable mariadb
        systemctl start mariadb
        print_success "MariaDB instalado"
    fi
    
    read -p "Instalar Firebird? (s/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        apt install -y firebird3.0-server
        print_success "Firebird instalado"
    fi
}

# Verificar instalação
verify_installation() {
    print_step "Verificando instalação..."
    
    # Verificar backend
    if systemctl is-active --quiet database-backend; then
        print_success "Backend está rodando"
    else
        print_error "Backend não está rodando"
        systemctl status database-backend
    fi
    
    # Verificar Nginx
    if systemctl is-active --quiet nginx; then
        print_success "Nginx está rodando"
    else
        print_error "Nginx não está rodando"
    fi
    
    # Testar API
    sleep 2
    if curl -s http://localhost:8000/api/health > /dev/null; then
        print_success "API respondendo"
    else
        print_error "API não está respondendo"
    fi
}

# Mostrar informações finais
show_final_info() {
    echo -e "${GREEN}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║              Instalação Concluída com Sucesso!                 ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
    echo -e "${BLUE}Informações de Acesso:${NC}"
    echo "  • Interface Web: http://$(hostname -I | awk '{print $1}')"
    echo "  • API Docs: http://$(hostname -I | awk '{print $1}')/docs"
    echo "  • Diretório de Instalação: $INSTALL_DIR"
    echo "  • Logs: $LOG_DIR"
    echo ""
    echo -e "${BLUE}Comandos Úteis:${NC}"
    echo "  • Ver logs do backend: sudo journalctl -u database-backend -f"
    echo "  • Reiniciar backend: sudo systemctl restart database-backend"
    echo "  • Status do backend: sudo systemctl status database-backend"
    echo "  • Ver logs do Nginx: sudo tail -f /var/log/nginx/database-error.log"
    echo ""
    echo -e "${YELLOW}Próximos Passos:${NC}"
    echo "  1. Configure seu banco de dados (PostgreSQL, MariaDB, etc.)"
    echo "  2. Acesse a interface web e configure a conexão"
    echo "  3. Consulte a documentação em /opt/database/docs/"
    echo ""
}

# Função principal
main() {
    print_header
    
    check_root
    check_ubuntu_version
    
    print_info "Iniciando instalação do Database..."
    print_info "Este processo pode levar alguns minutos."
    echo ""
    
    update_system
    install_system_deps
    install_python
    install_nodejs
    install_nginx
    create_directories
    
    # Copiar arquivos (assumindo que estão no diretório atual)
    print_step "Copiando arquivos..."
    cp -r backend/* "$INSTALL_DIR/backend/"
    cp -r frontend/* "$INSTALL_DIR/frontend/"
    cp -r docs "$INSTALL_DIR/"
    print_success "Arquivos copiados"
    
    setup_backend
    setup_frontend
    setup_nginx
    setup_systemd
    
    install_databases
    
    verify_installation
    show_final_info
}

# Executar instalação
main "$@"
