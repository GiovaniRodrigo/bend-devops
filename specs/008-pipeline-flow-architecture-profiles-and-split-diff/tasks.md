# Tarefas de Implementação: Pipeline Flow, Architecture Profiles, Split Diff & Coverage

Lista estruturada de tarefas atômicas sequenciadas no fluxo TDD. Cada tarefa de implementação é precedida pela sua respectiva especificação e teste correspondente.

---

- [x] 1. Escrever testes unitários para reordenação de estágios de pipeline (`frontend/src/app/app.spec.ts`)
- [x] 2. Implementar suporte a HTML5 Drag & Drop e botões de precisão nos estágios do pipeline (`frontend/src/app/app.html` e `frontend/src/app/app.ts`)
- [x] 3. Implementar renderizador dinâmico de diagrama de fluxo visual de pipeline com conexões SVG (`frontend/src/app/app.html`)
- [x] 4. Escrever testes unitários para o modal de detalhes de regras ao clicar no card (`frontend/src/app/app.spec.ts`)
- [x] 5. Implementar modal de visualização detalhada de regras `rule-details-modal` (`frontend/src/app/app.html` e `frontend/src/app/app.ts`)
- [x] 6. Escrever testes para criação, edição e turnover de status (Ativo/Inativo) de Architecture Profiles (`frontend/src/app/app.spec.ts`)
- [x] 7. Implementar modal de edição de Architecture Profiles e botão de turnover de status direto (`frontend/src/app/app.html` e `frontend/src/app/app.ts`)
- [x] 8. Isolar a barra de rolagem do conteúdo central em relação ao menu lateral para baixa carga cognitiva (`frontend/src/app/app.html`)
- [x] 9. Escrever testes unitários para a visualização em 2 colunas e sincronismo de Split Diff no Branch Analysis (`frontend/src/app/app.spec.ts`)
- [x] 10. Reestruturar a visualização de *Branch Analysis Result* com coluna de resumo à esquerda e Live Split Code & Diff Inspector à direita (`frontend/src/app/app.html` e `frontend/src/app/app.ts`)
- [x] 11. Configurar `.coveragerc`, `requirements.txt` e `package.json` com `coverage>=7.16.1` e scripts de execução (`requirements.txt`, `.coveragerc`, `package.json`)
- [x] 12. Atualizar `./scripts/validate.sh` e `.github/workflows/ci.yml` para medir cobertura de testes Python e gerar relatórios no terminal e HTML (`scripts/validate.sh`, `.github/workflows/ci.yml`)
- [x] 13. Executar validação completa do pipeline (51 testes Angular Vitest, testes Bend HVM, testes Python Coverage, 20 screenshots Playwright) (`./scripts/validate.sh`)
