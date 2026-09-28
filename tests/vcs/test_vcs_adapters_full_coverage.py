"""
Full branch and line coverage test suite for scripts/vcs_adapters/
"""

import sys
import os
import json
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.vcs_adapters import (
    get_vcs_adapter,
    detect_vcs_environment,
    BaseVcsAdapter,
    GitHubAdapter,
    GitLabAdapter,
    BitbucketAdapter,
    BranchPolicyEngine,
    WebhookGateway,
    VcsPullRequestEvent,
    parse_unified_diff,
    parse_unified_diff_structured,
    extract_changed_lines,
    ParsedDiffFile
)


class TestVcsAdaptersFullCoverage(unittest.TestCase):
    def test_detect_vcs_environment(self):
        with patch.dict("os.environ", {"GITHUB_ACTIONS": "true"}, clear=True):
            self.assertEqual(detect_vcs_environment(), "github")

        with patch.dict("os.environ", {"GITLAB_CI": "true"}, clear=True):
            self.assertEqual(detect_vcs_environment(), "gitlab")

        with patch.dict("os.environ", {"BITBUCKET_BUILD_NUMBER": "123"}, clear=True):
            self.assertEqual(detect_vcs_environment(), "bitbucket")

        with patch.dict("os.environ", {}, clear=True):
            self.assertIsNone(detect_vcs_environment())

    def test_get_vcs_adapter_fallbacks(self):
        with patch.dict("os.environ", {}, clear=True):
            self.assertIsNone(get_vcs_adapter("unknown_provider"))

    def test_diff_parser_comprehensive_modes(self):
        # 1. Added file
        diff_added = (
            "diff --git a/new_file.py b/new_file.py\n"
            "new file mode 100644\n"
            "--- /dev/null\n"
            "+++ b/new_file.py\n"
            "@@ -0,0 +1,3 @@\n"
            "+def added():\n"
            "+    pass\n"
            "+# end\n"
        )
        files_add = parse_unified_diff_structured(diff_added)
        self.assertEqual(len(files_add), 1)
        self.assertEqual(files_add[0].status, "added")
        self.assertEqual(files_add[0].additions_count, 3)

        # 2. Deleted file
        diff_del = (
            "diff --git a/old_file.py b/old_file.py\n"
            "deleted file mode 100644\n"
            "--- a/old_file.py\n"
            "+++ /dev/null\n"
            "@@ -1,2 +0,0 @@\n"
            "-def old():\n"
            "-    pass\n"
        )
        files_del = parse_unified_diff_structured(diff_del)
        self.assertEqual(len(files_del), 1)
        self.assertEqual(files_del[0].status, "deleted")
        self.assertEqual(files_del[0].deletions_count, 2)

        # 3. Renamed file
        diff_rename = (
            "diff --git a/old_name.py b/new_name.py\n"
            "similarity index 98%\n"
            "rename from old_name.py\n"
            "rename to new_name.py\n"
            "--- a/old_name.py\n"
            "+++ b/new_name.py\n"
            "@@ -1,3 +1,4 @@\n"
            " def func():\n"
            "+    # new comment\n"
            "     pass\n"
        )
        files_ren = parse_unified_diff_structured(diff_rename)
        self.assertEqual(len(files_ren), 1)
        self.assertEqual(files_ren[0].status, "renamed")
        self.assertEqual(files_ren[0].old_path, "old_name.py")
        self.assertEqual(files_ren[0].new_path, "new_name.py")

        # Empty diff
        self.assertEqual(parse_unified_diff(""), {})
        self.assertEqual(parse_unified_diff_structured(""), [])

    def test_branch_policy_engine_all_branches(self):
        engine = BranchPolicyEngine()
        
        # master
        ok, _, _ = engine.evaluate_gate("master", 95, 0, 0)
        self.assertTrue(ok)
        
        # release branch
        ok_rel, _, _ = engine.evaluate_gate("release/1.0.0", 92, 0, 1)
        self.assertTrue(ok_rel)

        # develop branch
        ok_dev, _, _ = engine.evaluate_gate("develop", 86, 0, 2)
        self.assertTrue(ok_dev)

        # develop fail on score
        fail_dev, _, _ = engine.evaluate_gate("develop", 80, 0, 2)
        self.assertFalse(fail_dev)

        # refs/heads/ and origin/ prefix stripping
        p1 = engine.resolve_policy_for_branch("refs/heads/main")
        self.assertEqual(p1["min_score"], 90)
        p2 = engine.resolve_policy_for_branch("origin/release/2.0")
        self.assertEqual(p2["min_score"], 90)

        # P1 warnings excess failure
        fail_p1, reason_p1, _ = engine.evaluate_gate("main", 95, 0, 10)
        self.assertFalse(fail_p1)
        self.assertIn("warnings", reason_p1)

    def test_webhook_gateway_fallbacks(self):
        gw = WebhookGateway()
        # Unsupported payload
        self.assertIsNone(gw.handle_webhook({"random": "data"}))
        self.assertIsNone(gw.handle_webhook({}, platform_hint="unsupported"))

        # Incomplete GitHub
        self.assertIsNone(gw.parse_github_event({}))
        # Incomplete GitLab
        self.assertIsNone(gw.parse_gitlab_event({}))
        # Incomplete Bitbucket
        self.assertIsNone(gw.parse_bitbucket_event({}))


if __name__ == "__main__":
    unittest.main()
