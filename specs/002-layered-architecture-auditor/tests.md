# Tests Specification: Universal 4-Tier Architecture Guardian

---

## 1. Universal Coverage Matrix

| Rule ID | Category / Requirement | Target Stacks | Criticality |
| :--- | :--- | :--- | :--- |
| **ARCH-LAYER-01** | Zero presentation HTML/tags (`<img>`, `<div>`, `<script>`) in Domain/Controllers | C#, Python, TS, Go, PHP, Java, Rust | 🔴 P0_BLOCKING |
| **ARCH-LAYER-02** | Zero direct database queries (`SELECT`, `DbContext`, `objects.filter()`) in Views | Razor, Jinja, Blade, JSX, HTML | 🔴 P0_BLOCKING |
| **ARCH-LAYER-03** | Zero transport coupling (`HttpContext`, `express.Request`, `request()`) in Domain | ASP.NET, FastAPI, Express, Laravel | 🔴 P0_BLOCKING |
| **ARCH-LAYER-04** | Thin Controllers & Application Service delegation | Multi-stack | 🟠 P1_WARNING |
| **ARCH-FE-01** | Zero direct network calls (`fetch`, `axios`) in Presentational UI components | React, Angular, Vue | 🔴 P0_BLOCKING |
| **CULT01** | Lazy code & unfinished TODOs (`TODO`, `FIXME`, `pass`) | Multi-stack | 🔴 P0_BLOCKING |
| **CULT02** | Requirement traceability tag (`@spec RFxx`) presence | Multi-stack | 🟠 P1_WARNING |
| **CULT03** | Automated test coverage file association | Multi-stack | 🔴 P0_BLOCKING |
| **CULT04** | Hardcoded secrets and API keys | Multi-stack | 🔴 P0_BLOCKING |
| **CULT05** | Strict type annotations on functions | Python, TypeScript | 🟠 P1_WARNING |

---

## 2. Test Execution Commands

```bash
# 1. Bend Rule Engine Unit Tests
bend run-rs backend/tests/test_rules.bend

# 2. Bend Parallel Engine Integration Tests
bend run-rs backend/tests/test_engine.bend

# 3. Angular Frontend Test Suite
cd frontend && npm run test -- --watch=false

# 4. CLI Scanner Verification
python3 scripts/culture_guard.py examples/compliant_agent_output.py examples/test_compliant_agent_output.py
```
