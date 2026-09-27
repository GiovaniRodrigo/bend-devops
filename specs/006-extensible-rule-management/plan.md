# Plano de Implementação: Extensible Rule Management & Custom Rule Engine

---

## 1. Arquivos a Criar/Editar

### 1.1. Backend & Rule Engine (Python)
* **`scripts/rule_model.py`**: Modelos de dados e enumerações (`RuleType`, `RuleSeverity`, `RuleStatus`, `RuleTier`).
* **`scripts/rule_registry.py`**: Registro central de regras com suporte a CRUD, clonagem e resolução hierárquica de precedência.
* **`scripts/rule_normalizer.py`**: Normalizador de regras e mapeador canônico para a engine Bend.
* **`scripts/rule_test_engine.py`**: Motor de teste unitário isolado com proteção ReDoS para validação de regras.
* **`backend/rules/rules_schema.json`**: JSON Schema formal para validação de manifests de regras customizadas.

### 1.2. Frontend (Angular 19)
* **`frontend/src/app/models/culture.model.ts`**: Tipos TypeScript sincronizados para regras customizadas.
* **`frontend/src/app/services/culture-guardian.service.ts`**: Métodos de integração para CRUD, importação, clonagem e testes de regras.
* **`frontend/src/app/app.ts` & `frontend/src/app/app.html`**: Wizard de criação de regras (8 passos), modal de clonagem, modal de teste interativo e log de mutações.

---

## 2. Estratégia Técnica (TDD)

1. **Test-First Red**: Escrever testes para schemas de validação e classes do `RuleRegistry`.
2. **Green**: Implementar `RuleRegistry`, `RuleModel` e `RuleNormalizer`.
3. **Refactor**: Integrar ao motor de redução paralela Bend e ao dashboard Angular.

---

## 3. Riscos e Mitigações

| Risco | Impacto | Mitigação |
| :--- | :--- | :--- |
| **Expressões regulares catastróficas (ReDoS)** | Alto | Timeout de 500ms em cada avaliação de regex e validação léxica prévia. |
| **Colisão de IDs de regras** | Médio | Validação de unicidade e bloqueio de sobrescrita sem flag explícita. |
