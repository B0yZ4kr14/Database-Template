# Database - Exemplos de API

Este documento contém exemplos práticos de uso da API do Database usando `curl`.

---

## Índice

1. [Health Check](#health-check)
2. [Configuração](#configuração)
3. [Motores](#motores)
4. [Teste de Conexão](#teste-de-conexão)
5. [Histórico de Conexões](#histórico-de-conexões)
6. [Manutenção](#manutenção)
7. [Backup](#backup)
8. [Migração](#migração)

---

## Health Check

### Verificar saúde da API

```bash
curl -X GET http://localhost:8000/api/health
```

**Resposta esperada:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "2.0.2"
}
```

---

## Configuração

### Obter configuração atual

```bash
curl -X GET http://localhost:8000/api/config
```

**Resposta esperada:**
```json
{
  "engine": "postgresql",
  "host": "localhost",
  "port": 5432,
  "database": "orthoplus",
  "username": "postgres",
  "password": "",
  "ssl_mode": "prefer"
}
```

### Salvar configuração

```bash
curl -X POST http://localhost:8000/api/config \
  -H "Content-Type: application/json" \
  -d '{
    "engine": "postgresql",
    "host": "localhost",
    "port": 5432,
    "database": "orthoplus",
    "username": "postgres",
    "password": "senha_segura",
    "ssl_mode": "prefer"
  }'
```

**Resposta esperada:**
```json
{
  "success": true,
  "message": "Configuração salva com sucesso"
}
```

### Configuração SQLite

```bash
curl -X POST http://localhost:8000/api/config \
  -H "Content-Type: application/json" \
  -d '{
    "engine": "sqlite",
    "host": "localhost",
    "port": 0,
    "database": "meubanco",
    "username": "",
    "password": "",
    "file_path": "/var/lib/orthoplus/database.db"
  }'
```

### Configuração MariaDB

```bash
curl -X POST http://localhost:8000/api/config \
  -H "Content-Type: application/json" \
  -d '{
    "engine": "mariadb",
    "host": "localhost",
    "port": 3306,
    "database": "orthoplus",
    "username": "root",
    "password": "senha_segura",
    "charset": "utf8mb4"
  }'
```

### Configuração Firebird

```bash
curl -X POST http://localhost:8000/api/config \
  -H "Content-Type: application/json" \
  -d '{
    "engine": "firebird",
    "host": "localhost",
    "port": 3050,
    "database": "/var/lib/firebird/data/orthoplus.fdb",
    "username": "SYSDBA",
    "password": "masterkey"
  }'
```

---

## Motores

### Listar todos os motores

```bash
curl -X GET http://localhost:8000/api/engines
```

**Resposta esperada:**
```json
{
  "engines": [
    {
      "id": "sqlite",
      "name": "SQLite",
      "description": "Banco de dados embutido",
      "default_port": 0
    },
    {
      "id": "postgresql",
      "name": "PostgreSQL",
      "description": "Banco de dados relacional avançado",
      "default_port": 5432
    },
    {
      "id": "mariadb",
      "name": "MariaDB",
      "description": "Banco de dados MySQL compatível",
      "default_port": 3306
    },
    {
      "id": "firebird",
      "name": "Firebird",
      "description": "Banco de dados relacional",
      "default_port": 3050
    }
  ]
}
```

### Obter detalhes de um motor

```bash
curl -X GET http://localhost:8000/api/engines/postgresql
```

**Resposta esperada:**
```json
{
  "id": "postgresql",
  "name": "PostgreSQL",
  "description": "Banco de dados relacional avançado",
  "default_port": 5432,
  "features": ["ACID", "JSON", "Full-text search", "Replication"],
  "tools": ["vacuum", "analyze", "reindex", "pg_checksums"]
}
```

---

## Teste de Conexão

### Testar conexão PostgreSQL

```bash
curl -X POST http://localhost:8000/api/test-connection \
  -H "Content-Type: application/json" \
  -d '{
    "engine": "postgresql",
    "host": "localhost",
    "port": 5432,
    "database": "orthoplus",
    "username": "postgres",
    "password": "senha_segura"
  }'
```

**Resposta de sucesso:**
```json
{
  "success": true,
  "message": "Conexão PostgreSQL bem-sucedida",
  "details": {
    "version": "PostgreSQL 14.5",
    "size_bytes": 8450000,
    "size_mb": 8.06
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Resposta de erro:**
```json
{
  "success": false,
  "message": "Falha na conexão PostgreSQL: autenticação falhou",
  "details": {},
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Testar conexão SQLite

```bash
curl -X POST http://localhost:8000/api/test-connection \
  -H "Content-Type: application/json" \
  -d '{
    "engine": "sqlite",
    "host": "localhost",
    "port": 0,
    "database": "meubanco",
    "username": "",
    "password": "",
    "file_path": "/var/lib/orthoplus/database.db"
  }'
```

---

## Histórico de Conexões

### Obter histórico

```bash
curl -X GET http://localhost:8000/api/connection-history
```

**Resposta esperada:**
```json
{
  "history": [
    {
      "timestamp": "2024-01-15T10:30:00Z",
      "engine": "postgresql",
      "host": "localhost",
      "database": "orthoplus",
      "success": true,
      "message": "Conexão bem-sucedida"
    },
    {
      "timestamp": "2024-01-15T10:25:00Z",
      "engine": "postgresql",
      "host": "localhost",
      "database": "orthoplus",
      "success": false,
      "message": "Autenticação falhou"
    }
  ],
  "count": 2
}
```

### Limpar histórico

```bash
curl -X DELETE http://localhost:8000/api/connection-history
```

**Resposta esperada:**
```json
{
  "success": true,
  "message": "Histórico de conexões limpo"
}
```

---

## Manutenção

### Listar ferramentas disponíveis

```bash
curl -X GET http://localhost:8000/api/maintenance/tools/postgresql
```

**Resposta esperada:**
```json
{
  "engine": "postgresql",
  "tools": [
    {
      "id": "vacuum",
      "name": "VACUUM",
      "description": "Remove registros mortos e recupera espaço"
    },
    {
      "id": "analyze",
      "name": "ANALYZE",
      "description": "Atualiza estatísticas para otimização de queries"
    },
    {
      "id": "reindex",
      "name": "REINDEX",
      "description": "Reconstrói índices"
    },
    {
      "id": "pg_checksums",
      "name": "pg_checksums",
      "description": "Verifica integridade de dados"
    }
  ]
}
```

### Executar VACUUM (PostgreSQL)

```bash
curl -X POST http://localhost:8000/api/maintenance/vacuum \
  -H "Content-Type: application/json" \
  -d '{
    "engine": "postgresql",
    "host": "localhost",
    "port": 5432,
    "database": "orthoplus",
    "username": "postgres",
    "password": "senha_segura"
  }'
```

**Resposta esperada:**
```json
{
  "success": true,
  "message": "VACUUM executado com sucesso",
  "details": {
    "space_recovered_mb": 15.5,
    "duration_seconds": 2.3
  }
}
```

### Executar ANALYZE

```bash
curl -X POST http://localhost:8000/api/maintenance/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "engine": "postgresql",
    "host": "localhost",
    "port": 5432,
    "database": "orthoplus",
    "username": "postgres",
    "password": "senha_segura"
  }'
```

---

## Backup

### Obter configuração de backup

```bash
curl -X GET http://localhost:8000/api/backup/config
```

**Resposta esperada:**
```json
{
  "auto_backup": false,
  "interval": "daily",
  "retention_days": 7,
  "compression": true,
  "encryption": false,
  "backup_dir": "/opt/database/backups"
}
```

### Salvar configuração de backup

```bash
curl -X POST http://localhost:8000/api/backup/config \
  -H "Content-Type: application/json" \
  -d '{
    "auto_backup": true,
    "interval": "daily",
    "retention_days": 14,
    "compression": true,
    "encryption": false
  }'
```

### Executar backup completo

```bash
curl -X POST http://localhost:8000/api/backup/execute \
  -H "Content-Type: application/json" \
  -d '{
    "type": "full",
    "engine": "postgresql",
    "host": "localhost",
    "port": 5432,
    "database": "orthoplus",
    "username": "postgres",
    "password": "senha_segura"
  }'
```

**Resposta esperada:**
```json
{
  "success": true,
  "message": "Backup completo executado",
  "details": {
    "file": "/opt/database/backups/orthoplus_20240115_103000.sql",
    "size_bytes": 12500000,
    "size_mb": 11.92,
    "duration_seconds": 5.2
  }
}
```

### Executar backup incremental

```bash
curl -X POST http://localhost:8000/api/backup/execute \
  -H "Content-Type: application/json" \
  -d '{
    "type": "incremental",
    "engine": "postgresql",
    "host": "localhost",
    "port": 5432,
    "database": "orthoplus",
    "username": "postgres",
    "password": "senha_segura"
  }'
```

### Obter histórico de backups

```bash
curl -X GET http://localhost:8000/api/backup/history
```

**Resposta esperada:**
```json
{
  "backups": [
    {
      "timestamp": "2024-01-15T10:30:00Z",
      "type": "full",
      "file": "/opt/database/backups/orthoplus_20240115_103000.sql",
      "size_mb": 11.92,
      "status": "success"
    }
  ],
  "count": 1
}
```

### Restaurar backup

```bash
curl -X POST http://localhost:8000/api/backup/restore \
  -H "Content-Type: application/json" \
  -d '{
    "file": "/opt/database/backups/orthoplus_20240115_103000.sql",
    "engine": "postgresql",
    "host": "localhost",
    "port": 5432,
    "database": "orthoplus",
    "username": "postgres",
    "password": "senha_segura"
  }'
```

**Resposta esperada:**
```json
{
  "success": true,
  "message": "Backup restaurado com sucesso",
  "details": {
    "duration_seconds": 8.5
  }
}
```

---

## Migração

### Exportar dados

```bash
curl -X POST http://localhost:8000/api/migration/export \
  -H "Content-Type: application/json" \
  -d '{
    "format": "json",
    "engine": "postgresql",
    "host": "localhost",
    "port": 5432,
    "database": "orthoplus",
    "username": "postgres",
    "password": "senha_segura"
  }'
```

**Resposta esperada:**
```json
{
  "success": true,
  "message": "Dados exportados com sucesso",
  "details": {
    "file": "/opt/database/backups/export_20240115_103000.json",
    "tables": 15,
    "records": 50000
  }
}
```

### Importar dados

```bash
curl -X POST http://localhost:8000/api/migration/import \
  -H "Content-Type: application/json" \
  -d '{
    "file": "/opt/database/backups/export_20240115_103000.json",
    "engine": "postgresql",
    "host": "localhost",
    "port": 5432,
    "database": "orthoplus",
    "username": "postgres",
    "password": "senha_segura"
  }'
```

### Executar migração entre motores

```bash
curl -X POST http://localhost:8000/api/migration/execute \
  -H "Content-Type: application/json" \
  -d '{
    "source": {
      "engine": "sqlite",
      "host": "localhost",
      "port": 0,
      "database": "meubanco",
      "username": "",
      "password": "",
      "file_path": "/var/lib/orthoplus/database.db"
    },
    "target": {
      "engine": "postgresql",
      "host": "localhost",
      "port": 5432,
      "database": "orthoplus",
      "username": "postgres",
      "password": "senha_segura"
    }
  }'
```

**Resposta esperada:**
```json
{
  "success": true,
  "message": "Migração executada com sucesso",
  "details": {
    "tables_migrated": 15,
    "records_migrated": 50000,
    "duration_seconds": 45.2
  }
}
```

---

## Documentação

### Obter links de documentação

```bash
curl -X GET http://localhost:8000/api/docs/postgresql
```

**Resposta esperada:**
```json
{
  "engine": "postgresql",
  "links": [
    {
      "title": "Documentação Oficial",
      "url": "https://www.postgresql.org/docs/"
    },
    {
      "title": "Guia de Instalação Ubuntu",
      "url": "https://www.postgresql.org/download/linux/ubuntu/"
    }
  ],
  "install_tips": [
    "sudo apt install postgresql postgresql-contrib",
    "sudo systemctl enable postgresql",
    "sudo -u postgres psql"
  ]
}
```

---

## Scripts Úteis

### Script de teste completo

```bash
#!/bin/bash
# test_api.sh - Script completo de teste da API

API_URL="http://localhost:8000/api"

echo "=== Testando Health Check ==="
curl -s $API_URL/health | jq

echo -e "\n=== Listando Motores ==="
curl -s $API_URL/engines | jq

echo -e "\n=== Salvando Configuração ==="
curl -s -X POST $API_URL/config \
  -H "Content-Type: application/json" \
  -d '{
    "engine": "postgresql",
    "host": "localhost",
    "port": 5432,
    "database": "orthoplus",
    "username": "postgres",
    "password": ""
  }' | jq

echo -e "\n=== Testando Conexão ==="
curl -s -X POST $API_URL/test-connection \
  -H "Content-Type: application/json" \
  -d '{
    "engine": "postgresql",
    "host": "localhost",
    "port": 5432,
    "database": "orthoplus",
    "username": "postgres",
    "password": ""
  }' | jq

echo -e "\n=== Obtendo Histórico ==="
curl -s $API_URL/connection-history | jq

echo -e "\n=== Teste completo finalizado ==="
```

---

## Notas

- Substitua `localhost:8000` pelo endereço real do seu servidor
- Substitua as credenciais (`senha_segura`, etc.) pelas suas credenciais reais
- Use `jq` para formatar as respostas JSON (instale com `sudo apt install jq`)
- Para produção, considere usar HTTPS e autenticação
