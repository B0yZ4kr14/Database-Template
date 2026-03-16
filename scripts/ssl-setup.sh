#!/bin/bash

# =============================================================================
# Database - SSL/TLS Setup Script
# =============================================================================
# Configura SSL/TLS com Let's Encrypt
# Uso: sudo ./ssl-setup.sh dominio.com [email]
# =============================================================================

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Verificar root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Este script precisa ser executado como root${NC}"
    exit 1
fi

# Verificar argumentos
if [ $# -lt 1 ]; then
    echo "Uso: $0 dominio.com [email]"
    echo "Exemplo: $0 database.exemplo.com admin@exemplo.com"
    exit 1
fi

DOMAIN=$1
EMAIL=${2:-"admin@$DOMAIN"}

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║           Database - Configuração SSL/TLS                      ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""
echo "Domínio: $DOMAIN"
echo "Email: $EMAIL"
echo ""

# Instalar Certbot
echo -e "${YELLOW}Instalando Certbot...${NC}"
apt update
apt install -y certbot python3-certbot-nginx

# Obter certificado
echo -e "${YELLOW}Obtendo certificado SSL...${NC}"
certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos --email "$EMAIL" || {
    echo -e "${RED}Falha ao obter certificado${NC}"
    exit 1
}

# Configurar renovação automática
echo -e "${YELLOW}Configurando renovação automática...${NC}"
systemctl enable certbot.timer
systemctl start certbot.timer

# Testar renovação
echo -e "${YELLOW}Testando renovação...${NC}"
certbot renew --dry-run

# Atualizar configuração Nginx
echo -e "${YELLOW}Atualizando configuração Nginx...${NC}"
cat > /etc/nginx/sites-available/database-ssl << EOF
server {
    listen 80;
    server_name $DOMAIN;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN;

    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    ssl_trusted_certificate /etc/letsencrypt/live/$DOMAIN/chain.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 1d;
    ssl_session_tickets off;

    add_header Strict-Transport-Security "max-age=63072000" always;

    root /opt/database/frontend/dist;
    index index.html;

    location / {
        try_files \$uri \$uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Ativar configuração
ln -sf /etc/nginx/sites-available/database-ssl /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/database.conf

# Testar e recarregar Nginx
nginx -t && systemctl reload nginx

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗"
echo "║              SSL/TLS Configurado com Sucesso!                  ║"
echo "╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}✓${NC} Certificado obtido para: $DOMAIN"
echo -e "${GREEN}✓${NC} Renovação automática configurada"
echo -e "${GREEN}✓${NC} Nginx configurado para HTTPS"
echo ""
echo "Acesse: https://$DOMAIN"
echo ""
echo "Para renovar manualmente: sudo certbot renew"
