# Project Guidelines: Bend DevOps Guardian (`bend-devops`)

Automated quality gate and architecture compliance engine on **Bend** (HVM) with **Angular 19** Web Dashboard.

---

## 🏛️ Core Principles

1. **Zero Lazy Code (`CULT01` - P0)**: No `TODO`, `FIXME`, or empty `pass` stubs in PRs.
2. **Spec Traceability (`CULT02` - P1)**: Declare `@spec RFxx` mapping to `specs/`.
3. **Mandatory Tests (`CULT03` - P0)**: Automated test coverage required for production code.
4. **Zero Secrets (`CULT04` - P0)**: No API keys or credentials in source.
5. **Strict Typing (`CULT05` - P1)**: Type annotations on public signatures.
6. **Layer Isolation (`ARCH-LAYER-01..04` - P0)**: Strict Clean Architecture boundaries.

---

## 🛠️ Key Commands

```bash
# Full validation suite
./scripts/validate.sh

# CLI Audit
python3 scripts/culture_guard.py src/ --architecture clean_architecture

# Rules CLI
python3 scripts/culture_guard.py rules list --active-only
python3 scripts/culture_guard.py rules test CULT01 --code "def fn(): pass"

# Dashboard & Server
python3 scripts/guardian_server.py --port 4200
npm --prefix frontend start
```
