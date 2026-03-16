#!/bin/bash

# =============================================================================
# Database - Script de Backup Automatizado (Cron)
# =============================================================================
# Adicione ao crontab: 0 2 * * * /opt/database/scripts/backup-cron.sh
# =============================================================================

set -e

# Configurações
BACKUP_DIR="/opt/database/backups"
DATA_DIR="/opt/database/data"
LOG_FILE="/var/log/database/backup-cron.log"
RETENTION_DAYS=7
DATE=$(date +%Y%m%d_%H%M%S)

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Funções
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERRO: $1${NC}" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] SUCESSO: $1${NC}" | tee -a "$LOG_FILE"
}

# Criar diretório de backup se não existir
mkdir -p "$BACKUP_DIR"

log "Iniciando backup automatizado..."

# Backup das configurações
log "Backup das configurações..."
tar -czf "$BACKUP_DIR/config_$DATE.tar.gz" -C "$DATA_DIR" . 2>/dev/null || {
    log_error "Falha ao fazer backup das configurações"
    exit 1
}
log_success "Configurações salvas em config_$DATE.tar.gz"

# Backup completo (se PostgreSQL estiver configurado)
if command -v pg_dump &> /dev/null; then
    log "Backup do PostgreSQL..."
    
    # Carregar configuração
    if [ -f "$DATA_DIR/db_config.json" ]; then
        DB_NAME=$(cat "$DATA_DIR/db_config.json" | grep -o '"database": "[^"]*"' | cut -d'"' -f4)
        DB_USER=$(cat "$DATA_DIR/db_config.json" | grep -o '"username": "[^"]*"' | cut -d'"' -f4)
        
        if [ -n "$DB_NAME" ]; then
            pg_dump -U "${DB_USER:-postgres}" -d "$DB_NAME" > "$BACKUP_DIR/postgresql_$DATE.sql" 2>/dev/null || {
                log "PostgreSQL backup não realizado (pode não estar configurado)"
            }
            
            if [ -f "$BACKUP_DIR/postgresql_$DATE.sql" ]; then
                gzip "$BACKUP_DIR/postgresql_$DATE.sql"
                log_success "PostgreSQL salvo em postgresql_$DATE.sql.gz"
            fi
        fi
    fi
fi

# Limpar backups antigos
log "Limpando backups antigos (mais de $RETENTION_DAYS dias)..."
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete 2>/dev/null || true
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete 2>/dev/null || true
log_success "Limpeza de backups antigos concluída"

# Enviar notificação (opcional)
BACKUP_COUNT=$(find "$BACKUP_DIR" -name "*$DATE*" | wc -l)
log "Backup concluído. Arquivos criados: $BACKUP_COUNT"

# Verificar espaço em disco
DISK_USAGE=$(df -h "$BACKUP_DIR" | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 80 ]; then
    log_error "ALERTA: Uso de disco em ${DISK_USAGE}%"
else
    log "Uso de disco: ${DISK_USAGE}%"
fi

log_success "Backup automatizado concluído com sucesso!"
exit 0
