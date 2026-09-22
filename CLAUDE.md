# Project Guidelines: Bend DevOps Guardian (`bend-devops`)

This repository serves as the **automated quality gate and architecture compliance engine for CI/CD pipelines and pull requests**. Every code modification submitted to the repository is validated by this engine built in **Bend** (massively parallel HVM reduction) and monitored visually via the **Angular Web Dashboard**.

---

## 🏛️ Non-Negotiable DevOps & Architecture Principles

1. **Zero Lazy Code (`CULT01` - Blocking P0)**: Never leave `TODO`, `FIXME`, `pass`, or incomplete functional stubs in pull requests.
2. **Mandatory Spec Traceability (`CULT02` - Warning P1)**: Every core module must declare `@spec RFxx` mapping back to requirements in `specs/`.
3. **Test Pyramid (`CULT03` - Blocking P0)**: No production code is accepted without automated unit/integration tests.
4. **Zero Hardcoded Secrets (`CULT04` - Blocking P0)**: API keys, tokens, or plaintext credentials trigger an immediate merge block.
5. **Strict Typing (`CULT05` - Warning P1)**: Explicit parameter and return type declarations across all public functions.
6. **Layer Separation (`ARCH-LAYER-01` to `ARCH-LAYER-04` - Blocking P0)**: Strict separation of concerns (no frontend markup in Models/Controllers, no queries in Views, no transport in Domain).

---

## 🛠️ Development & Validation Commands

```bash
# Complete end-to-end 8-stage validation (Bend + Angular + VCS + Filters + CLI)
./scripts/validate.sh

# Backend / Bend Engine
bend check backend/src/guardian.bend
bend run-rs backend/tests/test_rules.bend
bend run-rs backend/tests/test_engine.bend
bend run-rs backend/src/guardian.bend

# Frontend Angular (Dashboard)
npm run dev               # Start local development server from workspace root
cd frontend && npm run dev # Or directly from frontend directory
npm run build             # Production build for Angular dashboard
npm test -- --watch=false # Run Angular unit tests with Vitest

# CLI Audit & CI/CD Gating
python3 scripts/culture_guard.py <file_paths>
python3 scripts/culture_guard.py --vcs github
python3 scripts/culture_guard.py --format json <file_paths>
```

---

## 📂 Directory Structure

- `frontend/`: Web Dashboard in **Angular 19** (Standalone Components, Signals, Vitest).
- `backend/`: Functional engine in **Bend** (`backend/src/guardian.bend`), tests (`backend/tests/`), and 4-tier rule manifests (`backend/rules/`).
- `specs/`: Formal specifications following the Spec-Driven Development (SDD) standard.
- `scripts/`: CLI orchestrator, token boundary filters, and VCS adapters (`scripts/culture_guard.py`, `scripts/validate.sh`, `scripts/vcs_adapters/`).
- `tests/`: Automated TDD Python test suite for VCS adapters, token filters, and suppression pragmas.
- `examples/`: Compliant and non-compliant code samples for quality gate verification.
- `.github/workflows/`, `.gitlab-ci.yml`, `bitbucket-pipelines.yml`: Multi-platform CI/CD automation pipelines.
