# Plano de Implementação: Escopo e Composição de Regras Arquiteturais Orientadas ao Usuário

Este plano detalha as alterações no Frontend (Angular 19), Scripts CLI/Servidor (Python/Bend) e Contratos de Dados para viabilizar a orquestração dinâmica de escopos de análise e combinação modular de regras pelo usuário.

---

## 1. Arquivos a Criar/Editar

### 1.1. Modelos de Dados & Tipos
* **`frontend/src/app/models/culture.model.ts`**:
  * Adicionar interfaces `AuditScopeConfig`, `RuleSelectionPreset`, `CustomEvaluationRequest`, `RepositoryScopeSummary`.
  * Expandir enumerações de escopo para suportar `full_branch`, `working_tree_diff`, `subdirectory`, `single_file`.

### 1.2. Camada de Serviço & Orquestração
* **`frontend/src/app/services/culture-guardian.service.ts`**:
  * Adicionar métodos para disparar avaliação com payload de escopo (`runScopedEvaluation(request: CustomEvaluationRequest)`).
  * Salvar e restaurar perfis de regras e escopos por repositório no storage local/API.

### 1.3. Interface de Usuário & Componentes
* **`frontend/src/app/app.ts`**:
  * Adicionar Signals de controle de escopo: `auditScopeMode`, `scopeSubdirectoryPath`, `scopeSingleFilePath`.
  * Adicionar Signals de seleção de regras complementares: `activeRuleIds`, `ruleSeverityOverrides`.
  * Adicionar ações para alternar regras em lote e salvar perfis de regras.
* **`frontend/src/app/app.html`**:
  * Adicionar barra visual de parametrização de escopo na aba "Live Code & Diff Auditor" e "Dashboard".
  * Adicionar gaveta/painel de composição modular de regras complementares com checkboxes e badges de categorias.

### 1.4. Backend / Scripts de Auditoria
* **`scripts/culture_guard.py`**:
  * Expandir argumentos CLI: `--scope <full|diff|subdir|file>`, `--subdir <path>`, `--rules <rule1,rule2,...>`, `--rules-file <path>`.
  * Implementar resolvedor de arquivos por escopo antes de repassar ao motor Bend / analisador léxico.
* **`scripts/guardian_server.py`**:
  * Suportar payload com escopo e lista dinâmica de regras no endpoint `/api/audit/evaluate`.

---

## 2. Estratégia Técnica

### 2.1. Resolução do Escopo de Arquivos
A resolução do escopo ocorre de maneira determinística antes do disparo das regras:

```python
# Estratégia de resolução de escopo em scripts/culture_guard.py
def resolve_scope_files(repo_path: str, scope: str, target: str = None) -> list[str]:
    if scope == 'single_file':
        return [target] if os.path.isfile(target) else []
    elif scope == 'subdirectory':
        base_dir = os.path.join(repo_path, target) if target else repo_path
        return [os.path.join(root, f) for root, _, files in os.walk(base_dir) for f in files if is_source_code(f)]
    elif scope == 'working_tree_diff':
        return get_git_modified_files(repo_path)
    else: # full_branch
        return get_all_git_tracked_files(repo_path)
```

### 2.2. Composição Modular de Regras
As regras são compostas através de um mapa de regras ativas onde cada regra possui seu identificador, condição de disparo e severidade customizável pelo usuário.

---

## 3. Dependências e Pré-requisitos

- [x] Motor léxico e analisador estrutural de regras funcionais em Python/Bend.
- [x] Suporte a leitura de repositórios locais e GitHub via `CultureGuardianService`.
- [x] Interface reativa com Angular 19 Signals para atualização instantânea da UI.

---

## 4. Riscos e Pontos de Atenção

| Risco | Impacto | Mitigação |
| :--- | :--- | :--- |
| **Escopo muito amplo em monorepos (milhares de arquivos)** | Médio (tempo de execução) | Paralelismo na resolução de arquivos e indicador de progresso com contagem prévia de arquivos. |
| **Nenhuma regra selecionada pelo usuário** | Baixo | Validação preventiva na UI: desabilitar o botão de auditoria se 0 regras estiverem ativas, exibindo alerta instrutivo. |
| **Caminho de subdiretório inválido ou inexistente** | Baixo | Validador visual imediato no input de texto com feedback de diretório válido/inválido. |
