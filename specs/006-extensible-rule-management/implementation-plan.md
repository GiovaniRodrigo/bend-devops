# Implementation Plan: Extensible Rule Management

**Spec ID**: `SPEC-006-PLAN`  
**Parent**: `SPEC-006`  

---

## 1. Execution Steps & Milestones

1. **Schema & Models Evolution**:
   - Update `backend/rules/rules_schema.json` with multi-tier, extensible schemas.
   - Implement `scripts/rule_model.py` containing robust typed dataclasses.
2. **Rule Registry Core (`scripts/rule_registry.py`)**:
   - Central Registry with in-memory caching and JSON file persistence in `backend/rules/custom/`, `organization/`, `projects/`.
   - Precedence resolver: Builtin < Organization < Project < Custom.
   - ReDoS regex protection & input safety checks.
   - Audit trail logger with structured event records.
3. **Rule Normalizer & Test Engine**:
   - `scripts/rule_normalizer.py`: Canonical normalization for Bend and Python.
   - `scripts/rule_test_engine.py`: Isolated rule execution against code fixtures and inline pragmas.
4. **Bend Parallel Engine Integration**:
   - Update `scripts/culture_guard.py` harness synthesis to generate Bend AST expressions from resolved effective rules.
   - Add/verify Bend tests in `backend/tests/` preserving 100% pass rate.
5. **REST API (`scripts/guardian_server.py`)**:
   - Add all `/api/rules/*` endpoints (CRUD, validate, test, clone, enable/disable, import/export, categories, statuses, audit trail, healthz).
6. **CLI Subcommands (`scripts/culture_guard.py`)**:
   - Implement `guardian rules` subcommands (list, show, create, edit, clone, delete, enable, disable, validate, test, import, export, search).
7. **Angular 19 Frontend Dashboard**:
   - Update `culture.model.ts` and `culture-guardian.service.ts`.
   - Implement rich "Rules" management section with filterable catalog, details drawer, create/edit wizard, dynamic rule type forms, and interactive tester console.
8. **Automated Testing Suite**:
   - Python unit & integration tests (`tests/test_rule_registry.py`, `tests/test_rule_engine.py`, `tests/test_rule_api.py`, `tests/test_rule_cli.py`).
   - Playwright E2E tests capturing screenshots of rule management flows.
9. **Documentation Updates**:
   - Update `README.md`, `ARCHITECTURE.md`, `PIPELINE.md`, `RULES.md`, `QUICKSTART.md`, `INTEGRATIONS.md`, `CONTRIBUTING.md`.
   - Create `CUSTOM-RULES.md`, `RULE-AUTHORING.md`, `RULE-API.md`.
   - Update `docs/infra/relatorio-qualidade-infra.md` with Section 8.
10. **Full Validation (`scripts/validate.sh`)**:
    - Run end-to-end quality gate script and verify 0 regressions.
