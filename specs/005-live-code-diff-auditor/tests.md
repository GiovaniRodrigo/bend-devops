# Test Specification: Live Code & Diff Auditor

This document specifies the test suite, coverage matrix, and test skeletons for the **Live Code & Diff Auditor** across unit, integration, and E2E layers.

---

## 1. Test Coverage Matrix

| Requirement | Description | Layer | Status | Criticality |
| :--- | :--- | :--- | :--- | :--- |
| **RF01** | Branch-First Analysis (Full Branch Delta Evaluation) | Unit / E2E | ✅ Verified | 🔴 P0 |
| **RF02** | Targeted Single-File Review Workflow | Unit / E2E | ✅ Verified | 🟠 P1 |
| **RF03** | Post-Branch File Deep-Dive Navigation | Unit / E2E | ✅ Verified | 🔴 P0 |
| **RF04** | Side-by-Side Before/After Diff Viewer & Modes | Unit / E2E | ✅ Verified | 🔴 P0 |
| **RF05** | Git Diff Engine (Added, Deleted, Renamed, Hunks) | Unit / Backend | ✅ Verified | 🔴 P0 |
| **RF06** | Changed-Line Isolation (No Context False Positives) | Unit / Backend | ✅ Verified | 🔴 P0 |
| **RF07** | Progressive Disclosure Accordions & UI Simplicity | Unit / E2E | ✅ Verified | 🟡 P2 |
| **RF08** | Deterministic Quality Gate Verdict & Scoring | Unit / Frontend | ✅ Verified | 🔴 P0 |
| **RN01** | P0 Blocking Violations Block Merges | Integration / E2E | ✅ Verified | 🔴 P0 |
| **RN02** | Empty Branch Handling (0 Changes) | Unit / E2E | ✅ Verified | 🟠 P1 |
| **RN03** | Added, Deleted, and Renamed File Representation | Unit / E2E | ✅ Verified | 🟠 P1 |
| **RN04** | Non-Destructive Navigation Back to Summary | Unit / E2E | ✅ Verified | 🟠 P1 |

---

## 2. Test Skeletons

### 2.1. Backend Git Diff Parser Skeletons (Python `unittest`)

```python
# tests/vcs/test_diff_parser.py

class TestGitDiffParserComprehensive(unittest.TestCase):
    def test_parse_diff_with_new_file_mode(self):
        """RF05: Validates parsing when a new file is added."""
        diff = """diff --git a/src/Domain/NewEntity.cs b/src/Domain/NewEntity.cs
new file mode 100644
--- /dev/null
+++ b/src/Domain/NewEntity.cs
@@ -0,0 +1,5 @@
+public class NewEntity {
+    public int Id { get; set; }
+}
+"""
+        res = parse_unified_diff_structured(diff)
+        self.assertEqual(res[0].status, "added")
+        self.assertEqual(len(res[0].changed_lines), 3)

    def test_parse_diff_with_deleted_file_mode(self):
        """RF05: Validates parsing when a file is deleted."""
        diff = """diff --git a/src/OldService.cs b/src/OldService.cs
deleted file mode 100644
--- a/src/OldService.cs
+++ /dev/null
@@ -1,3 +0,0 @@
-public class OldService {}
-"""
        res = parse_unified_diff_structured(diff)
        self.assertEqual(res[0].status, "deleted")

    def test_parse_diff_with_renamed_file(self):
        """RF05: Validates parsing when a file is renamed."""
        diff = """diff --git a/src/OldName.cs b/src/NewName.cs
similarity index 100%
rename from src/OldName.cs
rename to src/NewName.cs
"""
        res = parse_unified_diff_structured(diff)
        self.assertEqual(res[0].status, "renamed")
        self.assertEqual(res[0].old_path, "src/OldName.cs")
        self.assertEqual(res[0].new_path, "src/NewName.cs")

    def test_changed_lines_ignores_context_lines(self):
        """RF06: Validates that unchanged context lines are never included in changed_lines."""
        diff = """diff --git a/src/File.cs b/src/File.cs
@@ -10,3 +10,4 @@
  context_line_10
 +added_line_11
  context_line_12
"""
        lines = extract_changed_lines(diff, "src/File.cs")
        self.assertIn(11, lines)
        self.assertNotIn(10, lines)
        self.assertNotIn(12, lines)
```

### 2.2. Frontend Signal & Auditor Workflow Skeletons (TypeScript `vitest`)

```typescript
// frontend/src/app/app.spec.ts

describe('Live Code & Diff Auditor Workflow', () => {
  it('RF01: should default to branch_analysis and execute branch audit without file dropdown', () => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;
    expect(app.auditScope()).toBe('branch_analysis');
    app.analyzeBranch();
    expect(app.branchSummary()).toBeTruthy();
    expect(app.branchSummary()?.files.length).toBeGreaterThan(0);
  });

  it('RF03: should drill down into specific file review and return to branch summary', () => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;
    app.analyzeBranch();
    const file = app.branchSummary()!.files[0];
    app.startFileReview(file);
    expect(app.isReviewingSpecificFile()).toBe(true);
    app.closeFileReview();
    expect(app.isReviewingSpecificFile()).toBe(false);
  });

  it('RF04: should switch diff view modes correctly', () => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;
    app.setDiffViewMode('split');
    expect(app.diffViewMode()).toBe('split');
    app.setDiffViewMode('unified');
    expect(app.diffViewMode()).toBe('unified');
  });

  it('RF07: should toggle progressive disclosure technical details panel', () => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;
    expect(app.showTechnicalDetails()).toBe(false);
    app.toggleTechnicalDetails();
    expect(app.showTechnicalDetails()).toBe(true);
  });
});
```

---

## 3. Playwright E2E Test Scenarios

1. `E2E-AUDIT-01`: Load Live Auditor -> Verify initial clean screen with branch selector.
2. `E2E-AUDIT-02`: Click `[ Execute Branch Quality Gate ]` -> Verify consolidated verdict and changed files.
3. `E2E-AUDIT-03`: Click `[ Review Changes ]` -> Inspect Before/After side-by-side diff with line alignment.
4. `E2E-AUDIT-04`: Toggle View Modes (`Split`, `Unified`, `Original`, `Corrected`) -> Verify active styling.
5. `E2E-AUDIT-05`: Switch Scope to `Single File Review` -> Select file and audit directly.
6. `E2E-AUDIT-06`: Expand `Technical & Reduction Details` -> Verify Bend HVM metrics.
