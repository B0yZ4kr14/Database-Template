# Política de Segurança - Database

## Versões Suportadas

| Versão | Suportada          |
|--------|--------------------|
| 2.0.x  | :white_check_mark: |
| 1.0.x  | :x:                |

## Reportando Vulnerabilidades

Se você descobrir uma vulnerabilidade de segurança no Database, por favor:

1. **NÃO** abra uma issue pública
2. Envie um email para: security@database.com
3. Inclua:
   - Descrição detalhada da vulnerabilidade
   - Passos para reproduzir
   - Possível impacto
   - Sugestões de correção (se houver)

## Boas Práticas de Segurança

### Senhas

- Nunca armazene senhas em texto plano
- Use variáveis de ambiente para credenciais
- Rotacione senhas regularmente

### Rede

- Use HTTPS em produção
- Restrinja acesso à API apenas para hosts confiáveis
- Configure firewall adequadamente

### Sistema

- Mantenha o sistema atualizado
- Use usuário dedicado para executar o serviço
- Configure logs de auditoria

### Banco de Dados

- Use conexões SSL quando possível
- Limite privilégios do usuário de aplicação
- Faça backups regulares

## Configurações Recomendadas

### Produção

```bash
# .env
ENVIRONMENT=production
LOG_LEVEL=WARNING
CORS_ORIGINS=https://seu-dominio.com
```

### Firewall

```bash
# Permitir apenas portas necessárias
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp  # SSH
sudo ufw enable
```

## Contato

- Email: security@database.com
- PGP Key: [Link para chave PGP]
