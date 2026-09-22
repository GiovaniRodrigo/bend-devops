# Implementation Plan: Universal 4-Tier Architecture & Layer Guardian

---

## 1. Files Created and Managed

### 1.1. 4-Tier Modular Rules Catalog (`backend/rules/`)
* **[`1_architectures/`](../../backend/rules/1_architectures/)**: Architecture profiles:
  - `layered_mvc.json` / `layered_mvc.md`
  - `clean_architecture.json` / `clean_architecture.md`
  - `microservices.json` / `microservices.md`
  - `cqrs_event_sourcing.json` / `cqrs_event_sourcing.md`
  - `rest_api.json` / `rest_api.md`
  - `frontend_clean.json` / `frontend_clean.md`
* **[`2_rules/`](../../backend/rules/2_rules/)**: Abstract boundary and culture rules:
  - `layer_boundaries.json`: Rules `ARCH-LAYER-01` through `ARCH-LAYER-04`.
  - `culture_standards.json`: Rules `CULT01` through `CULT05`.
* **[`3_languages/`](../../backend/rules/3_languages/)**: Language-specific AST/token adapters:
  - `csharp.json`, `python.json`, `typescript.json`, `php.json`, `golang.json`, `java.json`, `rust.json`.
* **[`4_scanner/`](../../backend/rules/4_scanner/)**: Engine execution and scanner configuration:
  - `scanner_config.json`, `pipeline_definition.md`.
* **[`layer_vocabulary.json`](../../backend/rules/layer_vocabulary.json)** / **[`layer_vocabulary.md`](../../backend/rules/layer_vocabulary.md)**: Token and tag vocabulary taxonomy.
* **[`README.md`](../../backend/rules/README.md)**: Central catalog index and documentation.

### 1.2. Functional Core & Engine (`backend/src/` & `backend/tests/`)
* **[`backend/src/guardian.bend`](../../backend/src/guardian.bend)**: Pure functional algebraic types (`TargetFile`, `Violation`, `FileTree`, `CultureReport`) and parallel reduction algorithms on HVM.
* **[`backend/tests/test_rules.bend`](../../backend/tests/test_rules.bend)**: Functional unit test suite for rules.
* **[`backend/tests/test_engine.bend`](../../backend/tests/test_engine.bend)**: Integration test suite for parallel tree reductions.

### 1.3. CLI & Orchestration (`scripts/`)
* **[`scripts/culture_guard.py`](../../scripts/culture_guard.py)**: Multi-stack layer classifier, token inspection, and Bend engine harness compiler.
* **[`scripts/validate.sh`](../../scripts/validate.sh)**: End-to-end CI/CD quality gate script.

### 1.4. Web Dashboard (`frontend/`)
* **[`frontend/src/app/`](../../frontend/src/app/)**: Angular 19 dashboard with real-time audit visualization, rules explorer, and Vitest test suite.

---

## 2. Technical Strategy & Decisions

1. **4-Tier Pipeline**: Decouple architectural topology from rules, language syntax, and scanner reduction.
2. **Token Taxonomy**: Model tokens (HTML tags, SQL, ORM, HTTP Context) as declarative sets with forbidden target layer boundaries.
3. **Massively Parallel Reduction**: Represent files as binary `FileTree` evaluated simultaneously on HVM.

---

## 3. Risks & Mitigations

| Risk | Impact | Mitigation |
| :--- | :--- | :--- |
| False positives on generic names | Medium | Combine directory path matching with strict token regex sets. |
| Mixed-language monorepos | Low | Language adapters trigger based on file extensions. |
