"""
Unit Tests for Rule Test Engine and ReDoS Safety Validator
Spec: specs/006-extensible-rule-management/
"""

import unittest
from scripts.rule_model import (
    RuleDefinition,
    RuleType,
    RuleSeverity,
    RuleStatus,
    RuleTier,
    RuleScope,
    RuleCondition,
    RuleSuppressionConfig
)
from scripts.rule_test_engine import RuleTestEngine, RegexSafetyValidator


class TestRuleTestEngineStandalone(unittest.TestCase):
    def setUp(self):
        self.rule = RuleDefinition(
            id="SEC-009",
            version="1.0.0",
            name="No Hardcoded Passwords",
            description="Flags hardcoded password assignments",
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
                pattern=r"password\s*=\s*['\"][A-Za-z0-9_\-\.]{8,}['\"]"
            ),
            message="Hardcoded password detected.",
            suggestion="Use secure secrets store.",
            suppression=RuleSuppressionConfig(
                allowed=True,
                pragma="@guardian-ignore",
                requires_reason=True,
                minimum_reason_length=8
            )
        )

    def test_redos_pattern_rejection(self):
        """ReDoS catastrophic backtracking pattern is rejected."""
        unsafe_pattern = r"(a+)+b"
        safe, msg = RegexSafetyValidator.is_safe_pattern(unsafe_pattern)
        self.assertFalse(safe)
        self.assertIn("ReDoS", msg)

    def test_safe_pattern_accepted(self):
        """Safe non-backtracking regex pattern is accepted."""
        safe_pattern = r"def\s+[a-z_][a-z0-9_]*\s*\("
        safe, msg = RegexSafetyValidator.is_safe_pattern(safe_pattern)
        self.assertTrue(safe)
        self.assertIsNone(msg)

    def test_rule_execution_positive_match(self):
        """RuleTestEngine flags violation on positive match."""
        snippet = 'password = "supersecretpassword123"'
        result = RuleTestEngine.run_test(self.rule, snippet, file_name="src/auth.py")
        self.assertTrue(result.has_violation)
        self.assertEqual(len(result.violations), 1)
        self.assertEqual(result.violations[0]["rule_id"], "SEC-009")

    def test_rule_execution_negative_match(self):
        """RuleTestEngine passes clean code without violations."""
        snippet = 'password = os.getenv("AUTH_PASSWORD")'
        result = RuleTestEngine.run_test(self.rule, snippet, file_name="src/auth.py")
        self.assertFalse(result.has_violation)
        self.assertEqual(len(result.violations), 0)

    def test_inline_suppression_with_valid_reason(self):
        """RuleTestEngine respects valid inline pragma suppression."""
        snippet = (
            '# @guardian-ignore SEC-009: Test mock fixture password\n'
            'password = "supersecretpassword123"\n'
        )
        result = RuleTestEngine.run_test(self.rule, snippet, file_name="src/auth.py")
        self.assertTrue(result.is_suppressed)
        self.assertTrue(result.has_violation)
        self.assertEqual(len(result.violations), 0)


if __name__ == "__main__":
    unittest.main()
