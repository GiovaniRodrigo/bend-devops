"""
==============================================================================
TDD Unit Tests: Branch Policy Engine
==============================================================================
@spec RF06 - Configurable Gate Policies
==============================================================================
"""

import unittest
from scripts.vcs_adapters.policy_engine import BranchPolicyEngine

class TestBranchPolicyEngine(unittest.TestCase):
    def setUp(self):
        self.engine = BranchPolicyEngine()

    def test_main_branch_requires_strict_score_and_zero_p0(self):
        # 100 score, 0 P0 -> Pass
        ok, reason, _ = self.engine.evaluate_gate("main", score=95, p0_count=0)
        self.assertTrue(ok)
        self.assertIn("Gate Passed", reason)

        # 85 score on main (<90) -> Fail
        ok, reason, _ = self.engine.evaluate_gate("main", score=85, p0_count=0)
        self.assertFalse(ok)
        self.assertIn("below minimum threshold of 90", reason)

        # 95 score with 1 P0 -> Fail
        ok, reason, _ = self.engine.evaluate_gate("main", score=95, p0_count=1)
        self.assertFalse(ok)
        self.assertIn("blocking P0", reason)

    def test_feature_branch_permissive_policy(self):
        # 82 score on feature branch (>= 80) -> Pass
        ok, reason, _ = self.engine.evaluate_gate("feature/order-refactor", score=82, p0_count=0)
        self.assertTrue(ok)
        self.assertIn("Gate Passed", reason)

        # 75 score on feature branch (< 80) -> Fail
        ok, reason, _ = self.engine.evaluate_gate("feature/order-refactor", score=75, p0_count=0)
        self.assertFalse(ok)
        self.assertIn("below minimum threshold of 80", reason)

    def test_custom_policy_overrides(self):
        custom = {
            "hotfix/*": {
                "min_score": 95,
                "max_p0": 0,
                "max_p1": 2
            }
        }
        engine = BranchPolicyEngine(custom)
        ok, _, policy = engine.evaluate_gate("hotfix/security-patch", score=90, p0_count=0)
        self.assertFalse(ok)
        self.assertEqual(policy["min_score"], 95)

if __name__ == "__main__":
    unittest.main()
