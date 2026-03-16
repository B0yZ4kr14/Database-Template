# Database v2.0.2

Template completo para configuração, gerenciamento e manutenção de múltiplos motores de banco de dados em **Ubuntu Server LTS**.

![Version](https://img.shields.io/badge/version-2.0.2-blue)
![Ubuntu](https://img.shields.io/badge/Ubuntu-22.04%20LTS%20%7C%2024.04%20LTS-orange)
![Python](https://img.shields.io/badge/Python-3.11+-green)
![React](https://img.shields.io/badge/React-18-61DAFB)

---

## ✨ Funcionalidades

- **4 Motores de BD**: SQLite, PostgreSQL, MariaDB, Firebird
- **6 Tabs de Configuração**: Motor, Config, Reparo, Migração, Templates, Docs
- **Ferramentas de Manutenção**: VACUUM, ANALYZE, REINDEX, pg_checksums
- **Backup Local**: Completo e Incremental com agendamento
- **Migração Assistida**: Entre diferentes motores
- **Persistência**: Configurações salvas em JSON
- **Documentação Integrada**: Links e dicas de instalação

---

## 📸 Screenshots

O layout segue as especificações visuais das imagens de referência:

### Tab Motor - Seleção de Engine
- Cards dos 4 motores: SQLite, PostgreSQL, MariaDB, Firebird
- Detalhes de cada motor (Quando usar, Limitações, Recursos)

### Tab Config - Configuração de Conexão
- Campos: Host, Porta, Banco de Dados, Usuário, Senha
- Botão de teste de conexão

### Tab Reparo - Ferramentas de Manutenção
- Ferramentas específicas por motor (VACUUM, ANALYZE, REINDEX, etc.)
- Histórico de conexões

### Tab Migração
- Exportar/Importar dados
- Migração assistida entre motores

### Tab Docs
- Links para documentação oficial
- Dicas de instalação por SO

### Backup Local
- Explicação sobre backups
- Tabs: Local, Nuvem, Distribuído
- Agendamento automático

---

## 🚀 Instalação Rápida

### Ubuntu Server LTS (Recomendado)

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/database.git
cd database

# 2. Execute o script de instalação
sudo bash scripts/install.sh

# 3. Configure o PostgreSQL (opcional)
sudo bash scripts/setup-postgresql.sh

# 4. Acesse a interface
# http://seu-servidor-ip
```

### Docker Compose

```bash
# Iniciar todos os serviços
cd docker
docker-compose up -d

# Com PostgreSQL incluído
docker-compose --profile with-postgres up -d
```

---

## 📁 Estrutura do Projeto

```
Database/
├── backend/                    # API FastAPI (Arquitetura Modular)
│   ├── app/
│   │   ├── api/               # Rotas da API
│   │   │   └── routes/
│   │   │       ├── health.py
│   │   │       ├── config.py
│   │   │       ├── engines.py
│   │   │       ├── connection.py
│   │   │       ├── maintenance.py
│   │   │       ├── backup.py
│   │   │       ├── migration.py
│   │   │       └── docs.py
│   │   ├── core/              # Configurações centrais
│   │   │   ├── config.py      # Settings com Pydantic
│   │   │   └── constants.py   # Constantes e enums
│   │   ├── models/            # Modelos Pydantic
│   │   │   ├── config.py
│   │   │   ├── responses.py
│   │   │   └── engine.py
│   │   ├── services/          # Lógica de negócio
│   │   │   ├── storage.py
│   │   │   ├── connection.py
│   │   │   ├── maintenance.py
│   │   │   ├── backup.py
│   │   │   └── migration.py
│   │   └── data/              # Dados estáticos
│   │       └── engines.py     # Detalhes dos motores
│   ├── tests/                 # Testes automatizados
│   ├── main.py                # Entry point
│   ├── requirements.txt
│   └── wsgi.py
├── frontend/                   # React + TypeScript
│   ├── src/
│   │   ├── components/
│   │   │   └── settings/
│   │   │       ├── DatabaseSettings.tsx
│   │   │       └── LocalBackup.tsx
│   │   ├── types/
│   │   ├── App.tsx
│   │   └── main.tsx
│   └── ...
├── landing/                    # Landing page interativa
│   └── index.html
├── docs/                       # Documentação
│   ├── DEVELOPER.md
│   ├── API_EXAMPLES.md
│   ├── CHANGELOG.md
│   └── MIGRATION_GUIDE.md
├── scripts/                    # Scripts de instalação
│   ├── install.sh
│   ├── setup-postgresql.sh
│   ├── validate.sh
│   ├── health-check.sh
│   ├── monitor.sh
│   ├── backup-cron.sh
│   ├── api-examples.sh
│   └── ssl-setup.sh
├── config-examples/            # Exemplos de configuração
│   ├── postgresql.json
│   ├── sqlite.json
│   ├── mariadb.json
│   └── firebird.json
├── docker/                     # Docker
├── nginx/                      # Nginx
├── systemd/                    # Systemd
├── .github/                    # CI/CD GitHub Actions
├── Makefile                    # Comandos automatizados
├── LICENSE
├── CONTRIBUTING.md
├── SECURITY.md
└── README.md
```

---

## 🛠️ Stack Tecnológico

| Componente | Tecnologia | Versão |
|------------|------------|--------|
| Backend | Python/FastAPI | 3.11+ |
| Frontend | React/TypeScript | 18+ |
| Estilização | Tailwind CSS | 3.4+ |
| Build Tool | Vite | 5.1+ |
| Servidor Web | Nginx | 1.24+ |

---

## 📖 Documentação

- **[Guia do Desenvolvedor](docs/DEVELOPER.md)** - Documentação técnica completa
- **[Exemplos de API](docs/API_EXAMPLES.md)** - Comandos e exemplos práticos
- **[Changelog](docs/CHANGELOG.md)** - Histórico de versões
- **[Guia de Migração](docs/MIGRATION_GUIDE.md)** - Migração de versões anteriores
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Como contribuir
- **[SECURITY.md](SECURITY.md)** - Política de segurança

---

## 🔧 Comandos Úteis (Makefile)

```bash
# Ver todos os comandos disponíveis
make help

# Instalação
make install              # Instala o Database no sistema
make install-postgres     # Configura PostgreSQL

# Desenvolvimento
make dev-backend          # Inicia backend em modo dev
make dev-frontend         # Inicia frontend em modo dev
make build                # Build do frontend para produção

# Docker
make docker-up            # Inicia containers Docker
make docker-down          # Para containers Docker
make docker-logs          # Mostra logs dos containers

# Deploy
make deploy               # Deploy completo
make restart              # Reinicia todos os serviços
make status               # Mostra status dos serviços

# Testes
make test                 # Executa testes de validação
make test-backend         # Testes do backend (pytest)
make test-frontend        # Testes do frontend (vitest)
make test-coverage        # Testes com cobertura
make validate             # Valida instalação

# Monitoramento
make monitor              # Monitora métricas em tempo real
make health               # Verifica saúde do sistema
make health-json          # Saúde do sistema (JSON)

# SSL/TLS
make ssl-setup DOMAIN=... # Configura SSL com Let's Encrypt

# Logs
make logs-backend         # Logs do backend
make logs-nginx           # Logs do Nginx

# Backup
make backup-full          # Backup completo do sistema

# Utilidades
make api-examples         # Executa exemplos de API
make update               # Atualiza dependências

# Manutenção
make clean                # Limpa arquivos temporários
make docs                 # Mostra documentação disponível
```

---

## ⚙️ Configuração

### Variáveis de Ambiente

Copie o arquivo de exemplo e ajuste conforme necessário:

```bash
cp .env.example .env
nano .env
```

Principais variáveis:

```bash
# Ambiente
ENVIRONMENT=production

# Diretórios
DATA_DIR=/opt/database/data
BACKUP_DIR=/opt/database/backups
LOG_DIR=/var/log/database

# API
API_HOST=0.0.0.0
API_PORT=8000

# Banco de Dados (PostgreSQL padrão)
DB_ENGINE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_NAME=orthoplus
DB_USER=postgres
DB_PASSWORD=
```

---

## 🐛 Correções na v2.0.1

- ✅ Corrigido erro de logging ao iniciar
- ✅ Corrigido `config.dict()` para `config.model_dump()` (Pydantic v2)
- ✅ Adicionado endpoint DELETE para limpar histórico
- ✅ Adicionado validação de formulários no frontend
- ✅ Corrigido tratamento de erros nas requisições API
- ✅ Adicionado feedback visual para todas as operações
- ✅ **Refatoração completa do backend** - Arquitetura modular

---

## 🤝 Contribuindo

1. Fork o repositório
2. Crie uma branch: `git checkout -b feature/nova-funcionalidade`
3. Commit: `git commit -am 'Adiciona nova funcionalidade'`
4. Push: `git push origin feature/nova-funcionalidade`
5. Crie um Pull Request

Consulte o [Guia do Desenvolvedor](docs/DEVELOPER.md) para mais detalhes.

---

## 📄 Licença

MIT License - veja [LICENSE](LICENSE) para detalhes.

---

<p align="center">
  <strong>Database</strong> - Configuração de banco de dados simplificada
</p>
