"""
Comprehensive unit tests for scripts/rule_model.py, rule_normalizer.py, rule_registry.py, rule_test_engine.py, token_filter.py.
"""

import sys
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.rule_model import (
    RuleDefinition,
    RuleType,
    RuleSeverity,
    RuleStatus,
    RuleTier,
    RuleScope,
    RuleCondition,
    RuleTestFixture
)
from scripts.rule_normalizer import RuleNormalizer
from scripts.rule_registry import RuleRegistry
from scripts.rule_test_engine import RuleTestEngine, RegexSafetyValidator, RuleTestResult
from scripts.token_filter import (
    TokenFilter,
    IgnoredFilePattern,
    strip_comments,
    parse_inline_pragmas,
    matches_exact_token,
    load_guardianignore,
    is_file_or_rule_exempt
)


class TestRuleModelComprehensive(unittest.TestCase):
    def test_enums_and_values(self):
        self.assertEqual(RuleSeverity.normalize("p0"), RuleSeverity.P0)
        self.assertEqual(RuleSeverity.normalize("p1_warning"), RuleSeverity.P1)
        self.assertEqual(RuleSeverity.normalize("p2_info"), RuleSeverity.P2)
        self.assertEqual(RuleSeverity.normalize("p3"), RuleSeverity.P3)
        self.assertEqual(RuleSeverity.normalize("info"), RuleSeverity.INFO)

        self.assertEqual(RuleStatus.normalize("active"), RuleStatus.ACTIVE)
        self.assertEqual(RuleStatus.normalize("draft"), RuleStatus.DRAFT)
        self.assertEqual(RuleStatus.normalize("testing"), RuleStatus.TESTING)
        self.assertEqual(RuleStatus.normalize("deprecated"), RuleStatus.DEPRECATED)
        self.assertEqual(RuleStatus.normalize("archived"), RuleStatus.ARCHIVED)

        self.assertEqual(RuleTier.BUILTIN, RuleTier("builtin"))
        self.assertEqual(RuleTier.ORGANIZATION, RuleTier("organization"))
        self.assertEqual(RuleTier.PROJECT, RuleTier("project"))
        self.assertEqual(RuleTier.CUSTOM, RuleTier("custom"))

        self.assertEqual(RuleType.PATTERN, RuleType("pattern"))
        self.assertEqual(RuleType.NAMING, RuleType("naming"))
        self.assertEqual(RuleType.DEPENDENCY, RuleType("dependency"))
        self.assertEqual(RuleType.ARCHITECTURE, RuleType("architecture"))

    def test_rule_definition_to_from_dict(self):
        data = {
            "id": "CUSTOM-001",
            "name": "Test Custom Rule",
            "description": "Rule description",
            "category": "Security",
            "severity": "P0",
            "status": "ACTIVE",
            "tier": "custom",
            "type": "pattern",
            "pattern": r"secret_\w+",
            "languages": ["python", "csharp"],
            "penaltyPoints": 35,
            "message": "Secret found",
            "suggestion": "Remove secret",
            "metadata": {"author": "QA Engineer"}
        }
        rule = RuleNormalizer.normalize_rule_dict(data)
        self.assertEqual(rule.id, "CUSTOM-001")
        self.assertEqual(rule.severity, RuleSeverity.P0)
        self.assertEqual(rule.penalty_points, 35)

        exported = rule.to_dict()
        self.assertEqual(exported["id"], "CUSTOM-001")
        self.assertEqual(exported["severity"], "P0")
        self.assertIn("metadata", exported)


class TestRuleNormalizerComprehensive(unittest.TestCase):
    def test_normalize_incomplete_rule(self):
        minimal_data = {
            "name": "Minimal Rule Without ID",
            "pattern": "console\\.log"
        }
        rule = RuleNormalizer.normalize_rule_dict(minimal_data)
        self.assertEqual(rule.id, "")
        self.assertIn("python", rule.languages)
        self.assertEqual(rule.status, RuleStatus.ACTIVE)

    def test_normalize_naming_rule(self):
        naming_data = {
            "id": "NAME-01",
            "name": "PascalCase Interfaces",
            "type": "naming",
            "namingConvention": "PascalCase",
            "prefix": "I",
            "category": "Naming"
        }
        rule = RuleNormalizer.normalize_rule_dict(naming_data)
        self.assertEqual(rule.type, RuleType.NAMING)


class TestRegexSafetyValidator(unittest.TestCase):
    def test_safe_patterns(self):
        safe_pattern = r"(?i)(api[_-]?key|secret)\s*=\s*['\"][A-Za-z0-9]{12,}['\"]"
        is_safe, error = RegexSafetyValidator.is_safe_pattern(safe_pattern)
        self.assertTrue(is_safe)
        self.assertIsNone(error)

    def test_invalid_syntax_pattern(self):
        invalid_pattern = r"[a-z"
        is_safe, error = RegexSafetyValidator.is_safe_pattern(invalid_pattern)
        self.assertFalse(is_safe)
        self.assertIn("Invalid regex syntax", error)

    def test_redos_catastrophic_pattern(self):
        # Nested quantifiers
        dangerous_pattern = r"(a+)+"
        is_safe, error = RegexSafetyValidator.is_safe_pattern(dangerous_pattern)
        self.assertFalse(is_safe)
        self.assertIn("nested quantifiers", error)


class TestRuleTestEngineComprehensive(unittest.TestCase):
    def setUp(self):
        self.rule = RuleDefinition(
            id="TEST-HTTP-01",
            name="No HttpContext in Domain",
            description="Blocks direct HttpContext coupling",
            category="Architecture",
            severity=RuleSeverity.P0,
            status=RuleStatus.ACTIVE,
            tier=RuleTier.CUSTOM,
            type=RuleType.PATTERN,
            condition=RuleCondition(pattern=r"(?i)HttpContext\.Current"),
            message="Direct HttpContext coupling detected",
            suggestion="Use dependency injection",
            penalty_points=35
        )

    def test_rule_test_with_violation(self):
        code = "public void DoWork() {\n    var ctx = HttpContext.Current;\n}\n"
        res = RuleTestEngine.test_rule(self.rule, code, "OrderService.cs")
        self.assertTrue(res.has_violation)
        self.assertEqual(len(res.violations), 1)
        self.assertEqual(res.matched_lines, [2])
        self.assertFalse(res.is_suppressed)

    def test_rule_test_with_pragma_suppression(self):
        code = "public void DoWork() {\n    // @guardian-ignore TEST-HTTP-01: Valid justification for test\n    var ctx = HttpContext.Current;\n}\n"
        res = RuleTestEngine.test_rule(self.rule, code, "OrderService.cs")
        self.assertTrue(res.is_suppressed)
        self.assertEqual(len(res.violations), 0)

    def test_rule_test_clean_code(self):
        code = "public void DoWork() {\n    Console.WriteLine(\"Done\");\n}\n"
        res = RuleTestEngine.test_rule(self.rule, code, "OrderService.cs")
        self.assertFalse(res.has_violation)
        self.assertEqual(len(res.violations), 0)

    def test_rule_test_cases_suite(self):
        rule_with_test_cases = RuleDefinition(
            id="TEST-TC-01",
            name="Rule with Test Cases",
            description="Validation",
            category="Quality",
            severity=RuleSeverity.P1,
            status=RuleStatus.ACTIVE,
            tier=RuleTier.CUSTOM,
            type=RuleType.PATTERN,
            condition=RuleCondition(pattern=r"debugger;"),
            message="Debugger found",
            tests=[
                RuleTestFixture(name="Should fail", input="const a = 1;\ndebugger;", expected_violation=True),
                RuleTestFixture(name="Should pass", input="const a = 1;\nconsole.log(a);", expected_violation=False)
            ]
        )
        passed, results = RuleTestEngine.run_all_rule_fixtures(rule_with_test_cases)
        self.assertTrue(passed)
        self.assertEqual(len(results), 2)
        self.assertTrue(all(r.passed for r in results))

        exec_res = RuleTestEngine.execute_fixtures(rule_with_test_cases)
        self.assertTrue(exec_res["passed"])
        self.assertEqual(exec_res["total_fixtures"], 2)


class TestTokenFilterComprehensive(unittest.TestCase):
    def test_strip_comments_all_languages(self):
        # Python comments
        self.assertEqual(TokenFilter.strip_comments("x = 10 # comment", ".py"), "x = 10")
        
        # C# / Java / JS comments
        self.assertEqual(TokenFilter.strip_comments("int x = 10; // comment", ".cs"), "int x = 10;")
        self.assertEqual(TokenFilter.strip_comments("const x = 10; // comment", ".ts"), "const x = 10;")

        # SQL comments
        self.assertEqual(TokenFilter.strip_comments("SELECT * FROM users; -- comment", ".sql"), "SELECT * FROM users;")

    def test_parse_inline_pragmas(self):
        lines = [
            "// @guardian-ignore CULT01: Mandatory justification reason here",
            "// TODO: later",
            "// @guardian-ignore-start ARCH-01: Valid justification block reason",
            "var http = HttpContext.Current;",
            "// @guardian-ignore-end"
        ]
        suppressed, warnings = TokenFilter.parse_inline_pragmas(lines)
        self.assertIn(2, suppressed)
        self.assertIn(4, suppressed)
        self.assertIn("CULT01", suppressed[2])
        self.assertIn("ARCH-01", suppressed[4])

    def test_is_file_or_rule_exempt(self):
        pat_all = IgnoredFilePattern("legacy/**", ["ALL"], "Legacy code")
        pat_single = IgnoredFilePattern("scripts/guardian_mock.py", ["CULT01"], "Mock file")
        
        self.assertTrue(pat_all.matches("legacy/old_code.py", "CULT01"))
        self.assertTrue(pat_single.matches("scripts/guardian_mock.py", "CULT01"))
        self.assertFalse(pat_single.matches("scripts/guardian_mock.py", "CULT02"))
        self.assertFalse(pat_all.matches("src/main.py", "CULT01"))


class TestRuleRegistryComprehensive(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.registry = RuleRegistry.get_instance()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_registry_filters_and_queries(self):
        # Search
        results = self.registry.search("Traceability")
        self.assertIsInstance(results, list)

        # List by categories, severities, tiers
        p0_rules = self.registry.list(severity=RuleSeverity.P0)
        self.assertTrue(all(r.severity == RuleSeverity.P0 for r in p0_rules))

        active_rules = self.registry.list(active_only=True)
        self.assertTrue(all(r.status == RuleStatus.ACTIVE for r in active_rules))

        builtin_rules = self.registry.list(tier=RuleTier.BUILTIN)
        self.assertTrue(all(r.tier == RuleTier.BUILTIN for r in builtin_rules))


if __name__ == "__main__":
    unittest.main()
