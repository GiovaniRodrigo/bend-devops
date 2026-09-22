"""
==============================================================================
TDD Unit Tests: GitHub Actions Adapter & SARIF Exporter
==============================================================================
@spec RF01 - GitHub Integration
==============================================================================
"""

import json
import unittest
from unittest.mock import patch, MagicMock
from scripts.vcs_adapters.github_adapter import GitHubAdapter

class TestGitHubAdapter(unittest.TestCase):
    def setUp(self):
        self.adapter = GitHubAdapter(
            token="ghp_mock_token_1234567890abcdef",
            repo="org/repo",
            pr_number=42,
            commit_sha="a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2"
        )

    def test_generate_sarif_report_produces_valid_v2_json(self):
        violations = [
            {
                "rule_id": "ARCH-LAYER-01",
                "severity": "P0_BLOCKING",
                "penalty": 40,
                "path": "src/Domain/Order.cs",
                "line": 12,
                "message": "Forbidden presentation markup inside Domain class"
            }
        ]
        sarif_str = self.adapter.generate_report_artifact(violations, score=60, approved=False)
        sarif_data = json.loads(sarif_str)
        
        self.assertEqual(sarif_data["version"], "2.1.0")
        self.assertEqual(len(sarif_data["runs"]), 1)
        self.assertEqual(sarif_data["runs"][0]["tool"]["driver"]["name"], "Bend DevOps Guardian")
        self.assertEqual(len(sarif_data["runs"][0]["results"]), 1)
        self.assertEqual(sarif_data["runs"][0]["results"][0]["ruleId"], "ARCH-LAYER-01")

    def test_build_markdown_summary_redacts_secrets_rn02(self):
        violations = [
            {
                "rule_id": "CULT04",
                "severity": "P0_BLOCKING",
                "penalty": 40,
                "path": "src/config.py",
                "line": 5,
                "message": "Hardcoded secret: secret_api_key_sample_12345"
            }
        ]
        summary = self.adapter.build_markdown_summary(violations, score=60, approved=False)
        self.assertNotIn("secret_api_key_sample_12345", summary)
        self.assertIn("[***REDACTED***]", summary)

    @patch("urllib.request.urlopen")
    def test_publish_commit_status_makes_http_post(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.getcode.return_value = 201
        mock_urlopen.return_value.__enter__.return_value = mock_response

        success = self.adapter.publish_commit_status("success", "Score: 100/100 · 0 Infractions", 100)
        self.assertTrue(success)

    @patch("urllib.request.urlopen")
    def test_publish_annotations_creates_check_run(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.getcode.return_value = 201
        mock_urlopen.return_value.__enter__.return_value = mock_response

        violations = [{
            "path": "src/Domain/Order.cs",
            "line": 12,
            "rule_id": "ARCH-LAYER-01",
            "severity": "P0_BLOCKING",
            "message": "Forbidden HTML in model"
        }]
        success = self.adapter.publish_annotations(violations)
        self.assertTrue(success)

    @patch("urllib.request.urlopen")
    def test_get_changed_files_from_github_api(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.getcode.return_value = 200
        mock_response.read.return_value = json.dumps([
            {"filename": "src/Domain/Order.cs"},
            {"filename": "src/Views/Order.cshtml"}
        ]).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_response

        files = self.adapter.get_changed_files()
        self.assertEqual(len(files), 2)
        self.assertIn("src/Domain/Order.cs", files)

if __name__ == "__main__":
    unittest.main()
