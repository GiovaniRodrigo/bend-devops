# Especificação de Testes (TDD): Extensible Rule Management

---

## 1. Matriz de Cobertura de Testes

| RF/RN | Descrição | Status | Criticidade | Camada |
| :--- | :--- | :--- | :--- | :--- |
| **RF01** | CRUD completo de regras customizadas | ❌ Ausente | 🔴 P0 | Unitário / Backend |
| **RF02** | Validação contra JSON Schema (`rules_schema.json`) | ❌ Ausente | 🔴 P0 | Unitário / Schema |
| **RF03** | Resolução hierárquica de precedência (Built-in -> Org -> Proj -> Repo) | ❌ Ausente | 🔴 P0 | Unitário |
| **RF04** | Motor de teste isolado com proteção ReDoS | ❌ Ausente | 🔴 P0 | Unitário / Engine |
| **RF05** | Clonagem e versionamento de regras | ❌ Ausente | 🟠 P1 | Unitário |
| **RF06** | Importação e exportação em lote de manifests JSON | ❌ Ausente | 🟠 P1 | Integração |
| **RF07** | Execução e recalibração no Quality Gate do dashboard | ❌ Ausente | 🔴 P0 | Integração / UI |

---

## 2. Esqueletos de Teste TDD (`tests/test_rule_registry.py`, `tests/test_rule_api.py`)

```python
import unittest
from scripts.rule_registry import RuleRegistry
from scripts.rule_test_engine import RuleTestEngine

class TestRuleManagementTDD(unittest.TestCase):
    def setUp(self):
        self.registry = RuleRegistry()
        self.test_engine = RuleTestEngine()

    def test_RF01_create_and_get_rule(self):
        """TDD: Criação e recuperação de regra no catálogo"""
        rule = {"id": "CUSTOM-01", "name": "Custom", "type": "pattern", "severity": "P0"}
        self.registry.register(rule)
        self.assertEqual(self.registry.get("CUSTOM-01")["name"], "Custom")

    def test_RF04_redos_protection(self):
        """TDD: ReDoS seguro com timeout"""
        evil_regex = r"^(a+)+$"
        evil_input = "a" * 100 + "!"
        result = self.test_engine.evaluate_regex(evil_regex, evil_input, timeout_ms=100)
        self.assertFalse(result.matched)
```
