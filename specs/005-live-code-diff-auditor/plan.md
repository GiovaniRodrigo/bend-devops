# Implementation Plan: Live Code & Diff Auditor

This plan outlines the architecture, layers, and concrete file modifications to implement and validate the **Live Code & Diff Auditor** workflow for **Bend DevOps Guardian**.

---

## 1. Files to Create / Modify

### 1.1. Specification Layer (`specs/005-live-code-diff-auditor/`)
* **`specs/005-live-code-diff-auditor/spec.md`**: Functional & non-functional requirements, use scenarios, acceptance criteria, Mermaid diagrams.
* **`specs/005-live-code-diff-auditor/plan.md`**: Implementation plan and technical strategy.
* **`specs/005-live-code-diff-auditor/data-model.md`**: Domain models (`AuditScope`, `FileDiff`, `DiffHunk`, `DiffLine`, `QualityGateVerdict`, `BranchSummary`).
* **`specs/005-live-code-diff-auditor/research.md`**: Architecture analysis, Git diff algorithms, Bend AST integration.
* **`specs/005-live-code-diff-auditor/tasks.md`**: Actionable tasks in TDD sequence.
* **`specs/005-live-code-diff-auditor/tests.md`**: Test matrix and specification skeletons.
* **`specs/005-live-code-diff-auditor/quickstart.md`**: Setup and verification guide.
* **`specs/005-live-code-diff-auditor/contracts/interfaces.md`**: TypeScript & Python contract definitions.

### 1.2. Backend & Interface Adapters Layer (`scripts/`, `tests/`)
* **`scripts/vcs_adapters/diff_parser.py`**: Extend Git diff parsing engine to support structured diff files, additions, deletions, renames, and hunk line tracking.
* **`scripts/culture_guard.py`**: Ensure CLI and audit runner support `--diff` and `--branch` delta analysis modes with full `@spec` tagging.
* **`tests/vcs/test_diff_parser.py`**: TDD unit tests for Git diff parser covering added, deleted, renamed files, empty diffs, and multiple hunks.

### 1.3. Frontend & UI Layer (`frontend/src/app/`)
* **`frontend/src/app/app.ts`**: State signals (`auditScope`, `branchSummary`, `isReviewingSpecificFile`, `diffViewMode`, `activeTab`), analysis methods, and computed verdicts.
* **`frontend/src/app/app.html`**: Clean branch-first template, progressive disclosure accordions, side-by-side Before/After diff viewer with line alignment.
* **`frontend/src/app/app.spec.ts`**: Comprehensive Vitest unit test suite validating all user journeys.
* **`tests/e2e/capture_screenshots.py`**: Playwright E2E automation for visual verification across all auditor states.

---

## 2. Technical Strategy

### 2.1. Clean Architecture Alignment
The Live Code & Diff Auditor adheres to Clean Architecture:
- **Domain Layer**: Bend AST rules in `backend/src/guardian.bend` define architectural constraints and penalties.
- **Application Layer**: Use cases (`AnalyzeBranchDelta`, `AuditSingleFile`, `EvaluateQualityGate`) orchestrate rules and aggregations.
- **Interface Adapters**: `diff_parser.py` and `CultureGuardianService` transform VCS diff formats and AST outputs into normalized diff structures.
- **Frameworks & Drivers**: Angular 19 signals UI and CLI interface provide presentation and command execution.

### 2.2. Changed-Line Semantics
In unified diff patches:
- Lines starting with `+` are new/added code and undergo architecture rule scanning.
- Lines starting with `-` are deleted code and do not trigger new violations.
- Lines starting with ` ` (space) are unchanged context and advance line numbering without being audited.

### 2.3. Progressive Disclosure
To eliminate visual noise and adhere to the 3-second comprehension principle:
1. **Initial Screen**: Only shows Scope Switcher (`Branch Analysis` vs. `Single File`) and the primary Action CTA.
2. **Post-Analysis Screen**: Shows the Consolidated Verdict Card, Changed Files List, and drill-down CTAs.
3. **Drill-Down Screen**: Shows synchronized side-by-side Before/After diff viewer.
4. **Secondary Panel**: Technical HVM and AST details are placed under `▸ Technical & Reduction Details` accordion.

---

## 3. Dependencies & Prerequisites

- Python 3.10+ with standard library (`re`, `json`, `unittest`).
- Node.js 20+ and Angular CLI 19.
- Vitest and Playwright test runners installed in `frontend/` and project root.
- Bend compiler (`bend`) installed and functional.

---

## 4. Risk Matrix & Mitigations

| Risk | Impact | Mitigation |
| :--- | :--- | :--- |
| Large diffs causing browser lag | Medium | Virtualized / chunked diff rendering and collapsible hunks. |
| Inaccurate line offset in multi-hunk diffs | High | Strict unit tests in `test_diff_parser.py` validating cumulative hunk offsets. |
| Preexisting violations flagged in unmodified lines | High | Strict changed-line filter (`extract_changed_lines`) isolating additions only. |
| UI state desynchronization on navigation | Low | Reactive Angular signals (`computed` & `signal`) guaranteeing single source of truth. |
