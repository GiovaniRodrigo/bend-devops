# Rules Schema: DevOps Standards & Architecture Quality Gate

---

## 1. Rule Format

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "version": "1.0.0",
  "manifesto_name": "DevOps Engineering Culture & Quality Standards Manifesto",
  "rules": [
    {
      "id": "CULT01",
      "name": "Zero Lazy Code & Complete Implementation",
      "severity": "P0_BLOCKING",
      "penalty_points": 35,
      "description": "Prohibits incomplete code in production branches.",
      "rationale": "Engineering standards require complete implementations without hidden operational gaps.",
      "remediation": "Implement the logic completely or split into tracked issues."
    }
  ]
}
```
