# Quickstart: Escopo e Regras Arquiteturais do Usuário

Guia rápido para configurar, executar e testar a funcionalidade de escopo e composição de regras arquiteturais localmente.

---

## Pré-requisitos

- **Python 3.10+** instalado
- **Node.js 18+** e **npm 10+** instalados
- Repositório `bend-devops` clonado localmente

---

## Passos

### 1. Iniciar o Servidor Guardian & Dashboard Web

```bash
# Terminal 1: Iniciar o servidor de avaliação local
python3 scripts/guardian_server.py --port 4201

# Terminal 2: Iniciar a interface web Angular
cd frontend && npm run dev
```

Acesse o painel em `http://localhost:4200`.

---

### 2. Execução via CLI com Escopo e Regras Personalizadas

```bash
# Exemplo 1: Auditar apenas o subdiretório backend/ aplicando apenas regras de Clean Architecture
python3 scripts/culture_guard.py --scope subdirectory --subdir backend/ --rules ARCH-LAYER-01,ARCH-LAYER-02

# Exemplo 2: Auditar apenas as alterações recentes (diff do working tree) com regras de segurança
python3 scripts/culture_guard.py --scope diff --rules SEC-001,SEC-002,SEC-003 --format json

# Exemplo 3: Auditar um arquivo isolado
python3 scripts/culture_guard.py --scope file --target backend/domain/model.py
```

---

## Verificação

Execute a suíte de testes dedicada à funcionalidade para validar a resolução de escopos e regras:

```bash
# Rodar testes automatizados de escopo em Python
python3 -m unittest tests/test_user_scoped_rules.py

# Rodar testes de frontend com Vitest
cd frontend && npm test -- --watch=false
```

---

## Variáveis de Ambiente

| Variável | Valor de Exemplo | Descrição |
| :--- | :--- | :--- |
| `GUARDIAN_PORT` | `4201` | Porta do servidor de avaliação |
| `DEFAULT_AUDIT_SCOPE` | `full_branch` | Escopo padrão quando não informado |
| `MOCK_MODE` | `false` | Se ativo, utiliza cenários simulados |
