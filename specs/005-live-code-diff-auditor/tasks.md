# Tasks: Live Code & Diff Auditor (Spec 005)

<!-- Ordered by execution dependency following TDD: Tests specified before implementation -->

- [x] 1. Spec Definition & Requirements Structuring (`specs/005-live-code-diff-auditor/spec.md`, `plan.md`, `data-model.md`, `research.md`)
- [x] 2. Unit Test Suite for Git Diff Parser Edge Cases (Added, Deleted, Renamed, Hunks) (`tests/vcs/test_diff_parser.py`)
- [x] 3. Git Diff Engine Implementation with Full Delta & Mode Support (`scripts/vcs_adapters/diff_parser.py`)
- [x] 4. Unit Test Suite for Angular Branch-First Auditor & State Machine (`frontend/src/app/app.spec.ts`)
- [x] 5. Implement Clean Branch-First Auditor UI with Progressive Disclosure (`frontend/src/app/app.ts`, `frontend/src/app/app.html`)
- [x] 6. Implement Synchronized Side-by-Side Before/After Diff Viewer with 4 View Modes (`frontend/src/app/app.ts`, `frontend/src/app/app.html`)
- [x] 7. E2E Playwright Automation & Visual Verification for All Auditor Scenarios (`tests/e2e/capture_screenshots.py`, `tests/e2e/test_playwright_e2e.py`)
- [x] 8. Full End-to-End Validation Run (`./scripts/validate.sh`)
