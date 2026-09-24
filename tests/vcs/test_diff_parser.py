"""
==============================================================================
TDD Unit Tests: Git Diff Parser & Hunk Line Extractor
==============================================================================
@spec RF04 - Delta Diff Analysis
@spec RF05 - Unified Diff Multi-Mode Support (Added, Deleted, Renamed)
@spec RF06 - Strict Changed-Line Semantic Isolation
==============================================================================
"""

import unittest
from scripts.vcs_adapters.diff_parser import (
    parse_unified_diff,
    parse_unified_diff_structured,
    extract_changed_lines,
    ParsedDiffFile
)

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

SAMPLE_ADDED_DIFF = """diff --git a/src/Domain/NewEntity.cs b/src/Domain/NewEntity.cs
new file mode 100644
index 0000000..abcdef1
--- /dev/null
+++ b/src/Domain/NewEntity.cs
@@ -0,0 +1,5 @@
+namespace Domain.Entities;
+
+public class NewEntity {
+    public int Id { get; set; }
+}
"""

SAMPLE_DELETED_DIFF = """diff --git a/src/LegacyService.cs b/src/LegacyService.cs
deleted file mode 100644
index abcdef1..0000000
--- a/src/LegacyService.cs
+++ /dev/null
@@ -1,4 +0,0 @@
-public class LegacyService {
-    public void OldMethod() {}
-}
"""

SAMPLE_RENAMED_DIFF = """diff --git a/src/OldName.cs b/src/NewName.cs
similarity index 100%
rename from src/OldName.cs
rename to src/NewName.cs
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

    def test_parse_empty_diff_returns_empty_dict(self):
        """RF05 / RN02: Empty diff string returns empty dictionary and empty list."""
        self.assertEqual(parse_unified_diff(""), {})
        self.assertEqual(parse_unified_diff("   \n\n"), {})
        self.assertEqual(parse_unified_diff_structured(""), [])

    def test_structured_diff_added_file(self):
        """RF05: Added file detection and line tracking."""
        files = parse_unified_diff_structured(SAMPLE_ADDED_DIFF)
        self.assertEqual(len(files), 1)
        f = files[0]
        self.assertEqual(f.new_path, "src/Domain/NewEntity.cs")
        self.assertEqual(f.status, "added")
        self.assertEqual(f.additions_count, 5)
        self.assertEqual(f.deletions_count, 0)
        self.assertIn(1, f.changed_lines)
        self.assertIn(5, f.changed_lines)

    def test_structured_diff_deleted_file(self):
        """RF05: Deleted file detection."""
        files = parse_unified_diff_structured(SAMPLE_DELETED_DIFF)
        self.assertEqual(len(files), 1)
        f = files[0]
        self.assertEqual(f.old_path, "src/LegacyService.cs")
        self.assertEqual(f.status, "deleted")
        self.assertEqual(f.deletions_count, 3)
        self.assertEqual(f.additions_count, 0)

    def test_structured_diff_renamed_file(self):
        """RF05: Renamed file detection."""
        files = parse_unified_diff_structured(SAMPLE_RENAMED_DIFF)
        self.assertEqual(len(files), 1)
        f = files[0]
        self.assertEqual(f.old_path, "src/OldName.cs")
        self.assertEqual(f.new_path, "src/NewName.cs")
        self.assertEqual(f.status, "renamed")

    def test_changed_line_isolation_ignores_context(self):
        """RF06: Context lines starting with space must NOT be added to changed_lines."""
        context_diff = (
            "diff --git a/test.cs b/test.cs\n"
            "--- a/test.cs\n"
            "+++ b/test.cs\n"
            "@@ -10,3 +10,4 @@\n"
            " context_line_10\n"
            "+added_line_11\n"
            " context_line_12\n"
        )
        changed = extract_changed_lines(context_diff, "test.cs")
        self.assertEqual(changed, {11})
        self.assertNotIn(10, changed)
        self.assertNotIn(12, changed)

if __name__ == "__main__":
    unittest.main()
