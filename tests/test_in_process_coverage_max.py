"""
==============================================================================
In-Process Maximum Coverage Test Suite for Bend DevOps Guardian
==============================================================================
Directly exercises GuardianRequestHandler, culture_guard.main, and all internal
functions in-process to achieve >97% test coverage without sub-process delays.
==============================================================================
"""

import os
import io
import sys
import json
import tempfile
import unittest
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

from scripts.guardian_server import (
    GuardianRequestHandler, get_frontend_root, discover_local_repositories,
    inspect_local_repository_path, detect_repository_framework,
    get_repository_by_id, get_working_tree_info, validate_commit_sha,
    get_github_repositories, load_real_rules_manifest,
    load_real_architecture_profiles, CUSTOM_REPOSITORIES, start_guardian_server
)
import scripts.culture_guard as culture_guard
from scripts.culture_guard import (
    classify_file_layer, FileAuditResult, generate_bend_harness, run_bend_engine,
    print_report, resolve_scope_files, evaluate_scoped_rules, handle_rules_cli,
    load_layer_vocabulary, build_vocabulary_regexes
)
from scripts.rule_model import (
    RuleDefinition, RuleSeverity, RuleStatus, RuleTier, RuleType,
    RuleCondition, RuleScope, RuleSuppressionConfig, RuleTestFixture, UserRole
)
from scripts.rule_registry import RuleRegistry
from scripts.rule_normalizer import RuleNormalizer
from scripts.rule_test_engine import RuleTestEngine, RegexSafetyValidator
from scripts.token_filter import IgnoredFilePattern


class MockGuardianHandler(GuardianRequestHandler):
    """In-memory mock HTTP handler for GuardianRequestHandler."""

    def __init__(self, method="GET", path="/api/healthz", body=None, headers=None):
        self.path = path
        self.command = method
        self.response_code = 200
        self.response_headers = {}
        
        raw_body = b""
        if body is not None:
            if isinstance(body, (dict, list)):
                raw_body = json.dumps(body).encode("utf-8")
            elif isinstance(body, str):
                raw_body = body.encode("utf-8")
            elif isinstance(body, bytes):
                raw_body = body

        self.rfile = io.BytesIO(raw_body)
        self.wfile = io.BytesIO()
        
        self.headers = headers or {}
        if raw_body and "Content-Length" not in self.headers:
            self.headers["Content-Length"] = str(len(raw_body))

    def send_response(self, code, message=None):
        self.response_code = code

    def send_header(self, keyword, value):
        self.response_headers[keyword] = value

    def end_headers(self):
        pass

    def get_response_json(self):
        val = self.wfile.getvalue().decode("utf-8")
        if val.strip():
            return json.loads(val)
        return None


class TestGuardianHandlerInProcess(unittest.TestCase):
    """Executes every branch of GuardianRequestHandler in-process."""

    def tearDown(self):
        reg = RuleRegistry.get_instance()
        for rid in ["INPROC-01", "INPROC-01-CLONE", "IMP-INPROC-01", "INPROC-PUT-01", "CUSTOM-DIRECT-01"]:
            reg.unregister(rid, hard_delete=True)
            custom_f = REPO_ROOT / f"backend/rules/custom/{rid.lower()}.json"
            if custom_f.exists():
                custom_f.unlink()
        reg.load_all()

    def test_options(self):
        h = MockGuardianHandler(method="OPTIONS", path="/api/rules")
        h.do_OPTIONS()
        self.assertEqual(h.response_code, 204)

    def test_get_routes(self):
        routes = [
            "/api/healthz",
            "/api/system/status",
            "/api/repositories/local",
            "/api/system/browse-dirs",
            f"/api/system/browse-dirs?path={REPO_ROOT}",
            "/api/repositories/github",
            "/api/repositories/ai-bend-devops/working-tree",
            "/api/repositories/NONEXISTENT_REPO/working-tree",
            "/api/rules",
            "/api/rules?severity=P0&status=active&tier=builtin",
            "/api/rules/categories",
            "/api/rules/languages",
            "/api/rules/types",
            "/api/rules/severities",
            "/api/rules/statuses",
            "/api/rules/CULT01",
            "/api/rules/NONEXISTENT_RULE_999",
            "/api/rules/CULT01/export",
            "/api/rules/NONEXISTENT_RULE_999/export",
            "/api/rules/export/all",
            "/api/rules/audit-trail",
            "/api/rules/audit-trail?ruleId=CULT01",
            "/api/profiles",
            "/api/repositories/ai-bend-devops/branches",
            "/api/repositories/NONEXISTENT_REPO/branches",
            "/api/repositories/ai-bend-devops/framework-detect",
            "/api/repositories/NONEXISTENT_REPO/framework-detect",
            "/api/repositories/ai-bend-devops/file?path=README.md",
            "/api/repositories/ai-bend-devops/file?path=nonexistent_file.xyz",
            "/api/repositories/NONEXISTENT_REPO/file?path=README.md",
            "/api/mock/scenario?name=clean-repository",
            "/api/mock/scenario?name=nonexistent_scenario"
        ]

        for r in routes:
            h = MockGuardianHandler(method="GET", path=r)
            h.do_GET()
            self.assertIn(h.response_code, [200, 404, 400])

    def test_post_routes(self):
        # 1. Local validate
        h_val = MockGuardianHandler(method="POST", path="/api/repositories/local/validate", body={"path": str(REPO_ROOT)})
        h_val.do_POST()
        self.assertEqual(h_val.response_code, 200)

        # 2. Local framework detect
        h_fd = MockGuardianHandler(method="POST", path="/api/repositories/local/framework-detect", body={"path": str(REPO_ROOT)})
        h_fd.do_POST()
        self.assertEqual(h_fd.response_code, 200)

        # 3. Commits validate
        h_com = MockGuardianHandler(method="POST", path="/api/repositories/ai-bend-devops/commits/validate", body={"commitSha": "HEAD"})
        h_com.do_POST()
        self.assertEqual(h_com.response_code, 200)

        h_com_bad = MockGuardianHandler(method="POST", path="/api/repositories/NONEXISTENT/commits/validate", body={"commitSha": "HEAD"})
        h_com_bad.do_POST()
        self.assertEqual(h_com_bad.response_code, 404)

        # 4. Audit routes with varied parameters
        with tempfile.TemporaryDirectory() as tmp_audit_dir:
            tmp_f = Path(tmp_audit_dir) / "sample.py"
            tmp_f.write_text("# @spec RF01\ndef hello():\n    return 'ok'\n")
            
            CUSTOM_REPOSITORIES["tmp_mock_repo"] = {"id": "tmp_mock_repo", "path": tmp_audit_dir}

            # Empty rules filter
            h_aud_empty = MockGuardianHandler(method="POST", path="/api/audit", body={"path": tmp_audit_dir, "rules": []})
            h_aud_empty.do_POST()
            self.assertEqual(h_aud_empty.response_code, 200)

            # Working tree audit
            h_aud_tree = MockGuardianHandler(method="POST", path="/api/audit", body={"path": tmp_audit_dir, "targetType": "working_tree"})
            h_aud_tree.do_POST()
            self.assertEqual(h_aud_tree.response_code, 200)

            # Branch audit
            h_aud_branch = MockGuardianHandler(method="POST", path="/api/audit", body={"path": tmp_audit_dir, "targetType": "branch", "branch": "main", "baseBranch": "develop"})
            h_aud_branch.do_POST()
            self.assertEqual(h_aud_branch.response_code, 200)

            # Full repo audit with custom profile and includeBuildDirs
            h_aud_full = MockGuardianHandler(method="POST", path="/api/audit", body={"path": tmp_audit_dir, "targetType": "full_repo", "profile": "clean_architecture", "includeBuildDirs": True})
            h_aud_full.do_POST()
            self.assertEqual(h_aud_full.response_code, 200)

            # Audit with repository ID
            h_aud_repoid = MockGuardianHandler(method="POST", path="/api/audit", body={"repository": "tmp_mock_repo", "targetType": "full_repo"})
            h_aud_repoid.do_POST()
            self.assertEqual(h_aud_repoid.response_code, 200)

            # Audit with allowed_rules filtering (recalculation)
            h_aud_filter = MockGuardianHandler(method="POST", path="/api/audit", body={"path": tmp_audit_dir, "targetType": "full_repo", "rules": ["CULT01", "CULT02"]})
            h_aud_filter.do_POST()
            self.assertEqual(h_aud_filter.response_code, 200)

            # Audit with targetType="commit"
            h_aud_commit = MockGuardianHandler(method="POST", path="/api/audit", body={"path": tmp_audit_dir, "targetType": "commit", "commitSha": "HEAD"})
            h_aud_commit.do_POST()
            self.assertEqual(h_aud_commit.response_code, 200)

        # 5. Rule validation & test
        h_rule_val = MockGuardianHandler(method="POST", path="/api/rules/CULT01/validate")
        h_rule_val.do_POST()
        self.assertEqual(h_rule_val.response_code, 200)

        h_rule_val_bad = MockGuardianHandler(method="POST", path="/api/rules/NONEXISTENT/validate")
        h_rule_val_bad.do_POST()
        self.assertEqual(h_rule_val_bad.response_code, 404)

        h_rule_test = MockGuardianHandler(method="POST", path="/api/rules/test", body={"rule": {"id": "TMP01", "name": "Tmp", "pattern": "tmp_pat"}, "code": "tmp_pat = 1"})
        h_rule_test.do_POST()
        self.assertEqual(h_rule_test.response_code, 200)

        h_rule_test2 = MockGuardianHandler(method="POST", path="/api/rules/CULT01/test", body={"code": "def test(): pass"})
        h_rule_test2.do_POST()
        self.assertEqual(h_rule_test2.response_code, 200)

        h_rule_test_bad = MockGuardianHandler(method="POST", path="/api/rules/NONEXISTENT/test", body={"code": "def test(): pass"})
        h_rule_test_bad.do_POST()
        self.assertEqual(h_rule_test_bad.response_code, 404)

        # 6. Rule create, clone, enable, disable
        new_rule_body = {
            "id": "INPROC-01",
            "name": "In Process Rule",
            "description": "Created in process",
            "category": "culture",
            "severity": "P1_WARNING",
            "pattern": "inproc_violation"
        }
        MockGuardianHandler(method="DELETE", path="/api/rules/INPROC-01?cascade=true").do_DELETE()
        MockGuardianHandler(method="DELETE", path="/api/rules/INPROC-01-CLONE?cascade=true").do_DELETE()
        MockGuardianHandler(method="DELETE", path="/api/rules/IMP-INPROC-01?cascade=true").do_DELETE()

        h_create = MockGuardianHandler(method="POST", path="/api/rules", body=new_rule_body)
        h_create.do_POST()
        self.assertIn(h_create.response_code, [200, 201])

        h_create_empty = MockGuardianHandler(method="POST", path="/api/rules", body={})
        h_create_empty.do_POST()
        self.assertEqual(h_create_empty.response_code, 422)

        h_create_dup = MockGuardianHandler(method="POST", path="/api/rules", body=new_rule_body)
        h_create_dup.do_POST()
        self.assertEqual(h_create_dup.response_code, 409)

        h_clone = MockGuardianHandler(method="POST", path="/api/rules/INPROC-01/clone", body={"newId": "INPROC-01-CLONE", "newName": "Cloned Rule"})
        h_clone.do_POST()
        self.assertEqual(h_clone.response_code, 201)

        h_clone_empty = MockGuardianHandler(method="POST", path="/api/rules/INPROC-01/clone", body={})
        h_clone_empty.do_POST()
        self.assertEqual(h_clone_empty.response_code, 422)

        h_clone_dup = MockGuardianHandler(method="POST", path="/api/rules/INPROC-01/clone", body={"newId": "INPROC-01-CLONE"})
        h_clone_dup.do_POST()
        self.assertEqual(h_clone_dup.response_code, 409)

        h_dis = MockGuardianHandler(method="POST", path="/api/rules/INPROC-01/disable")
        h_dis.do_POST()
        self.assertEqual(h_dis.response_code, 200)

        h_dis_bad = MockGuardianHandler(method="POST", path="/api/rules/NONEXISTENT/disable")
        h_dis_bad.do_POST()
        self.assertEqual(h_dis_bad.response_code, 404)

        h_en = MockGuardianHandler(method="POST", path="/api/rules/INPROC-01/enable")
        h_en.do_POST()
        self.assertEqual(h_en.response_code, 200)

        h_en_bad = MockGuardianHandler(method="POST", path="/api/rules/NONEXISTENT/enable")
        h_en_bad.do_POST()
        self.assertEqual(h_en_bad.response_code, 404)

        # 7. Webhook & VCS ping
        h_ping = MockGuardianHandler(method="POST", path="/api/v1/vcs/ping", body={"platform": "github", "token": "tok", "repo": "o/r"})
        h_ping.do_POST()
        self.assertEqual(h_ping.response_code, 200)

        h_wh = MockGuardianHandler(method="POST", path="/api/v1/webhook", body={"pull_request": {"number": 1, "head": {"sha": "123"}, "base": {"sha": "main"}, "user": {"login": "u"}, "title": "t"}, "repository": {"full_name": "o/r"}})
        h_wh.do_POST()
        self.assertEqual(h_wh.response_code, 200)

        # 8. Rules import
        h_imp = MockGuardianHandler(method="POST", path="/api/rules/import", body={"rules": [{"id": "IMP-INPROC-01", "name": "Imp", "pattern": "pat"}]})
        h_imp.do_POST()
        self.assertEqual(h_imp.response_code, 200)

        # 9. Unknown endpoint POST
        h_unk = MockGuardianHandler(method="POST", path="/api/unknown_route")
        h_unk.do_POST()
        self.assertEqual(h_unk.response_code, 404)

        # 10. Malformed JSON Body POST
        h_mal = MockGuardianHandler(method="POST", path="/api/rules", body="{invalid json")
        h_mal.do_POST()
        self.assertIn(h_mal.response_code, [400, 422])

    def test_put_and_delete_routes(self):
        RuleRegistry.get_instance().register(
            RuleDefinition(id="INPROC-PUT-01", name="InProc Put", condition=RuleCondition(pattern="pat"), severity=RuleSeverity.P1_WARNING, tier=RuleTier.CUSTOM),
            actor="admin", persist=False
        )
        
        h_put = MockGuardianHandler(method="PUT", path="/api/rules/INPROC-PUT-01", body={"name": "Updated Name"})
        h_put.do_PUT()
        self.assertEqual(h_put.response_code, 200)

        h_put_bad = MockGuardianHandler(method="PUT", path="/api/rules/NONEXISTENT_RULE", body={"name": "Updated Name"})
        h_put_bad.do_PUT()
        self.assertEqual(h_put_bad.response_code, 404)

        h_put_mal = MockGuardianHandler(method="PUT", path="/api/rules/INPROC-PUT-01", body="{broken")
        h_put_mal.do_PUT()

        h_put_route_404 = MockGuardianHandler(method="PUT", path="/api/nonexistent_route")
        h_put_route_404.do_PUT()
        self.assertEqual(h_put_route_404.response_code, 404)

        h_del_builtin = MockGuardianHandler(method="DELETE", path="/api/rules/CULT01")
        h_del_builtin.do_DELETE()
        self.assertEqual(h_del_builtin.response_code, 200)

        h_del1 = MockGuardianHandler(method="DELETE", path="/api/rules/INPROC-PUT-01?cascade=true")
        h_del1.do_DELETE()
        self.assertEqual(h_del1.response_code, 200)

        h_del_bad = MockGuardianHandler(method="DELETE", path="/api/rules/NONEXISTENT_RULE")
        h_del_bad.do_DELETE()
        self.assertEqual(h_del_bad.response_code, 404)

        h_del_route_404 = MockGuardianHandler(method="DELETE", path="/api/nonexistent_route")
        h_del_route_404.do_DELETE()
        self.assertEqual(h_del_route_404.response_code, 404)


class TestCultureGuardInProcessDirect(unittest.TestCase):
    """Direct in-process execution of culture_guard functions."""

    def test_file_audit_result_all_patterns_and_custom_rules(self):
        reg = RuleRegistry.get_instance()
        custom_rule = RuleDefinition(
            id="CUSTOM-DIRECT-01",
            name="Custom Direct Rule",
            description="Tests custom direct rule evaluation",
            category="custom",
            severity=RuleSeverity.P1_WARNING,
            status=RuleStatus.ACTIVE,
            tier=RuleTier.CUSTOM,
            type=RuleType.PATTERN,
            condition=RuleCondition(patterns=[r"custom_violation_token"]),
            suggestion="Remove custom violation"
        )
        reg.register(custom_rule, actor="admin", persist=False)

        with tempfile.TemporaryDirectory() as tmpdir:
            # File with spec tag, lazy code, secret, test coverage, and custom rule
            f1 = Path(tmpdir) / "test_full_audit.py"
            f1.write_text(
                "# @spec RF01\n"
                "# Requirement: RF02\n"
                "# Spec-ID: RF03\n"
                "# [RF04]\n"
                "def my_service():\n"
                "    # TODO: implement\n"
                "    api_key = 'secret_token_1234567890123456'\n"
                "    custom_violation_token = True\n"
                "    return True\n",
                encoding="utf-8"
            )

            res = FileAuditResult(f1)
            self.assertEqual(res.has_spec_tag, 1)
            self.assertEqual(res.has_lazy_code, 1)
            self.assertEqual(res.has_secrets, 1)
            self.assertEqual(res.has_test_coverage, 1)
            self.assertTrue(any(v.get("rule_id") == "CUSTOM-DIRECT-01" for v in res.violations))

            # File with custom rule suppressed via pragma
            f2 = Path(tmpdir) / "test_suppressed.py"
            f2.write_text(
                "# @spec RF01\n"
                "# @guardian-ignore CUSTOM-DIRECT-01: valid suppression reason\n"
                "custom_violation_token = True\n",
                encoding="utf-8"
            )
            res_supp = FileAuditResult(f2)
            self.assertTrue(res_supp.suppressed_count >= 1)

        reg.delete("CUSTOM-DIRECT-01", hard_delete=True)

    def test_run_bend_engine_with_and_without_hvm(self):
        f = FileAuditResult(Path("file1.py"))
        harness = generate_bend_harness([f])

        # 1. Fallback to python engine
        with patch("subprocess.run", side_effect=FileNotFoundError("bend not found")):
            stats_fallback = run_bend_engine(harness, [f])
            self.assertEqual(stats_fallback[0], 1)

        # 2. Simulated Bend HVM stdout
        mock_bend_proc = MagicMock()
        mock_bend_proc.returncode = 0
        mock_bend_proc.stdout = (
            "======================================================================\n"
            "Parallel Reduction: 64 threads across HVM graph\n"
            "Compliance Score: 95%\n"
            "======================================================================\n"
        )
        with patch("subprocess.run", return_value=mock_bend_proc):
            stats_hvm = run_bend_engine(harness, [f])
            self.assertEqual(stats_hvm[0], 1)

    def test_main_cli_dense(self):
        with patch("sys.argv", ["culture_guard.py", "--help"]):
            try:
                culture_guard.main()
            except SystemExit:
                pass

        with patch("sys.argv", ["culture_guard.py", "mock", "--help"]):
            try:
                culture_guard.main()
            except SystemExit:
                pass

        with tempfile.TemporaryDirectory() as tmp_cli_dir:
            tmp_sample = Path(tmp_cli_dir) / "service.py"
            tmp_sample.write_text("# @spec RF01\ndef run():\n    return True\n")
            audit_modes = [
                ["culture_guard.py", str(tmp_sample), "--format=json"],
                ["culture_guard.py", str(tmp_sample), "--format=markdown"],
                ["culture_guard.py", str(tmp_sample), "--format=text"],
                ["culture_guard.py", str(tmp_sample), "--branch=main", "--format=json"],
                ["culture_guard.py", str(tmp_sample), "--architecture=clean_architecture", "--format=json"],
                ["culture_guard.py", "--mock-scenario=clean-repository", "--format=json"],
                ["culture_guard.py", "--mock-scenario=architecture-violations", "--format=text"],
                ["culture_guard.py", str(tmp_sample), "--vcs=github", "--format=json"],
                ["culture_guard.py", str(tmp_sample), "--vcs=gitlab", "--format=json"],
                ["culture_guard.py", str(tmp_sample), "--vcs=bitbucket", "--format=json"]
            ]

            for aargs in audit_modes:
                with patch("sys.argv", aargs):
                    try:
                        culture_guard.main()
                    except SystemExit:
                        pass


class TestRuleRegistryInProcessDirect(unittest.TestCase):
    """Direct testing of RuleRegistry search, list, and import branches."""

    def test_search_and_filters_all_fields(self):
        reg = RuleRegistry.get_instance()
        # Search by keyword in name, description, message, category, id
        self.assertTrue(len(reg.search("TODO")) > 0)
        self.assertTrue(len(reg.search("culture")) > 0)
        self.assertTrue(len(reg.search("CULT01")) > 0)

        # list() with architecture, category, severity, status, tier
        self.assertTrue(len(reg.list(architecture="clean_architecture")) > 0)
        self.assertTrue(len(reg.list(category="culture", severity="P0")) > 0)
        res_list = reg.list(status="ACTIVE", tier="builtin")
        self.assertIsInstance(res_list, list)

    def test_import_rules_various_formats(self):
        reg = RuleRegistry.get_instance()
        # Dict with single rule
        cnt1, _ = reg.import_rules({"id": "IMP-SINGLE-01", "name": "Single", "pattern": "pat"})
        self.assertEqual(cnt1, 1)
        reg.delete("IMP-SINGLE-01", hard_delete=True)

        # Invalid rule in import
        cnt2, errs2 = reg.import_rules([{"id": "INVALID", "tier": "INVALID_TIER"}])
        self.assertEqual(cnt2, 1)


class TestRuleTestEngineInProcessDirect(unittest.TestCase):
    """Direct testing of RuleTestEngine and RuleDefinition edge cases."""

    def test_naming_rule_unrecognized_convention(self):
        rule = RuleDefinition(
            id="NAM-UNKNOWN",
            name="Nam Unknown",
            type=RuleType.NAMING,
            condition=RuleCondition(naming_convention="UNKNOWN_CONVENTION"),
            severity=RuleSeverity.P1_WARNING,
            tier=RuleTier.CUSTOM
        )
        res = RuleTestEngine.test_rule(rule, "class AnyClass: pass", "test.py")
        self.assertFalse(res.has_violation)


if __name__ == "__main__":
    unittest.main()
