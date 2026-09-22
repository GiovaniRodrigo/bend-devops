"""
==============================================================================
TDD Unit Tests: Inline Pragma Suppression & Justification Validation
==============================================================================
@spec RF03, RF05 - Inline Suppression Pragmas
==============================================================================
"""

import unittest
from scripts.token_filter import parse_inline_pragmas

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

if __name__ == "__main__":
    unittest.main()
