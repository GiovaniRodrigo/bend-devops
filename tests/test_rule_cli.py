"""
Integration Tests for Guardian CLI Rule Subcommands
"""

import sys
import json
import unittest
import tempfile
import shutil
from pathlib import Path
from io import StringIO
from unittest.mock import patch

from scripts.culture_guard import handle_rules_cli
from scripts.rule_registry import RuleRegistry


class TestGuardianRuleCli(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.custom_dir = Path(self.temp_dir) / "custom"
        self.custom_dir.mkdir(parents=True, exist_ok=True)
        self.registry = RuleRegistry(custom_rules_dir=self.custom_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_cli_rules_list(self):
        with patch("sys.stdout", new=StringIO()) as fake_out:
            exit_code = handle_rules_cli(["list"])
            output = fake_out.getvalue()
            self.assertEqual(exit_code, 0)
            self.assertIn("GUARDIAN DECLARATIVE RULES CATALOG", output)
            self.assertIn("CULT01", output)

    def test_cli_rules_show(self):
        with patch("sys.stdout", new=StringIO()) as fake_out:
            exit_code = handle_rules_cli(["show", "CULT01"])
            output = fake_out.getvalue()
            self.assertEqual(exit_code, 0)
            self.assertIn("Rule: CULT01", output)

    def test_cli_rules_search(self):
        with patch("sys.stdout", new=StringIO()) as fake_out:
            exit_code = handle_rules_cli(["search", "secret"])
            output = fake_out.getvalue()
            self.assertEqual(exit_code, 0)
            self.assertIn("SEARCH RESULTS", output)

    def test_cli_rules_validate(self):
        with patch("sys.stdout", new=StringIO()) as fake_out:
            exit_code = handle_rules_cli(["validate", "CULT01"])
            output = fake_out.getvalue()
            self.assertEqual(exit_code, 0)
            self.assertIn("VALID", output)

    def test_cli_rules_test(self):
        with patch("sys.stdout", new=StringIO()) as fake_out:
            exit_code = handle_rules_cli([
                "test", "CULT01",
                "--code", "def compute():\n    # TODO: implement later\n    pass\n"
            ])
            output = fake_out.getvalue()
            self.assertIn("TEST EXECUTION", output)

    def test_cli_rules_export_and_import(self):
        export_file = Path(self.temp_dir) / "exported_cult01.json"
        with patch("sys.stdout", new=StringIO()) as fake_out:
            exit_code = handle_rules_cli(["export", "CULT01", "--out", str(export_file)])
            self.assertEqual(exit_code, 0)
            self.assertTrue(export_file.exists())

        with patch("sys.stdout", new=StringIO()) as fake_out:
            exit_code = handle_rules_cli(["import", str(export_file), "--overwrite"])
            self.assertEqual(exit_code, 0)


if __name__ == "__main__":
    unittest.main()
