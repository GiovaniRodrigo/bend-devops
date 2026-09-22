"""
==============================================================================
TDD Unit Tests: Inline Pragma Suppression & Justification Validation
==============================================================================
@spec RF03, RF04, RF05 - Inline Suppression Pragmas & .guardianignore
==============================================================================
"""

import unittest
from pathlib import Path
from scripts.token_filter import (
    parse_inline_pragmas,
    TokenFilter,
    IgnoredFilePattern,
    load_guardianignore,
    is_file_or_rule_exempt
)

class TestInlinePragmas(unittest.TestCase):
    def test_parse_valid_inline_pragma(self):
        lines = [
            "// @guardian-ignore ARCH-LAYER-01: Legitimate domain avatar serialization",
            "public string AvatarHtml => \"<img src='...' />\";"
        ]
        suppressed_map, warnings = parse_inline_pragmas(lines)
        self.assertIn(2, suppressed_map)
        self.assertIn("ARCH-LAYER-01", suppressed_map[2])
        self.assertEqual(len(warnings), 0)

    def test_parse_invalid_inline_pragma_missing_reason(self):
        lines = [
            "// @guardian-ignore ARCH-LAYER-01",
            "public string AvatarHtml => \"<img src='...' />\";"
        ]
        suppressed_map, warnings = parse_inline_pragmas(lines)
        # Missing reason does NOT exempt line and emits a warning
        self.assertEqual(len(suppressed_map), 0)
        self.assertEqual(len(warnings), 1)
        self.assertEqual(warnings[0]["rule_id"], "PRAGMA-INVALID")

    def test_parse_all_rules_inline_pragma(self):
        lines = [
            "# @guardian-ignore ALL: Legacy test mock code",
            "def raw_hack():",
            "    pass"
        ]
        suppressed_map, warnings = parse_inline_pragmas(lines)
        self.assertIn(2, suppressed_map)
        self.assertIn("ALL", suppressed_map[2])

    def test_parse_block_scoped_pragma(self):
        lines = [
            "// @guardian-ignore-start ARCH-LAYER-01: Bulk legacy markup block",
            "public string Line1 => \"<img src='1.png' />\";",
            "public string Line2 => \"<div class='box'></div>\";",
            "// @guardian-ignore-end ARCH-LAYER-01",
            "public string Line3 => \"<span>Unprotected</span>\";"
        ]
        suppressed_map, warnings = parse_inline_pragmas(lines)
        self.assertEqual(len(warnings), 0)
        self.assertIn(2, suppressed_map)
        self.assertIn(3, suppressed_map)
        self.assertNotIn(5, suppressed_map)

    def test_parse_block_scoped_pragma_missing_reason_emits_warning(self):
        lines = [
            "// @guardian-ignore-start ARCH-LAYER-01",
            "public string Line1 => \"<img src='1.png' />\";",
            "// @guardian-ignore-end"
        ]
        suppressed_map, warnings = parse_inline_pragmas(lines)
        self.assertEqual(len(warnings), 1)
        self.assertEqual(warnings[0]["rule_id"], "PRAGMA-INVALID")

    def test_guardianignore_pattern_matching(self):
        pattern = IgnoredFilePattern("legacy/**", exempted_rules=["ARCH-LAYER-01"], reason="Legacy folder")
        self.assertTrue(pattern.matches("legacy/models/OldUser.cs", "ARCH-LAYER-01"))
        self.assertFalse(pattern.matches("legacy/models/OldUser.cs", "ARCH-LAYER-02"))
        self.assertFalse(pattern.matches("src/Domain/User.cs", "ARCH-LAYER-01"))

    def test_guardianignore_wildcard_all_rules(self):
        pattern = IgnoredFilePattern("migrations/*", exempted_rules=[], reason="Database migrations")
        self.assertTrue(pattern.matches("migrations/001_init.py", "ARCH-LAYER-02"))
        self.assertTrue(pattern.matches("migrations/001_init.py", "CULT01"))

    def test_load_guardianignore_from_file(self):
        tmp_ignore = Path("/tmp/.guardianignore_test")
        tmp_ignore.write_text("""# Project Exemptions
legacy/** [ARCH-LAYER-01, ARCH-LAYER-03] # Legacy backend
tests/fixtures/* # Test fixtures
""", encoding="utf-8")
        try:
            exemptions = load_guardianignore(tmp_ignore)
            self.assertEqual(len(exemptions), 2)
            self.assertTrue(is_file_or_rule_exempt("legacy/app.cs", "ARCH-LAYER-01", exemptions))
            self.assertTrue(is_file_or_rule_exempt("tests/fixtures/sample.py", "CULT01", exemptions))
            self.assertFalse(is_file_or_rule_exempt("src/main.py", "CULT01", exemptions))
        finally:
            if tmp_ignore.exists():
                tmp_ignore.unlink()

if __name__ == "__main__":
    unittest.main()
