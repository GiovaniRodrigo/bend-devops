"""
==============================================================================
TDD Unit Tests: Token Boundary Filtering & Comment Stripping
==============================================================================
@spec RF01, RF02 - False-Positive Reduction
==============================================================================
"""

import unittest
from scripts.token_filter import strip_comments, matches_exact_token

class TestTokenFilter(unittest.TestCase):
    def test_strip_single_line_slash_comment(self):
        line = 'public int Id { get; set; } // SELECT * FROM users'
        stripped = strip_comments(line, ".cs")
        self.assertEqual(stripped, 'public int Id { get; set; }')

    def test_strip_single_line_hash_comment(self):
        line = 'def process(): # <img src="bad.png">'
        stripped = strip_comments(line, ".py")
        self.assertEqual(stripped, 'def process():')

    def test_matches_exact_token_ignores_method_and_variable_substrings(self):
        # Method get_image_url should NOT match <img
        line1 = 'public string GetImageUrl() => "/path";'
        self.assertFalse(matches_exact_token("<img", line1))
        self.assertFalse(matches_exact_token("<img>", line1))

        # Method select_item should NOT match SELECT * FROM
        line2 = 'public void SelectItem(int id) { }'
        self.assertFalse(matches_exact_token("SELECT * FROM", line2))
        self.assertFalse(matches_exact_token("SELECT", line2))

        # Variable input_data should NOT match <input>
        line3 = 'const input_data = 42;'
        self.assertFalse(matches_exact_token("<input>", line3))
        self.assertFalse(matches_exact_token("<input", line3))

    def test_matches_exact_token_detects_real_violations(self):
        # Genuine <img tag
        line1 = 'return "<img src=\'/path\' />";'
        self.assertTrue(matches_exact_token("<img", line1))

        # Genuine SELECT statement
        line2 = 'var q = "SELECT * FROM users WHERE active = 1";'
        self.assertTrue(matches_exact_token("SELECT * FROM", line2))
        self.assertTrue(matches_exact_token("SELECT", line2))

        # Genuine HttpContext usage
        line3 = 'public void Handle(HttpContext context)'
        self.assertTrue(matches_exact_token("HttpContext", line3))

if __name__ == "__main__":
    unittest.main()
