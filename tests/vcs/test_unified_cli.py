"""
==============================================================================
TDD Integration Tests: Unified VCS Factory & CLI Auto-Detection
==============================================================================
@spec RF05, RF06 - Unified Dispatcher
==============================================================================
"""

import os
import unittest
from unittest.mock import patch
from scripts.vcs_adapters import detect_vcs_environment, get_vcs_adapter, GitHubAdapter, GitLabAdapter, BitbucketAdapter

class TestUnifiedVcsDispatcher(unittest.TestCase):
    def test_detect_vcs_environment_github(self):
        with patch.dict(os.environ, {"GITHUB_ACTIONS": "true"}):
            self.assertEqual(detect_vcs_environment(), "github")

    def test_detect_vcs_environment_gitlab(self):
        with patch.dict(os.environ, {"GITLAB_CI": "true", "GITHUB_ACTIONS": ""}):
            self.assertEqual(detect_vcs_environment(), "gitlab")

    def test_detect_vcs_environment_bitbucket(self):
        with patch.dict(os.environ, {"BITBUCKET_BUILD_NUMBER": "42", "GITHUB_ACTIONS": "", "GITLAB_CI": ""}):
            self.assertEqual(detect_vcs_environment(), "bitbucket")

    def test_get_vcs_adapter_creates_correct_instance(self):
        gh = get_vcs_adapter("github", token="t", repo="r", pr_number=1, commit_sha="s")
        self.assertIsInstance(gh, GitHubAdapter)

        gl = get_vcs_adapter("gitlab", token="t", repo="r", pr_number=1, commit_sha="s")
        self.assertIsInstance(gl, GitLabAdapter)

        bb = get_vcs_adapter("bitbucket", token="t", repo="r", pr_number=1, commit_sha="s")
        self.assertIsInstance(bb, BitbucketAdapter)

if __name__ == "__main__":
    unittest.main()
