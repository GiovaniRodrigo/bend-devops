# Quickstart: Pipeline Flow, Architecture Profiles, Split Diff & Coverage

Guia prático para inicializar, testar e utilizar os recursos da Spec 008 localmente.

---

## 1. Pré-requisitos

- Node.js 20+ e npm
- Python 3.12+ com `pip`
- Rust / Cargo (para Bend HVM)

---

## 2. Instalação de Dependências

```bash
# 1. Instalar dependências do Frontend (Angular 21 + Tailwind)
cd frontend
npm install
cd ..

# 2. Instalar dependências Python (Coverage.py 7.16.x + Playwright)
pip install -r requirements.txt
```

---

## 3. Execução do Servidor de Desenvolvimento

```bash
# Iniciar frontend Angular em modo interativo
npm run dev

# Abrir no navegador: http://localhost:4200
```

---

## 4. Testes e Validação de Cobertura

```bash
# 1. Executar testes unitários do frontend (Vitest - 51 testes)
cd frontend && npm test -- --watch=false && cd ..

# 2. Executar medição de cobertura Python e gerar HTML (Coverage.py 7.16.x)
npm run coverage

# Visualizar o relatório HTML gerado
# Abra o arquivo htmlcov/index.html no navegador:
# xdg-open htmlcov/index.html

# 3. Executar o pipeline de validação completo (8 etapas com screenshots)
./scripts/validate.sh
```

---

## 5. Roteiro de Uso Rápido na Interface

1. **Reordenação de Pipeline**:
   - Acesse a aba **Pipelines**.
   - Arraste um estágio pela alça `⠿` ou utilize as setas de precisão &uarr; / &darr;.
   - Observe o diagrama de fluxo reordenado em tempo real.

2. **Perfis de Arquitetura & Turnover**:
   - Acesse a aba **Architecture Profiles**.
   - Clique no interruptor **Ativo / Inativo** para alternar o status do perfil em 1 clique.
   - Clique em **Editar** para ajustar regras, camadas e dependências permitidas.

3. **Live Code & Diff Auditor (Split View)**:
   - Acesse a aba **Live Code Auditor**.
   - Selecione o escopo **Branch Analysis** e clique em **Analyze Branch**.
   - Na lista de arquivos à esquerda, clique em qualquer arquivo.
   - O painel direito exibirá imediatamente o **Split Diff (Before vs After)** com realce de sintaxe e correções do Guardian.
