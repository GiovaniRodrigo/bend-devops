"""
Comprehensive test suite targeting 100% coverage of scripts/culture_guard.py
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
    classify_file_layer,
    build_vocabulary_regexes,
    load_layer_vocabulary,
    FileAuditResult,
    generate_bend_harness,
    run_bend_engine,
    print_report,
    evaluate_scoped_rules,
    resolve_scope_files,
    handle_rules_cli,
    main
)


class TestCultureGuardFullCoverage(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_layer_classification_and_vocab_fallbacks(self):
        # View layer
        self.assertEqual(classify_file_layer("src/views/index.cshtml"), "View")
        self.assertEqual(classify_file_layer("src/components/ui/Button.tsx"), "PresentationalUI")
        self.assertEqual(classify_file_layer("src/queries/schema.sql"), "Infrastructure")
        self.assertEqual(classify_file_layer("src/controllers/UserController.cs"), "Controller")
        self.assertEqual(classify_file_layer("src/services/UserService.cs"), "Service")
        self.assertEqual(classify_file_layer("src/validators/UserRequest.cs"), "RequestValidator")
        self.assertEqual(classify_file_layer("src/random/Unknown.xyz"), "Generic")

        # Empty vocabulary fallback
        regexes = build_vocabulary_regexes({})
        self.assertIn("Model", regexes)
        self.assertIn("Domain", regexes)

    def test_rules_cli_all_subcommands(self):
        # 1. list
        with patch("sys.stdout"):
            self.assertEqual(handle_rules_cli(["list"]), 0)
            self.assertEqual(handle_rules_cli(["list", "--category=security", "--severity=P0", "--status=active", "--tier=builtin", "--type=pattern"]), 0)
            self.assertEqual(handle_rules_cli(["list", "--json"]), 0)

        # 2. show
        with patch("sys.stdout"):
            self.assertEqual(handle_rules_cli(["show", "CULT01"]), 0)
            self.assertEqual(handle_rules_cli(["show", "CULT01", "--json"]), 0)
            self.assertEqual(handle_rules_cli(["show", "NON_EXISTENT_RULE_999"]), 1)

        # 3. create & edit & delete
        rule_file = self.temp_path / "custom_rule.json"
        rule_file.write_text(json.dumps({
            "id": "CLI-TEST-01",
            "name": "CLI Test Rule",
            "pattern": "bad_code\\(\\)"
        }), encoding="utf-8")

        with patch("sys.stdout"):
            self.assertEqual(handle_rules_cli(["create", str(rule_file)]), 0)
            self.assertEqual(handle_rules_cli(["create", "/nonexistent/file.json"]), 1)

            # edit
            self.assertEqual(handle_rules_cli(["edit", "CLI-TEST-01", str(rule_file)]), 0)
            self.assertEqual(handle_rules_cli(["edit", "CLI-TEST-01", "/nonexistent.json"]), 1)

            # clone
            self.assertEqual(handle_rules_cli(["clone", "CLI-TEST-01", "CLI-TEST-CLONE", "--name=Cloned"]), 0)
            self.assertEqual(handle_rules_cli(["clone", "NONEXISTENT", "CLONE_FAIL"]), 1)

            # enable & disable
            self.assertEqual(handle_rules_cli(["disable", "CLI-TEST-01"]), 0)
            self.assertEqual(handle_rules_cli(["enable", "CLI-TEST-01"]), 0)
            self.assertEqual(handle_rules_cli(["enable", "NONEXISTENT"]), 1)
            self.assertEqual(handle_rules_cli(["disable", "NONEXISTENT"]), 1)

            # validate
            self.assertEqual(handle_rules_cli(["validate", str(rule_file)]), 0)
            self.assertEqual(handle_rules_cli(["validate", "CLI-TEST-01"]), 0)
            self.assertEqual(handle_rules_cli(["validate", "/nonexistent.json"]), 1)

            # test
            self.assertEqual(handle_rules_cli(["test", "CLI-TEST-01", "--code=bad_code()", "--json"]), 0)
            self.assertEqual(handle_rules_cli(["test", "CLI-TEST-01", "--code=bad_code()"]), 0)
            self.assertEqual(handle_rules_cli(["test", "NONEXISTENT"]), 1)

            # export
            export_out = self.temp_path / "export_single.json"
            self.assertEqual(handle_rules_cli(["export", "CLI-TEST-01", f"--out={export_out}"]), 0)
            self.assertEqual(handle_rules_cli(["export", "CLI-TEST-01"]), 0)
            self.assertEqual(handle_rules_cli(["export", "NONEXISTENT"]), 1)

            # import
            self.assertEqual(handle_rules_cli(["import", str(export_out)]), 0)

            # search
            self.assertEqual(handle_rules_cli(["search", "CLI"]), 0)

            # delete
            self.assertEqual(handle_rules_cli(["delete", "CLI-TEST-01", "--force"]), 0)
            self.assertEqual(handle_rules_cli(["delete", "CLI-TEST-CLONE", "--force"]), 0)
            self.assertEqual(handle_rules_cli(["delete", "NONEXISTENT"]), 1)

    def test_main_cli_modes_and_formats(self):
        sample_code = self.temp_path / "Sample.cs"
        sample_code.write_text("// @spec RF01\npublic class Sample {\n    // TODO: implement\n}\n", encoding="utf-8")

        # 1. Main rules subcommand dispatch
        with patch("sys.argv", ["culture_guard.py", "rules", "list"]):
            with patch("sys.stdout"):
                main()

        # 2. Mock mode execution
        with patch("sys.argv", ["culture_guard.py", "--mock-scenario=clean-repository", "--format=json"]):
            with patch("sys.stdout"):
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 0)

        with patch("sys.argv", ["culture_guard.py", "--mock-scenario=clean-repository", "--format=text"]):
            with patch("sys.stdout"):
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 0)

        # 3. Real audit with markdown, json, text formats, branch policy, and include-build-dirs
        with patch("sys.argv", ["culture_guard.py", str(sample_code), "--format=markdown", "--branch=develop"]):
            with patch("sys.stdout"):
                with self.assertRaises(SystemExit):
                    main()

        with patch("sys.argv", ["culture_guard.py", str(sample_code), "--format=json", "--branch=main"]):
            with patch("sys.stdout"):
                with self.assertRaises(SystemExit):
                    main()

        with patch("sys.argv", ["culture_guard.py", str(sample_code), "--format=text", "--include-build-dirs"]):
            with patch("sys.stdout"):
                with self.assertRaises(SystemExit):
                    main()

        # 4. VCS adapter options in main
        with patch("sys.argv", ["culture_guard.py", str(sample_code), "--vcs=github"]):
            with patch("sys.stdout"):
                with self.assertRaises(SystemExit):
                    main()


if __name__ == "__main__":
    unittest.main()
