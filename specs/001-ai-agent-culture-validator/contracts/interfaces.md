# Interfaces: AI Agent Culture Validator

---

## 1. Bend Algebraic Types

```bend
type TargetFile:
  TargetFile { name, lines_count, has_spec_tag, has_lazy_code, has_secrets, has_test_coverage, has_type_annotations }

type Violation:
  Violation { rule_id, file_name, severity, penalty, message }

type CultureReport:
  CultureReport { total_files, total_violations, p0_count, p1_count, p2_count, penalty_total, score, is_approved }
```
