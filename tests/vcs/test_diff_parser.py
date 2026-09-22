"""
==============================================================================
TDD Unit Tests: Git Diff Parser & Hunk Line Extractor
==============================================================================
@spec RF04 - Delta Diff Analysis
==============================================================================
"""

import unittest
from scripts.vcs_adapters.diff_parser import parse_unified_diff, extract_changed_lines

SAMPLE_DIFF = """diff --git a/src/Domain/Order.cs b/src/Domain/Order.cs
index 1234567..89abcdef 100644
--- a/src/Domain/Order.cs
+++ b/src/Domain/Order.cs
@@ -10,4 +10,6 @@ public class Order
     public int Id { get; set; }
+    public string AvatarHtml => "<img src='...' />";
+    public string Name { get; set; }
diff --git a/src/Views/Product.cshtml b/src/Views/Product.cshtml
index 1111111..2222222 100644
--- a/src/Views/Product.cshtml
+++ b/src/Views/Product.cshtml
@@ -1,3 +1,4 @@
 <div>
+    <span>New Product</span>
 </div>
"""

class TestGitDiffParser(unittest.TestCase):
    def test_parse_unified_diff_extracts_all_modified_files(self):
        parsed = parse_unified_diff(SAMPLE_DIFF)
        self.assertIn("src/Domain/Order.cs", parsed)
        self.assertIn("src/Views/Product.cshtml", parsed)
        self.assertEqual(len(parsed), 2)

    def test_extract_changed_lines_returns_correct_line_numbers(self):
        lines_order = extract_changed_lines(SAMPLE_DIFF, "src/Domain/Order.cs")
        self.assertIn(11, lines_order)
        self.assertIn(12, lines_order)
        self.assertNotIn(10, lines_order)

    def test_extract_changed_lines_for_empty_or_missing_file(self):
        lines_missing = extract_changed_lines(SAMPLE_DIFF, "non_existent_file.py")
        self.assertEqual(lines_missing, set())

    def test_extract_changed_lines_handles_multiple_hunks(self):
        multi_hunk_diff = """diff --git a/app.py b/app.py
--- a/app.py
+++ b/app.py
@@ -5,2 +5,3 @@
 def old_func():
+    pass
@@ -20,2 +21,3 @@
 def another_func():
+    return True
"""
        lines = extract_changed_lines(multi_hunk_diff, "app.py")
        self.assertIn(6, lines)
        self.assertIn(22, lines)

if __name__ == "__main__":
    unittest.main()
