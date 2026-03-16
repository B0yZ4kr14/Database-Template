# Changelog - Database

Todas as mudanças notáveis deste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

---

## [2.0.2] - 2024-03-16

### Corrigido

- ✅ Corrigido problema de indentação em `storage.py`
- ✅ Corrigido imports não utilizados em vários módulos
- ✅ Corrigido inconsistência de campo `encrypt` para `encryption`
- ✅ Corrigido versão no `package.json` do frontend
- ✅ Corrigido tipos TypeScript para consistência com backend

### Melhorado

- 🔄 Melhorada segurança com SHA256 para checksums
- 🔄 Adicionado tratamento de race conditions com file locking
- 🔄 Melhorado tratamento de erros nas requisições API
- 🔄 Adicionado sanitização de identificadores SQL

---

## [2.0.1] - 2024-01-15

### Corrigido

- ✅ Corrigido erro de logging ao iniciar (diretório de logs criado antes)
- ✅ Corrigido `config.dict()` para `config.model_dump()` (Pydantic v2)
- ✅ Corrigido tratamento de erros nas requisições API
- ✅ Corrigido tipos TypeScript para consistência

### Adicionado

- ✅ Adicionado endpoint DELETE para limpar histórico de conexões
- ✅ Adicionado validação de formulários no frontend
- ✅ Adicionado feedback visual para todas as operações
- ✅ Adicionado documentação de exemplos de API (API_EXAMPLES.md)
- ✅ Adicionado arquivo CHANGELOG.md dedicado
- ✅ Adicionado Guia de Migração (MIGRATION_GUIDE.md)

### Melhorado

- 🔄 Melhorada documentação do desenvolvedor
- 🔄 Consolidada documentação do projeto
- 🔄 Padronizadas versões de Python (3.11+)

### Alterado

- 🔄 **BREAKING**: Renomeado projeto de `database-template` para `database`
- 🔄 **BREAKING**: Alterados caminhos de `/opt/database-template` para `/opt/database`
- 🔄 **BREAKING**: Renomeado serviço de `database-template-backend` para `database-backend`

---

## [2.0.0] - 2024-01-10

### Adicionado

- ✅ Suporte a 4 motores de banco de dados: SQLite, PostgreSQL, MariaDB, Firebird
- ✅ Interface web com 6 tabs de configuração
- ✅ Ferramentas de manutenção: VACUUM, ANALYZE, REINDEX, pg_checksums
- ✅ Sistema de backup local (completo e incremental)
- ✅ Agendamento automático de backups
- ✅ Migração assistida entre motores
- ✅ Persistência de configurações em JSON
- ✅ Documentação integrada com links oficiais
- ✅ Landing page interativa
- ✅ Suporte a Ubuntu Server LTS (22.04 e 24.04)
- ✅ Configuração Docker Compose
- ✅ Scripts de instalação automatizados
- ✅ Configuração systemd para serviços
- ✅ Configuração Nginx como reverse proxy

### Stack Tecnológico

- Backend: Python 3.11+ com FastAPI
- Frontend: React 18+ com TypeScript
- Estilização: Tailwind CSS 3.4+
- Build: Vite 5.1+
- Servidor: Nginx 1.24+

---

## [1.0.0] - 2023-12-01

### Lançamento Inicial

- 🚀 Versão inicial do Database
- ✅ Configuração básica de conexão com banco de dados
- ✅ Teste de conexão
- ✅ Suporte a PostgreSQL

---

## Roadmap

### [2.1.0] - Planejado

- [ ] Suporte a MySQL (além de MariaDB)
- [ ] Suporte a MongoDB
- [ ] Dashboard com métricas de banco de dados
- [ ] Notificações por email para falhas de backup
- [ ] Integração com AWS S3 para backup na nuvem

### [2.2.0] - Planejado

- [ ] Autenticação de usuários
- [ ] Controle de acesso baseado em roles (RBAC)
- [ ] Auditoria de operações
- [ ] API de webhooks

### [3.0.0] - Planejado

- [ ] Suporte a cluster de bancos de dados
- [ ] Replicação automática
- [ ] Monitoramento avançado com Prometheus/Grafana
- [ ] Interface de query SQL

---

## Convenções de Versionamento

- **MAJOR** (X.0.0): Mudanças incompatíveis com versões anteriores
- **MINOR** (0.X.0): Adição de funcionalidades mantendo compatibilidade
- **PATCH** (0.0.X): Correções de bugs e melhorias menores

---

## Como Contribuir

Se você encontrar um bug ou tiver uma sugestão:

1. Verifique se o problema já foi reportado
2. Crie uma issue descrevendo o problema
3. Se possível, envie um Pull Request com a correção

Consulte o [Guia do Desenvolvedor](DEVELOPER.md) para mais informações.
