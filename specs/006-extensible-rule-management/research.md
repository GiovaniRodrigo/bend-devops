# Pesquisa e Referências: Extensible Rule Management

---

## 1. Padrões Existentes
- Manifests JSON em `backend/rules/`
- Schema JSON em `backend/rules/rules_schema.json`

## 2. Decisões Técnicas
- **ReDoS Protection**: Timeout via `signal` ou `threading` em 100ms.
- **Hierarquia de Tiers**: `builtin` (base) < `organization` < `project` < `repository` (prioridade máxima).
