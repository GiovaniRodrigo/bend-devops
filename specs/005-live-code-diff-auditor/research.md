# Research: Live Code & Diff Auditor

This document consolidates research on Git diff formats, parallel AST evaluation via Bend HVM, cognitive UX patterns for code review, and state management in Angular 19.

---

## 1. Existing Patterns in the Repository

| Pattern / Component | Location | Relevance |
| :--- | :--- | :--- |
| **Git Diff Parser** | `scripts/vcs_adapters/diff_parser.py` | Unified diff line number extraction and hunk parsing. |
| **4-Tier Standards Engine** | `scripts/culture_guard.py` | AST parsing, token filtering, and DevOps standards scoring. |
| **Bend Parallel AST** | `backend/src/guardian.bend` | High-performance tree reduction across architecture layers. |
| **VCS Adapters** | `scripts/vcs_adapters/` | GitHub, GitLab, and Bitbucket payload handlers and comment formatters. |
| **Angular Signals UI** | `frontend/src/app/app.ts` | Reactive state management with zero-overhead reactivity. |

---

## 2. Git Unified Diff Format Analysis

A standard Git patch produced by `git diff origin/main...HEAD` adheres to the following grammar:

```diff
diff --git a/path/to/old.cs b/path/to/new.cs
index 1234567..89abcdef 100644
--- a/path/to/old.cs
+++ b/path/to/new.cs
@@ -old_start,old_count +new_start,new_count @@
 context line (space)
-deleted line (minus)
+added line (plus)
```

### Edge Cases in Git Diffs:
1. **New File Mode**: `--- /dev/null`, `+++ b/path/to/file`, lines are all additions.
2. **Deleted File Mode**: `--- a/path/to/file`, `+++ /dev/null`, lines are all deletions.
3. **Renamed File**: `similarity index 100%`, `rename from old.cs`, `rename to new.cs`.
4. **Binary Files**: `Binary files a/img.png and b/img.png differ`.

---

## 3. Cognitive UX Patterns: Progressive Disclosure

Code review tools often overwhelm engineers with excessive metadata. Following the **3-Second Comprehension Model**:
1. **Primary Area (Instant Focus)**: Scope switch (`Branch Changes` vs. `Single File`) and Action CTA (`Analyze Branch`).
2. **Result Area**: Clear verdict badge (`APPROVED` in green or `BLOCKED` in red) with key counts.
3. **Inspection Area**: Side-by-side diff with synchronized scroll, highlighting only actionable violations.
4. **Secondary Area (Progressive Disclosure)**: Technical metadata (HVM reduction depths, raw AST tokens, execution timings) hidden under collapsible panels.

---

## 4. Architectural Decisions

### Decision 1: Client-Side Synchronized Line Alignment
- **Option A**: Render raw monospaced text block without line correlation.
- **Option B**: Structured side-by-side lines with paired row index and rule markers.
- **Decision**: **Option B**. Allows exact line alignment, inline rule callouts, and clean Before/After remediation rendering.

### Decision 2: Scope-Driven State Machine
- **Option A**: Global unstructured flags.
- **Option B**: Strongly-typed Angular signals (`auditScope`, `branchSummary`, `isReviewingSpecificFile`, `diffViewMode`).
- **Decision**: **Option B**. Guarantees determinism, avoids race conditions, and eliminates UI flicker.
