# Guia de Migração - Database v2.0.2

Este guia ajuda você a migrar de versões anteriores do Database.

---

## Resumo das Alterações

A versão 2.0.2 inclui correções de bugs e melhorias de código após análise completa do projeto.

### Principais Mudanças da v2.0.1 para v2.0.2

- Correções de inconsistências entre backend e frontend
- Melhorias na segurança (SHA256 para checksums)
- Prevenção de SQL injection em manutenção
- Correção de race conditions em storage

### Migração da v2.0.0 ou anterior

Se estiver migrando da v2.0.0 ou anterior, note que houve uma **refatoração completa da arquitetura backend**:

- Estrutura modular reorganizada
- Novos endpoints de API
- Modelos Pydantic atualizados

---

## Alterações de Caminhos

Os caminhos permanecem os mesmos desde a v2.0.0:

### Diretórios

| Caminho | Descrição |
|--------|------|
| `/opt/database` | Diretório principal |
| `/var/log/database` | Logs do sistema |
| `/opt/database/data` | Dados persistentes |
| `/opt/database/backups` | Backups |

### Serviços Systemd

| Serviço | Descrição |
|--------|------|
| `database-backend.service` | API Backend |

### Configuração Nginx

| Arquivo | Descrição |
|--------|------|
| `database.conf` | Configuração do site |

### Containers Docker

| Container | Descrição |
|--------|------|
| `database-backend` | API FastAPI |
| `database-frontend` | Frontend Nginx |
| `database-postgres` | PostgreSQL (opcional) |
| `database-mariadb` | MariaDB (opcional) |
| `database-network` | Rede Docker |

---

## Passos para Migração

### 1. Backup dos Dados

Antes de migrar, faça backup de todos os dados:

```bash
# Backup do diretório de dados
sudo cp -r /opt/database/data /opt/database/data.backup

# Backup dos backups existentes
sudo cp -r /opt/database/backups /opt/database/backups.backup

# Backup das configurações
sudo cp -r /opt/database /opt/database.full.backup
```

### 2. Parar os Serviços Antigos

```bash
# Parar o serviço backend
sudo systemctl stop database-backend
sudo systemctl disable database-backend

# Parar nginx (se necessário)
sudo systemctl stop nginx
```

### 3. Criar Nova Estrutura de Diretórios

```bash
# Criar novos diretórios
sudo mkdir -p /opt/database/{backend,frontend,data,backups,logs}
sudo mkdir -p /var/log/database

# Definir permissões
sudo chown -R www-data:www-data /opt/database
sudo chown -R www-data:www-data /var/log/database
```

### 4. Migrar os Dados

```bash
# Copiar dados para novo local
sudo cp -r /opt/database/data/* /opt/database/data/
sudo cp -r /opt/database/backups/* /opt/database/backups/

# Ajustar permissões
sudo chown -R www-data:www-data /opt/database/data
sudo chown -R www-data:www-data /opt/database/backups
```

### 5. Instalar Nova Versão

```bash
# Clone ou copie os novos arquivos
cd /opt/database

# Copiar backend
sudo cp -r /caminho/para/novo/backend/* /opt/database/backend/

# Copiar frontend
sudo cp -r /caminho/para/novo/frontend/* /opt/database/frontend/

# Configurar ambiente virtual do backend
cd /opt/database/backend
sudo python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate

# Build do frontend
cd /opt/database/frontend
npm install
npm run build
```

### 6. Configurar Novo Serviço Systemd

```bash
# Remover serviço antigo
sudo rm -f /etc/systemd/system/database-backend.service

# Copiar novo serviço
sudo cp /opt/database/systemd/database-backend.service /etc/systemd/system/

# Recarregar systemd
sudo systemctl daemon-reload

# Habilitar e iniciar novo serviço
sudo systemctl enable database-backend
sudo systemctl start database-backend
```

### 7. Configurar Nginx

```bash
# Remover configuração antiga
sudo rm -f /etc/nginx/sites-available/database
sudo rm -f /etc/nginx/sites-enabled/database

# Copiar nova configuração
sudo cp /opt/database/nginx/database.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/database.conf /etc/nginx/sites-enabled/

# Testar configuração
sudo nginx -t

# Reiniciar nginx
sudo systemctl restart nginx
```

### 8. Verificar Instalação

```bash
# Verificar status do backend
sudo systemctl status database-backend

# Verificar logs
sudo journalctl -u database-backend -f

# Testar API
curl http://localhost:8000/api/health

# Testar interface web
curl http://localhost
```

### 9. Limpar Arquivos Antigos (Opcional)

Após confirmar que tudo está funcionando:

```bash
# Remover diretório antigo
sudo rm -rf /opt/database

# Remover logs antigos (opcional)
sudo rm -rf /var/log/database

# Remover backups de migração (após alguns dias de uso)
sudo rm -rf /opt/database.full.backup
```

---

## Migração com Docker Compose

Se estiver usando Docker Compose:

```bash
# Parar containers antigos
cd /caminho/para/docker-compose-antigo
docker-compose down

# Fazer backup dos volumes
docker volume ls | grep database

# Copiar dados dos volumes (se necessário)
docker run --rm -v database_data:/source -v /tmp/backup:/backup alpine cp -r /source /backup

# Iniciar nova versão
cd /caminho/para/nova/versao/docker
docker-compose up -d

# Verificar logs
docker-compose logs -f
```

---

## Troubleshooting

### Problema: Permissões negadas

**Solução:**
```bash
sudo chown -R www-data:www-data /opt/database
sudo chmod -R 755 /opt/database
```

### Problema: Serviço não inicia

**Solução:**
```bash
# Verificar logs
sudo journalctl -u database-backend -n 50

# Verificar permissões do diretório
ls -la /opt/database/

# Testar manualmente
cd /opt/database/backend
source venv/bin/activate
python main.py
```

### Problema: Nginx retorna 502

**Solução:**
```bash
# Verificar se backend está rodando
sudo systemctl status database-backend

# Verificar configuração do nginx
sudo nginx -t

# Verificar logs do nginx
sudo tail -f /var/log/nginx/database-error.log
```

### Problema: Dados não aparecem

**Solução:**
```bash
# Verificar se dados foram copiados
ls -la /opt/database/data/

# Verificar permissões
sudo chown www-data:www-data /opt/database/data/*.json
sudo chmod 644 /opt/database/data/*.json
```

---

## Rollback (Se Necessário)

Se precisar voltar para a versão anterior:

```bash
# Parar novos serviços
sudo systemctl stop database-backend
sudo systemctl disable database-backend

# Restaurar backup
sudo rm -rf /opt/database
sudo cp -r /opt/database.full.backup /opt/database

# Restaurar serviço antigo
sudo cp /opt/database/systemd/database-backend.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable database-backend
sudo systemctl start database-backend

# Restaurar nginx
sudo rm -f /etc/nginx/sites-available/database.conf
sudo rm -f /etc/nginx/sites-enabled/database.conf
sudo cp /opt/database/nginx/database.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/database.conf /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

---

## Suporte

Se encontrar problemas durante a migração:

1. Verifique os logs: `sudo journalctl -u database-backend -f`
2. Consulte a documentação em `/opt/database/docs/`
3. Verifique a saúde da API: `curl http://localhost:8000/api/health`
