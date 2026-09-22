# Tests Specification: Multi-Platform VCS Integration

---

## 1. Coverage Matrix

| ID | Description | Test Type | Criticality | Status |
| :--- | :--- | :--- | :--- | :--- |
| **RF01** | GitHub Check Runs, Annotations & SARIF Export | Unit / Mock API | 🔴 P0 | ✅ Covered via TDD |
| **RF02** | GitLab Code Quality JSON & MR Note Posting | Unit / Mock API | 🔴 P0 | ✅ Covered via TDD |
| **RF03** | Bitbucket Code Insights & Build Status Checks | Unit / Mock API | 🔴 P0 | ✅ Covered via TDD |
| **RF04** | Git Diff Parser & Hunk Modified Lines Extraction | Unit | 🔴 P0 | ✅ Covered via TDD |
| **RF05** | Unified Webhook Gateway Request Routing | Unit | 🟠 P1 | ✅ Covered via TDD |
| **RF06** | Branch Policy Gating Logic (Strict vs Permissive) | Unit | 🔴 P0 | ✅ Covered via TDD |
| **RF07** | Markdown Comment Generation & Secret Redaction | Unit | 🔴 P0 | ✅ Covered via TDD |
| **RN01** | Commit Status Failure on P0 Violations | Integration | 🔴 P0 | ✅ Covered via TDD |
| **RN02** | Zero Secret Exposure in PR Comment Tables | Unit | 🔴 P0 | ✅ Covered via TDD |

---

## 2. Test Execution Commands

```bash
# Run all VCS TDD unit and integration tests
python3 -m unittest discover -s tests/vcs -p "test_*.py"

# Run end-to-end multi-tier pipeline validation
./scripts/validate.sh
```
