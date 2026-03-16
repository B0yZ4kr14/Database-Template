# Database - Documentação para Desenvolvedores

## Índice

1. [Visão Geral](#visão-geral)
2. [Arquitetura do Sistema](#arquitetura-do-sistema)
3. [Estrutura do Backend](#estrutura-do-backend)
4. [Estrutura do Frontend](#estrutura-do-frontend)
5. [API Reference](#api-reference)
6. [Guia de Instalação](#guia-de-instalação)
7. [Configuração de Banco de Dados](#configuração-de-banco-de-dados)
8. [Deploy em Produção](#deploy-em-produção)
9. [Troubleshooting](#troubleshooting)
10. [Contribuindo](#contribuindo)

---

## Visão Geral

O **Database** é uma aplicação web completa para configuração, gerenciamento e manutenção de múltiplos motores de banco de dados. Desenvolvido especificamente para **Ubuntu Server LTS**, oferece uma interface moderna e intuitiva.

### Funcionalidades Principais

- **4 Motores Suportados**: SQLite, PostgreSQL, MariaDB, Firebird
- **6 Tabs de Configuração**: Motor, Config, Reparo, Migração, Templates, Docs
- **Ferramentas de Manutenção**: VACUUM, ANALYZE, REINDEX, etc.
- **Backup Local**: Completo e Incremental com agendamento
- **Migração Assistida**: Entre diferentes motores
- **Persistência**: Configurações salvas em JSON

### Stack Tecnológico

| Componente | Tecnologia | Versão |
|------------|------------|--------|
| Backend | Python/FastAPI | 3.11+ |
| Frontend | React/TypeScript | 18+ |
| Estilização | Tailwind CSS | 3.4+ |
| Build Tool | Vite | 5.1+ |
| Servidor Web | Nginx | 1.24+ |

---

## Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                        Nginx (80/443)                       │
│                    (Reverse Proxy + Static)                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
         ┌─────────────┴─────────────┐
         │                           │
┌────────▼─────────┐      ┌──────────▼──────────┐
│  Frontend        │      │  Backend (FastAPI)  │
│  React/Vite      │      │  Port: 8000         │
│  Port: 3000      │      │                     │
└──────────────────┘      └──────────┬──────────┘
                                     │
                        ┌────────────┴────────────┐
                        │                         │
               ┌────────▼─────────┐   ┌──────────▼──────────┐
               │  Config JSON     │   │  Connection Tests   │
               │  /opt/database/  │   │  (SQLite, PG,       │
               │  data/           │   │  MariaDB, Firebird) │
               └──────────────────┘   └─────────────────────┘
```

---

## Estrutura do Backend

O backend segue uma arquitetura modular:

```
backend/
├── app/
│   ├── api/                   # Rotas da API
│   │   └── routes/
│   │       ├── health.py      # Health check
│   │       ├── config.py      # Configurações
│   │       ├── engines.py     # Motores de BD
│   │       ├── connection.py  # Teste de conexão
│   │       ├── maintenance.py # Manutenção
│   │       ├── backup.py      # Backup
│   │       ├── migration.py   # Migração
│   │       └── docs.py        # Documentação
│   ├── core/                  # Configurações
│   │   ├── config.py          # Settings Pydantic
│   │   └── constants.py       # Constantes e enums
│   ├── models/                # Modelos Pydantic
│   │   ├── config.py          # DatabaseConfig, BackupConfig
│   │   ├── responses.py       # Respostas da API
│   │   └── engine.py          # EngineDetails
│   ├── services/              # Lógica de negócio
│   │   ├── storage.py         # Persistência JSON
│   │   ├── connection.py      # Testes de conexão
│   │   ├── maintenance.py     # Manutenção
│   │   ├── backup.py          # Backup/Restore
│   │   └── migration.py       # Migração
│   └── data/                  # Dados estáticos
│       └── engines.py         # Detalhes dos motores
├── tests/                     # Testes
├── main.py                    # Entry point
└── requirements.txt
```

### Módulos Principais

#### Core (`app/core/`)

- **config.py**: Configurações centralizadas usando Pydantic Settings
- **constants.py**: Enums e constantes (EngineType, MaintenanceAction, etc.)

#### Models (`app/models/`)

- **config.py**: `DatabaseConfig`, `BackupConfig`
- **responses.py**: `ConnectionTestResult`, `MaintenanceResult`, etc.
- **engine.py**: `EngineDetails`, `EngineInfo`, `MaintenanceTool`

#### Services (`app/services/`)

- **storage.py**: Persistência em JSON
- **connection.py**: Testes de conexão com 4 motores
- **maintenance.py**: Ferramentas de manutenção
- **backup.py**: Backup e restore
- **migration.py**: Migração entre motores

#### API Routes (`app/api/routes/`)

Cada arquivo define rotas para um domínio específico:

| Arquivo | Endpoints |
|---------|-----------|
| health.py | `GET /api/health` |
| config.py | `GET/POST /api/config` |
| engines.py | `GET /api/engines`, `GET /api/engines/{id}` |
| connection.py | `POST /api/test-connection`, `GET/DELETE /api/connection-history` |
| maintenance.py | `GET /api/maintenance/tools/{engine}`, `POST /api/maintenance/{action}` |
| backup.py | `GET/POST /api/backup/config`, `POST /api/backup/execute`, `GET /api/backup/history` |
| migration.py | `POST /api/migration/export`, `POST /api/migration/import`, `POST /api/migration/execute` |
| docs.py | `GET /api/docs/{engine}` |

---

## Estrutura do Frontend

```
frontend/
├── src/
│   ├── components/
│   │   └── settings/
│   │       ├── DatabaseSettings.tsx   # 6 tabs principais
│   │       └── LocalBackup.tsx        # Backup com 3 subtabs
│   ├── types/
│   │   └── index.ts                   # Tipos TypeScript
│   ├── App.tsx                        # Componente principal
│   └── main.tsx                       # Entry point
├── index.html
├── package.json
├── vite.config.ts
├── tailwind.config.js
└── tsconfig.json
```

---

## API Reference

### Endpoints

#### Health

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/health` | Verifica saúde da API |

#### Configuração

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/config` | Obtém configuração atual |
| POST | `/api/config` | Salva configuração |

#### Motores

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/engines` | Lista todos os motores |
| GET | `/api/engines/{id}` | Detalhes de um motor |

#### Conexão

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/test-connection` | Testa conexão |
| GET | `/api/connection-history` | Histórico |
| DELETE | `/api/connection-history` | Limpa histórico |

#### Manutenção

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/maintenance/tools/{engine}` | Lista ferramentas |
| POST | `/api/maintenance/{action}` | Executa ação |

#### Backup

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/backup/config` | Configuração |
| POST | `/api/backup/config` | Salva config |
| POST | `/api/backup/execute` | Executa backup |
| GET | `/api/backup/history` | Histórico |

#### Migração

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/migration/export` | Exporta dados |
| POST | `/api/migration/import` | Importa dados |
| POST | `/api/migration/execute` | Executa migração |

---

## Guia de Instalação

### Requisitos

- Ubuntu Server 22.04 LTS ou 24.04 LTS
- 2GB RAM mínimo (4GB recomendado)
- 10GB espaço em disco
- Acesso root ou sudo

### Passos

```bash
# 1. Atualizar sistema
sudo apt update && sudo apt upgrade -y

# 2. Instalar dependências
sudo apt install -y python3 python3-pip python3-venv nodejs npm nginx

# 3. Criar diretórios
sudo mkdir -p /opt/database/{backend,frontend,data,backups,logs}
sudo mkdir -p /var/log/database

# 4. Configurar backend
cd /opt/database/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 5. Configurar frontend
cd /opt/database/frontend
npm install
npm run build

# 6. Configurar Nginx
sudo cp nginx/database.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/database.conf /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl restart nginx

# 7. Configurar systemd
sudo cp systemd/database-backend.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable database-backend
sudo systemctl start database-backend
```

---

## Configuração de Banco de Dados

### PostgreSQL

```bash
sudo apt install postgresql postgresql-contrib
sudo -u postgres psql -c "CREATE DATABASE orthoplus;"
sudo -u postgres psql -c "CREATE USER dbuser WITH PASSWORD 'senha';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE orthoplus TO dbuser;"
```

### MariaDB

```bash
sudo apt install mariadb-server mariadb-client
sudo mysql -e "CREATE DATABASE orthoplus;"
sudo mysql -e "CREATE USER 'dbuser'@'localhost' IDENTIFIED BY 'senha';"
sudo mysql -e "GRANT ALL PRIVILEGES ON orthoplus.* TO 'dbuser'@'localhost';"
```

---

## Deploy em Produção

### Docker Compose

```bash
cd docker
docker-compose up -d
```

### SSL/TLS (Let's Encrypt)

```bash
sudo bash scripts/ssl-setup.sh seu-dominio.com
```

---

## Troubleshooting

### API não inicia

```bash
sudo journalctl -u database-backend -f
sudo systemctl restart database-backend
```

### Frontend não carrega

```bash
sudo nginx -t
sudo systemctl restart nginx
```

### Conexão falha

```bash
# Verificar PostgreSQL
sudo systemctl status postgresql
```

---

## Contribuindo

1. Fork o repositório
2. Crie uma branch: `git checkout -b feature/nova-funcionalidade`
3. Commit: `git commit -am 'feat: nova funcionalidade'`
4. Push: `git push origin feature/nova-funcionalidade`
5. Crie um Pull Request

---

## Licença

MIT License
