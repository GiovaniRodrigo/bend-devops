# Project Scan: Bend DevOps Guardian

**Date**: 2026-09-22  
**Repository**: `ai-bend-devops` (`GiovaniRodrigo/bend-devops`)  
**Lead Auditor**: Autonomous SDD Staff Software Engineer, Architect & QA Lead

---

## 1. Technology Stack

| Layer / Subsystem | Technology | Version / Runtime | Details |
| :--- | :--- | :--- | :--- |
| **Core Reduction Engine** | **Bend** | HVM (Rust runtime) | Pure functional AST reduction, interaction combinators, divide-and-conquer binary trees |
| **CLI & Interface Adapters** | **Python** | 3.11 / 3.12 | Standard library (`urllib`, `dataclasses`, `re`, `argparse`, `fnmatch`, `hashlib`) |
| **Frontend Web UI** | **Angular** | 19+ (21.x framework) | Standalone components, reactive Signals, Computed state, Tailwind CSS 3.4, Lucide icons |
| **Frontend Testing** | **Vitest** | 4.x / jsdom | Angular TestBed component and unit testing |
| **Backend Testing** | **Bend HVM & Python unittest** | Builtin / Rust | `bend run-rs`, `bend check`, `unittest` discovery |
| **VCS CI/CD Runners** | **GitHub Actions, GitLab CI, Bitbucket** | Docker / Ubuntu | SARIF v2.1.0, GitLab Code Quality JSON, Bitbucket Code Insights |

---

## 2. Repository Structure

```text
ai-bend-devops/
├── backend/
│   ├── rules/
│   │   ├── 1_architectures/     # Structural profile catalogs (MVC, Clean, Microservices, CQRS, REST, FE Clean)
│   │   ├── 2_rules/             # Abstract constraints (ARCH-LAYER-01..04, CULT01..05)
│   │   ├── 3_languages/         # Multi-stack syntax tokens (C#, Python, TS, PHP, Go, Java, Rust)
│   │   ├── 4_scanner/           # Engine configs and pipeline definitions
│   │   ├── layer_vocabulary.json# Canonical token containment taxonomy
│   │   └── rules_schema.json    # JSON Schema definition for all declarative rule manifests
│   ├── src/
│   │   └── guardian.bend        # Core functional algebraic types & HVM parallel tree reducer
│   └── tests/
│       ├── test_rules.bend      # Unit test suite for CULT01..CULT05 in Bend
│       └── test_engine.bend     # Integration test suite for parallel FileTree reduction in Bend
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── models/          # TypeScript contracts (CultureRule, LayerRule, LayerViolation, etc.)
│   │   │   ├── services/        # CultureGuardianService (mock MR presets, diff simulator, rule toggling)
│   │   │   ├── app.ts           # Root dashboard standalone component
│   │   │   ├── app.html         # Responsive layout (Dashboard, Analysis, Results, History, Rules tabs)
│   │   │   ├── app.css          # Styling overrides
│   │   │   └── app.spec.ts      # Vitest test suite for UI workflows
│   │   ├── styles.css           # Tailwind CSS directives
│   │   └── main.ts              # Angular bootstrap
│   ├── package.json             # NPM dependencies
│   └── tsconfig.json            # TypeScript configuration
├── scripts/
│   ├── culture_guard.py         # Main CLI gate runner and orchestrator
│   ├── token_filter.py          # Word boundary fence, comment stripper, pragma parser, .guardianignore
│   ├── validate.sh              # Universal 8-stage quality gate verification script
│   └── vcs_adapters/
│       ├── __init__.py          # Platform auto-detection & adapter factory
│       ├── base_adapter.py      # Abstract BaseVcsAdapter contract
│       ├── github_adapter.py    # GitHub Checks API, Check Runs, SARIF exporter
│       ├── gitlab_adapter.py    # GitLab CI/CD, MR notes, Code Quality JSON exporter
│       ├── bitbucket_adapter.py # Bitbucket Code Insights report & status publisher
│       ├── diff_parser.py       # Unified git diff & hunk line extractor
│       ├── policy_engine.py     # Branch policy engine (main/develop/feature branch rules)
│       └── webhook_gateway.py   # Unified webhook ingestion parser (GitHub, GitLab, Bitbucket)
├── specs/                       # Formal SDD Specifications
│   ├── 001-devops-standards-validator/
│   ├── 002-layered-architecture-auditor/
│   ├── 003-vcs-git-platforms-integration/
│   └── 004-false-positive-suppression-engine/
├── tests/                       # Automated Test Suites
│   ├── test_false_positives.py  # Scanner false-positive prevention tests
│   ├── test_suppressions.py     # Inline pragmas (@guardian-ignore) and .guardianignore tests
│   ├── test_token_filter.py     # Token boundary fencing and multi-language comment stripping tests
│   └── vcs/
│       ├── test_bitbucket_adapter.py
│       ├── test_diff_parser.py
│       ├── test_github_adapter.py
│       ├── test_gitlab_adapter.py
│       ├── test_policy_engine.py
│       ├── test_unified_cli.py
│       └── test_webhook_gateway.py
├── .github/workflows/           # GitHub Actions workflows (guardian.yml, ci.yml)
├── .gitlab-ci.yml               # GitLab CI/CD pipeline template
├── bitbucket-pipelines.yml      # Bitbucket Pipelines template
├── package.json                 # Root project metadata & validation scripts
└── [Documentation Files]        # README.md, ARCHITECTURE.md, PIPELINE.md, INTEGRATIONS.md, RULES.md, etc.
```

---

## 3. Architecture & Data Flow

```text
[ Developer Commit / PR / MR ]
              ↓
[ VCS Platform (GitHub / GitLab / Bitbucket) ]
              ↓
[ CI Runner / CLI: scripts/culture_guard.py ]
              ↓
[ scripts/vcs_adapters/diff_parser.py ] ──> Extracts modified files & changed line numbers
              ↓
[ scripts/token_filter.py ] ──────────────> Word boundary fencing, comment stripping, @guardian-ignore & .guardianignore
              ↓
[ Synthesis: generate_bend_harness ] ─────> Builds algebraic FileTree AST
              ↓
[ HVM Runtime: backend/src/guardian.bend ]> Parallel binary tree reduction (CULT01..05, ARCH-LAYER-01..03)
              ↓
[ scripts/vcs_adapters/policy_engine.py ] > Evaluates branch-specific thresholds (e.g. main >= 90)
              ↓
[ VCS Dispatcher & Exporters ] ───────────> Posts Commit Status, SARIF, Code Quality JSON, PR Discussion Comments
              ↓
[ Angular Dashboard / Local Developer ] ─> Interactive triage & real-time compliance visualization
```

---

## 4. Modules & Subsystems

1. **Enterprise Core (Bend)**: Pure algebraic data types (`TargetFile`, `Violation`, `CultureReport`, `FileTree`) and purely functional rule evaluation.
2. **Lexical Analysis (Python)**: Multi-language comment stripper, word boundary regex matcher, inline pragma parser, project ignore parser.
3. **VCS Integrations (Python)**: Platform adapters for GitHub, GitLab, and Bitbucket; unified webhook gateway; git diff hunk extractor; branch policy engine.
4. **Declarative Rule Catalog (JSON)**: 6 architectural profiles, 9 abstract rules, 7 language adapters, and 1 token taxonomy validated against JSON schema.
5. **Interactive UI (Angular 19)**: Dashboard with live metrics, MR diff simulator, rule toggles, historical audit log, and violation drilldowns.

---

## 5. Security & Isolation

- **Zero Secret Exposure (`RN02`)**: Secret tokens extracted in audit are masked as `[***REDACTED***]` prior to emission in comments or logs.
- **Least-Privilege Token Integration**: Adapters require only granular scope tokens (`checks:write`, `pull-requests:write`).
- **Stateless Execution**: Pure functional HVM reduction ensures side-effect-free, deterministic execution with no shared mutable state.

---

## 6. Initial Findings & Compliance Assessment

- **Code Quality**: Zero critical TODOs, zero stubs, zero unhandled errors.
- **Spec Coverage**: All 4 specification suites in `specs/` are backed by implementations and test suites.
- **Validation Suite**: 8-stage verification pipeline (`./scripts/validate.sh`) executes cleanly in under 20 seconds.
