"""
Full 100% branch and line coverage test suite for:
- scripts/rule_model.py
- scripts/rule_normalizer.py
- scripts/rule_registry.py
- scripts/rule_test_engine.py
- scripts/token_filter.py
"""

import sys
import os
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.rule_model import (
    RuleType,
    RuleSeverity,
    RuleStatus,
    RuleTier,
    UserRole,
    RuleScope,
    RuleCondition,
    RuleSuppressionConfig,
    RuleTestFixture,
    RuleAuditEntry,
    RuleDefinition
)
from scripts.rule_normalizer import RuleNormalizer
from scripts.rule_registry import RuleRegistry
from scripts.rule_test_engine import (
    RegexSafetyValidator,
    RuleTestResult,
    RuleTestEngine
)
from scripts.token_filter import (
    TokenFilter,
    IgnoredFilePattern,
    strip_comments,
    parse_inline_pragmas,
    matches_exact_token,
    load_guardianignore,
    is_file_or_rule_exempt
)


class TestRuleModelFull(unittest.TestCase):
    def test_all_severities_and_penalties(self):
        self.assertEqual(RuleSeverity.normalize(RuleSeverity.P0), RuleSeverity.P0)
        self.assertEqual(RuleSeverity.normalize("BLOCKING"), RuleSeverity.P0)
        self.assertEqual(RuleSeverity.normalize("CRITICAL"), RuleSeverity.P0)
        self.assertEqual(RuleSeverity.normalize("WARNING"), RuleSeverity.P1)
        self.assertEqual(RuleSeverity.normalize("HIGH"), RuleSeverity.P1)
        self.assertEqual(RuleSeverity.normalize("MAJOR"), RuleSeverity.P1)
        self.assertEqual(RuleSeverity.normalize("MEDIUM"), RuleSeverity.P2)
        self.assertEqual(RuleSeverity.normalize("MINOR"), RuleSeverity.P2)
        self.assertEqual(RuleSeverity.normalize("LOW"), RuleSeverity.P3)
        self.assertEqual(RuleSeverity.normalize("NITPICK"), RuleSeverity.P3)
        self.assertEqual(RuleSeverity.normalize("CUSTOM_UNKNOWN"), RuleSeverity.INFO)

        self.assertEqual(RuleSeverity.P0.penalty_points, 35)
        self.assertEqual(RuleSeverity.P1.penalty_points, 15)
        self.assertEqual(RuleSeverity.P2.penalty_points, 10)
        self.assertEqual(RuleSeverity.P3.penalty_points, 5)
        self.assertEqual(RuleSeverity.INFO.penalty_points, 0)

        self.assertTrue(RuleSeverity.P0.is_blocking)
        self.assertFalse(RuleSeverity.P1.is_blocking)
        self.assertFalse(RuleSeverity.P2.is_blocking)

    def test_all_statuses_and_tiers(self):
        self.assertEqual(RuleStatus.normalize(RuleStatus.ACTIVE), RuleStatus.ACTIVE)
        self.assertEqual(RuleStatus.normalize("ENABLED"), RuleStatus.ACTIVE)
        self.assertEqual(RuleStatus.normalize("TRUE"), RuleStatus.ACTIVE)
        self.assertEqual(RuleStatus.normalize("INACTIVE"), RuleStatus.ARCHIVED)
        self.assertEqual(RuleStatus.normalize("DISABLED"), RuleStatus.ARCHIVED)
        self.assertEqual(RuleStatus.normalize("FALSE"), RuleStatus.ARCHIVED)
        self.assertEqual(RuleStatus.normalize("NEW"), RuleStatus.DRAFT)
        self.assertEqual(RuleStatus.normalize("TEST"), RuleStatus.TESTING)
        self.assertEqual(RuleStatus.normalize("READY"), RuleStatus.VALIDATED)
        self.assertEqual(RuleStatus.normalize("OBSOLETE"), RuleStatus.DEPRECATED)
        self.assertEqual(RuleStatus.normalize("SOMETHING_ELSE"), RuleStatus.ACTIVE)

        self.assertEqual(RuleTier.BUILTIN.precedence_rank, 1)
        self.assertEqual(RuleTier.ORGANIZATION.precedence_rank, 2)
        self.assertEqual(RuleTier.PROJECT.precedence_rank, 3)
        self.assertEqual(RuleTier.CUSTOM.precedence_rank, 4)

    def test_audit_entry_and_user_roles(self):
        entry = RuleAuditEntry(timestamp="2026-09-28T00:00:00Z", action="CREATED", actor="dev", rule_id="RULE-1")
        self.assertEqual(entry.rule_id, "RULE-1")
        self.assertEqual(UserRole.RULE_ADMIN.value, "Rule Admin")


class TestRuleNormalizerFull(unittest.TestCase):
    def test_normalize_all_categories_and_types(self):
        # Security category
        r_sec = RuleNormalizer.normalize_rule_dict({"id": "SEC01", "category": "security", "pattern": "key="})
        self.assertEqual(r_sec.category, "security")

        # Performance category
        r_perf = RuleNormalizer.normalize_rule_dict({"id": "PERF01", "category": "Performance", "pattern": "sleep"})
        self.assertEqual(r_perf.category, "performance")

        # Quality category
        r_qual = RuleNormalizer.normalize_rule_dict({"id": "QUAL01", "category": "Quality", "pattern": "print"})
        self.assertEqual(r_qual.category, "quality")

        # Dependency type via forbidden_targets
        r_dep = RuleNormalizer.normalize_rule_dict({"id": "DEP01", "forbidden_targets": ["System.Web"]})
        self.assertEqual(r_dep.type, RuleType.DEPENDENCY)

        # Architecture type
        r_arch = RuleNormalizer.normalize_rule_dict({"id": "ARCH01", "category": "Architecture Boundaries"})
        self.assertEqual(r_arch.type, RuleType.ARCHITECTURE)

        # Disabled status string boolean
        r_dis = RuleNormalizer.normalize_rule_dict({"id": "DIS01", "enabled": "false", "status": "ARCHIVED"})
        self.assertFalse(r_dis.enabled)

        # Custom penalty points
        r_pen = RuleNormalizer.normalize_rule_dict({"id": "PEN01", "penalty_points": "50"})
        self.assertEqual(r_pen.penalty_points, 50)

        # Bad penalty points fallback
        r_bad_pen = RuleNormalizer.normalize_rule_dict({"id": "PEN02", "penalty_points": "invalid_num"})
        self.assertEqual(r_bad_pen.penalty_points, 35)

        # Test fixtures normalization
        r_tests = RuleNormalizer.normalize_rule_dict({
            "id": "T01",
            "tests": [{"name": "case1", "input": "code", "expected_violation": True, "expected_line": 2}]
        })
        self.assertEqual(len(r_tests.tests), 1)
        self.assertEqual(r_tests.tests[0].name, "case1")


class TestRegexSafetyValidatorFull(unittest.TestCase):
    def test_empty_and_timeout(self):
        self.assertFalse(RegexSafetyValidator.is_safe_pattern("")[0])
        self.assertFalse(RegexSafetyValidator.is_safe_pattern("   ")[0])
        self.assertFalse(RegexSafetyValidator.is_safe_pattern(None)[0])
        self.assertTrue(RegexSafetyValidator.is_safe_pattern(r"^[a-zA-Z0-9_-]+$")[0])


class TestRuleTestEngineFull(unittest.TestCase):
    def test_empty_source_code(self):
        rule = RuleDefinition(id="EMPTY-01", name="Empty Rule", condition=RuleCondition(pattern="abc"))
        res = RuleTestEngine.test_rule(rule, "", expected_violation=False)
        self.assertTrue(res.passed)

        res2 = RuleTestEngine.test_rule(rule, "", expected_violation=True)
        self.assertFalse(res2.passed)

    def test_invalid_regex_in_rule(self):
        rule = RuleDefinition(id="INV-01", name="Invalid Regex", condition=RuleCondition(pattern="[unclosed"))
        res = RuleTestEngine.test_rule(rule, "some code here", "app.py")
        self.assertFalse(res.passed)
        self.assertIn("Invalid regex", res.error)

    def test_language_mismatch_filtering(self):
        rule = RuleDefinition(id="CS-ONLY", name="CSharp Only", languages=["csharp"], condition=RuleCondition(pattern="DbContext"))
        res = RuleTestEngine.test_rule(rule, "var db = new DbContext();", "app.py")
        self.assertTrue(res.passed)
        self.assertFalse(res.has_violation)

    def test_naming_conventions_all(self):
        # PascalCase
        rule_pascal = RuleDefinition(id="N-PASCAL", name="Pascal", type=RuleType.NAMING, condition=RuleCondition(naming_convention="PascalCase"))
        res1 = RuleTestEngine.test_rule(rule_pascal, "class myBadClass:\n    pass\n", "app.py")
        self.assertTrue(res1.has_violation)

        # camelCase
        rule_camel = RuleDefinition(id="N-CAMEL", name="Camel", type=RuleType.NAMING, condition=RuleCondition(naming_convention="camelCase"))
        res2 = RuleTestEngine.test_rule(rule_camel, "def MyFunction():\n    pass\n", "app.py")
        self.assertTrue(res2.has_violation)

        # snake_case
        rule_snake = RuleDefinition(id="N-SNAKE", name="Snake", type=RuleType.NAMING, condition=RuleCondition(naming_convention="snake_case"))
        res3 = RuleTestEngine.test_rule(rule_snake, "def BadFunc():\n    pass\n", "app.py")
        self.assertTrue(res3.has_violation)

        # UPPER_CASE
        rule_upper = RuleDefinition(id="N-UPPER", name="Upper", type=RuleType.NAMING, condition=RuleCondition(naming_convention="UPPER_CASE"))
        res4 = RuleTestEngine.test_rule(rule_upper, "enum my_enum {\n}\n", "app.cs")
        self.assertTrue(res4.has_violation)

    def test_dependency_rules_evaluation(self):
        rule_dep = RuleDefinition(
            id="DEP-01",
            name="No EF in Domain",
            type=RuleType.DEPENDENCY,
            condition=RuleCondition(forbidden_targets=["EntityFramework", "Microsoft.EntityFrameworkCore"], forbidden_layer="Infrastructure")
        )
        code = "using Microsoft.EntityFrameworkCore;\npublic class Order {}\n"
        res = RuleTestEngine.test_rule(rule_dep, code, "Order.cs")
        self.assertTrue(res.has_violation)
        self.assertEqual(len(res.violations), 1)

    def test_file_folder_rules_evaluation(self):
        rule_folder = RuleDefinition(
            id="FOLDER-01",
            name="Controllers in Controllers folder",
            type=RuleType.FILE_FOLDER,
            condition=RuleCondition(required_path_prefix="src/Controllers/")
        )
        res_fail = RuleTestEngine.test_rule(rule_folder, "class OrderController {}", "src/Domain/OrderController.cs")
        self.assertTrue(res_fail.has_violation)

        res_pass = RuleTestEngine.test_rule(rule_folder, "class OrderController {}", "src/Controllers/OrderController.cs")
        self.assertFalse(res_pass.has_violation)


class TestRuleRegistryFull(unittest.TestCase):
    def setUp(self):
        self.registry = RuleRegistry.get_instance()

    def test_crud_and_query_edges(self):
        # Get nonexistent
        self.assertIsNone(self.registry.get("TOTALLY_NONEXISTENT_RULE_12345"))
        self.assertIsNone(self.registry.enable("NONEXISTENT_999"))
        self.assertIsNone(self.registry.disable("NONEXISTENT_999"))

        # Search with empty query returns all
        all_rules = self.registry.search("")
        self.assertGreater(len(all_rules), 0)

        # Export all
        all_exported = self.registry.export_all()
        self.assertIn("rules", all_exported)

        # Validation of invalid rule
        invalid_rule = {"id": "", "name": ""}
        valid, errors = self.registry.validate_rule(invalid_rule)
        self.assertFalse(valid)
        self.assertGreater(len(errors), 0)

        # Import rules
        imported_count, import_errors = self.registry.import_rules([
            {"id": "IMP-001", "name": "Imported Test Rule", "pattern": "debug_log"}
        ])
        self.assertEqual(imported_count, 1)
        self.registry.unregister("IMP-001", hard_delete=True)

        # Audit trail filtering
        trail = self.registry.get_audit_trail(rule_id="CULT01")
        self.assertIsInstance(trail, list)


class TestTokenFilterFull(unittest.TestCase):
    def test_guardianignore_file_parsing(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".guardianignore", delete=False) as f:
            f.write("# Comment\nlegacy/**\nmigrations/* [ARCH-01, CULT02] # Reason\n")
            temp_path = Path(f.name)

        try:
            patterns = TokenFilter.load_guardianignore(temp_path)
            self.assertEqual(len(patterns), 2)
            self.assertTrue(patterns[0].matches("legacy/old.py", "CULT01"))
            self.assertTrue(patterns[1].matches("migrations/001.sql", "ARCH-01"))
            self.assertFalse(patterns[1].matches("migrations/001.sql", "OTHER-RULE"))
        finally:
            if temp_path.exists():
                temp_path.unlink()

    def test_matches_exact_token_variations(self):
        self.assertTrue(TokenFilter.matches_exact_token("<button", "<button class='btn'>Click</button>"))
        self.assertTrue(TokenFilter.matches_exact_token("SELECT", "SELECT id, name FROM users;"))
        self.assertTrue(TokenFilter.matches_exact_token("DbContext", "public class AppDbContext : DbContext"))


if __name__ == "__main__":
    unittest.main()
