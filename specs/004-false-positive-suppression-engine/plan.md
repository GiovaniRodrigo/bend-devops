# Implementation Plan: False-Positive Elimination & Inline Exemption Engine

This document outlines the technical strategy for implementing word boundary fencing, comment scoping, and inline suppression pragmas in the **Bend DevOps Guardian**.

---

## 1. Files and Components

### 1.1. Core Filtering & Lexical Scoping Engine (`scripts/token_filter.py`)
* **`scripts/token_filter.py`**:
  - `strip_comments_and_docstrings(code, extension)`: Strips inline/block comments before token analysis.
  - `parse_inline_suppressions(code)`: Detects `@guardian-ignore <RULE_ID>: <reason>` and maps line numbers to ignored rules.
  - `is_syntactic_word_boundary_match(token, line, pattern)`: Ensures token matches only actual tags or standalone statements, not identifier substrings.

### 1.2. CLI Integration (`scripts/culture_guard.py`)
* **`scripts/culture_guard.py`**:
  - Integrate `token_filter.py` into `FileAuditResult._analyze(path)`.
  - Filter out suppressed violations from blocking penalties while preserving audit metadata.
  - Parse `.guardianignore` if present in repository root.

### 1.3. Automated TDD Test Suite (`tests/test_false_positives.py`)
* **`tests/test_false_positives.py`**:
  - Tests for method and variable names containing token substrings (`get_img()`, `select_box()`, `input_data()`).
  - Tests for inline suppression pragmas with valid vs missing justifications.
  - Tests for comments containing SQL or HTML examples without triggering violations.

---

## 2. Technical Strategy (Test-Driven Development)

1. **Step 1 — Write Failing Tests**: Implement test cases in `tests/test_false_positives.py` demonstrating false positive scenarios (e.g. `public string GetImageUrl()` being falsely flagged as `<img`).
2. **Step 2 — Implement Token Filter & Lexical Scoper**: Create `scripts/token_filter.py`.
3. **Step 3 — Integrate into Scanner**: Update `scripts/culture_guard.py`.
4. **Step 4 — Verify Green CI Suite**: Execute `./scripts/validate.sh`.
