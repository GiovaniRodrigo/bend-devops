# Implementation Plan: AI Agent Culture and Engineering Standards Validator

This document outlines the technical strategy for developing the core **AI Culture Guardian** evaluation engine and CI/CD orchestration.

---

## 1. Files to Create/Modify

### 1.1. Bend Functional Engine (`backend/src/`)
* **`backend/src/guardian.bend`**: Core algebraic types, pure rule checking functions, and parallel tree reduction.

### 1.2. Automated Tests (`backend/tests/`)
* **`backend/tests/test_rules.bend`**: Unit tests verifying each culture rule.
* **`backend/tests/test_engine.bend`**: Integration tests for parallel tree evaluation.

### 1.3. CLI & CI Orchestration (`scripts/`)
* **`scripts/culture_guard.py`**: Python CLI scanner, harness generator, and report printer.
* **`scripts/validate.sh`**: Universal end-to-end validation script.

---

## 2. Technical Decisions

- Purely functional divide-and-conquer binary trees (`FileTree`) for evaluating files simultaneously on HVM.
- Clean separation between I/O orchestration (Python CLI) and core evaluation (Bend).
