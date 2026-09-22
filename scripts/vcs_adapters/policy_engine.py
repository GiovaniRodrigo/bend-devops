"""
==============================================================================
Configurable Branch Gating Policy Engine
==============================================================================
@spec RF06 - Configurable Gate Policies
==============================================================================
"""

import fnmatch
from typing import Dict, Any, Optional, Tuple

DEFAULT_POLICIES: Dict[str, Dict[str, Any]] = {
    "main": {
        "min_score": 90,
        "max_p0": 0,
        "max_p1": 5,
        "description": "Production branch policy: strict compliance"
    },
    "master": {
        "min_score": 90,
        "max_p0": 0,
        "max_p1": 5,
        "description": "Production master branch policy"
    },
    "release/*": {
        "min_score": 90,
        "max_p0": 0,
        "max_p1": 5,
        "description": "Release candidate policy"
    },
    "develop": {
        "min_score": 85,
        "max_p0": 0,
        "max_p1": 10,
        "description": "Integration develop branch policy"
    },
    "*": {
        "min_score": 80,
        "max_p0": 0,
        "max_p1": 20,
        "description": "Default feature branch policy"
    }
}


class BranchPolicyEngine:
    """Evaluates quality gate criteria against branch-specific policies."""

    def __init__(self, custom_policies: Optional[Dict[str, Dict[str, Any]]] = None):
        self.policies = dict(DEFAULT_POLICIES)
        if custom_policies:
            self.policies.update(custom_policies)

    def resolve_policy_for_branch(self, branch_name: str) -> Dict[str, Any]:
        """Finds matching policy config by branch name or glob pattern."""
        clean_name = branch_name.strip()
        if clean_name.startswith("refs/heads/"):
            clean_name = clean_name[len("refs/heads/"):]
        if clean_name.startswith("origin/"):
            clean_name = clean_name[len("origin/"):]
        
        # 1. Exact match
        if clean_name in self.policies:
            return self.policies[clean_name]

        # 2. Glob match
        for pat, policy in self.policies.items():
            if pat != "*" and fnmatch.fnmatch(clean_name, pat):
                return policy

        # 3. Wildcard fallback
        return self.policies.get("*", DEFAULT_POLICIES["*"])

    def evaluate_gate(
        self,
        branch_name: str,
        score: int,
        p0_count: int,
        p1_count: int = 0
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Evaluates whether a commit/PR passes the branch gate.
        Returns:
            (is_approved, verdict_reason, policy_applied)
        """
        policy = self.resolve_policy_for_branch(branch_name)
        min_score = policy.get("min_score", 80)
        max_p0 = policy.get("max_p0", 0)
        max_p1 = policy.get("max_p1", 20)

        if p0_count > max_p0:
            reason = f"Gate Failed: Found {p0_count} blocking P0 violations (maximum allowed: {max_p0}) on branch '{branch_name}'."
            return False, reason, policy

        if score < min_score:
            reason = f"Gate Failed: Score {score}/100 is below minimum threshold of {min_score} for branch '{branch_name}'."
            return False, reason, policy

        if p1_count > max_p1:
            reason = f"Gate Failed: Found {p1_count} warnings (maximum allowed: {max_p1}) on branch '{branch_name}'."
            return False, reason, policy

        reason = f"Gate Passed: Score {score}/100 meets requirement ({min_score}+) with {p0_count} P0 issues on branch '{branch_name}'."
        return True, reason, policy
