"""
==============================================================================
Max Coverage 97%+ Final Suite for Bend DevOps Guardian
==============================================================================
Exhaustive branch & statement tests targeting:
- scripts/rule_test_engine.py -> 100%
- scripts/rule_registry.py -> >98%
- scripts/guardian_server.py -> >98%
- scripts/culture_guard.py -> >98%
==============================================================================
"""

import os
import sys
import io
import json
import time
import shutil
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

from scripts.rule_model import (
    RuleDefinition, RuleSeverity, RuleStatus, RuleTier,
    RuleType, RuleScope, RuleCondition, RuleSuppressionConfig, RuleTestFixture, UserRole
)
from scripts.rule_normalizer import RuleNormalizer
from scripts.rule_test_engine import RuleTestEngine, RegexSafetyValidator, RuleTestResult
from scripts.rule_registry import RuleRegistry
from scripts.token_filter import (
    TokenFilter, IgnoredFilePattern, strip_comments, parse_inline_pragmas,
    matches_exact_token, load_guardianignore, is_file_or_rule_exempt
)
from scripts.culture_guard import (
    classify_file_layer, FileAuditResult, generate_bend_harness, run_bend_engine,
    print_report, resolve_scope_files, evaluate_scoped_rules, handle_rules_cli,
    load_layer_vocabulary, build_vocabulary_regexes
)
import scripts.culture_guard as culture_guard
import scripts.guardian_server as guardian_server


class MockHttpHelper:
    @staticmethod
    def create_handler(method="GET", path="/api/healthz", body=None):
        handler = guardian_server.GuardianRequestHandler.__new__(guardian_server.GuardianRequestHandler)
        handler.command = method
        handler.path = path
        handler.request_version = "HTTP/1.1"
        handler.headers = {}
        if body is not None:
            if isinstance(body, (dict, list)):
                raw_bytes = json.dumps(body).encode("utf-8")
            elif isinstance(body, str):
                raw_bytes = body.encode("utf-8")
            else:
                raw_bytes = body
            handler.headers["Content-Length"] = str(len(raw_bytes))
            handler.rfile = io.BytesIO(raw_bytes)
        else:
            handler.headers["Content-Length"] = "0"
            handler.rfile = io.BytesIO(b"")
        handler.wfile = io.BytesIO()
        handler.send_response = MagicMock()
        handler.send_header = MagicMock()
        handler.end_headers = MagicMock()
        return handler

    @staticmethod
    def get_response_json(handler):
        out = handler.wfile.getvalue().decode("utf-8")
        if not out:
            return {}
        try:
            return json.loads(out)
        except Exception:
            return {"raw": out}


class TestRuleTestEngineExhaustive(unittest.TestCase):
    """Exhaustive tests for rule_test_engine.py lines and branches."""

    def test_empty_pattern_in_patterns_list(self):
        rule = RuleDefinition(
            id="TEST-EMPTY-PAT",
            name="Empty Pattern Test",
            type=RuleType.PATTERN,
            condition=RuleCondition(patterns=["", "bad_var_name"]),
            severity=RuleSeverity.P1_WARNING,
            penalty_points=10
        )
        res = RuleTestEngine.test_rule(rule, "bad_var_name = 1")
        self.assertTrue(res.has_violation)

    def test_naming_rule_with_suppression(self):
        rule = RuleDefinition(
            id="NAMING-SUPP",
            name="Naming Supp Test",
            type=RuleType.NAMING,
            condition=RuleCondition(naming_convention="PascalCase"),
            severity=RuleSeverity.P1_WARNING,
            penalty_points=10
        )
        # Pragma on line 1 applies to line 2
        code = "// @guardian-ignore NAMING-SUPP: Justification minimum 8 chars\nclass bad_class_name:\n    pass\n"
        res = RuleTestEngine.test_rule(rule, code)
        self.assertTrue(res.has_violation)
        self.assertTrue(res.is_suppressed)
        self.assertIn("Justification", res.suppression_reason)

    def test_dependency_rule_with_suppression_and_forbidden_layer(self):
        rule = RuleDefinition(
            id="DEP-SUPP",
            name="Dep Supp Test",
            type=RuleType.DEPENDENCY,
            condition=RuleCondition(
                forbidden_targets=["System.Data.SqlClient"],
                forbidden_layer="Infrastructure"
            ),
            severity=RuleSeverity.P0_BLOCKING,
            penalty_points=35
        )
        # Block pragma on lines 1..3
        code = "// @guardian-ignore-start DEP-SUPP: Intentional testing justification\nusing Infrastructure;\n// @guardian-ignore-end DEP-SUPP\n"
        res = RuleTestEngine.test_rule(rule, code)
        self.assertTrue(res.has_violation)
        self.assertTrue(res.is_suppressed)
        self.assertEqual(res.suppression_reason, "Intentional testing justification")

    def test_file_folder_rule_match_and_mismatch(self):
        rule = RuleDefinition(
            id="FOLDER-01",
            name="Folder Rule",
            type=RuleType.FILE_FOLDER,
            condition=RuleCondition(required_path_prefix="src/Domain/"),
            severity=RuleSeverity.P1_WARNING,
            penalty_points=15
        )
        # Match
        res_match = RuleTestEngine.test_rule(rule, "public class Item {}", file_path="src/Domain/Item.cs")
        self.assertFalse(res_match.has_violation)
        self.assertTrue(res_match.passed)

        # Mismatch
        res_mismatch = RuleTestEngine.test_rule(rule, "public class Item {}", file_path="src/Controllers/Item.cs")
        self.assertTrue(res_mismatch.has_violation)
        self.assertFalse(res_mismatch.passed)
        self.assertEqual(len(res_mismatch.violations), 1)

    def test_fixtures_execution_failure_handling(self):
        rule = RuleDefinition(
            id="FIXTURE-FAIL",
            name="Fixture Failure Rule",
            type=RuleType.PATTERN,
            condition=RuleCondition(pattern="forbidden_token"),
            tests=[
                RuleTestFixture(name="Failing Expectation", input="forbidden_token()", expected_violation=False),
                RuleTestFixture(name="Passing Expectation", input="valid_token()", expected_violation=False)
            ]
        )
        passed, results = RuleTestEngine.run_all_rule_fixtures(rule)
        self.assertFalse(passed)
        self.assertEqual(len(results), 2)
        summary = RuleTestEngine.execute_fixtures(rule)
        self.assertFalse(summary["passed"])
        self.assertEqual(summary["passed_fixtures"], 1)
        self.assertEqual(summary["failed_fixtures"], 1)

    def test_rule_without_languages_specified(self):
        rule = RuleDefinition(
            id="NO-LANG",
            name="No Lang Rule",
            type=RuleType.PATTERN,
            condition=RuleCondition(pattern="secret_key"),
            languages=[]
        )
        res = RuleTestEngine.test_rule(rule, "secret_key = 123", file_path="config.py")
        self.assertTrue(res.has_violation)


class TestRuleRegistryExhaustive(unittest.TestCase):
    """Exhaustive tests for rule_registry.py permission matrix, validation, and operations."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_dir = Path(self.temp_dir.name)
        self.reg = RuleRegistry(self.base_dir)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_permissions_matrix(self):
        # Admin
        self.assertTrue(self.reg.check_permission(UserRole.ADMINISTRATOR, "delete"))
        self.assertTrue(self.reg.check_permission(UserRole.ADMIN, "create"))
        self.assertTrue(self.reg.check_permission(UserRole.RULE_ADMIN, "enable"))

        # Maintainer
        self.assertTrue(self.reg.check_permission(UserRole.RULE_MAINTAINER, "create"))
        self.assertTrue(self.reg.check_permission(UserRole.RULE_MAINTAINER, "delete"))
        self.assertTrue(self.reg.check_permission(UserRole.RULE_MAINTAINER, "deprecate"))
        self.assertFalse(self.reg.check_permission(UserRole.RULE_MAINTAINER, "unknown_action"))

        # Author
        self.assertTrue(self.reg.check_permission(UserRole.RULE_AUTHOR, "create"))
        self.assertTrue(self.reg.check_permission(UserRole.RULE_AUTHOR, "test"))
        self.assertFalse(self.reg.check_permission(UserRole.RULE_AUTHOR, "delete"))
        self.assertFalse(self.reg.check_permission(UserRole.RULE_AUTHOR, "enable"))

        # Viewer
        self.assertTrue(self.reg.check_permission(UserRole.VIEWER, "view"))
        self.assertTrue(self.reg.check_permission(UserRole.VIEWER, "search"))
        self.assertFalse(self.reg.check_permission(UserRole.VIEWER, "create"))
        self.assertFalse(self.reg.check_permission(UserRole.VIEWER, "delete"))

    def test_permission_error_exceptions(self):
        rule = RuleDefinition(id="REG-PERM-01", name="Perm Test Rule", condition=RuleCondition(pattern="xyz"))

        # Viewer trying to register
        with self.assertRaises(PermissionError):
            self.reg.register(rule, user_role=UserRole.VIEWER)

        # Viewer trying to unregister
        with self.assertRaises(PermissionError):
            self.reg.unregister("REG-PERM-01", user_role=UserRole.VIEWER)

        # Viewer trying to enable
        with self.assertRaises(PermissionError):
            self.reg.enable("REG-PERM-01", user_role=UserRole.VIEWER)

        # Viewer trying to disable
        with self.assertRaises(PermissionError):
            self.reg.disable("REG-PERM-01", user_role=UserRole.VIEWER)

        # Viewer trying to clone
        with self.assertRaises(PermissionError):
            self.reg.clone("REG-PERM-01", "REG-CLONE", user_role=UserRole.VIEWER)

        # Viewer trying to import manifest
        with self.assertRaises(PermissionError):
            self.reg.import_manifest({"rules": []}, user_role=UserRole.VIEWER)

    def test_validate_rule_invalid_types_and_safety(self):
        # Non-dict non-RuleDefinition
        valid, errors = self.reg.validate_rule(12345)
        self.assertFalse(valid)
        self.assertIn("Invalid rule data format", errors[0])

        # Invalid ID, Name, Type
        valid, errors = self.reg.validate_rule({
            "id": "bad id with spaces",
            "name": "a",
            "type": "invalid_type"
        })
        self.assertFalse(valid)
        self.assertEqual(len(errors), 3)

        # Unsafe ReDoS pattern
        valid, errors = self.reg.validate_rule({
            "id": "UNSAFE-01",
            "name": "Unsafe Regex Rule",
            "type": "pattern",
            "condition": {"pattern": "(a+)+$"}
        })
        self.assertFalse(valid)
        self.assertTrue(any("Unsafe pattern" in e for e in errors))

    def test_register_invalid_raises_value_error(self):
        invalid_rule = RuleDefinition(id="bad id", name="a", condition=RuleCondition())
        with self.assertRaises(ValueError):
            self.reg.register(invalid_rule)

    def test_unregister_archive_soft_delete(self):
        rule = RuleDefinition(id="SOFT-DEL-01", name="Soft Delete Rule", condition=RuleCondition(pattern="abc"))
        self.reg.register(rule, persist=True)
        self.assertTrue(self.reg.get("SOFT-DEL-01").enabled)

        # Soft delete (archive)
        ok = self.reg.unregister("SOFT-DEL-01", hard_delete=False)
        self.assertTrue(ok)
        r = self.reg.get("SOFT-DEL-01")
        self.assertFalse(r.enabled)
        self.assertEqual(r.status, RuleStatus.ARCHIVED)

    def test_clone_source_not_found_or_exists(self):
        with self.assertRaises(ValueError) as ctx:
            self.reg.clone("NONEXISTENT", "NEW-ID")
        self.assertIn("not found", str(ctx.exception))

        rule = RuleDefinition(id="EXISTING-01", name="Existing Rule", condition=RuleCondition(pattern="abc"))
        self.reg.register(rule)
        with self.assertRaises(ValueError) as ctx:
            self.reg.clone("EXISTING-01", "EXISTING-01")
        self.assertIn("already exists", str(ctx.exception))

    def test_import_rules_from_directory_and_malformed(self):
        # 1. Create a dir with valid and invalid json files
        import_dir = self.base_dir / "import_tests"
        import_dir.mkdir(parents=True, exist_ok=True)
        
        valid_file = import_dir / "valid.json"
        valid_file.write_text(json.dumps({
            "id": "IMP-DIR-01",
            "name": "Imported Dir Rule",
            "type": "pattern",
            "condition": {"pattern": "dir_token"}
        }))

        invalid_json = import_dir / "corrupted.json"
        invalid_json.write_text("{corrupted json")

        cnt, errs = self.reg.import_rules(str(import_dir))
        self.assertEqual(cnt, 1)
        self.assertTrue(any("Failed to read file" in e for e in errs))

        # 2. Non-dict items in list
        cnt2, errs2 = self.reg.import_rules(["not a dict", {"id": "bad id spaces"}])
        self.assertEqual(cnt2, 0)
        self.assertEqual(len(errs2), 1)

    def test_import_manifest_errors_and_overwrite(self):
        # Invalid JSON string
        res = self.reg.import_manifest("invalid json string {")
        self.assertEqual(res["imported"], 0)
        self.assertEqual(res["failed"], 1)

        # Overwrite=False
        rule_data = {
            "id": "NO-OVERWRITE-01",
            "name": "No Overwrite",
            "type": "pattern",
            "condition": {"pattern": "abc"}
        }
        self.reg.import_manifest({"rules": [rule_data]})
        res2 = self.reg.import_manifest({"rules": [rule_data]}, overwrite=False)
        self.assertEqual(res2["imported"], 0)
        self.assertEqual(res2["failed"], 1)
        self.assertIn("already exists", res2["errors"][0])

        # Item validation error
        res3 = self.reg.import_manifest({"rules": [{"id": "INVALID ID SPACES"}]})
        self.assertEqual(res3["failed"], 1)

    def test_export_methods_and_categories(self):
        rule = RuleDefinition(id="EXP-01", name="Export Rule", category="security", condition=RuleCondition(pattern="pwd"))
        self.reg.register(rule)
        
        exp_single = self.reg.export_rule("EXP-01")
        self.assertEqual(exp_single["id"], "EXP-01")
        self.assertIsNone(self.reg.export_rule("NONEXISTENT"))

        exp_all = self.reg.export_all()
        self.assertIn("rules", exp_all)

        exp_man = self.reg.export_manifest(RuleTier.CUSTOM)
        self.assertIn("Bend DevOps Guardian Exported Ruleset", exp_man)

        cats = self.reg.get_categories()
        self.assertIn("security", cats)
        langs = self.reg.get_languages()
        self.assertIn("csharp", langs)
        types = self.reg.get_types()
        self.assertIn("pattern", types)

    def test_corrupted_legacy_rule_files(self):
        legacy_dir = self.base_dir / "2_rules"
        legacy_dir.mkdir(parents=True, exist_ok=True)
        (legacy_dir / "corrupted.json").write_text("{corrupted")
        
        (self.base_dir / "architecture_bad.json").write_text("{corrupted")
        (self.base_dir / "culture_manifesto.json").write_text("{corrupted")

        # Calling _load_from_legacy_rules should safely pass exceptions
        self.reg._load_from_legacy_rules()

    def test_load_from_dir_edge_cases(self):
        # 1. Directory does not exist
        self.reg._load_from_dir(Path("/nonexistent/dir"), RuleTier.CUSTOM)
        
        # 2. Directory with multi-rule JSON file
        multi_dir = self.base_dir / "multi_rules"
        multi_dir.mkdir(parents=True, exist_ok=True)
        multi_file = multi_dir / "rules.json"
        multi_file.write_text(json.dumps({
            "rules": [
                {"id": "MULTI-01", "name": "Multi Rule 1", "condition": {"pattern": "abc"}},
                {"id": "MULTI-02", "name": "Multi Rule 2", "condition": {"pattern": "def"}}
            ]
        }))
        self.reg._load_from_dir(multi_dir, RuleTier.CUSTOM)
        self.reg._invalidate_cache()
        self.assertIsNotNone(self.reg.get("MULTI-01"))
        self.assertIsNotNone(self.reg.get("MULTI-02"))

    def test_enable_custom_rule_persists(self):
        rule = RuleDefinition(id="CUSTOM-PERSIST-01", name="Custom Persist", tier=RuleTier.CUSTOM, condition=RuleCondition(pattern="abc"))
        self.reg.register(rule, persist=True)
        self.reg.disable("CUSTOM-PERSIST-01")
        res = self.reg.enable("CUSTOM-PERSIST-01")
        self.assertIsNotNone(res)
        self.assertTrue(res.enabled)

    def test_get_categories_empty_category(self):
        rule = RuleDefinition(id="NO-CAT-01", name="No Cat Rule", category="", condition=RuleCondition(pattern="abc"))
        self.reg.register(rule)
        cats = self.reg.get_categories()
        self.assertIsInstance(cats, list)


class TestGuardianServerExhaustive(unittest.TestCase):
    """Exhaustive tests for guardian_server.py endpoints and git functions."""

    def test_start_guardian_server_graceful_shutdown(self):
        with patch("scripts.guardian_server.HTTPServer") as mock_http:
            mock_server_inst = MagicMock()
            mock_server_inst.serve_forever.side_effect = KeyboardInterrupt()
            mock_http.return_value = mock_server_inst
            
            # Should catch KeyboardInterrupt and exit gracefully
            guardian_server.start_guardian_server(port=4999, is_mock=True, scenario="clean-repository")
            self.assertTrue(guardian_server.GuardianRequestHandler.is_mock_mode)
            self.assertEqual(guardian_server.GuardianRequestHandler.mock_scenario, "clean-repository")

    def test_browse_local_directories_and_git_inspection_errors(self):
        # 1. Non-existent path fallback
        res = guardian_server.browse_local_directories("/non/existent/path/999")
        self.assertIn("currentPath", res)

        # 2. Subprocess error handling in inspect_local_repository_path
        with patch("subprocess.run", side_effect=Exception("Git fatal error")):
            res2 = guardian_server.inspect_local_repository_path(str(REPO_ROOT))
            self.assertFalse(res2["valid"])
            self.assertEqual(res2["errorType"], "GIT_ERROR")

    def test_get_working_tree_info_scenarios(self):
        # 1. Non-existent repo
        res = guardian_server.get_working_tree_info("/non/existent/repo/path")
        self.assertTrue(res["isClean"])
        self.assertIn("error", res)

        # 2. Clean status
        with patch("subprocess.run") as mock_sub:
            mock_sub.return_value = MagicMock(stdout="", returncode=0)
            res2 = guardian_server.get_working_tree_info(str(REPO_ROOT))
            self.assertTrue(res2["isClean"])

        # 3. Modified, Added, Deleted with diff
        with patch("subprocess.run") as mock_sub:
            def side_effect(cmd, **kwargs):
                if "status" in cmd:
                    return MagicMock(stdout=" M file1.py\n A file2.py\n D file3.py", returncode=0)
                elif "diff" in cmd:
                    return MagicMock(stdout="+++ file1.py\n+add line\n-del line", returncode=0)
                return MagicMock(stdout="", returncode=0)
            mock_sub.side_effect = side_effect
            res3 = guardian_server.get_working_tree_info(str(REPO_ROOT))
            self.assertFalse(res3["isClean"])
            self.assertEqual(len(res3["changedFiles"]), 3)

    def test_fetch_github_repositories(self):
        # 1. Successful 200 response
        mock_response = MagicMock()
        mock_response.getcode.return_value = 200
        mock_response.read.return_value = json.dumps([
            {"name": "repo1", "full_name": "org/repo1", "owner": {"login": "org"}, "default_branch": "main", "html_url": "https://github.com/org/repo1"}
        ]).encode("utf-8")
        mock_response.__enter__.return_value = mock_response

        with patch.dict(os.environ, {"GITHUB_TOKEN": "test_token"}):
            with patch("urllib.request.urlopen", return_value=mock_response):
                res = guardian_server.get_github_repositories()
                self.assertTrue(res["connected"])
                self.assertEqual(len(res["repositories"]), 1)

        # 2. Exception/failure
        with patch.dict(os.environ, {"GITHUB_TOKEN": "test_token"}):
            with patch("urllib.request.urlopen", side_effect=Exception("API limit exceeded")):
                res2 = guardian_server.get_github_repositories()
                self.assertFalse(res2["connected"])
                self.assertIn("API limit exceeded", res2["error"])

        # 3. Non-200 code
        mock_response_401 = MagicMock()
        mock_response_401.getcode.return_value = 401
        mock_response_401.__enter__.return_value = mock_response_401
        with patch.dict(os.environ, {"GITHUB_TOKEN": "test_token"}):
            with patch("urllib.request.urlopen", return_value=mock_response_401):
                res3 = guardian_server.get_github_repositories()
                self.assertIsNone(res3)

    def test_framework_detection_profiles(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_p = Path(tmp)
            
            # C# only
            cs_dir = tmp_p / "cs_project"
            cs_dir.mkdir()
            (cs_dir / "App.csproj").write_text("<Project></Project>")
            (cs_dir / "App.cs").write_text("public class App {}")
            res_cs = guardian_server.detect_repository_framework(str(cs_dir))
            self.assertIn("C#", res_cs["primaryFramework"])

            # Frontend only
            fe_dir = tmp_p / "fe_project"
            fe_dir.mkdir()
            (fe_dir / "package.json").write_text('{"dependencies": {"react": "18.0"}}')
            (fe_dir / "App.tsx").write_text("export const App = () => <div/>;")
            res_fe = guardian_server.detect_repository_framework(str(fe_dir))
            self.assertIn("Frontend", res_fe["primaryFramework"])

            # Python only
            py_dir = tmp_p / "py_project"
            py_dir.mkdir()
            (py_dir / "requirements.txt").write_text("pytest\n")
            (py_dir / "main.py").write_text("def main(): pass")
            res_py = guardian_server.detect_repository_framework(str(py_dir))
            self.assertIn("Python", res_py["primaryFramework"])

            # Generic
            gen_dir = tmp_p / "gen_project"
            gen_dir.mkdir()
            (gen_dir / "data.txt").write_text("data")
            res_gen = guardian_server.detect_repository_framework(str(gen_dir))
            self.assertIn("Universal", res_gen["primaryFramework"])

            # Corrupted package.json
            corrupt_dir = tmp_p / "corrupt_pkg"
            corrupt_dir.mkdir()
            (corrupt_dir / "package.json").write_text("{corrupt json")
            res_corrupt = guardian_server.detect_repository_framework(str(corrupt_dir))
            self.assertTrue(res_corrupt["valid"])

    def test_get_repository_by_id_path_and_custom_cache(self):
        res = guardian_server.get_repository_by_id(str(REPO_ROOT))
        self.assertIsNotNone(res)
        self.assertEqual(res["path"], str(REPO_ROOT))

    def test_api_rules_post_put_delete_edge_cases(self):
        reg = RuleRegistry.get_instance()
        reg.load_all()

        # POST /api/rules missing ID
        h_post_no_id = MockHttpHelper.create_handler("POST", "/api/rules", {"name": "No ID"})
        h_post_no_id.do_POST()
        res = MockHttpHelper.get_response_json(h_post_no_id)
        self.assertEqual(res.get("errorType"), "VALIDATION_ERROR")

        # POST /api/rules duplicate ID
        h_post_dup = MockHttpHelper.create_handler("POST", "/api/rules", {
            "id": "CULT01",
            "name": "Duplicate Rule",
            "type": "pattern",
            "condition": {"pattern": "abc"}
        })
        h_post_dup.do_POST()
        res_dup = MockHttpHelper.get_response_json(h_post_dup)
        self.assertEqual(res_dup.get("errorType"), "RULE_ALREADY_EXISTS")

        # POST /api/rules invalid schema
        h_post_inv = MockHttpHelper.create_handler("POST", "/api/rules", {
            "id": "VALID-ID-BUT-INVALID-SCHEMA",
            "name": "a", # too short
            "type": "invalid_type"
        })
        h_post_inv.do_POST()
        res_inv = MockHttpHelper.get_response_json(h_post_inv)
        self.assertEqual(res_inv.get("errorType"), "INVALID_RULE_SCHEMA")

        # POST /api/rules/<id>/clone missing new_id
        h_clone_no_id = MockHttpHelper.create_handler("POST", "/api/rules/CULT01/clone", {})
        h_clone_no_id.do_POST()
        res_c1 = MockHttpHelper.get_response_json(h_clone_no_id)
        self.assertEqual(res_c1.get("errorType"), "VALIDATION_ERROR")

        # POST /api/rules/<id>/clone duplicate new_id
        h_clone_dup = MockHttpHelper.create_handler("POST", "/api/rules/CULT01/clone", {"new_id": "CULT02"})
        h_clone_dup.do_POST()
        res_c2 = MockHttpHelper.get_response_json(h_clone_dup)
        self.assertEqual(res_c2.get("errorType"), "RULE_ALREADY_EXISTS")

        # POST /api/rules/<id>/clone exception
        h_clone_err = MockHttpHelper.create_handler("POST", "/api/rules/NONEXISTENT_SOURCE/clone", {"new_id": "NEW-ID-999"})
        h_clone_err.do_POST()
        res_c3 = MockHttpHelper.get_response_json(h_clone_err)
        self.assertIn("error", res_c3)

        # PUT /api/rules/<id> not found
        h_put_404 = MockHttpHelper.create_handler("PUT", "/api/rules/NONEXISTENT_999", {"name": "Updated"})
        h_put_404.do_PUT()
        res_p1 = MockHttpHelper.get_response_json(h_put_404)
        self.assertEqual(res_p1.get("errorType"), "RULE_NOT_FOUND")

        # PUT /api/rules/<id> invalid schema
        h_put_inv = MockHttpHelper.create_handler("PUT", "/api/rules/CULT01", {"name": "x"})
        h_put_inv.do_PUT()
        res_p2 = MockHttpHelper.get_response_json(h_put_inv)
        self.assertEqual(res_p2.get("errorType"), "INVALID_RULE_SCHEMA")

        # DELETE /api/rules/<id> not found
        h_del_404 = MockHttpHelper.create_handler("DELETE", "/api/rules/NONEXISTENT_999")
        h_del_404.do_DELETE()
        res_d1 = MockHttpHelper.get_response_json(h_del_404)
        self.assertEqual(res_d1.get("errorType"), "RULE_NOT_FOUND")

        # DELETE /api/rules/<id> builtin rule
        r_cult01 = reg.get("CULT01")
        if r_cult01:
            r_cult01.tier = RuleTier.BUILTIN
        h_del_builtin = MockHttpHelper.create_handler("DELETE", "/api/rules/CULT01")
        h_del_builtin.do_DELETE()
        res_d2 = MockHttpHelper.get_response_json(h_del_builtin)
        self.assertTrue(res_d2.get("success"))
        self.assertFalse(res_d2.get("deleted"))

    def test_api_audit_endpoints_and_branch_diff(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_p = Path(tmp)
            f1 = tmp_p / "Order.cs"
            f1.write_text("public class Order {\n    // TODO: implement\n}\n")

            # 1. POST /api/audit working_tree
            with patch("subprocess.run") as mock_sub:
                def side_effect(cmd, **kwargs):
                    if "status" in cmd:
                        return MagicMock(stdout=" M Order.cs\n", returncode=0)
                    elif "culture_guard.py" in str(cmd):
                        return MagicMock(stdout=json.dumps({
                            "total_files": 1,
                            "total_violations": 1,
                            "total_suppressed": 0,
                            "has_blocking_violations": True,
                            "culture_score": 65,
                            "approved": False,
                            "files": [{
                                "path": str(f1),
                                "layer": "Domain",
                                "suppressed_count": 0,
                                "violations": [{
                                    "rule_id": "CULT01",
                                    "severity": "P1_WARNING",
                                    "penalty": 10,
                                    "message": "Warning"
                                }]
                            }]
                        }), returncode=0)
                    return MagicMock(stdout="true", returncode=0)
                mock_sub.side_effect = side_effect

                h_audit_wt = MockHttpHelper.create_handler("POST", "/api/audit", {
                    "repoPath": str(tmp_p),
                    "targetType": "working_tree",
                    "rules": ["CULT01"]
                })
                h_audit_wt.do_POST()
                res_wt = MockHttpHelper.get_response_json(h_audit_wt)
                self.assertEqual(res_wt.get("total_files"), 1)

            # 2. POST /api/audit branch diff fallback
            with patch("subprocess.run") as mock_sub:
                def side_effect_branch(cmd, **kwargs):
                    if "diff" in cmd and "..." in str(cmd):
                        return MagicMock(stdout="", returncode=1)
                    elif "diff" in cmd and ".." in str(cmd):
                        return MagicMock(stdout="Order.cs\n", returncode=0)
                    elif "culture_guard.py" in str(cmd):
                        return MagicMock(stdout=json.dumps({
                            "total_files": 1,
                            "total_violations": 0,
                            "total_suppressed": 0,
                            "has_blocking_violations": False,
                            "culture_score": 100,
                            "approved": True,
                            "files": []
                        }), returncode=0)
                    return MagicMock(stdout="true", returncode=0)
                mock_sub.side_effect = side_effect_branch

                h_audit_br = MockHttpHelper.create_handler("POST", "/api/audit", {
                    "repoPath": str(tmp_p),
                    "targetType": "branch",
                    "branch": "feature/test",
                    "baseBranch": "main"
                })
                h_audit_br.do_POST()
                res_br = MockHttpHelper.get_response_json(h_audit_br)
                self.assertIn("culture_score", res_br)

    def test_inspect_local_repository_path_branches_and_head_variations(self):
        # 1. Top level return code != 0
        with patch("subprocess.run") as mock_sub:
            def side_effect(cmd, **kwargs):
                if "--is-inside-work-tree" in cmd:
                    return MagicMock(stdout="true", returncode=0)
                elif "--show-toplevel" in cmd:
                    return MagicMock(stdout="", returncode=1)
                return MagicMock(stdout="", returncode=0)
            mock_sub.side_effect = side_effect
            res = guardian_server.inspect_local_repository_path(str(REPO_ROOT))
            self.assertFalse(res["valid"])
            self.assertEqual(res["errorType"], "GIT_ERROR")

        # 2. Detached HEAD and named detached branch
        with patch("subprocess.run") as mock_sub:
            def side_effect_detached(cmd, **kwargs):
                if "--is-inside-work-tree" in cmd:
                    return MagicMock(stdout="true", returncode=0)
                elif "--show-toplevel" in cmd:
                    return MagicMock(stdout=str(REPO_ROOT), returncode=0)
                elif "--show-current" in cmd:
                    return MagicMock(stdout="", returncode=0)
                elif "--abbrev-ref" in cmd:
                    return MagicMock(stdout="HEAD", returncode=0)
                elif "for-each-ref" in cmd:
                    return MagicMock(stdout="", returncode=0)
                elif "branch" in cmd and "--list" in cmd:
                    return MagicMock(stdout="", returncode=0)
                return MagicMock(stdout="mock", returncode=0)
            mock_sub.side_effect = side_effect_detached
            res2 = guardian_server.inspect_local_repository_path(str(REPO_ROOT))
            self.assertTrue(res2["valid"])
            self.assertEqual(res2["repository"]["currentBranch"], "Detached HEAD")


class TestCultureGuardExhaustive(unittest.TestCase):
    """Exhaustive tests for culture_guard.py branches and CLI routines."""

    def test_layer_vocabulary_and_regex_builder(self):
        vocab_dict = {
            "layers": {
                "Presentation": {"tokens": {"html": ["<custom-tag"]}},
                "Interface_Transport": {"tokens": {"req": ["CustomRequest"]}},
                "Infrastructure_Persistence": {"tokens": {"db": ["CustomDbContext"]}}
            }
        }
        regexes = build_vocabulary_regexes(vocab_dict)
        self.assertIn("Model", regexes)
        self.assertIn("PresentationalUI", regexes)

    def test_load_layer_vocabulary_missing_file(self):
        with patch("scripts.culture_guard.RULES_BASE_DIR", Path("/nonexistent/dir")):
            vocab = load_layer_vocabulary()
            self.assertEqual(vocab, {})

    def test_file_audit_exemptions_all_and_individual(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_p = Path(tmp)
            
            # File with exemptions for CULT01, CULT02, CULT03, CULT04
            exempt_file = tmp_p / "service.py"
            exempt_file.write_text("TODO: fix later\napi_key = '12345'\n")

            exemptions = [
                IgnoredFilePattern(glob_pattern="*.py", exempted_rules=["CULT01"]),
                IgnoredFilePattern(glob_pattern="*.py", exempted_rules=["CULT02"]),
                IgnoredFilePattern(glob_pattern="*.py", exempted_rules=["CULT03"]),
                IgnoredFilePattern(glob_pattern="*.py", exempted_rules=["CULT04"]),
            ]

            audit = FileAuditResult(exempt_file, exemptions)
            self.assertEqual(len(audit.violations), 0)
            self.assertGreaterEqual(audit.suppressed_count, 4)

            # ALL exemption
            all_exemptions = [IgnoredFilePattern(glob_pattern="*.py", exempted_rules=["ALL"])]
            audit_all = FileAuditResult(exempt_file, all_exemptions)
            self.assertEqual(len(audit_all.violations), 0)

            # Non-existent file read failure handling
            audit_none = FileAuditResult(tmp_p / "nonexistent.py")
            self.assertEqual(audit_none.lines_count, 0)

    def test_file_audit_custom_rule_exemption(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_p = Path(tmp)
            f = tmp_p / "service.py"
            f.write_text("def fn() -> int:\n    # @spec RF01\n    return 42\n")
            (tmp_p / "test_service.py").write_text("def test_fn(): pass\n")

            reg = RuleRegistry.get_instance()
            custom_rule = RuleDefinition(
                id="CUSTOM-AUDIT-EXEMPT",
                name="Custom Audit Exempt",
                tier=RuleTier.CUSTOM,
                type=RuleType.PATTERN,
                condition=RuleCondition(pattern="fn"),
                severity=RuleSeverity.P1_WARNING,
                penalty_points=10
            )
            reg.register(custom_rule, persist=False)

            exemptions = [IgnoredFilePattern(glob_pattern="*.py", exempted_rules=["CUSTOM-AUDIT-EXEMPT"])]
            audit = FileAuditResult(f, exemptions)
            self.assertEqual(len(audit.violations), 0)
            self.assertGreaterEqual(audit.suppressed_count, 1)

    def test_generate_bend_harness_binary_tree_leaves(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_p = Path(tmp)
            files = []
            for i in range(5):
                f = tmp_p / f"file_{i}.py"
                f.write_text("def fn() -> int:\n    return 42\n")
                files.append(FileAuditResult(f))

            harness = generate_bend_harness(files)
            self.assertIn("evaluate_tree_parallel", harness)
            self.assertIn("FileTree/Node", harness)

    def test_run_bend_engine_with_subprocess_mock(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_p = Path(tmp)
            f = tmp_p / "sample.py"
            f.write_text("def fn() -> int:\n    return 42\n")
            audit_files = [FileAuditResult(f)]

            # Mock bend success
            with patch("subprocess.run") as mock_sub:
                mock_sub.return_value = MagicMock(stdout="(1, 0, 0, 0, 0, 100, 1)", returncode=0)
                stats = run_bend_engine("code", audit_files)
                self.assertEqual(stats[5], 100)

            # Mock bend failure
            with patch("subprocess.run", side_effect=Exception("Bend CLI not installed")):
                stats_fallback = run_bend_engine("code", audit_files)
                self.assertEqual(stats_fallback[0], 1)

    def test_resolve_scope_files_all_modes(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_p = Path(tmp)
            sub_dir = tmp_p / "src"
            sub_dir.mkdir()
            (sub_dir / "service.cs").write_text("public class Service {}")
            (tmp_p / "root.py").write_text("def fn() -> int:\n    return 42\n")

            # 1. scope='subdirectory' with target dir
            res_sub = resolve_scope_files(tmp_p, scope="subdirectory", target="src")
            self.assertEqual(len(res_sub), 1)

            # 2. scope='subdirectory' with target file
            res_sub_file = resolve_scope_files(tmp_p, scope="subdirectory", target="src/service.cs")
            self.assertEqual(len(res_sub_file), 1)

            # 3. scope='single_file' with target file
            res_single = resolve_scope_files(tmp_p, scope="single_file", target="root.py")
            self.assertEqual(len(res_single), 1)

            # 4. scope='working_tree_diff'
            with patch("subprocess.run") as mock_sub:
                mock_sub.return_value = MagicMock(stdout=" M src/service.cs\n", returncode=0)
                res_diff = resolve_scope_files(tmp_p, scope="working_tree_diff")
                self.assertEqual(len(res_diff), 1)

            # 5. scope='full_branch' with exclude patterns
            res_full = resolve_scope_files(tmp_p, scope="full_branch", exclude_patterns=["src/*"])
            self.assertEqual(len(res_full), 1)

    def test_evaluate_scoped_rules_custom_severities(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_p = Path(tmp)
            f = tmp_p / "Order.cs"
            # Violates CULT01 (TODO), CULT02 (missing @spec), CULT03 (missing test)
            f.write_text("public class Order {\n    // TODO: implement\n}\n")

            # Custom severities: P0, P1, P2/INFO
            rules_cfg = [
                {"id": "CULT01", "customSeverity": "P0_BLOCKING"},
                {"id": "CULT02", "customSeverity": "P2_INFO"},
                {"id": "CULT03", "customSeverity": "P1_WARNING"}
            ]

            res = evaluate_scoped_rules([str(f)], rules=rules_cfg)
            self.assertFalse(res["isApproved"])
            self.assertGreater(res["totalViolations"], 0)
            
            # Verify status tags in rulesEvaluated
            rule_statuses = {r["ruleId"]: r["status"] for r in res["rulesEvaluated"]}
            self.assertEqual(rule_statuses.get("CULT01"), "FAILED")
            self.assertEqual(rule_statuses.get("CULT02"), "WARNING")

    def test_cli_show_single_pattern_and_validate_failure(self):
        # 1. show rule with single pattern
        reg = RuleRegistry.get_instance()
        r_single = RuleDefinition(id="SHOW-PAT-01", name="Single Pat", condition=RuleCondition(pattern="single_pat"))
        reg.register(r_single, persist=False)

        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            ret = handle_rules_cli(["show", "SHOW-PAT-01"])
            self.assertEqual(ret, 0)
            self.assertIn("Pattern:", mock_out.getvalue())

        # 2. validate invalid rule json file
        with tempfile.TemporaryDirectory() as tmp:
            tmp_p = Path(tmp)
            bad_json = tmp_p / "bad_rule.json"
            bad_json.write_text(json.dumps({"id": "BAD ID SPACES", "name": "a"}))
            with patch("sys.stderr", new_callable=io.StringIO) as mock_err:
                ret_val = handle_rules_cli(["validate", str(bad_json)])
                self.assertEqual(ret_val, 1)
                self.assertIn("Validation failed", mock_err.getvalue())

        # 3. test with json file target
        with tempfile.TemporaryDirectory() as tmp:
            tmp_p = Path(tmp)
            test_rule_file = tmp_p / "valid_rule.json"
            test_rule_file.write_text(json.dumps({
                "id": "FILE-TARGET-RULE",
                "name": "File Target Rule",
                "type": "pattern",
                "condition": {"pattern": "secret"}
            }))
            with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
                ret_test = handle_rules_cli(["test", str(test_rule_file), "--code", "secret = 1"])
                self.assertEqual(ret_test, 0)
                self.assertIn("RULE TEST EXECUTION", mock_out.getvalue())

    def test_handle_rules_cli_all_commands(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_p = Path(tmp)
            rule_json = tmp_p / "cli_rule.json"
            rule_json.write_text(json.dumps({
                "id": "CLI-TEST-02",
                "name": "CLI Rule 2",
                "type": "pattern",
                "condition": {"pattern": "cli_test_pat"}
            }))

            # Test command
            with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
                ret = handle_rules_cli(["test", "CULT01", "--code", "TODO: test"])
                self.assertEqual(ret, 0)
                self.assertIn("RULE TEST EXECUTION", mock_out.getvalue())

            # Test command with json output
            with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
                ret = handle_rules_cli(["test", "CULT01", "--code", "TODO: test", "--json"])
                self.assertEqual(ret, 0)
                self.assertIn("has_violation", mock_out.getvalue())

            # Export command to file
            out_file = tmp_p / "exported_all.json"
            ret = handle_rules_cli(["export", "all", "--out", str(out_file)])
            self.assertEqual(ret, 0)
            self.assertTrue(out_file.exists())

            # Search command
            with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
                ret = handle_rules_cli(["search", "culture"])
                self.assertEqual(ret, 0)
                self.assertIn("SEARCH RESULTS", mock_out.getvalue())

    def test_main_cli_branches_and_vcs(self):
        # 1. Main with mock scenario argument (JSON output)
        with patch("sys.argv", ["culture_guard.py", "--mock-scenario=clean-repository", "--format=json"]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
                with self.assertRaises(SystemExit) as cm:
                    culture_guard.main()
                self.assertEqual(cm.exception.code, 0)
                self.assertIn("clean-repository", mock_out.getvalue())

        # 2. Main with mock scenario text output
        with patch("sys.argv", ["culture_guard.py", "--mock-scenario=clean-repository", "--format=text"]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
                with self.assertRaises(SystemExit) as cm:
                    culture_guard.main()
                self.assertEqual(cm.exception.code, 0)
                self.assertIn("MOCK SCENARIO", mock_out.getvalue())

        # 3. Main with VCS flags (github, gitlab, bitbucket)
        with tempfile.TemporaryDirectory() as tmp:
            tmp_p = Path(tmp)
            valid_src = tmp_p / "app.py"
            valid_src.write_text("# @spec RF01\ndef run() -> int:\n    return 42\n")
            (tmp_p / "test_app.py").write_text("def test_run(): pass\n")

            for vcs_name in ["github", "gitlab", "bitbucket"]:
                with patch("sys.argv", ["culture_guard.py", str(valid_src), f"--vcs={vcs_name}", "--format=json"]):
                    with patch("scripts.culture_guard.get_vcs_adapter") as mock_vcs:
                        mock_adapter_inst = MagicMock()
                        mock_adapter_inst.generate_report_artifact.return_value = "{}"
                        mock_adapter_inst.api_base = f"https://api.{vcs_name}.com"
                        mock_vcs.return_value = mock_adapter_inst
                        with self.assertRaises(SystemExit) as cm:
                            culture_guard.main()
                        self.assertEqual(cm.exception.code, 0)

    def test_main_cli_mock_and_rules_subcommands(self):
        # 1. Main with mock subcommand
        with patch("sys.argv", ["culture_guard.py", "mock", "--scenario=clean-repository"]):
            with patch("scripts.guardian_mock.main") as mock_m:
                culture_guard.main()
                mock_m.assert_called_once()

        # 2. Main with rules subcommand
        with patch("sys.argv", ["culture_guard.py", "rules", "search", "test"]):
            with patch("scripts.culture_guard.handle_rules_cli") as mock_h:
                culture_guard.main()
                mock_h.assert_called_once_with(["search", "test"])

    def test_evaluate_scoped_rules_edge_cases(self):
        # 1. Empty files list
        res_empty = evaluate_scoped_rules([], rules=["CULT01"])
        self.assertTrue(res_empty["isApproved"])
        self.assertEqual(res_empty["totalViolations"], 0)

        # 2. Disabled rule in dict
        res_disabled = evaluate_scoped_rules(["src/app.py"], rules=[{"id": "CULT01", "enabled": False}])
        self.assertTrue(res_disabled["isApproved"])

        # 3. String rule IDs
        res_str = evaluate_scoped_rules(["src/app.py"], rules=["CULT01", "CULT02"])
        self.assertIsInstance(res_str, dict)

    def test_resolve_scope_files_edge_cases(self):
        # 1. Scope subdirectory with invalid/non-existent target
        res1 = resolve_scope_files(str(REPO_ROOT), scope="subdirectory", target="nonexistent_folder_999")
        self.assertEqual(res1, [])

        # 2. Scope single_file with non-existent target
        res2 = resolve_scope_files(str(REPO_ROOT), scope="single_file", target="nonexistent_file_999.py")
        self.assertEqual(res2, [])

        # 3. Working tree diff exception
        with patch("subprocess.run", side_effect=Exception("Git error")):
            res3 = resolve_scope_files(str(REPO_ROOT), scope="working_tree_diff")
            self.assertEqual(res3, [])

    def test_build_vocabulary_partial_keys(self):
        # Only Presentation
        v1 = build_vocabulary_regexes({"layers": {"Presentation": {"tokens": {"t": ["div"]}}}})
        self.assertIn("Model", v1)

        # Only Interface_Transport
        v2 = build_vocabulary_regexes({"layers": {"Interface_Transport": {"tokens": {"t": ["req"]}}}})
        self.assertIn("Model", v2)

        # Only Infrastructure_Persistence
        v3 = build_vocabulary_regexes({"layers": {"Infrastructure_Persistence": {"tokens": {"t": ["db"]}}}})
        self.assertIn("View", v3)

    def test_handle_rules_cli_pragma_suppressed_and_import_warnings(self):
        # Test command with pragma suppression using a pattern rule
        reg = RuleRegistry.get_instance()
        r = RuleDefinition(
            id="CLI-SUPP-RULE",
            name="CLI Supp Rule",
            type=RuleType.PATTERN,
            condition=RuleCondition(pattern="forbidden_marker")
        )
        reg.register(r, persist=False)

        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            ret = handle_rules_cli(["test", "CLI-SUPP-RULE", "--code", "# @guardian-ignore CLI-SUPP-RULE: Suppressed for test\nforbidden_marker = 1\n"])
            self.assertEqual(ret, 0)
            self.assertIn("SUPPRESSED VIA PRAGMA", mock_out.getvalue())

        # Import command with warnings
        with tempfile.TemporaryDirectory() as tmp:
            tmp_p = Path(tmp)
            bad_json = tmp_p / "corrupt.json"
            bad_json.write_text("{invalid")
            with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
                ret2 = handle_rules_cli(["import", str(bad_json)])
                self.assertEqual(ret2, 0)
                self.assertIn("Warnings during import", mock_out.getvalue())

    def test_main_cli_directory_scan_and_scenario_no_report(self):
        # 1. Main with directory path
        with tempfile.TemporaryDirectory() as tmp:
            tmp_p = Path(tmp)
            d = tmp_p / "sub"
            d.mkdir()
            (d / "app.py").write_text("# @spec RF01\ndef run() -> int:\n    return 42\n")
            (d / "test_app.py").write_text("# @spec RF01\ndef test_run() -> None:\n    assert True\n")

            with patch("sys.argv", ["culture_guard.py", str(tmp_p), "--format=json"]):
                with self.assertRaises(SystemExit) as cm:
                    culture_guard.main()
                self.assertEqual(cm.exception.code, 0)

        # 2. Mock scenario without report
        with patch("sys.argv", ["culture_guard.py", "--mock-scenario=integration-error", "--format=text"]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
                with self.assertRaises(SystemExit) as cm:
                    culture_guard.main()
                self.assertEqual(cm.exception.code, 0)
                self.assertIn("MOCK SCENARIO", mock_out.getvalue())

    def test_guardian_server_audit_working_tree_empty_and_commit(self):
        # 1. Working tree audit with 0 changed files (clean)
        with patch("subprocess.run") as mock_sub:
            def side_effect_clean(cmd, **kwargs):
                if "--is-inside-work-tree" in cmd:
                    return MagicMock(stdout="true", returncode=0)
                elif "status" in cmd:
                    return MagicMock(stdout="", returncode=0)
                return MagicMock(stdout="", returncode=0)
            mock_sub.side_effect = side_effect_clean

            h = MockHttpHelper.create_handler("POST", "/api/audit", {
                "repoPath": str(REPO_ROOT),
                "targetType": "working_tree"
            })
            h.do_POST()
            res = MockHttpHelper.get_response_json(h)
            self.assertEqual(res.get("culture_score"), 100)
            self.assertEqual(res.get("total_files"), 0)

        # 2. Commit audit with commitSha
        with patch("subprocess.run") as mock_sub:
            def side_effect_commit(cmd, **kwargs):
                if "--is-inside-work-tree" in cmd:
                    return MagicMock(stdout="true", returncode=0)
                elif "show" in cmd:
                    return MagicMock(stdout="abc1234 commit title\nscripts/culture_guard.py\n", returncode=0)
                elif "culture_guard.py" in str(cmd):
                    return MagicMock(stdout=json.dumps({
                        "total_files": 1,
                        "total_violations": 0,
                        "total_suppressed": 0,
                        "has_blocking_violations": False,
                        "culture_score": 100,
                        "approved": True,
                        "files": []
                    }), returncode=0)
                return MagicMock(stdout="true", returncode=0)
            mock_sub.side_effect = side_effect_commit

            h2 = MockHttpHelper.create_handler("POST", "/api/audit", {
                "repoPath": str(REPO_ROOT),
                "targetType": "commit",
                "commitSha": "abc1234"
            })
            h2.do_POST()
            res2 = MockHttpHelper.get_response_json(h2)
            self.assertEqual(res2.get("culture_score"), 100)


if __name__ == "__main__":
    unittest.main()
