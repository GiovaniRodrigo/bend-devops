"""
Comprehensive Unit Tests for Extensible Rule Management, Rule Registry, Normalizer, Test Engine, and Precedence
"""

import os
import json
import unittest
import tempfile
import shutil
from pathlib import Path

from scripts.rule_model import (
    RuleDefinition,
    RuleType,
    RuleSeverity,
    RuleStatus,
    RuleTier,
    RuleScope,
    RuleCondition,
    RuleSuppressionConfig,
    RuleTestFixture,
    UserRole
)
from scripts.rule_normalizer import RuleNormalizer
from scripts.rule_test_engine import RuleTestEngine, RegexSafetyValidator
from scripts.rule_registry import RuleRegistry


class TestRegexSafetyValidator(unittest.TestCase):
    def test_safe_patterns(self):
        safe_regexes = [
            r"password\s*=\s*['\"][^'\"]+['\"]",
            r"^import\s+[a-zA-Z0-9_\.]+",
            r"@spec\s+RF\d+",
            r"TODO|FIXME",
            r"class\s+[A-Z][a-zA-Z0-9]*\s*:"
        ]
        for pattern in safe_regexes:
            valid, msg = RegexSafetyValidator.is_safe_pattern(pattern)
            self.assertTrue(valid, f"Pattern {pattern} should be safe but failed: {msg}")

    def test_redos_catastrophic_backtracking_patterns(self):
        unsafe_regexes = [
            r"([a-zA-Z0-9_]+\+)+",
            r"([a-zA-Z0-9_]+\*)+",
            r"(\.\*)+",
            r"(\.\+)+"
        ]
        for pattern in unsafe_regexes:
            valid, msg = RegexSafetyValidator.is_safe_pattern(pattern)
            self.assertFalse(valid, f"Pattern {pattern} should be flagged as unsafe")

    def test_invalid_syntax_pattern(self):
        valid, msg = RegexSafetyValidator.is_safe_pattern(r"[a-z(")
        self.assertFalse(valid)
        self.assertIn("Invalid regex syntax", msg)


class TestRuleNormalizer(unittest.TestCase):
    def test_normalize_valid_dict(self):
        data = {
            "id": "SEC-006",
            "version": "1.0.0",
            "name": "No Hardcoded Credentials",
            "description": "Detects hardcoded credentials",
            "type": "pattern",
            "category": "security",
            "severity": "P0",
            "enabled": True,
            "tier": "custom",
            "architectures": ["clean_architecture"],
            "languages": ["python", "typescript", "csharp"],
            "scope": {
                "include": ["src/**"],
                "exclude": ["tests/**"]
            },
            "condition": {
                "pattern": r"(api[_-]?key|secret|password)\s*[:=]\s*['\"][A-Za-z0-9_\-\.]{8,}['\"]"
            },
            "message": "Hardcoded credential detected.",
            "suggestion": "Use environment variables.",
            "suppression": {
                "allowed": True,
                "pragma": "@guardian-ignore",
                "requires_reason": True,
                "minimum_reason_length": 8
            }
        }
        rule = RuleNormalizer.normalize(data, fallback_tier=RuleTier.CUSTOM)
        self.assertIsInstance(rule, RuleDefinition)
        self.assertEqual(rule.id, "SEC-006")
        self.assertEqual(rule.type, RuleType.PATTERN)
        self.assertEqual(rule.severity, RuleSeverity.P0)
        self.assertEqual(rule.status, RuleStatus.ACTIVE)
        self.assertTrue(rule.suppression.requires_reason)
        self.assertEqual(rule.suppression.minimum_reason_length, 8)

    def test_normalize_legacy_manifest(self):
        legacy = {
            "id": "ARCH-LAYER-01",
            "name": "Zero Presentation Code in Domain",
            "category": "Architecture - Layer Boundaries",
            "severity": "P0_BLOCKING",
            "penaltyPoints": 40,
            "description": "Prohibits HTML in domain",
            "rationale": "Separation of concerns",
            "remediation": "Move to views",
            "languages": ["C#", "Python", "TypeScript"],
            "status": "active"
        }
        rule = RuleNormalizer.normalize(legacy, fallback_tier=RuleTier.BUILTIN)
        self.assertEqual(rule.id, "ARCH-LAYER-01")
        self.assertEqual(rule.type, RuleType.ARCHITECTURE)
        self.assertEqual(rule.severity, RuleSeverity.P0)
        self.assertEqual(rule.tier, RuleTier.BUILTIN)
        self.assertEqual(rule.status, RuleStatus.ACTIVE)


class TestRuleTestEngine(unittest.TestCase):
    def setUp(self):
        self.rule = RuleDefinition(
            id="SEC-006",
            version="1.0.0",
            name="No Hardcoded Credentials",
            description="Detects hardcoded credentials",
            type=RuleType.PATTERN,
            category="security",
            severity=RuleSeverity.P0,
            penalty_points=40,
            status=RuleStatus.ACTIVE,
            enabled=True,
            tier=RuleTier.CUSTOM,
            architectures=["clean_architecture"],
            languages=["python", "typescript"],
            scope=RuleScope(include=["src/**"], exclude=["tests/**"]),
            condition=RuleCondition(
                pattern=r"(password|secret|api_key)\s*=\s*['\"][A-Za-z0-9_\-\.]{8,}['\"]"
            ),
            message="Hardcoded credential detected.",
            suggestion="Use environment variables.",
            suppression=RuleSuppressionConfig(
                allowed=True,
                pragma="@guardian-ignore",
                requires_reason=True,
                minimum_reason_length=8
            )
        )

    def test_rule_detects_violation(self):
        code = 'password = "supersecretpassword123"'
        result = RuleTestEngine.run_test(self.rule, code, file_name="src/auth.py")
        self.assertTrue(result.has_violation)
        self.assertFalse(result.is_suppressed)
        self.assertEqual(len(result.violations), 1)
        self.assertEqual(result.matched_lines, [1])

    def test_rule_clean_code(self):
        code = 'password = os.environ.get("DB_PASSWORD")'
        result = RuleTestEngine.run_test(self.rule, code, file_name="src/auth.py")
        self.assertFalse(result.has_violation)
        self.assertEqual(len(result.violations), 0)

    def test_rule_justified_suppression(self):
        code = (
            '# @guardian-ignore SEC-006: Temporary mock key in sandbox testing environment\n'
            'password = "supersecretpassword123"'
        )
        result = RuleTestEngine.run_test(self.rule, code, file_name="src/auth.py")
        self.assertTrue(result.has_violation)
        self.assertTrue(result.is_suppressed)
        self.assertEqual(len(result.violations), 0)
        self.assertIn("Temporary mock key", result.suppression_reason)

    def test_rule_short_suppression_rejected(self):
        code = (
            '# @guardian-ignore SEC-006: short\n'
            'password = "supersecretpassword123"'
        )
        result = RuleTestEngine.run_test(self.rule, code, file_name="src/auth.py")
        self.assertTrue(result.has_violation)
        self.assertFalse(result.is_suppressed)
        self.assertEqual(len(result.violations), 1)

    def test_execute_fixtures(self):
        fixtures = [
            RuleTestFixture(
                name="Detects hardcoded password",
                input='password = "supersecretpassword123"',
                expected_violation=True
            ),
            RuleTestFixture(
                name="Passes env var reading",
                input='password = os.getenv("PASS")',
                expected_violation=False
            )
        ]
        self.rule.tests = fixtures
        report = RuleTestEngine.execute_fixtures(self.rule)
        self.assertTrue(report["passed"])
        self.assertEqual(report["passed_fixtures"], 2)


class TestRuleRegistry(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.custom_dir = Path(self.temp_dir) / "custom"
        self.custom_dir.mkdir(parents=True, exist_ok=True)
        self.registry = RuleRegistry(custom_rules_dir=self.custom_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_register_and_get_rule(self):
        rule = RuleDefinition(
            id="TEST-001",
            version="1.0.0",
            name="Test Rule",
            description="Test rule description",
            type=RuleType.PATTERN,
            category="custom",
            severity=RuleSeverity.P1,
            penalty_points=15,
            status=RuleStatus.ACTIVE,
            enabled=True,
            tier=RuleTier.CUSTOM,
            condition=RuleCondition(pattern=r"test_pattern"),
            message="Test pattern matched",
            suggestion="Fix test pattern"
        )
        created = self.registry.register(rule, actor="tester", user_role=UserRole.RULE_ADMIN)
        self.assertEqual(created.id, "TEST-001")

        fetched = self.registry.get("TEST-001")
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.name, "Test Rule")

    def test_precedence_resolution(self):
        # Builtin tier
        builtin_rule = RuleDefinition(
            id="PREC-01",
            version="1.0.0",
            name="Builtin Version",
            description="Desc",
            type=RuleType.PATTERN,
            category="architecture",
            severity=RuleSeverity.P2,
            penalty_points=5,
            tier=RuleTier.BUILTIN
        )
        # Custom tier with same ID
        custom_rule = RuleDefinition(
            id="PREC-01",
            version="2.0.0",
            name="Custom Override Version",
            description="Desc",
            type=RuleType.PATTERN,
            category="architecture",
            severity=RuleSeverity.P0,
            penalty_points=40,
            tier=RuleTier.CUSTOM
        )

        self.registry.register(builtin_rule, user_role=UserRole.RULE_ADMIN)
        self.registry.register(custom_rule, user_role=UserRole.RULE_ADMIN)

        effective = self.registry.get("PREC-01")
        self.assertIsNotNone(effective)
        self.assertEqual(effective.name, "Custom Override Version")
        self.assertEqual(effective.severity, RuleSeverity.P0)
        self.assertEqual(effective.tier, RuleTier.CUSTOM)

    def test_clone_rule(self):
        original = RuleDefinition(
            id="ARCH-SRC-01",
            version="1.0.0",
            name="Source Rule",
            description="Source description",
            type=RuleType.PATTERN,
            category="architecture",
            severity=RuleSeverity.P1,
            penalty_points=10,
            tier=RuleTier.BUILTIN,
            condition=RuleCondition(pattern=r"src_pattern")
        )
        self.registry.register(original, user_role=UserRole.RULE_ADMIN)

        cloned = self.registry.clone(
            "ARCH-SRC-01",
            new_id="ARCH-SRC-01-CUSTOM",
            new_name="Customized Source Rule",
            actor="engineer",
            user_role=UserRole.RULE_AUTHOR
        )
        self.assertEqual(cloned.id, "ARCH-SRC-01-CUSTOM")
        self.assertEqual(cloned.name, "Customized Source Rule")
        self.assertEqual(cloned.tier, RuleTier.CUSTOM)
        self.assertEqual(cloned.status, RuleStatus.DRAFT)

        self.assertIsNotNone(self.registry.get("ARCH-SRC-01-CUSTOM"))

    def test_delete_rule(self):
        rule = RuleDefinition(
            id="DEL-001",
            version="1.0.0",
            name="Delete Rule",
            description="To be deleted",
            type=RuleType.PATTERN,
            category="custom",
            severity=RuleSeverity.P2,
            penalty_points=5,
            tier=RuleTier.CUSTOM
        )
        self.registry.register(rule, user_role=UserRole.RULE_ADMIN)
        self.assertIsNotNone(self.registry.get("DEL-001"))

        deleted = self.registry.delete("DEL-001", actor="admin", user_role=UserRole.RULE_ADMIN)
        self.assertTrue(deleted)
        self.assertIsNone(self.registry.get("DEL-001"))

    def test_enable_disable_status_lifecycle(self):
        rule = RuleDefinition(
            id="LIFE-001",
            version="1.0.0",
            name="Lifecycle Rule",
            description="Lifecycle test",
            type=RuleType.PATTERN,
            category="quality",
            severity=RuleSeverity.P1,
            penalty_points=10,
            status=RuleStatus.DRAFT,
            enabled=False,
            tier=RuleTier.CUSTOM
        )
        self.registry.register(rule, user_role=UserRole.RULE_ADMIN)

        # Enable
        enabled_rule = self.registry.enable("LIFE-001", actor="admin", user_role=UserRole.RULE_ADMIN)
        self.assertTrue(enabled_rule.enabled)
        self.assertEqual(enabled_rule.status, RuleStatus.ACTIVE)

        # Disable
        disabled_rule = self.registry.disable("LIFE-001", actor="admin", user_role=UserRole.RULE_ADMIN)
        self.assertFalse(disabled_rule.enabled)

    def test_export_and_import_manifest(self):
        rule1 = RuleDefinition(
            id="IMP-001",
            version="1.0.0",
            name="Import Test 1",
            description="Desc 1",
            type=RuleType.PATTERN,
            category="security",
            severity=RuleSeverity.P0,
            penalty_points=30,
            tier=RuleTier.CUSTOM
        )
        rule2 = RuleDefinition(
            id="IMP-002",
            version="1.0.0",
            name="Import Test 2",
            description="Desc 2",
            type=RuleType.PATTERN,
            category="quality",
            severity=RuleSeverity.P1,
            penalty_points=10,
            tier=RuleTier.CUSTOM
        )
        self.registry.register(rule1, user_role=UserRole.RULE_ADMIN)
        self.registry.register(rule2, user_role=UserRole.RULE_ADMIN)

        exported_json = self.registry.export_manifest(tier=RuleTier.CUSTOM)
        manifest_data = json.loads(exported_json)
        self.assertIn("rules", manifest_data)
        self.assertEqual(len(manifest_data["rules"]), 2)

        # Import into fresh registry
        fresh_dir = Path(self.temp_dir) / "fresh_custom"
        fresh_dir.mkdir(parents=True, exist_ok=True)
        fresh_registry = RuleRegistry(custom_rules_dir=fresh_dir)
        import_result = fresh_registry.import_manifest(
            manifest_data["rules"],
            overwrite=True,
            actor="ci_importer",
            user_role=UserRole.RULE_ADMIN
        )
        self.assertEqual(import_result["imported"], 2)
        self.assertEqual(import_result["failed"], 0)
        self.assertIsNotNone(fresh_registry.get("IMP-001"))
        self.assertIsNotNone(fresh_registry.get("IMP-002"))

    def test_audit_trail_recorded(self):
        rule = RuleDefinition(
            id="AUDIT-001",
            version="1.0.0",
            name="Audit Rule",
            description="Desc",
            type=RuleType.PATTERN,
            category="quality",
            severity=RuleSeverity.P1,
            penalty_points=10,
            tier=RuleTier.CUSTOM
        )
        self.registry.register(rule, actor="alice", user_role=UserRole.RULE_ADMIN)
        self.registry.enable("AUDIT-001", actor="bob", user_role=UserRole.RULE_ADMIN)
        self.registry.disable("AUDIT-001", actor="charlie", user_role=UserRole.RULE_ADMIN)

        trail = self.registry.get_audit_trail("AUDIT-001")
        self.assertGreaterEqual(len(trail), 3)
        actions = [entry.action for entry in trail]
        self.assertIn("CREATE", actions)
        self.assertIn("ENABLE", actions)
        self.assertIn("DISABLE", actions)


if __name__ == "__main__":
    unittest.main()
