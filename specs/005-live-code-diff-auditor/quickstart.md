# Quickstart: Live Code & Diff Auditor

Guide for running, testing, and verifying the Live Code & Diff Auditor locally.

---

## Prerequisites

- Python 3.10+
- Node.js 20+ and npm
- Bend compiler (`bend`) installed and available in `$PATH`

---

## Verification Steps

### 1. Run Backend & VCS Unit Tests
```bash
python3 -m unittest discover tests
```

### 2. Run Angular Frontend Tests (Vitest)
```bash
cd frontend && npm test
```

### 3. Build Angular Application
```bash
cd frontend && npm run build
```

### 4. Run Playwright E2E Visual Verification Suite
```bash
python3 tests/e2e/capture_screenshots.py
```

### 5. Run Full 8-Stage End-to-End Validation
```bash
./scripts/validate.sh
```

---

## Expected Output

```text
🎉 ALL VALIDATIONS (BEND + ANGULAR + VCS + FILTERS + CLI) PASSED SUCCESSFULLY! 100% OPERATIONAL.
```
