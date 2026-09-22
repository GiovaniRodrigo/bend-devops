"""
==============================================================================
TDD Unit Tests: GitLab CI/CD Adapter & Code Quality Report Exporter
==============================================================================
@spec RF02 - GitLab Integration
==============================================================================
"""

import json
import unittest
from unittest.mock import patch, MagicMock
from scripts.vcs_adapters.gitlab_adapter import GitLabAdapter

class TestGitLabAdapter(unittest.TestCase):
    def setUp(self):
        self.adapter = GitLabAdapter(
            token="glpat-mock-token-987654321",
            repo="123456",  # GitLab project ID or URL-encoded path
            pr_number=14,   # Merge Request IID
            commit_sha="b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3"
        )

    def test_generate_code_quality_report_produces_valid_gl_format(self):
        violations = [
            {
                "rule_id": "ARCH-LAYER-02",
                "severity": "P0_BLOCKING",
                "penalty": 35,
                "path": "src/Views/ProductList.cshtml",
                "line": 6,
                "message": "Forbidden direct database or ORM query execution inside presentation template/view"
            }
        ]
        gl_report_str = self.adapter.generate_report_artifact(violations, score=65, approved=False)
        gl_report = json.loads(gl_report_str)

        self.assertIsInstance(gl_report, list)
        self.assertEqual(len(gl_report), 1)
        self.assertEqual(gl_report[0]["severity"], "blocker")
        self.assertEqual(gl_report[0]["location"]["path"], "src/Views/ProductList.cshtml")
        self.assertEqual(gl_report[0]["location"]["lines"]["begin"], 6)

    @patch("urllib.request.urlopen")
    def test_post_mr_note_makes_http_post(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.getcode.return_value = 201
        mock_urlopen.return_value.__enter__.return_value = mock_response

        success = self.adapter.post_pr_comment("## Merge Request Quality Summary")
        self.assertTrue(success)

if __name__ == "__main__":
    unittest.main()
