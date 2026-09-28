# Plano de Implementação: Pipeline Flow, Architecture Profiles, Split Diff & Coverage

Este documento descreve a estratégia técnica, arquitetura de componentes, arquivos afetados e gerenciamento de riscos para a implementação e evolução dos recursos de visualização de pipeline, edição de perfis, split view e governança com Coverage.py.

---

## 1. Arquivos Criados e Editados

### 1.1. Frontend (Angular 21 + Tailwind)
* **`frontend/src/app/app.html`**:
  * Adicionado renderizador de fluxo de pipeline CI/CD dinâmico com nós e setas SVG.
  * Adicionado suporte a Drag & Drop nativo nas etapas de pipeline com alça `⠿` e botões subir/descer.
  * Implementado modal de edição de Architecture Profiles (`architecture-profile-modal`).
  * Implementado modal de detalhes de regras ao clicar no card (`rule-details-modal`).
  * Reestruturada a visualização de *Branch Analysis Result* em grid de 2 colunas (`xl:col-span-5` para resumo/arquivos/violações e `xl:col-span-7` para Live Split Diff).
  * Adicionado layout com rolagem central independente (`overflow-y-auto` no container principal).

* **`frontend/src/app/app.ts`**:
  * Signals para estado de Drag & Drop (`draggedPipelineStageIndex`, `pipelineStages`).
  * Métodos para manipulação de estágios (`onPipelineDragStart`, `onPipelineDragOver`, `onPipelineDrop`, `movePipelineStage`).
  * Signals e métodos de Architecture Profiles (`architectureProfiles`, `isEditingArchitectureProfile`, `editingProfileForm`, `saveArchitectureProfileForm`, `toggleArchitectureProfile`, `setArchitectureProfileStatus`).
  * Sincronização de seleção de arquivos no branch (`selectBranchFile`, `findBranchFileIndex`).
  * Gerenciamento de modais de regras e perfis.

* **`frontend/src/app/app.spec.ts`**:
  * Testes unitários para Drag & Drop e reordenação de estágios.
  * Testes para criação, edição e turnover (Ativo/Inativo) de Architecture Profiles.
  * Testes para modal de detalhes de regras.
  * Testes para renderização de Split Diff lado a lado em Branch Analysis.

### 1.2. Backend & Scripts (Python + Bend)
* **`requirements.txt` & `requirements-dev.txt`**:
  * Declaração de `coverage>=7.16.1` e `playwright>=1.40.0`.
* **`.coveragerc`**:
  * Configuração padrão para medição de branch coverage, exclusão de boilerplates e relatórios HTML/XML/JSON.
* **`package.json`**:
  * Adicionados scripts `coverage`, `coverage:report` e `coverage:html`.
* **`scripts/validate.sh`**:
  * Integração de execução sob Coverage.py nas etapas de testes e geração de relatórios.
* **`.github/workflows/ci.yml`**:
  * Instalação automática de dependências Python via `pip install -r requirements.txt`.

---

## 2. Estratégia Técnica

### 2.1. Drag & Drop Nativo com HTML5 Drag and Drop API
Em vez de bibliotecas pesadas como CDK DragDrop, utilizamos a API nativa do HTML5 com `draggable="true"`, eventos `(dragstart)`, `(dragover)`, `(drop)` e `(dragend)`, complementada com botões táteis de acessibilidade (subir e descer). Isso mantém o bundle leve e sem dependências externas.

### 2.2. Visualização Dinâmica de Split Diff com Angular Signals
Utilização de `computed<CodeDiff>` que recalcula automaticamente `splitBefore`, `splitAfter`, `lines`, `explanations` sempre que o arquivo ativo (`inputFileName`) ou código (`inputSourceCode`) é alterado. A reatividade do Angular 21 garante atualizações instantâneas sem necessidade de reexecuções manuais de ciclo de vida.

### 2.3. Governança com Coverage.py 7.16.x
Adoção do Coverage.py com medição de branches (`branch = True`), geração de relatórios no terminal durante o `./scripts/validate.sh` e exportação do relatório visual completo para `htmlcov/index.html`.

---

## 3. Dependências e Pré-requisitos

- [x] Node.js 20+ e Angular CLI 21+
- [x] Python 3.12+ com `pip`
- [x] `coverage>=7.16.1` instalado
- [x] Compilador Rust/Cargo com Bend HVM configurado

---

## 4. Riscos e Mitigações

| Risco | Impacto | Mitigação |
|---|---|---|
| Inconsistência de números de linha entre código original e corrigido | Médio | Algoritmo de sincronização em `CultureGuardianService.generateCodeDiff` insere placeholders vazios para linhas desalinhadas. |
| Perda de acessibilidade em operações de Drag & Drop | Médio | Inclusão de botões direcionais de teclado/clique (Subir / Descer) ao lado de cada estágio. |
| Queda de desempenho ao rodar Coverage em CI | Baixo | Configuração de exclusão de arquivos de mock e execução seletiva nas pastas `scripts/` e `tests/`. |
