"""
==============================================================================
Deep Branch Coverage Test Suite for Bend DevOps Guardian
==============================================================================
Directly targets every single remaining branch to achieve >97% overall coverage.
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

import scripts.guardian_server as guardian_server
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
from scripts.token_filter import TokenFilter, IgnoredFilePattern, parse_inline_pragmas, load_guardianignore, is_file_or_rule_exempt


class MockHttpHelper(GuardianRequestHandler):
    def __init__(self, method="GET", path="/", body=None, headers=None):
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


class TestDeepBranches(unittest.TestCase):
    """Executes all remaining branches across all modules."""

    def test_guardian_server_audit_branch_coverage(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            p_repo = Path(tmpdir)
            (p_repo / "src").mkdir()
            sample_f = p_repo / "src" / "Entity.cs"
            sample_f.write_text("public class Entity {}\n", encoding="utf-8")

            # 1. target_type="branch" with git diff returning files
            h1 = MockHttpHelper(method="POST", path="/api/audit", body={
                "path": str(p_repo),
                "targetType": "branch",
                "branch": "feature/1",
                "baseBranch": "main"
            })
            with patch("subprocess.run") as mock_sub:
                def fake_sub(cmd, **kwargs):
                    m = MagicMock()
                    cmd_str = " ".join(cmd)
                    if "rev-parse --is-inside-work-tree" in cmd_str:
                        m.returncode = 0
                        m.stdout = "true"
                    elif "diff --name-only" in cmd_str:
                        m.returncode = 0
                        m.stdout = "src/Entity.cs\n"
                    elif "culture_guard.py" in cmd_str:
                        m.returncode = 0
                        m.stdout = json.dumps({
                            "files": [{"path": str(sample_f), "violations": [{"rule_id": "CULT01", "severity": "P0_BLOCKING", "penalty": 35}]}]
                        })
                    else:
                        m.returncode = 0
                        m.stdout = ""
                    return m
                mock_sub.side_effect = fake_sub
                h1.do_POST()
                self.assertEqual(h1.response_code, 200)

            # 2. target_type="branch" with empty diff -> approved=True 200
            h2 = MockHttpHelper(method="POST", path="/api/audit", body={
                "path": str(p_repo),
                "targetType": "branch",
                "branch": "feature/1",
                "baseBranch": "main"
            })
            with patch("subprocess.run") as mock_sub:
                def fake_sub2(cmd, **kwargs):
                    m = MagicMock()
                    cmd_str = " ".join(cmd)
                    if "rev-parse --is-inside-work-tree" in cmd_str:
                        m.returncode = 0
                        m.stdout = "true"
                    elif "diff --name-only" in cmd_str:
                        m.returncode = 0
                        m.stdout = ""
                    return m
                mock_sub.side_effect = fake_sub2
                h2.do_POST()
                self.assertEqual(h2.response_code, 200)

            # 3. target_type="working_tree" with dirty status
            h3 = MockHttpHelper(method="POST", path="/api/audit", body={
                "path": str(p_repo),
                "targetType": "working_tree"
            })
            with patch("subprocess.run") as mock_sub:
                def fake_sub3(cmd, **kwargs):
                    m = MagicMock()
                    cmd_str = " ".join(cmd)
                    if "rev-parse --is-inside-work-tree" in cmd_str:
                        m.returncode = 0
                        m.stdout = "true"
                    elif "status --porcelain" in cmd_str:
                        m.returncode = 0
                        m.stdout = " M src/Entity.cs\n"
                    elif "culture_guard.py" in cmd_str:
                        m.returncode = 0
                        m.stdout = json.dumps({
                            "files": [{"path": str(sample_f), "violations": [{"rule_id": "CULT05", "severity": "P1_WARNING", "penalty": 10}]}]
                        })
                    return m
                mock_sub.side_effect = fake_sub3
                h3.do_POST()
                self.assertEqual(h3.response_code, 200)

            # 4. target_type="commit" with commitSha
            h4 = MockHttpHelper(method="POST", path="/api/audit", body={
                "path": str(p_repo),
                "targetType": "commit",
                "commitSha": "abc1234"
            })
            with patch("subprocess.run") as mock_sub:
                def fake_sub4(cmd, **kwargs):
                    m = MagicMock()
                    cmd_str = " ".join(cmd)
                    if "rev-parse --is-inside-work-tree" in cmd_str:
                        m.returncode = 0
                        m.stdout = "true"
                    elif "show --name-only" in cmd_str:
                        m.returncode = 0
                        m.stdout = "abc1234 commit message\nsrc/Entity.cs\n"
                    elif "culture_guard.py" in cmd_str:
                        m.returncode = 0
                        m.stdout = json.dumps({
                            "files": [{"path": str(sample_f), "violations": []}]
                        })
                    return m
                mock_sub.side_effect = fake_sub4
                h4.do_POST()
                self.assertEqual(h4.response_code, 200)

            # 5. rules_filter == [] with files_to_audit
            h5 = MockHttpHelper(method="POST", path="/api/audit", body={
                "path": str(p_repo),
                "targetType": "branch",
                "branch": "feature/1",
                "baseBranch": "main",
                "rules": []
            })
            with patch("subprocess.run") as mock_sub:
                def fake_sub5(cmd, **kwargs):
                    m = MagicMock()
                    cmd_str = " ".join(cmd)
                    if "rev-parse --is-inside-work-tree" in cmd_str:
                        m.returncode = 0
                        m.stdout = "true"
                    elif "diff --name-only" in cmd_str:
                        m.returncode = 0
                        m.stdout = "src/Entity.cs\n"
                    return m
                mock_sub.side_effect = fake_sub5
                h5.do_POST()
                self.assertEqual(h5.response_code, 200)

            # 6. Audit allowed_rules filtering with P0 and P1
            h6 = MockHttpHelper(method="POST", path="/api/audit", body={
                "path": str(p_repo),
                "targetType": "full_repo",
                "rules": ["CULT01", "CULT05"]
            })
            with patch("subprocess.run") as mock_sub:
                def fake_sub6(cmd, **kwargs):
                    m = MagicMock()
                    cmd_str = " ".join(cmd)
                    if "rev-parse --is-inside-work-tree" in cmd_str:
                        m.returncode = 0
                        m.stdout = "true"
                    elif "culture_guard.py" in cmd_str:
                        m.returncode = 0
                        m.stdout = json.dumps({
                            "files": [
                                {
                                    "path": str(sample_f),
                                    "violations": [
                                        {"rule_id": "CULT01", "severity": "P0_BLOCKING", "penalty": 35},
                                        {"rule_id": "CULT05", "severity": "P1_WARNING", "penalty": 10},
                                        {"rule_id": "IGNORED_RULE", "severity": "P0_BLOCKING", "penalty": 35}
                                    ]
                                }
                            ]
                        })
                    return m
                mock_sub.side_effect = fake_sub6
                h6.do_POST()
                self.assertEqual(h6.response_code, 200)
                res_data = h6.get_response_json()
                self.assertFalse(res_data["approved"])
                self.assertEqual(res_data["total_violations"], 2)

    def test_guardian_server_helpers_deep(self):
        # 1. get_repository_by_id with ~ or /
        CUSTOM_REPOSITORIES.clear()
        repo = get_repository_by_id("~/some/path")
        self.assertIsNone(repo)

        # 2. validate_commit_sha branches
        self.assertFalse(validate_commit_sha("", "")["valid"])
        self.assertFalse(validate_commit_sha("/nonexistent", "1234")["valid"])

        # 3. get_github_repositories unauthenticated
        with patch.dict(os.environ, {}, clear=True):
            with patch("subprocess.run", side_effect=Exception("no git")):
                res_gh = get_github_repositories()
                self.assertFalse(res_gh["connected"])

    def test_rule_registry_deep_branches(self):
        reg = RuleRegistry.get_instance()
        
        # 1. _load_from_dir with single rule and syntax error
        with tempfile.TemporaryDirectory() as tmpdir:
            td = Path(tmpdir)
            (td / "single.json").write_text(json.dumps({
                "id": "REG-SINGLE-01",
                "name": "Single Rule",
                "pattern": "single_pat"
            }), encoding="utf-8")
            (td / "bad.json").write_text("{ corrupt", encoding="utf-8")
            reg._load_from_dir(td, RuleTier.CUSTOM)
            reg._invalidate_cache()
            self.assertIsNotNone(reg.get("REG-SINGLE-01"))
            reg.delete("REG-SINGLE-01", hard_delete=True)

        # 2. _load_from_legacy_rules
        with tempfile.TemporaryDirectory() as tmpdir:
            td = Path(tmpdir)
            legacy_dir = td / "2_rules"
            legacy_dir.mkdir()
            (legacy_dir / "r.json").write_text(json.dumps({"rules": [{"id": "LEG-01", "name": "L1", "pattern": "p"}]}), encoding="utf-8")
            (td / "architecture_custom.json").write_text(json.dumps({"rules": [{"id": "ARCH-LEG-01", "name": "A1", "pattern": "p"}]}), encoding="utf-8")
            (td / "culture_manifesto.json").write_text(json.dumps({"rules": [{"id": "CULT-LEG-01", "name": "C1", "pattern": "p"}]}), encoding="utf-8")
            
            with patch.object(reg, "base_dir", td):
                with patch.object(reg, "legacy_2rules_dir", legacy_dir):
                    reg._load_from_legacy_rules()
                    reg._invalidate_cache()
                    self.assertIsNotNone(reg.get("LEG-01"))
                    self.assertIsNotNone(reg.get("ARCH-LEG-01"))
                    self.assertIsNotNone(reg.get("CULT-LEG-01"))
                    reg.delete("LEG-01", hard_delete=True)
                    reg.delete("ARCH-LEG-01", hard_delete=True)
                    reg.delete("CULT-LEG-01", hard_delete=True)

        # 3. search() across all fields
        dummy = RuleDefinition(
            id="SRCH-01",
            name="Search Keyword Target",
            description="Detailed description for search indexing",
            message="Violations must be fixed immediately",
            category="custom",
            architectures=["clean_architecture"],
            languages=["csharp"],
            condition=RuleCondition(pattern="srch_pat"),
            severity=RuleSeverity.P1_WARNING,
            tier=RuleTier.CUSTOM,
            author="special_author",
            rationale="Special rationale explanation"
        )
        reg.register(dummy, actor="admin", persist=False)
        self.assertTrue(len(reg.search("Search Keyword Target")) > 0)
        self.assertTrue(len(reg.search("indexing")) > 0)
        self.assertTrue(len(reg.search("immediately")) > 0)
        self.assertTrue(len(reg.search("SRCH-01")) > 0)
        reg.delete("SRCH-01", hard_delete=True)

    def test_rule_test_engine_deep_branches(self):
        # 1. NAMING rule with convention not matching any branches
        rule_unknown = RuleDefinition(
            id="TEST-NAM-UNK",
            name="Unknown Nam",
            type=RuleType.NAMING,
            condition=RuleCondition(naming_convention="custom_nonexistent"),
            severity=RuleSeverity.P1_WARNING,
            tier=RuleTier.CUSTOM
        )
        res_unk = RuleTestEngine.test_rule(rule_unknown, "class Foo: pass", "test.py")
        self.assertFalse(res_unk.has_violation)

        # 2. DEPENDENCY rule with forbidden targets matching AST/regex
        rule_dep_re = RuleDefinition(
            id="TEST-DEP-RE",
            name="Dep RE",
            type=RuleType.DEPENDENCY,
            condition=RuleCondition(forbidden_targets=["UnityEngine", "UnityEditor"]),
            severity=RuleSeverity.P0_BLOCKING,
            tier=RuleTier.CUSTOM
        )
        res_dep = RuleTestEngine.test_rule(rule_dep_re, "using UnityEngine;\n", "Script.cs")
        self.assertTrue(res_dep.has_violation)

    def test_token_filter_deep_branches(self):
        # 1. Directory prefix match in IgnoredFilePattern
        pat = IgnoredFilePattern("src/Legacy", ["ALL"])
        self.assertTrue(pat.matches("src/Legacy/Controllers/Old.cs"))

        # 2. Single line pragma with empty reason (missing justification warning)
        lines = ["# @guardian-ignore CULT01", "pass"]
        supp, warns = parse_inline_pragmas(lines)
        self.assertEqual(len(warns), 1)

        # 3. Block pragma with short justification warning
        lines_block = ["# @guardian-ignore-start CULT01: short", "pass", "# @guardian-ignore-end"]
        supp_b, warns_b = parse_inline_pragmas(lines_block)
        self.assertEqual(len(warns_b), 1)

        # 4. is_file_or_rule_exempt with tuple order (glob, rule)
        exempts = [("src/legacy/*", "CULT01")]
        self.assertTrue(is_file_or_rule_exempt("src/legacy/file.py", "CULT01", exempts))

    def test_culture_guard_deep_branches(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # 1. Spec tags regexes
            f_spec = Path(tmpdir) / "spec.py"
            f_spec.write_text("# @spec RF01\n# Requirement: RF02\n# Spec-ID: RF03\n# [RF04]\ndef test(): pass\n", encoding="utf-8")
            res_spec = FileAuditResult(f_spec)
            self.assertEqual(res_spec.has_spec_tag, 1)

            # 2. Lazy patterns
            f_lazy = Path(tmpdir) / "lazy.py"
            f_lazy.write_text("def test():\n    raise NotImplementedError\n", encoding="utf-8")
            res_lazy = FileAuditResult(f_lazy)
            self.assertEqual(res_lazy.has_lazy_code, 1)

            # 3. Secrets patterns
            f_sec = Path(tmpdir) / "sec.py"
            f_sec.write_text("secret = '12345678901234567890'\n", encoding="utf-8")
            res_sec = FileAuditResult(f_sec)
            self.assertEqual(res_sec.has_secrets, 1)

            # 4. Test file detection
            f_test = Path(tmpdir) / "test_something.py"
            f_test.write_text("def test(): pass\n", encoding="utf-8")
            res_t = FileAuditResult(f_test)
            self.assertEqual(res_t.has_test_coverage, 1)

            # 5. Scoped rules evaluation with custom severities P0, P1, P2, INFO
            rules_sev = [
                {"id": "CULT01", "customSeverity": "P0_BLOCKING"},
                {"id": "CULT03", "customSeverity": "P1_WARNING"},
                {"id": "CULT05", "customSeverity": "P2_INFO"}
            ]
            eval_res = evaluate_scoped_rules([str(f_lazy)], rules=rules_sev)
            self.assertIsInstance(eval_res, dict)


if __name__ == "__main__":
    unittest.main()
