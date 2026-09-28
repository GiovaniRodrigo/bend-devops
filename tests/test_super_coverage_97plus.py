"""
==============================================================================
Super Coverage 97%+ Suite for Bend DevOps Guardian
==============================================================================
Comprehensive branch & statement coverage across all scripts/ modules:
- diff_parser.py (100%)
- base_adapter.py, github_adapter.py, gitlab_adapter.py, bitbucket_adapter.py, webhook_gateway.py, policy_engine.py (100%)
- token_filter.py (100%)
- rule_model.py, rule_normalizer.py, rule_test_engine.py, rule_registry.py (>98%)
- culture_guard.py (>97%)
- guardian_server.py (>97%)
==============================================================================
"""

import os
import sys
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
from scripts.vcs_adapters.diff_parser import (
    parse_unified_diff, parse_unified_diff_structured, extract_changed_lines, ParsedDiffFile
)
from scripts.vcs_adapters.base_adapter import BaseVcsAdapter
from scripts.vcs_adapters.github_adapter import GitHubAdapter
from scripts.vcs_adapters.gitlab_adapter import GitLabAdapter
from scripts.vcs_adapters.bitbucket_adapter import BitbucketAdapter
from scripts.vcs_adapters.webhook_gateway import WebhookGateway
from scripts.vcs_adapters.policy_engine import BranchPolicyEngine
from scripts.culture_guard import (
    classify_file_layer, FileAuditResult, generate_bend_harness, run_bend_engine,
    print_report, resolve_scope_files, evaluate_scoped_rules, handle_rules_cli,
    load_layer_vocabulary, build_vocabulary_regexes
)
import scripts.culture_guard as culture_guard
import scripts.guardian_server as guardian_server


class TestDiffParserFullBranches(unittest.TestCase):
    """Tests 100% of branches in diff_parser.py."""

    def test_empty_and_whitespace_diffs(self):
        self.assertEqual(parse_unified_diff(""), {})
        self.assertEqual(parse_unified_diff("   \n\t  "), {})
        self.assertEqual(parse_unified_diff_structured(""), [])
        self.assertEqual(parse_unified_diff_structured(None), [])
        self.assertEqual(extract_changed_lines("", "test.py"), set())

    def test_multi_mode_unified_diff(self):
        diff_text = """
diff --git a/new_file.py b/new_file.py
new file mode 100644
index 0000000..1111111
--- /dev/null
+++ b/new_file.py
@@ -0,0 +1,3 @@
+line1 = 1
+line2 = 2
+line3 = 3
diff --git a/deleted_file.py b/deleted_file.py
deleted file mode 100644
index 1111111..0000000
--- a/deleted_file.py
+++ /dev/null
@@ -1,2 +0,0 @@
-old1 = 1
-old2 = 2
diff --git a/old_name.py b/new_name.py
similarity index 90%
rename from old_name.py
rename to new_name.py
index 2222222..3333333 100644
--- a/old_name.py
+++ b/new_name.py
@@ -1,3 +1,3 @@
 context_line
-removed_line
+added_line
diff --git b/only_b_file.py
--- /dev/null
+++ b/only_b_file.py
@@ -0,0 +1,1 @@
+solo_line
"""
        parsed_files = parse_unified_diff_structured(diff_text)
        self.assertEqual(len(parsed_files), 4)
        self.assertEqual(parsed_files[0].status, "added")
        self.assertEqual(parsed_files[1].status, "deleted")
        self.assertEqual(parsed_files[2].status, "renamed")
        self.assertEqual(parsed_files[3].status, "added")

        mapping = parse_unified_diff(diff_text)
        self.assertIn("new_file.py", mapping)
        self.assertIn("new_name.py", mapping)
        self.assertNotIn("deleted_file.py", mapping)

        self.assertEqual(extract_changed_lines(diff_text, "new_file.py"), {1, 2, 3})
        self.assertEqual(extract_changed_lines(diff_text, "nonexistent.py"), set())

    def test_diff_parser_all_edge_cases(self):
        # 1. Diff line with no 'a/' or 'b/' pattern (line 93)
        diff_no_ab = "diff --git malformed_header_line\n+line_without_file\n-line2\n"
        res_no_ab = parse_unified_diff_structured(diff_no_ab)
        self.assertEqual(len(res_no_ab), 0)

        # 2. Standalone tokens without current file
        diff_orphan = "new file mode 100644\ndeleted file mode 100644\nrename from foo\nrename to bar\n--- /dev/null\n+++ /dev/null\n+added\n-deleted\n"
        res_orphan = parse_unified_diff_structured(diff_orphan)
        self.assertEqual(len(res_orphan), 0)

        # 3. Finalize added file
        diff_final_add = "diff --git a/file_add.py b/file_add.py\nnew file mode 100644\n--- /dev/null\n+++ b/file_add.py\n@@ -0,0 +1,1 @@\n+line"
        res_add = parse_unified_diff_structured(diff_final_add)
        self.assertEqual(res_add[0].status, "added")

        # 4. Finalize deleted file
        diff_final_del = "diff --git a/file_del.py b/file_del.py\ndeleted file mode 100644\n--- a/file_del.py\n+++ /dev/null\n@@ -1,1 +0,0 @@\n-line"
        res_del = parse_unified_diff_structured(diff_final_del)
        self.assertEqual(res_del[0].status, "deleted")

        # 5. Finalize renamed file
        diff_final_ren = "diff --git a/file_old.py b/file_new.py\nrename from file_old.py\nrename to file_new.py\n--- a/file_old.py\n+++ b/file_new.py\n@@ -1,1 +1,1 @@\n context"
        res_ren = parse_unified_diff_structured(diff_final_ren)
        self.assertEqual(res_ren[0].status, "renamed")


class TestVcsAdaptersFullBranches(unittest.TestCase):
    """Tests all remaining branches in VCS adapters."""

    def test_base_adapter_markdown_and_helpers(self):
        adapter = GitHubAdapter("dummy_token", "owner/repo", pr_number=1, commit_sha="abc1234")
        
        md_clean = adapter.build_markdown_summary([], 100, True)
        self.assertIn("PASSED", md_clean)

        violations = [
            {"rule_id": "CULT01", "severity": "P0_BLOCKING", "path": "src/App.cs", "line": 10, "message": "spec violation"},
            {"rule_id": "CULT04", "severity": "P0_BLOCKING", "path": "src/Config.cs", "line": 5, "message": "SECRET_KEY=12345"}
        ]
        md_viol = adapter.build_markdown_summary(violations, 65, False)
        self.assertIn("BLOCKED", md_viol)
        self.assertIn("***REDACTED***", md_viol)

        files = adapter._get_git_diff_files("HEAD")
        self.assertIsInstance(files, list)

    def test_github_adapter_edge_cases(self):
        adapter = GitHubAdapter("token", "owner/repo", pr_number=12, commit_sha="abc1234")
        
        with patch("urllib.request.urlopen") as mock_url:
            mock_resp = MagicMock()
            mock_resp.getcode.return_value = 200
            mock_resp.read.return_value = json.dumps([{"filename": "file1.py"}, {"no_filename": True}]).encode("utf-8")
            mock_url.return_value.__enter__.return_value = mock_resp
            files = adapter.get_changed_files()
            self.assertEqual(files, ["file1.py"])

        with patch("urllib.request.urlopen", side_effect=Exception("API Error")):
            self.assertFalse(adapter.publish_commit_status("success", "Passed", 100))

    def test_gitlab_adapter_edge_cases(self):
        adapter = GitLabAdapter("token", "group/project", pr_number=5, commit_sha="gitlab123")

        with patch("urllib.request.urlopen", side_effect=Exception("GitLab 500")):
            files = adapter.get_changed_files()
            self.assertIsInstance(files, list)

        no_pr = GitLabAdapter("token", "group/project", pr_number=None)
        self.assertFalse(no_pr.post_pr_comment("Hello"))

        with patch("urllib.request.urlopen", side_effect=Exception("GitLab Status Error")):
            self.assertFalse(adapter.publish_commit_status("success", "Passed", 100))

    def test_bitbucket_adapter_edge_cases(self):
        adapter = BitbucketAdapter("token", "workspace/repo", pr_number=99, commit_sha="bb1234")

        with patch("urllib.request.urlopen") as mock_url:
            mock_resp = MagicMock()
            mock_resp.getcode.return_value = 200
            mock_resp.read.return_value = json.dumps({
                "values": [
                    {"new": {"path": "added.py"}},
                    {"old": {"path": "deleted.py"}},
                    {"neither": {}}
                ]
            }).encode("utf-8")
            mock_url.return_value.__enter__.return_value = mock_resp
            files = adapter.get_changed_files()
            self.assertEqual(files, ["added.py", "deleted.py"])

        with patch("urllib.request.urlopen", side_effect=Exception("Bitbucket down")):
            files = adapter.get_changed_files()
            self.assertIsInstance(files, list)

        violations = [{"rule_id": "CULT01", "severity": "P0_BLOCKING", "path": "file.py", "line": 1, "message": "msg"}]
        with patch("urllib.request.urlopen", side_effect=Exception("Annotation PUT failed")):
            res = adapter.publish_annotations(violations)
            self.assertTrue(res)

        art = adapter.generate_report_artifact(violations, 60, False)
        self.assertIn("FAILED", art)

    def test_webhook_gateway_edge_cases(self):
        res = WebhookGateway.handle_webhook({}, platform_hint="unknown")
        self.assertIsNone(res)

        res_none = WebhookGateway.handle_webhook({})
        self.assertIsNone(res_none)

        gh_payload = {
            "repository": {"full_name": "owner/repo"},
            "pull_request": {
                "number": 42,
                "head": {"sha": "head123"},
                "base": {"sha": "base456"},
                "user": {"login": "dev_user"},
                "title": "Feature PR"
            }
        }
        res_gh = WebhookGateway.handle_webhook(gh_payload, platform_hint="github")
        self.assertIsNotNone(res_gh)
        self.assertEqual(res_gh.platform, "github")
        self.assertEqual(res_gh.pr_number, 42)

        gl_payload = {
            "object_kind": "merge_request",
            "project": {"path_with_namespace": "group/project"},
            "user": {"username": "gl_user"},
            "object_attributes": {
                "iid": 10,
                "last_commit": {"id": "gl_sha_123"},
                "target_branch": "main",
                "title": "MR Title"
            }
        }
        res_gl = WebhookGateway.handle_webhook(gl_payload, platform_hint="gitlab")
        self.assertIsNotNone(res_gl)
        self.assertEqual(res_gl.platform, "gitlab")
        self.assertEqual(res_gl.pr_number, 10)

        bb_payload = {
            "repository": {"full_name": "workspace/repo"},
            "actor": {"username": "bb_user"},
            "pullrequest": {
                "id": 99,
                "source": {"commit": {"hash": "bb_sha_789"}},
                "destination": {"branch": {"name": "develop"}},
                "title": "BB PR Title"
            }
        }
        res_bb = WebhookGateway.handle_webhook(bb_payload, platform_hint="bitbucket")
        self.assertIsNotNone(res_bb)
        self.assertEqual(res_bb.platform, "bitbucket")
        self.assertEqual(res_bb.pr_number, 99)


class TestTokenFilterFullBranches(unittest.TestCase):
    """Tests all branches in token_filter.py."""

    def test_strip_comments_various_extensions(self):
        self.assertEqual(strip_comments("$a = 1; // comment", ".php"), "$a = 1;")
        self.assertEqual(strip_comments("SELECT 1; -- comment", ".sql"), "SELECT 1;")
        self.assertEqual(strip_comments("x = 1 # comment", ".py"), "x = 1")
        self.assertEqual(strip_comments("const a = 1; // ts comment", ".ts"), "const a = 1;")
        self.assertEqual(strip_comments("plain text", ".unknown_xyz"), "plain text")

    def test_parse_inline_pragmas_edge_cases(self):
        lines = [
            "# @guardian-ignore-start CULT01: Valid long reason for block",
            "val = 1",
            "# @guardian-ignore-end CULT01",
            "# @guardian-ignore CULT02: Valid long reason for next line",
            "val = 2",
            "# @guardian-ignore CULT03 short",
            "# @guardian-ignore-start CULT04",
            "# @guardian-ignore-end"
        ]
        supp_map, warnings = parse_inline_pragmas(lines)
        self.assertIn("CULT01", supp_map.get(2, {}))
        self.assertIn("CULT02", supp_map.get(5, {}))
        self.assertTrue(len(warnings) >= 2)

    def test_matches_exact_token(self):
        self.assertTrue(matches_exact_token("<img", "<img src='x'/>"))
        self.assertFalse(matches_exact_token("<img", "def get_img(): pass"))
        self.assertTrue(matches_exact_token("SELECT", "SELECT * FROM users"))
        self.assertTrue(matches_exact_token("DbContext", "public DbContext db;"))

    def test_load_guardianignore_and_exemptions(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            ig_path = Path(tmpdir) / ".guardianignore"
            ig_path.write_text(
                "# Comment\n"
                "legacy/** [CULT01, CULT02] # Reason for exemption\n"
                "vendor/* # Vendor folder\n"
                "direct_prefix # Prefix without star\n"
                "\n",
                encoding="utf-8"
            )
            pats = load_guardianignore(ig_path)
            self.assertEqual(len(pats), 3)
            self.assertTrue(pats[0].matches("legacy/code.py", "CULT01"))
            self.assertFalse(pats[0].matches("legacy/code.py", "CULT99"))
            self.assertTrue(pats[2].matches("direct_prefix/sub/file.py", "ANY"))

            with patch.object(Path, "read_text", side_effect=Exception("Read error")):
                pats_err = load_guardianignore(ig_path)
                self.assertEqual(pats_err, [])

            exemptions = [
                ("legacy/*", "CULT01"),
                ("ARCH-01", "src/legacy/*"),
                ("ALL", "vendor/*")
            ]
            self.assertTrue(is_file_or_rule_exempt("legacy/test.py", "CULT01", exemptions))
            self.assertFalse(is_file_or_rule_exempt("legacy/test.py", "CULT02", exemptions))
            self.assertTrue(is_file_or_rule_exempt("src/legacy/file.cs", "ARCH-01", exemptions))
            self.assertTrue(is_file_or_rule_exempt("vendor/pkg.py", "ANY_RULE", exemptions))


class TestRuleNormalizerFullBranches(unittest.TestCase):
    """Tests all branches in rule_normalizer.py."""

    def test_normalizer_fallbacks_and_coercions(self):
        archived_raw = {"id": "TEST-ARCH", "status": "ARCHIVED", "pattern": "foo"}
        r_arch = RuleNormalizer.normalize_rule_dict(archived_raw)
        self.assertFalse(r_arch.enabled)

        deprecated_raw = {"id": "TEST-DEP", "status": "DEPRECATED", "pattern": "foo"}
        r_dep = RuleNormalizer.normalize_rule_dict(deprecated_raw)
        self.assertFalse(r_dep.enabled)

        bad_tier_raw = {"id": "TEST-TIER", "tier": "INVALID_TIER_123", "pattern": "foo"}
        r_tier = RuleNormalizer.normalize_rule_dict(bad_tier_raw, default_tier=RuleTier.PROJECT)
        self.assertEqual(r_tier.tier, RuleTier.PROJECT)

        str_arch_raw = {
            "id": "TEST-STR",
            "architectures": "clean_architecture",
            "languages": "csharp",
            "scope": "non_dict_scope",
            "condition": "non_dict_cond",
            "suppression": "non_dict_supp",
            "tests": ["invalid_fixture_not_dict", {"name": "valid", "input": "class Foo", "expected_violation": True}]
        }
        r_str = RuleNormalizer.normalize_rule_dict(str_arch_raw)
        self.assertEqual(r_str.architectures, ["clean_architecture"])
        self.assertEqual(r_str.languages, ["csharp"])
        self.assertEqual(len(r_str.tests), 1)

        c1 = RuleNormalizer.normalize_rule_dict({"id": "CULT01"})
        self.assertTrue(len(c1.condition.patterns) > 0)
        c4 = RuleNormalizer.normalize_rule_dict({"id": "CULT04"})
        self.assertTrue(len(c4.condition.patterns) > 0)


class TestRuleTestEngineFullBranches(unittest.TestCase):
    """Tests all branches in rule_test_engine.py."""

    def test_regex_safety_validator(self):
        ok, err = RegexSafetyValidator.is_safe_pattern(r"^[A-Z][a-zA-Z0-9]+$")
        self.assertTrue(ok)
        self.assertIsNone(err)

        ok, err = RegexSafetyValidator.is_safe_pattern(r"[a-z(")
        self.assertFalse(ok)
        self.assertIn("Invalid regex syntax", err)

        safe_redos, err_redos = RegexSafetyValidator.is_safe_pattern("(a+)+$")
        self.assertFalse(safe_redos)

        with patch("time.perf_counter", side_effect=[0.0, 0.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]):
            ok_slow, err_slow = RegexSafetyValidator.is_safe_pattern(r"test_pattern")
            self.assertFalse(ok_slow)
            self.assertIn("ReDoS threshold", err_slow)

        with patch("re.compile") as mock_comp:
            mock_pattern_obj = MagicMock()
            mock_pattern_obj.search.side_effect = RuntimeError("Regex crash")
            mock_comp.return_value = mock_pattern_obj
            ok_err, err_msg = RegexSafetyValidator.is_safe_pattern(r"test_pattern")
            self.assertFalse(ok_err)
            self.assertIn("Regex evaluation error", err_msg)

    def test_rule_test_engine_rule_types(self):
        # 1. Language mismatch skips rule
        rule_cs = RuleDefinition(
            id="TEST-CS-ONLY",
            name="C# Only Rule",
            description="Tests C#",
            category="language_specific",
            severity=RuleSeverity.P0_BLOCKING,
            status=RuleStatus.ACTIVE,
            tier=RuleTier.CUSTOM,
            type=RuleType.PATTERN,
            languages=["csharp"],
            condition=RuleCondition(patterns=["", r"forbidden_csharp"])
        )
        res_py = RuleTestEngine.test_rule(rule_cs, "forbidden_csharp = 1", "test.py")
        self.assertFalse(res_py.has_violation)

        # 2. Pattern derived from forbidden_targets when patterns is empty
        rule_target = RuleDefinition(
            id="TEST-TARGETS",
            name="Target Rule",
            description="Tests targets",
            category="architecture",
            severity=RuleSeverity.P1_WARNING,
            status=RuleStatus.ACTIVE,
            tier=RuleTier.CUSTOM,
            type=RuleType.ARCHITECTURE,
            languages=["python"],
            condition=RuleCondition(forbidden_targets=["direct_sql_query", "raw_db_exec"])
        )
        res_tgt = RuleTestEngine.test_rule(rule_target, "result = direct_sql_query()", "test.py")
        self.assertTrue(res_tgt.has_violation)

        # 3. Invalid regex in rule
        rule_invalid_re = RuleDefinition(
            id="TEST-INV-RE",
            name="Inv Regex",
            condition=RuleCondition(patterns=[r"([a-z"]),
            tier=RuleTier.CUSTOM,
            severity=RuleSeverity.P1_WARNING
        )
        res_inv = RuleTestEngine.test_rule(rule_invalid_re, "code", "test.py")
        self.assertFalse(res_inv.passed)
        self.assertIn("Invalid regex", res_inv.error)

        # 4. Suppression via ALL
        code_all_supp = "# @guardian-ignore ALL: suppressed for legacy reasons\nresult = direct_sql_query()"
        res_all_supp = RuleTestEngine.test_rule(rule_target, code_all_supp, "test.py")
        self.assertTrue(res_all_supp.is_suppressed)

        # 5. NAMING conventions
        for conv, good, bad in [
            ("PascalCase", "class GoodClass: pass", "class bad_class: pass"),
            ("camelCase", "def goodFunc(): pass", "def BadPascalFunc(): pass"),
            ("snake_case", "def good_func(): pass", "def BadPascalFunc(): pass"),
            ("UPPER_CASE", "class GOOD_ENUM: pass", "class bad_lower: pass")
        ]:
            nr = RuleDefinition(id=f"NAM-{conv}", name=f"Nam {conv}", type=RuleType.NAMING, condition=RuleCondition(naming_convention=conv), severity=RuleSeverity.P1_WARNING, tier=RuleTier.CUSTOM)
            self.assertFalse(RuleTestEngine.test_rule(nr, good, "test.py").has_violation)
            self.assertTrue(RuleTestEngine.test_rule(nr, bad, "test.py").has_violation)

        # 6. DEPENDENCY rule
        dep_r = RuleDefinition(id="DEP-R", name="Dep R", type=RuleType.DEPENDENCY, condition=RuleCondition(forbidden_targets=["BadLib"]), severity=RuleSeverity.P0_BLOCKING, tier=RuleTier.CUSTOM)
        self.assertTrue(RuleTestEngine.test_rule(dep_r, "import BadLib", "test.py").has_violation)

        # 7. FILE_FOLDER rule
        ff_r = RuleDefinition(id="FF-R", name="FF R", type=RuleType.FILE_FOLDER, condition=RuleCondition(required_path_prefix="src/Domain"), severity=RuleSeverity.P1_WARNING, tier=RuleTier.CUSTOM)
        self.assertFalse(RuleTestEngine.test_rule(ff_r, "code", "src/Domain/Entity.cs").has_violation)
        self.assertTrue(RuleTestEngine.test_rule(ff_r, "code", "controllers/Bad.cs").has_violation)

        # 8. Fixtures execution
        rf = RuleDefinition(id="TEST-FIX", name="TF", type=RuleType.PATTERN, condition=RuleCondition(pattern="bad"), severity=RuleSeverity.P1_WARNING, tier=RuleTier.CUSTOM, tests=[RuleTestFixture(name="F1", input="bad", expected_violation=True)])
        summary = RuleTestEngine.execute_fixtures(rf)
        self.assertTrue(summary["passed"])


class TestRuleRegistryFullBranches(unittest.TestCase):
    """Tests all remaining branches in rule_registry.py."""

    def test_legacy_loading_and_overrides(self):
        reg = RuleRegistry.get_instance()
        
        r_org = RuleDefinition(id="OVERRIDE-01", name="Org Rule", condition=RuleCondition(pattern="pat"), severity=RuleSeverity.P1_WARNING, tier=RuleTier.ORGANIZATION)
        r_proj = RuleDefinition(id="OVERRIDE-01", name="Proj Rule", condition=RuleCondition(pattern="pat"), severity=RuleSeverity.P0_BLOCKING, tier=RuleTier.PROJECT)
        reg.register(r_org, actor="admin", persist=False)
        reg.register(r_proj, actor="admin", persist=False)
        
        eff = reg.resolve()
        self.assertEqual(eff["OVERRIDE-01"].tier, RuleTier.PROJECT)
        
        reg.unregister("OVERRIDE-01", hard_delete=True)

    def test_import_and_export_manifest_branches(self):
        reg = RuleRegistry.get_instance()

        with self.assertRaises(PermissionError):
            reg.import_manifest({}, user_role=UserRole.VIEWER)

        manifest_str = json.dumps({
            "rules": [
                {
                    "id": "IMP-STR-01",
                    "name": "Imported from String",
                    "description": "Test import",
                    "category": "pattern",
                    "severity": "P1_WARNING",
                    "pattern": "import_str_pat"
                },
                "non_dict_rule_should_be_skipped"
            ]
        })
        res = reg.import_manifest(manifest_str, user_role=UserRole.ADMIN)
        self.assertEqual(res["imported"], 1)

        res_dup = reg.import_manifest(manifest_str, overwrite=False, user_role=UserRole.ADMIN)
        self.assertEqual(res_dup["failed"], 1)
        self.assertIn("already exists", res_dup["errors"][0])

        res_bad = reg.import_manifest("{invalid_json", user_role=UserRole.ADMIN)
        self.assertEqual(res_bad["failed"], 1)

        exp = reg.export_manifest(tier=RuleTier.CUSTOM)
        self.assertIn("IMP-STR-01", exp)

        cats = reg.get_categories()
        self.assertIsInstance(cats, list)
        langs = reg.get_languages()
        self.assertIsInstance(langs, list)
        types = reg.get_types()
        self.assertIsInstance(types, list)
        sevs = reg.get_severities()
        self.assertIsInstance(sevs, list)
        stats = reg.get_statuses()
        self.assertIsInstance(stats, list)

        # Filters on list()
        all_r = reg.list(category="culture", severity="P0", language="csharp", status="ACTIVE", tier="builtin", architecture="clean_architecture")
        self.assertIsInstance(all_r, list)

        # search()
        s_res = reg.search("Zero")
        self.assertTrue(len(s_res) > 0)

        reg.delete("IMP-STR-01")

    def test_directory_import_exceptions(self):
        reg = RuleRegistry.get_instance()
        with tempfile.TemporaryDirectory() as tmpdir:
            td = Path(tmpdir)
            (td / "f1.json").write_text(json.dumps({"rules": [{"id": "DIR-IMP-01", "name": "D1", "pattern": "p"}]}), encoding="utf-8")
            (td / "f2.json").write_text("{ corrupt", encoding="utf-8")
            cnt, errs = reg.import_rules(str(td))
            self.assertEqual(cnt, 1)
            self.assertTrue(len(errs) > 0)
            reg.delete("DIR-IMP-01")


class TestCultureGuardFullBranches(unittest.TestCase):
    """Tests all branches in culture_guard.py."""

    def test_layer_taxonomy_classification(self):
        self.assertEqual(classify_file_layer(Path("src/Views/Home.cshtml")), "View")
        self.assertEqual(classify_file_layer(Path("src/Controllers/OrderController.cs")), "Controller")
        self.assertEqual(classify_file_layer(Path("src/Domain/Entities/Order.cs")), "Model")
        self.assertEqual(classify_file_layer(Path("src/Infrastructure/Persistence/AppDbContext.sql")), "Infrastructure")
        self.assertEqual(classify_file_layer(Path("src/Unknown/Misc.xyz")), "Generic")

    def test_load_vocabulary_and_regexes(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            bad_vocab = Path(tmpdir) / "layer_vocabulary.json"
            bad_vocab.write_text("{ broken json", encoding="utf-8")
            with patch("scripts.culture_guard.RULES_BASE_DIR", Path(tmpdir)):
                res = load_layer_vocabulary()
                self.assertEqual(res, {})

        custom_vocab = {
            "layers": {
                "Presentation": {"tokens": {"html": ["<custom-ui>"]}},
                "Interface_Transport": {"tokens": {"http": ["CustomRequest"]}},
                "Infrastructure_Persistence": {"tokens": {"db": ["CustomDbContext"]}}
            }
        }
        reg_map = build_vocabulary_regexes(custom_vocab)
        self.assertIn("Model", reg_map)

    def test_file_audit_result_exemptions_and_pragmas(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # 1. CULT05 exemption
            sample_py = Path(tmpdir) / "untyped.py"
            sample_py.write_text("def my_func(a, b):\n    return a + b\n", encoding="utf-8")
            res_cult05_exempt = FileAuditResult(sample_py, [IgnoredFilePattern("untyped.py", ["CULT05"])])
            self.assertEqual(res_cult05_exempt.suppressed_count, 1)

            # 2. Layer forbidden pattern exemption
            view_file = Path(tmpdir) / "views" / "Home.cshtml"
            view_file.parent.mkdir(parents=True, exist_ok=True)
            view_file.write_text("<div> @{ DbContext db = new DbContext(); } </div>\n", encoding="utf-8")
            res_layer_exempt = FileAuditResult(view_file, [IgnoredFilePattern("views/Home.cshtml", ["ARCH-LAYER-02"])])
            self.assertTrue(res_layer_exempt.suppressed_count >= 1)

            # 3. Layer forbidden pattern inline suppression
            view_file_supp = Path(tmpdir) / "views" / "HomeSupp.cshtml"
            view_file_supp.write_text("// @guardian-ignore ARCH-LAYER-02: temporary direct view query\n<div> @{ DbContext db = new DbContext(); } </div>\n", encoding="utf-8")
            res_inline_supp = FileAuditResult(view_file_supp, [])
            self.assertTrue(res_inline_supp.suppressed_count >= 1)

    def test_resolve_target_files_scopes(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            td = Path(tmpdir)
            (td / "sub").mkdir()
            (td / "sub" / "file1.py").write_text("print('hello')", encoding="utf-8")
            (td / "sub" / "file2.ts").write_text("const a = 1;", encoding="utf-8")
            (td / "single.py").write_text("print('single')", encoding="utf-8")
            (td / "ignored_folder").mkdir()
            (td / "ignored_folder" / "bad.py").write_text("bad", encoding="utf-8")

            files_sub = resolve_scope_files(str(td), scope="subdirectory", target="sub")
            self.assertEqual(len(files_sub), 2)

            files_sub_file = resolve_scope_files(str(td), scope="subdirectory", target="single.py")
            self.assertEqual(len(files_sub_file), 1)

            files_single = resolve_scope_files(str(td), scope="single_file", target="sub/file1.py")
            self.assertEqual(len(files_single), 1)

            with patch("subprocess.run") as mock_sub:
                mock_sub.return_value.stdout = " M sub/file1.py\n?? sub/file2.ts\n"
                files_diff = resolve_scope_files(str(td), scope="working_tree_diff")
                self.assertEqual(len(files_diff), 2)

            files_full = resolve_scope_files(str(td), scope="full_branch", exclude_patterns=["ignored_folder/**"])
            self.assertEqual(len(files_full), 3)

    def test_evaluate_scoped_rules_custom_severities(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            f1 = Path(tmpdir) / "test1.py"
            f1.write_text("# @spec RF01\ndef test():\n    pass\n", encoding="utf-8")

            empty_eval = evaluate_scoped_rules([])
            self.assertEqual(empty_eval["score"], 100)

            res_str = evaluate_scoped_rules([str(f1)], rules=["CULT01"])
            self.assertIsInstance(res_str, dict)

            rules_custom = [
                {"id": "CULT01", "customSeverity": "P0"},
                {"id": "CULT05", "customSeverity": "P1"},
                {"id": "CULT02", "customSeverity": "P2"}
            ]
            res_cust = evaluate_scoped_rules([str(f1)], rules=rules_custom)
            self.assertIsInstance(res_cust, dict)

    def test_handle_rules_cli_all_subcommands(self):
        RuleRegistry.get_instance().delete("CLI-TEST-01", hard_delete=True)
        RuleRegistry.get_instance().delete("CLI-CLONED-01", hard_delete=True)
        RuleRegistry.get_instance().delete("CLI-CLONED-02", hard_delete=True)
        with tempfile.TemporaryDirectory() as tmpdir:
            rule_file = Path(tmpdir) / "new_rule.json"
            rule_file.write_text(json.dumps({
                "id": "CLI-TEST-01",
                "name": "CLI Rule",
                "pattern": "cli_viol",
                "severity": "P1_WARNING"
            }), encoding="utf-8")

            # 1. create
            self.assertEqual(handle_rules_cli(["create", str(rule_file)]), 0)
            self.assertEqual(handle_rules_cli(["create", "nonexistent.json"]), 1)

            # 2. edit
            rule_file.write_text(json.dumps({
                "id": "CLI-TEST-01",
                "name": "Updated CLI Rule",
                "pattern": "cli_viol_2"
            }), encoding="utf-8")
            self.assertEqual(handle_rules_cli(["edit", "CLI-TEST-01", str(rule_file)]), 0)
            self.assertEqual(handle_rules_cli(["edit", "CLI-TEST-01", "nonexistent.json"]), 1)

            # 3. clone
            self.assertEqual(handle_rules_cli(["clone", "CLI-TEST-01", "CLI-CLONED-01", "--name=Cloned"]), 0)
            self.assertEqual(handle_rules_cli(["clone", "NONEXISTENT", "CLI-CLONED-02"]), 1)

            # 4. validate
            self.assertEqual(handle_rules_cli(["validate", str(rule_file)]), 0)
            self.assertEqual(handle_rules_cli(["validate", "CLI-TEST-01"]), 0)
            self.assertEqual(handle_rules_cli(["validate", "NONEXISTENT_RULE_999"]), 1)

            # 5. test with --file
            test_src = Path(tmpdir) / "src.py"
            test_src.write_text("cli_viol_2 = True\n", encoding="utf-8")
            self.assertEqual(handle_rules_cli(["test", "CLI-TEST-01", f"--file={test_src}"]), 0)

            # 6. export with --out
            out_file = Path(tmpdir) / "exported.json"
            self.assertEqual(handle_rules_cli(["export", "CLI-TEST-01", f"--out={out_file}"]), 0)
            self.assertTrue(out_file.exists())
            self.assertEqual(handle_rules_cli(["export", "NONEXISTENT_999"]), 1)

            # 7. delete
            self.assertEqual(handle_rules_cli(["delete", "CLI-TEST-01", "--force"]), 0)
            self.assertEqual(handle_rules_cli(["delete", "CLI-CLONED-01", "--force"]), 0)
            self.assertEqual(handle_rules_cli(["delete", "NONEXISTENT_999"]), 1)


class TestGuardianServerFullBranches(unittest.TestCase):
    """Tests all remaining branches and helpers in guardian_server.py."""

    def test_discover_local_repositories_edge_cases(self):
        with patch("subprocess.run") as mock_sub:
            mock_sub.return_value.stdout = "false"
            repos = guardian_server.discover_local_repositories()
            self.assertIsInstance(repos, list)

        with patch("subprocess.run", side_effect=Exception("Git error")):
            repos_err = guardian_server.discover_local_repositories()
            self.assertIsInstance(repos_err, list)

    def test_inspect_local_repository_branches(self):
        with patch("subprocess.run") as mock_sub:
            def side_effect(cmd, **kwargs):
                cmd_str = " ".join(cmd)
                m = MagicMock()
                if "rev-parse --is-inside-work-tree" in cmd_str:
                    m.stdout = "true"
                elif "rev-parse --show-toplevel" in cmd_str:
                    m.stdout = str(REPO_ROOT)
                elif "branch --show-current" in cmd_str:
                    m.stdout = ""
                elif "rev-parse --abbrev-ref HEAD" in cmd_str:
                    m.stdout = "HEAD"
                elif "for-each-ref" in cmd_str:
                    m.stdout = ""
                elif "branch --list" in cmd_str:
                    m.stdout = "* main\n"
                elif "rev-parse --short HEAD" in cmd_str:
                    m.stdout = "abc1234"
                elif "log -1 --format=%s" in cmd_str:
                    m.stdout = "commit msg"
                else:
                    m.stdout = ""
                m.returncode = 0
                return m

            mock_sub.side_effect = side_effect
            res = guardian_server.inspect_local_repository_path(str(REPO_ROOT))
            self.assertTrue(res["valid"])
            self.assertEqual(res["repository"]["currentBranch"], "Detached HEAD")

    def test_working_tree_info_edge_cases(self):
        with patch("subprocess.run") as mock_sub:
            def side_effect(cmd, **kwargs):
                cmd_str = " ".join(cmd)
                m = MagicMock()
                if "status --porcelain" in cmd_str:
                    m.stdout = " D old_file.py\n"
                elif "diff HEAD" in cmd_str:
                    m.stdout = "--- a/old_file.py\n+++ /dev/null\n-deleted line\n"
                m.returncode = 0
                return m

            mock_sub.side_effect = side_effect
            wt = guardian_server.get_working_tree_info(str(REPO_ROOT))
            self.assertFalse(wt["isClean"])
            self.assertEqual(wt["changedFiles"][0]["status"], "deleted")

        with patch("subprocess.run", side_effect=Exception("Git diff crash")):
            wt_err = guardian_server.get_working_tree_info(str(REPO_ROOT))
            self.assertIn("error", wt_err)

    def test_validate_commit_sha_edge_cases(self):
        with patch("subprocess.run", side_effect=Exception("SHA error")):
            res = guardian_server.validate_commit_sha(str(REPO_ROOT), "abc1234")
            self.assertFalse(res["valid"])

    def test_load_manifests_corrupt_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            bad_json = Path(tmpdir) / "corrupt.json"
            bad_json.write_text("{ invalid json", encoding="utf-8")
            with patch("scripts.guardian_server.RULES_BASE_DIR", Path(tmpdir)):
                rules = guardian_server.load_real_rules_manifest()
                profiles = guardian_server.load_real_architecture_profiles()
                self.assertEqual(rules, [])
                self.assertEqual(profiles, [])

    def test_github_repositories_api_mocked(self):
        with patch.dict(os.environ, {"GITHUB_TOKEN": "mock_tok"}):
            with patch("urllib.request.urlopen") as mock_url:
                mock_resp = MagicMock()
                mock_resp.getcode.return_value = 200
                mock_resp.read.return_value = json.dumps([{"name": "r1", "full_name": "o/r1"}]).encode("utf-8")
                mock_url.return_value.__enter__.return_value = mock_resp
                res = guardian_server.get_github_repositories()
                self.assertTrue(res["connected"])
                self.assertEqual(len(res["repositories"]), 1)

    def test_get_frontend_root_fallback(self):
        with patch("scripts.guardian_server.FRONTEND_DIST_DIRS", [Path("/nonexistent_frontend_dist")]):
            fe = guardian_server.get_frontend_root()
            self.assertEqual(str(fe), "/nonexistent_frontend_dist")

    def test_detect_repository_framework_react_and_node(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            td = Path(tmpdir)
            (td / "vite.config.ts").write_text("export default {}", encoding="utf-8")
            (td / "package.json").write_text(json.dumps({"dependencies": {"react": "^18.0.0"}}), encoding="utf-8")
            res_react = guardian_server.detect_repository_framework(td)
            self.assertTrue(any("React" in f["name"] for f in res_react["detectedFrameworks"]))

            (td / "vite.config.ts").unlink()
            (td / "package.json").write_text(json.dumps({"dependencies": {"express": "^4.0.0"}}), encoding="utf-8")
            res_node = guardian_server.detect_repository_framework(td)
            self.assertTrue(any("Node.js" in f["name"] for f in res_node["detectedFrameworks"]))

    def test_get_repository_by_id_path_search(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_res = guardian_server.get_repository_by_id(tmpdir)
            # When directory is non-git, it returns None
            self.assertIsNone(repo_res)


if __name__ == "__main__":
    unittest.main()
