"""
Comprehensive unit tests for scripts/vcs_adapters/ (Base, GitHub, GitLab, Bitbucket, DiffParser, PolicyEngine, WebhookGateway).
"""

import sys
import json
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
from io import BytesIO

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.vcs_adapters.base_adapter import BaseVcsAdapter
from scripts.vcs_adapters.github_adapter import GitHubAdapter
from scripts.vcs_adapters.gitlab_adapter import GitLabAdapter
from scripts.vcs_adapters.bitbucket_adapter import BitbucketAdapter
from scripts.vcs_adapters.diff_parser import (
    parse_unified_diff,
    parse_unified_diff_structured,
    ParsedDiffFile,
    extract_changed_lines
)
from scripts.vcs_adapters.policy_engine import BranchPolicyEngine
from scripts.vcs_adapters.webhook_gateway import WebhookGateway, VcsPullRequestEvent
from scripts.vcs_adapters import get_vcs_adapter


class ConcreteVcsAdapter(BaseVcsAdapter):
    def get_changed_files(self):
        return ["file1.py"]

    def publish_commit_status(self, state, description, score):
        return True

    def post_pr_comment(self, markdown_body):
        return True

    def publish_annotations(self, violations):
        return True

    def generate_report_artifact(self, violations, score, approved):
        return "{}"


class TestBaseVcsAdapter(unittest.TestCase):
    def test_base_adapter_contract(self):
        adapter = ConcreteVcsAdapter("token123", "owner/repo", pr_number=10, commit_sha="abc1234")
        self.assertEqual(adapter.token, "token123")
        self.assertEqual(adapter.repo, "owner/repo")
        self.assertEqual(adapter.pr_number, 10)
        self.assertEqual(adapter.commit_sha, "abc1234")

        # Test markdown summary with zero violations
        summary_empty = adapter.build_markdown_summary([], score=100, approved=True)
        self.assertIn("Zero architectural infractions", summary_empty)
        self.assertIn("PASSED", summary_empty)

        # Test markdown summary with violations including secret redaction
        violations = [
            {"rule_id": "CULT01", "severity": "P0_BLOCKING", "path": "app.py", "line": 5, "message": "TODO found"},
            {"rule_id": "CULT04", "severity": "P0_BLOCKING", "path": "config.py", "line": 10, "message": "secret_key=xyz"}
        ]
        summary_viols = adapter.build_markdown_summary(violations, score=60, approved=False)
        self.assertIn("BLOCKED", summary_viols)
        self.assertIn("[***REDACTED***]", summary_viols)

        # Test _get_git_diff_files
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="file1.py\nfile2.py\n")
            files = adapter._get_git_diff_files()
            self.assertEqual(files, ["file1.py", "file2.py"])

            mock_run.side_effect = Exception("git error")
            files_err = adapter._get_git_diff_files()
            self.assertEqual(files_err, [])


class TestGitHubAdapterComprehensive(unittest.TestCase):
    def setUp(self):
        self.adapter = GitHubAdapter("gh_token", "octocat/hello-world", pr_number=42, commit_sha="6dcb09b5")

    @patch("urllib.request.urlopen")
    def test_get_changed_files_success(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.getcode.return_value = 200
        mock_resp.read.return_value = json.dumps([{"filename": "src/main.py"}, {"filename": "README.md"}]).encode("utf-8")
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        files = self.adapter.get_changed_files()
        self.assertEqual(files, ["src/main.py", "README.md"])

    @patch("urllib.request.urlopen")
    def test_get_changed_files_error_fallback(self, mock_urlopen):
        mock_urlopen.side_effect = Exception("network error")
        with patch.object(self.adapter, "_get_git_diff_files", return_value=["local.py"]):
            files = self.adapter.get_changed_files()
            self.assertEqual(files, ["local.py"])

    def test_get_changed_files_no_pr(self):
        adapter = GitHubAdapter("gh_token", "octocat/hello-world", pr_number=None)
        with patch.object(adapter, "_get_git_diff_files", return_value=["diff.py"]):
            files = adapter.get_changed_files()
            self.assertEqual(files, ["diff.py"])

    @patch("urllib.request.urlopen")
    def test_publish_commit_status(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.getcode.return_value = 201
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        res = self.adapter.publish_commit_status("success", "Passed quality gate", 100)
        self.assertTrue(res)

        mock_urlopen.side_effect = Exception("fail")
        res_fail = self.adapter.publish_commit_status("failure", "Violations detected", 50)
        self.assertFalse(res_fail)

    def test_publish_commit_status_missing_sha(self):
        adapter = GitHubAdapter("gh_token", "octocat/hello-world", commit_sha=None)
        self.assertFalse(adapter.publish_commit_status("success", "desc", 100))

    @patch("urllib.request.urlopen")
    def test_post_pr_comment(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.getcode.return_value = 201
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        res = self.adapter.post_pr_comment("## Report summary")
        self.assertTrue(res)

        mock_urlopen.side_effect = Exception("network")
        res_fail = self.adapter.post_pr_comment("comment")
        self.assertFalse(res_fail)

    def test_post_pr_comment_no_pr(self):
        adapter = GitHubAdapter("gh_token", "octocat/hello-world", pr_number=None)
        self.assertFalse(adapter.post_pr_comment("comment"))

    @patch("urllib.request.urlopen")
    def test_publish_annotations(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.getcode.return_value = 201
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        violations = [
            {"rule_id": "CULT01", "severity": "P0_BLOCKING", "path": "main.py", "line": 10, "message": "TODO"},
            {"rule_id": "ARCH-01", "severity": "P1_WARNING", "fileName": "util.py", "line": 15, "message": "Arch"}
        ]
        res = self.adapter.publish_annotations(violations)
        self.assertTrue(res)

        mock_urlopen.side_effect = Exception("err")
        res_fail = self.adapter.publish_annotations(violations)
        self.assertFalse(res_fail)

    def test_publish_annotations_missing_sha(self):
        adapter = GitHubAdapter("gh_token", "octocat/hello-world", commit_sha=None)
        self.assertFalse(adapter.publish_annotations([]))

    def test_generate_report_artifact(self):
        violations = [
            {"rule_id": "CULT01", "severity": "P0_BLOCKING", "path": "main.py", "line": 10, "message": "TODO"}
        ]
        sarif_str = self.adapter.generate_report_artifact(violations, score=65, approved=False)
        sarif = json.loads(sarif_str)
        self.assertEqual(sarif["version"], "2.1.0")
        self.assertEqual(len(sarif["runs"][0]["results"]), 1)


class TestGitLabAdapterComprehensive(unittest.TestCase):
    def setUp(self):
        self.adapter = GitLabAdapter("gl_token", "12345", pr_number=7, commit_sha="abcdef12")

    @patch("urllib.request.urlopen")
    def test_get_changed_files(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.getcode.return_value = 200
        mock_resp.read.return_value = json.dumps({"changes": [{"new_path": "lib/service.py"}]}).encode("utf-8")
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        files = self.adapter.get_changed_files()
        self.assertEqual(files, ["lib/service.py"])

    def test_get_changed_files_no_mr(self):
        adapter = GitLabAdapter("gl_token", "12345", pr_number=None)
        with patch.object(adapter, "_get_git_diff_files", return_value=["diff.py"]):
            files = adapter.get_changed_files()
            self.assertEqual(files, ["diff.py"])

    @patch("urllib.request.urlopen")
    def test_publish_commit_status(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.getcode.return_value = 201
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        res = self.adapter.publish_commit_status("success", "Passed", 100)
        self.assertTrue(res)

        mock_urlopen.side_effect = Exception("err")
        res_fail = self.adapter.publish_commit_status("failure", "Failed", 50)
        self.assertFalse(res_fail)

    def test_publish_commit_status_no_sha(self):
        adapter = GitLabAdapter("gl_token", "12345", commit_sha=None)
        self.assertFalse(adapter.publish_commit_status("success", "Passed", 100))

    @patch("urllib.request.urlopen")
    def test_post_pr_comment(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.getcode.return_value = 201
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        res = self.adapter.post_pr_comment("Summary comment")
        self.assertTrue(res)

        mock_urlopen.side_effect = Exception("err")
        self.assertFalse(self.adapter.post_pr_comment("Summary"))

    def test_post_pr_comment_no_mr(self):
        adapter = GitLabAdapter("gl_token", "12345", pr_number=None)
        self.assertFalse(self.adapter.post_pr_comment("Summary"))

    @patch("urllib.request.urlopen")
    def test_publish_annotations(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.getcode.return_value = 201
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        violations = [
            {"rule_id": "CULT01", "severity": "P0_BLOCKING", "path": "main.py", "line": 10, "message": "TODO"}
        ]
        self.assertTrue(self.adapter.publish_annotations(violations))
        self.assertFalse(self.adapter.publish_annotations([]))

    def test_generate_report_artifact(self):
        violations = [
            {"rule_id": "CULT01", "severity": "P0_BLOCKING", "path": "main.py", "line": 10, "message": "TODO"}
        ]
        cq_str = self.adapter.generate_report_artifact(violations, score=65, approved=False)
        cq = json.loads(cq_str)
        self.assertEqual(len(cq), 1)
        self.assertIn("CULT01", cq[0]["description"])


class TestBitbucketAdapterComprehensive(unittest.TestCase):
    def setUp(self):
        self.adapter = BitbucketAdapter("bb_token", "workspace/repo-slug", pr_number=15, commit_sha="bb123456")

    @patch("urllib.request.urlopen")
    def test_get_changed_files(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.getcode.return_value = 200
        mock_resp.read.return_value = json.dumps({"values": [{"new": {"path": "src/App.cs"}}]}).encode("utf-8")
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        files = self.adapter.get_changed_files()
        self.assertEqual(files, ["src/App.cs"])

    def test_get_changed_files_no_pr(self):
        adapter = BitbucketAdapter("bb_token", "workspace/repo", pr_number=None)
        with patch.object(adapter, "_get_git_diff_files", return_value=["diff.py"]):
            files = adapter.get_changed_files()
            self.assertEqual(files, ["diff.py"])

    @patch("urllib.request.urlopen")
    def test_publish_commit_status(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.getcode.return_value = 200
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        res = self.adapter.publish_commit_status("success", "Passed", 100)
        self.assertTrue(res)

        mock_urlopen.side_effect = Exception("err")
        self.assertFalse(self.adapter.publish_commit_status("failure", "Failed", 50))

    def test_publish_commit_status_no_sha(self):
        adapter = BitbucketAdapter("bb_token", "workspace/repo", commit_sha=None)
        self.assertFalse(adapter.publish_commit_status("success", "Passed", 100))

    @patch("urllib.request.urlopen")
    def test_post_pr_comment(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.getcode.return_value = 201
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        res = self.adapter.post_pr_comment("Bitbucket comment")
        self.assertTrue(res)

        mock_urlopen.side_effect = Exception("err")
        self.assertFalse(self.adapter.post_pr_comment("Bitbucket comment"))

    def test_post_pr_comment_no_pr(self):
        adapter = BitbucketAdapter("bb_token", "workspace/repo", pr_number=None)
        self.assertFalse(adapter.post_pr_comment("Bitbucket comment"))

    @patch("urllib.request.urlopen")
    def test_publish_annotations(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.getcode.return_value = 200
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        violations = [
            {"rule_id": "CULT01", "severity": "P0_BLOCKING", "path": "main.py", "line": 10, "message": "TODO"}
        ]
        self.assertTrue(self.adapter.publish_annotations(violations))
        self.assertFalse(self.adapter.publish_annotations([]))

    def test_publish_annotations_no_sha(self):
        adapter = BitbucketAdapter("bb_token", "workspace/repo", commit_sha=None)
        self.assertFalse(adapter.publish_annotations([]))

    def test_generate_report_artifact(self):
        violations = [
            {"rule_id": "CULT01", "severity": "P0_BLOCKING", "path": "main.py", "line": 10, "message": "TODO"}
        ]
        rep_str = self.adapter.generate_report_artifact(violations, score=65, approved=False)
        rep = json.loads(rep_str)
        self.assertEqual(rep["title"], "Bend DevOps Guardian")
        self.assertEqual(rep["result"], "FAILED")


class TestDiffParserAndPolicyEngine(unittest.TestCase):
    def test_diff_parser_unified_diff(self):
        raw_diff = (
            "diff --git a/src/app.py b/src/app.py\n"
            "index 1234..5678 100644\n"
            "--- a/src/app.py\n"
            "+++ b/src/app.py\n"
            "@@ -1,4 +1,5 @@\n"
            " def hello():\n"
            "-    return 'old'\n"
            "+    # TODO: fix\n"
            "+    return 'new'\n"
        )
        files = parse_unified_diff_structured(raw_diff)
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0].new_path, "src/app.py")
        self.assertEqual(files[0].additions_count, 2)
        self.assertEqual(files[0].deletions_count, 1)

        dict_lines = parse_unified_diff(raw_diff)
        self.assertIn("src/app.py", dict_lines)
        self.assertEqual(extract_changed_lines(raw_diff, "src/app.py"), {2, 3})

    def test_branch_policy_engine(self):
        engine = BranchPolicyEngine()
        # main branch requires 90 score and 0 P0
        ok_main, reason_main, _ = engine.evaluate_gate("main", score=95, p0_count=0, p1_count=0)
        self.assertTrue(ok_main)

        fail_main, reason_fail, _ = engine.evaluate_gate("main", score=85, p0_count=0, p1_count=0)
        self.assertFalse(fail_main)

        # feature branch allows lower threshold (min_score: 80)
        ok_feat, _, _ = engine.evaluate_gate("feature/new-login", score=85, p0_count=0, p1_count=1)
        self.assertTrue(ok_feat)


class TestWebhookGatewayAndFactory(unittest.TestCase):
    def test_webhook_gateway(self):
        gw = WebhookGateway()
        
        # GitHub PR event
        gh_payload = {
            "action": "opened",
            "number": 42,
            "pull_request": {
                "number": 42,
                "head": {"sha": "1234567890abcdef"},
                "base": {"sha": "abcdef1234567890"},
                "user": {"login": "octocat"},
                "title": "Feature PR"
            },
            "repository": {"full_name": "owner/repo"}
        }
        event = gw.handle_webhook(gh_payload, platform_hint="github")
        self.assertIsNotNone(event)
        self.assertEqual(event.platform, "github")
        self.assertEqual(event.pr_number, 42)
        self.assertEqual(event.commit_sha, "1234567890abcdef")
        self.assertEqual(event.author, "octocat")
        self.assertEqual(event.to_dict()["platform"], "github")

        # GitLab MR event
        gl_payload = {
            "object_kind": "merge_request",
            "project": {"path_with_namespace": "group/project"},
            "object_attributes": {
                "iid": 10,
                "last_commit": {"id": "gl_sha_123"},
                "target_branch": "main",
                "title": "GitLab MR"
            },
            "user": {"username": "gl_user"}
        }
        event_gl = gw.handle_webhook(gl_payload)
        self.assertIsNotNone(event_gl)
        self.assertEqual(event_gl.platform, "gitlab")
        self.assertEqual(event_gl.commit_sha, "gl_sha_123")

        # Bitbucket PR event
        bb_payload = {
            "event_key": "pullrequest:created",
            "pullrequest": {
                "id": 5,
                "source": {"commit": {"hash": "bb_sha_456"}},
                "destination": {"branch": {"name": "main"}},
                "title": "BB PR"
            },
            "repository": {"full_name": "ws/repo"},
            "actor": {"username": "bb_user"}
        }
        event_bb = gw.handle_webhook(bb_payload)
        self.assertIsNotNone(event_bb)
        self.assertEqual(event_bb.platform, "bitbucket")
        self.assertEqual(event_bb.commit_sha, "bb_sha_456")

    def test_get_vcs_adapter_factory(self):
        with patch.dict("os.environ", {
            "GITHUB_TOKEN": "gh_token",
            "GITHUB_REPOSITORY": "owner/repo",
            "GITHUB_SHA": "abc1234"
        }):
            adapter = get_vcs_adapter("github")
            self.assertIsInstance(adapter, GitHubAdapter)

        with patch.dict("os.environ", {
            "GITLAB_TOKEN": "gl_token",
            "CI_PROJECT_ID": "12345",
            "CI_COMMIT_SHA": "abcdef"
        }):
            adapter_gl = get_vcs_adapter("gitlab")
            self.assertIsInstance(adapter_gl, GitLabAdapter)

        with patch.dict("os.environ", {
            "BITBUCKET_TOKEN": "bb_token",
            "BITBUCKET_REPO_FULL_NAME": "ws/repo",
            "BITBUCKET_COMMIT": "112233"
        }):
            adapter_bb = get_vcs_adapter("bitbucket")
            self.assertIsInstance(adapter_bb, BitbucketAdapter)


if __name__ == "__main__":
    unittest.main()
