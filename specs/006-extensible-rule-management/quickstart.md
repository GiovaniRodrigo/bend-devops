# Quickstart: Extensible Rule Management

Guia para criação, validação e teste de regras customizadas.

---

## Comandos CLI

```bash
# 1. Listar todas as regras registradas
python3 scripts/culture_guard.py rules list

# 2. Testar uma regra interativamente
python3 scripts/culture_guard.py rules test CULT01 --code "def fn(): pass"

# 3. Validar manifest JSON de regras
python3 scripts/culture_guard.py rules validate backend/rules/custom/my_rule.json

# 4. Executar suíte de testes de regras
python3 -m unittest discover tests/ -p "test_rule_*.py"
```
