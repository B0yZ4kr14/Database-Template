# Guia de Contribuição - Database

Obrigado por seu interesse em contribuir com o Database! Este documento fornece diretrizes para contribuir com o projeto.

---

## 📋 Índice

1. [Código de Conduta](#código-de-conduta)
2. [Como Contribuir](#como-contribuir)
3. [Configuração do Ambiente](#configuração-do-ambiente)
4. [Padrões de Código](#padrões-de-código)
5. [Processo de Pull Request](#processo-de-pull-request)
6. [Reportando Bugs](#reportando-bugs)
7. [Solicitando Funcionalidades](#solicitando-funcionalidades)

---

## 📜 Código de Conduta

Este projeto segue um código de conduta que espera que todos os participantes sejam:

- **Respeitosos**: Trate todos com respeito e consideração
- **Colaborativos**: Trabalhe juntos de forma construtiva
- **Pacientes**: Entenda que nem todos têm o mesmo nível de experiência
- **Abertos**: Aceite críticas construtivas e aprenda com elas

---

## 🤝 Como Contribuir

### 1. Fork o Repositório

```bash
# Fork no GitHub, depois clone seu fork
git clone https://github.com/seu-usuario/database.git
cd database
```

### 2. Crie uma Branch

```bash
git checkout -b feature/nome-da-funcionalidade
# ou
git checkout -b fix/nome-do-bug
```

### 3. Faça suas Alterações

- Siga os padrões de código
- Adicione testes quando apropriado
- Atualize a documentação se necessário

### 4. Commit suas Alterações

```bash
git add .
git commit -m "tipo: descrição curta"
```

**Tipos de commit:**
- `feat:` Nova funcionalidade
- `fix:` Correção de bug
- `docs:` Alteração na documentação
- `style:` Formatação, semicolons, etc.
- `refactor:` Refatoração de código
- `test:` Adição ou correção de testes
- `chore:` Tarefas de build, configuração, etc.

### 5. Push e Pull Request

```bash
git push origin feature/nome-da-funcionalidade
```

Depois abra um Pull Request no GitHub.

---

## ⚙️ Configuração do Ambiente

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install pytest flake8 black
```

### Frontend

```bash
cd frontend
npm install
```

---

## 📝 Padrões de Código

### Python

- Siga PEP 8
- Use type hints
- Documente funções com docstrings
- Máximo de 100 caracteres por linha

```python
def minha_funcao(param1: str, param2: int) -> bool:
    """
    Descrição da função.
    
    Args:
        param1: Descrição do parâmetro 1
        param2: Descrição do parâmetro 2
    
    Returns:
        Descrição do retorno
    """
    return True
```

### TypeScript/React

- Use interfaces para tipos
- Nomeie componentes em PascalCase
- Use hooks de forma consistente
- Prefira funções arrow

```typescript
interface Props {
  title: string;
  onClick: () => void;
}

export const MeuComponente: React.FC<Props> = ({ title, onClick }) => {
  return <button onClick={onClick}>{title}</button>;
};
```

---

## 🔍 Processo de Pull Request

1. **Descrição Clara**: Explique o que e por que
2. **Testes**: Certifique-se de que todos os testes passam
3. **Documentação**: Atualize se necessário
4. **Revisão**: Aguarde revisão de mantenedores
5. **Merge**: Será feito após aprovação

---

## 🐛 Reportando Bugs

Use o template de issue e inclua:

- **Descrição**: O que aconteceu
- **Passos para reproduzir**: Como reproduzir o bug
- **Comportamento esperado**: O que deveria acontecer
- **Screenshots**: Se aplicável
- **Ambiente**: SO, versão, etc.

---

## 💡 Solicitando Funcionalidades

Use o template de feature request e inclua:

- **Descrição**: O que você quer
- **Motivação**: Por que é útil
- **Alternativas**: Outras soluções consideradas
- **Contexto adicional**: Qualquer informação extra

---

## 📞 Contato

- Issues: GitHub Issues
- Discussões: GitHub Discussions
- Email: dev@database.com

---

Obrigado por contribuir! 🎉
