"""
Unit Tests for Rule Schema Validation (backend/rules/rules_schema.json)
Spec: specs/006-extensible-rule-management/
"""

import json
import unittest
from pathlib import Path

from scripts.rule_registry import RuleRegistry
from scripts.rule_normalizer import RuleNormalizer
from scripts.rule_model import RuleDefinition, RuleType, RuleSeverity, RuleTier


class TestRuleSchema(unittest.TestCase):
    def setUp(self):
        self.schema_path = Path(__file__).resolve().parent.parent / "backend" / "rules" / "rules_schema.json"
        self.registry = RuleRegistry.get_instance()

    def test_schema_file_exists_and_valid_json(self):
        """Verifies rules_schema.json exists and is valid JSON schema."""
        self.assertTrue(self.schema_path.exists(), "rules_schema.json not found")
        schema = json.loads(self.schema_path.read_text(encoding="utf-8"))
        self.assertEqual(schema.get("$schema"), "http://json-schema.org/draft-07/schema#")
        rule_props = schema["definitions"]["rule_item"]["properties"]
        self.assertIn("id", rule_props)
        self.assertIn("type", rule_props)

    def test_valid_rule_passes_schema_validation(self):
        """Valid declarative rule payload passes schema validation."""
        valid_payload = {
            "id": "SEC-CUSTOM-001",
            "name": "Disallow Hardcoded JWT Secrets",
            "description": "Flags hardcoded JWT signing secrets in source code",
            "category": "security",
            "type": "pattern",
            "severity": "P0",
            "languages": ["python", "typescript", "csharp"],
            "condition": {
                "pattern": r"jwt\.sign\(.*,\s*['\"][a-zA-Z0-9_\-]{8,}['\"]"
            },
            "message": "Hardcoded JWT secret detected",
            "suggestion": "Read secret from environment variables or Key Vault"
        }
        valid, errors = self.registry.validate_rule(valid_payload)
        self.assertTrue(valid, f"Validation should succeed but got errors: {errors}")
        self.assertEqual(len(errors), 0)

    def test_invalid_rule_missing_required_fields_fails(self):
        """Rule payload missing mandatory fields fails schema validation."""
        invalid_payload = {
            "name": "Missing ID and Type Rule"
        }
        valid, errors = self.registry.validate_rule(invalid_payload)
        self.assertFalse(valid)
        self.assertTrue(any("id" in str(e).lower() or "type" in str(e).lower() for e in errors))

    def test_invalid_rule_type_fails(self):
        """Rule with unsupported type fails schema validation."""
        invalid_type_payload = {
            "id": "TEST-001",
            "name": "Invalid Type Test",
            "type": "unsupported_magic_type",
            "category": "architecture",
            "severity": "P0"
        }
        valid, errors = self.registry.validate_rule(invalid_type_payload)
        self.assertFalse(valid)


if __name__ == "__main__":
    unittest.main()
