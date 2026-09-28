"""
Unit tests for scripts/culture_guard.py (Core CLI, AST features, Bend harness, and rule evaluation).
"""

import sys
import os
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.culture_guard import (
    load_layer_vocabulary,
    escape_for_regex,
    build_vocabulary_regexes,
    classify_file_layer,
    FileAuditResult,
    generate_bend_harness,
    run_bend_engine,
    print_report,
    resolve_scope_files,
    evaluate_scoped_rules,
    handle_rules_cli,
    main
)
from scripts.rule_model import RuleDefinition, RuleType, RuleSeverity, RuleStatus, RuleTier
from scripts.rule_registry import RuleRegistry


class TestCultureGuard(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_load_layer_vocabulary(self):
        vocab = load_layer_vocabulary()
        self.assertIsInstance(vocab, dict)

    def test_escape_for_regex(self):
        token = "<div>*?"
        escaped = escape_for_regex(token)
        self.assertTrue("<" in escaped and "*" not in escaped or "\\*" in escaped)

    def test_build_vocabulary_regexes(self):
        custom_vocab = {
            "layers": {
                "Presentation": {"tokens": {"html": ["<div>", "<span>"]}},
                "Interface_Transport": {"tokens": {"http": ["HttpContext"]}},
                "Infrastructure_Persistence": {"tokens": {"db": ["DB::table"]}}
            }
        }
        regexes = build_vocabulary_regexes(custom_vocab)
        self.assertIn("Model", regexes)
        self.assertIn("View", regexes)
        self.assertIn("PresentationalUI", regexes)

        empty_regexes = build_vocabulary_regexes({})
        self.assertIn("Model", empty_regexes)

    def test_classify_file_layer(self):
        self.assertEqual(classify_file_layer(Path("src/Domain/Entities/Order.cs")), "Model")
        self.assertEqual(classify_file_layer(Path("src/Controllers/OrderController.cs")), "Controller")
        self.assertEqual(classify_file_layer(Path("src/Views/Order.cshtml")), "View")
        self.assertEqual(classify_file_layer(Path("src/Services/OrderService.cs")), "Service")
        self.assertEqual(classify_file_layer(Path("src/DTOs/OrderRequest.cs")), "RequestValidator")
        self.assertEqual(classify_file_layer(Path("src/components/ui/Button.tsx")), "PresentationalUI")
        self.assertEqual(classify_file_layer(Path("src/db/migrations/001.sql")), "Infrastructure")
        self.assertEqual(classify_file_layer(Path("src/random.xyz")), "Generic")

    def test_file_audit_result_unreadable_file(self):
        non_existent = Path("/non/existent/path.py")
        res = FileAuditResult(non_existent)
        self.assertEqual(res.lines_count, 0)

    def test_file_audit_result_compliant(self):
        f = self.temp_path / "compliant.py"
        test_f = self.temp_path / "test_compliant.py"
        test_f.write_text("# tests", encoding="utf-8")
        f.write_text(
            "# @spec RF01\ndef calculate(a: int) -> int:\n    return a * 2\n",
            encoding="utf-8"
        )
        res = FileAuditResult(f)
        self.assertEqual(res.has_spec_tag, 1)
        self.assertEqual(res.has_test_coverage, 1)
        self.assertEqual(res.has_lazy_code, 0)
        self.assertEqual(res.has_secrets, 0)
        self.assertEqual(len(res.violations), 0)

    def test_file_audit_result_violations(self):
        # Lazy code, missing spec tag, missing type hints, secrets
        f = self.temp_path / "Domain" / "Entities" / "Order.cs"
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(
            "// Missing spec tag\n"
            "// TODO: implement later\n"
            "var apiKey = 'secret123456789012';\n"
            "var html = '<div>hello</div>';\n"
            "var req = HttpContext.Current;\n",
            encoding="utf-8"
        )
        res = FileAuditResult(f)
        self.assertEqual(res.layer, "Model")
        self.assertEqual(res.has_spec_tag, 0)
        self.assertEqual(res.has_lazy_code, 1)
        self.assertEqual(res.has_secrets, 1)
        self.assertGreater(len(res.violations), 0)
        rule_ids = [v["rule_id"] for v in res.violations]
        self.assertIn("CULT01", rule_ids)
        self.assertIn("CULT02", rule_ids)
        self.assertIn("CULT03", rule_ids)
        self.assertIn("CULT04", rule_ids)
        self.assertIn("ARCH-LAYER-01", rule_ids)
        self.assertIn("ARCH-LAYER-03", rule_ids)

    def test_file_audit_result_exemptions(self):
        f = self.temp_path / "Order.cs"
        f.write_text("// TODO: later\n", encoding="utf-8")
        res = FileAuditResult(f, project_exemptions=[("ALL", "Order.cs")])
        self.assertGreater(res.suppressed_count, 0)

    def test_file_audit_result_python_type_annotations(self):
        f = self.temp_path / "untyped.py"
        test_f = self.temp_path / "test_untyped.py"
        test_f.write_text("# tests", encoding="utf-8")
        f.write_text("# @spec RF01\ndef do_something(x, y):\n    return x + y\n", encoding="utf-8")
        res = FileAuditResult(f)
        self.assertEqual(res.has_type_annotations, 0)
        rule_ids = [v["rule_id"] for v in res.violations]
        self.assertIn("CULT05", rule_ids)

    def test_generate_bend_harness(self):
        f1 = self.temp_path / "test1.py"
        f1.write_text("# @spec RF01\ndef f(x: int) -> int:\n    return x\n", encoding="utf-8")
        audit1 = FileAuditResult(f1)
        harness = generate_bend_harness([audit1])
        self.assertIn("def main()", harness)
        self.assertIn("Tree/Leaf", harness)

        harness_empty = generate_bend_harness([])
        self.assertIn("def main()", harness_empty)

    def test_run_bend_engine(self):
        f1 = self.temp_path / "test1.py"
        f1.write_text("# @spec RF01\ndef f(x: int) -> int:\n    return x\n", encoding="utf-8")
        audit1 = FileAuditResult(f1)
        harness = generate_bend_harness([audit1])
        stats = run_bend_engine(harness, [audit1])
        self.assertEqual(len(stats), 7)
        self.assertEqual(stats[0], 1)

    def test_print_report(self):
        f1 = self.temp_path / "test1.py"
        f1.write_text("# @spec RF01\ndef f(x: int) -> int:\n    return x\n", encoding="utf-8")
        audit1 = FileAuditResult(f1)
        bend_stats = (1, 0, 0, 0, 0, 100, 1)

        # Text output approved
        ok = print_report([audit1], bend_stats, format_type="text")
        self.assertTrue(ok)

        # Text output with branch policy
        ok2 = print_report([audit1], bend_stats, format_type="text", branch_policy_verdict=(True, "Branch compliant"))
        self.assertTrue(ok2)

        # JSON output
        ok_json = print_report([audit1], bend_stats, format_type="json")
        self.assertTrue(ok_json)

        # Blocked report
        audit1.violations.append({"rule_id": "CULT01", "severity": "P0_BLOCKING", "penalty": 35, "message": "Blocked"})
        blocked_stats = (1, 1, 1, 0, 35, 65, 0)
        not_ok = print_report([audit1], blocked_stats, format_type="text")
        self.assertFalse(not_ok)

    def test_resolve_scope_files(self):
        sub_dir = self.temp_path / "src" / "Domain"
        sub_dir.mkdir(parents=True, exist_ok=True)
        f1 = sub_dir / "Order.cs"
        f1.write_text("public class Order {}", encoding="utf-8")
        f2 = self.temp_path / "README.md"
        f2.write_text("# Readme", encoding="utf-8")

        # Scope: full_branch
        files_full = resolve_scope_files(self.temp_path, scope="full_branch")
        self.assertIn(str(f1), files_full)

        # Scope: subdirectory
        files_sub = resolve_scope_files(self.temp_path, scope="subdirectory", target="src/Domain")
        self.assertIn(str(f1), files_sub)

        # Scope: single_file
        files_single = resolve_scope_files(self.temp_path, scope="single_file", target=str(f1))
        self.assertEqual(files_single, [str(f1)])

        # Scope: diff
        files_diff = resolve_scope_files(self.temp_path, scope="working_tree_diff")
        self.assertIsInstance(files_diff, list)

    def test_evaluate_scoped_rules(self):
        # Empty files list
        res_empty = evaluate_scoped_rules([])
        self.assertTrue(res_empty["isApproved"])
        self.assertEqual(res_empty["score"], 100)

        # Scoped evaluation with files
        f1 = self.temp_path / "src" / "Model.cs"
        f1.parent.mkdir(parents=True, exist_ok=True)
        f1.write_text("// TODO: incomplete\n", encoding="utf-8")

        res = evaluate_scoped_rules(
            [str(f1)],
            rules=[{"id": "CULT01", "customSeverity": "P0_BLOCKING"}],
            repo_root=self.temp_path
        )
        self.assertFalse(res["isApproved"])
        self.assertGreater(res["totalViolations"], 0)

    def test_handle_rules_cli(self):
        # List rules
        ret = handle_rules_cli(["list", "--json"])
        self.assertEqual(ret, 0)

        # Search rules
        ret_search = handle_rules_cli(["search", "architecture"])
        self.assertEqual(ret_search, 0)

        # Export all
        ret_exp = handle_rules_cli(["export", "all"])
        self.assertEqual(ret_exp, 0)

        # Show rule
        ret_show = handle_rules_cli(["show", "CULT01", "--json"])
        self.assertEqual(ret_show, 0)

        # Validate rule by id
        ret_val = handle_rules_cli(["validate", "CULT01"])
        self.assertEqual(ret_val, 0)

        # Test rule
        ret_test = handle_rules_cli(["test", "CULT01", "--code", "# TODO: fix later", "--json"])
        self.assertEqual(ret_test, 0)

    def test_main_cli_scenarios(self):
        # Mock scenario
        with patch.object(sys, "argv", ["culture_guard.py", "--mock-scenario", "clean-repository", "--format", "json"]):
            with self.assertRaises(SystemExit) as cm:
                main()
            self.assertEqual(cm.exception.code, 0)

        # Rules dispatcher
        with patch.object(sys, "argv", ["culture_guard.py", "rules", "list"]):
            main()


if __name__ == "__main__":
    unittest.main()
