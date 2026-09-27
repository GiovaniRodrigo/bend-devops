# Tarefas de Implementação: Extensible Rule Management (TDD)

---

- [ ] 1. Escrever testes de validação de schema para regras (`tests/test_rule_schema.py`)
- [ ] 2. Implementar schema de validação JSON (`backend/rules/rules_schema.json`)
- [ ] 3. Escrever testes unitários para o `RuleRegistry` e resolução de precedência (`tests/test_rule_registry.py`)
- [ ] 4. Implementar a classe `RuleRegistry` com CRUD, clonagem e versionamento (`scripts/rule_registry.py`)
- [ ] 5. Escrever testes para o `RuleTestEngine` e proteção ReDoS (`tests/test_rule_test_engine.py`)
- [ ] 6. Implementar o `RuleTestEngine` com sandbox e timeout (`scripts/rule_test_engine.py`)
- [ ] 7. Escrever testes de integração para endpoints REST de regras (`tests/test_rule_api.py`)
- [ ] 8. Implementar rotas de CRUD e teste de regras no servidor (`scripts/guardian_server.py`)
- [ ] 9. Escrever testes de serviço frontend para gerenciamento de regras (`frontend/src/app/services/culture-guardian.service.spec.ts`)
- [ ] 10. Implementar métodos de API no serviço Angular (`frontend/src/app/services/culture-guardian.service.ts`)
- [ ] 11. Implementar Wizard de criação e Console de teste no template Angular (`frontend/src/app/app.html`)
- [ ] 12. Executar suíte completa de testes de regras e frontend (`pytest tests/ && npm test`)
