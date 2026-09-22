# Tests Specification: False-Positive Elimination & Exemption Engine

---

## 1. Coverage Matrix

| ID | Description | Test Type | Criticality | Status |
| :--- | :--- | :--- | :--- | :--- |
| **RF01** | Method/Function Name False Positive Filtering (`get_img()`, `select_item()`) | Unit | 🔴 P0 | ✅ Covered via TDD |
| **RF02** | Comments & Docstring Stripping (SQL/HTML in comments ignored) | Unit | 🔴 P0 | ✅ Covered via TDD |
| **RF03** | Inline Pragma Suppression (`@guardian-ignore RULE_ID: Reason`) | Unit | 🔴 P0 | ✅ Covered via TDD |
| **RF04** | Project-Level `.guardianignore` File Path Matching | Unit | 🔴 P0 | ✅ Covered via TDD |
| **RF05** | Mandatory Justification Validation (Warn if reason omitted) | Unit | 🟠 P1 | ✅ Covered via TDD |
| **RN01** | Missing Rationale on `@guardian-ignore` Emits `P1_WARNING` | Unit | 🟠 P1 | ✅ Covered via TDD |

---

## 2. Test Execution Commands

```bash
# Run all false-positive and suppression tests
python3 -m unittest discover -s tests -p "test_*.py"

# Run all VCS adapter tests
python3 -m unittest discover -s tests/vcs -p "test_*.py"

# Run end-to-end quality gate script
./scripts/validate.sh
```
