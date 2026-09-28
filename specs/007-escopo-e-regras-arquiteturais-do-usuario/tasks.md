# Tarefas de Implementação: Escopo e Regras Arquiteturais do Usuário

Lista de tarefas ordenadas por dependência de execução (fluxo TDD). Cada tarefa é atômica e verificável.

---

- [x] 1. Escrever testes unitários para resolução de escopos de arquivos (`tests/test_user_scoped_rules.py`)
- [x] 2. Implementar a função de resolução de escopos `resolve_scope_files` (`scripts/culture_guard.py`)
- [x] 3. Escrever testes para composição dinâmica de regras e cálculo de score (`tests/test_user_scoped_rules.py`)
- [x] 4. Atualizar o motor de avaliação para aceitar lista customizada de regras e severidades (`scripts/culture_guard.py`)
- [x] 5. Expandir os modelos de dados com interfaces de escopo e requisição customizada (`frontend/src/app/models/culture.model.ts`)
- [x] 6. Escrever testes de serviço para chamada do endpoint de avaliação com escopo (`frontend/src/app/services/culture-guardian.service.spec.ts`)
- [x] 7. Implementar método `runScopedEvaluation` no serviço Angular (`frontend/src/app/services/culture-guardian.service.ts`)
- [x] 8. Adicionar controles visuais de escopo (Full, Diff, Subdir, File) no template (`frontend/src/app/app.html`)
- [x] 9. Adicionar painel de seleção modular de regras complementares e calibração de severidade (`frontend/src/app/app.html` e `frontend/src/app/app.ts`)
- [x] 10. Atualizar o endpoint `/api/audit/evaluate` no servidor para aceitar payload com escopo e regras (`scripts/guardian_server.py`)
- [x] 11. Atualizar comandos e documentação CLI para suporte aos novos parâmetros de escopo (`scripts/culture_guard.py` e `docs/`)
- [x] 12. Executar a suíte de testes completa de frontend e backend para validação final (`./scripts/validate.sh`)
