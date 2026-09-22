"""
==============================================================================
TDD Unit Tests: Bitbucket Pipelines Adapter & Code Insights Exporter
==============================================================================
@spec RF03 - Bitbucket Integration
==============================================================================
"""

import json
import unittest
from unittest.mock import patch, MagicMock
from scripts.vcs_adapters.bitbucket_adapter import BitbucketAdapter

class TestBitbucketAdapter(unittest.TestCase):
    def setUp(self):
        self.adapter = BitbucketAdapter(
            token="bb_mock_token_abcdef123456",
            repo="workspace/repo_slug",
            pr_number=8,
            commit_sha="c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4"
        )

    def test_generate_code_insights_report_payload_structure(self):
        violations = [
            {
                "rule_id": "ARCH-LAYER-03",
                "severity": "P0_BLOCKING",
                "penalty": 30,
                "path": "src/Domain/Account.py",
                "line": 8,
                "message": "Forbidden HTTP transport protocol coupling inside Domain Entity"
            }
        ]
        report_str = self.adapter.generate_report_artifact(violations, score=70, approved=False)
        report = json.loads(report_str)

        self.assertEqual(report["title"], "AI Culture & Architecture Guardian")
        self.assertEqual(report["result"], "FAILED")
        self.assertEqual(report["report_type"], "SECURITY")
        self.assertEqual(len(report["data"]), 2)

    @patch("urllib.request.urlopen")
    def test_publish_commit_status_makes_http_post(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.getcode.return_value = 200
        mock_urlopen.return_value.__enter__.return_value = mock_response

        success = self.adapter.publish_commit_status("SUCCESSFUL", "Score: 90/100 · Gate Passed", 90)
        self.assertTrue(success)

if __name__ == "__main__":
    unittest.main()
