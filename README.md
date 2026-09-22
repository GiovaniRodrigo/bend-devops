# 🛡️ Bend DevOps Guardian (`bend-devops`)

> **High-Performance Architecture & Engineering Standards Quality Gate for DevOps CI/CD Pipelines.**
> Built with the purely functional and massively parallel **[Bend](https://github.com/HigherOrderCO/Bend)** (HVM) engine and an interactive **Angular 19** web dashboard.

---

## 🧭 Documentation Portal & Sitemap

The documentation for **Bend DevOps Guardian** is organized into specialized modular guides:

| Document | Description |
| :--- | :--- |
| 🏛️ **[`ARCHITECTURE.md`](./ARCHITECTURE.md)** | **Clean Architecture**, runtime characteristics, parallel HVM reduction model, and C4/Mermaid topology diagrams. |
| ⚡ **[`QUICKSTART.md`](./QUICKSTART.md)** | Step-by-step installation, prerequisites, CLI usage examples, and dashboard execution. |
| 🔬 **[`PIPELINE.md`](./PIPELINE.md)** | 4-Tier Declarative Pipeline (`1_architectures`, `2_rules`, `3_languages`, `4_scanner`) and Token Taxonomy matrix. |
| 🌐 **[`INTEGRATIONS.md`](./INTEGRATIONS.md)** | Multi-platform VCS setup for **GitHub Actions**, **GitLab CI/CD**, and **Bitbucket Pipelines**. |
| 📜 **[`RULES.md`](./RULES.md)** | Complete rules catalog (`CULT01..05`, `ARCH-LAYER-01..04`), severities, and inline suppression pragmas (`@guardian-ignore`). |
| 🤝 **[`CONTRIBUTING.md`](./CONTRIBUTING.md)** | Spec-Driven Development (SDD), Test-Driven Development (TDD) workflow, and commit standards. |

---

## 🎯 Overview & Philosophy

In modern high-velocity continuous integration and delivery (CI/CD) environments, rapid code modifications, architectural drift, incomplete stubs, missing automated tests, accidental credential leaks, and cross-tier boundary violations can silently compromise software reliability.

The **Bend DevOps Guardian** acts as an uncompromising automated quality gate embedded directly into DevOps workflows:
- **Massively Parallel Reduction**: Analyzes dozens of files and hundreds of rules simultaneously using functional binary tree reductions on the Bend High-Order Virtual Machine (HVM).
- **Multi-Platform CI/CD Gate**: Operates natively in **GitHub Actions**, **GitLab CI/CD**, and **Bitbucket Pipelines**, posting PR/MR comments, inline diff annotations, SARIF reports, and commit status checks.
- **Universal Architecture Taxonomy**: Enforces declarative architectural profiles (Layered MVC, Clean Architecture, Microservices, CQRS, REST APIs, Frontend Clean Architecture) across any tech stack (.NET, Python, TypeScript, PHP, Go, Java, Rust).
- **False-Positive Elimination**: Syntactic word boundary fencing, comment scoping, and inline documented suppression pragmas (`@guardian-ignore`).
- **Interactive DevOps Dashboard**: Visualizes pipeline compliance metrics, rules catalog, and real-time pull request diff simulations.

---

## 🧅 Clean Architecture Summary

The system strictly adheres to Clean Architecture with concentric layer isolation:
- **Layer 1 (Enterprise Core)**: Pure algebraic data types and functional rule evaluators in [`backend/src/guardian.bend`](./backend/src/guardian.bend) and [`backend/rules/layer_vocabulary.json`](./backend/rules/layer_vocabulary.json).
- **Layer 2 (Application Use Cases)**: Parallel binary tree reduction, harness synthesis, and quality score calculation.
- **Layer 3 (Interface Adapters)**: Multi-platform VCS adapters in [`scripts/vcs_adapters/`](./scripts/vcs_adapters/), syntactic token boundary filter in [`scripts/token_filter.py`](./scripts/token_filter.py), and SARIF exporters.
- **Layer 4 (Frameworks & Drivers)**: CLI gate runner [`scripts/culture_guard.py`](./scripts/culture_guard.py), CI/CD pipelines, and Angular 19 dashboard in [`frontend/`](./frontend/).

*For detailed architectural flowcharts and interaction sequence diagrams, see [`ARCHITECTURE.md`](./ARCHITECTURE.md).*

---

## 📁 Repository Structure

```
bend-devops/
├── backend/
│   ├── rules/                         # 🏛️ 4-Tier Declarative Catalog & Vocabulary
│   │   ├── 1_architectures/           # Architecture Profiles (MVC, Clean, Microservices, CQRS)
│   │   ├── 2_rules/                   # Abstract Boundary & Culture Rules
│   │   ├── 3_languages/               # Language Syntax & AST Adapters (C#, Py, TS, PHP, Go, Java, Rust)
│   │   ├── 4_scanner/                 # Scanner & Engine Configurations
│   │   ├── layer_vocabulary.json      # Complete Word, Tag & Token Taxonomy
│   │   ├── layer_vocabulary.md        # Comprehensive Layer Taxonomy Guide
│   │   └── rules_schema.json          # JSON Schema validating all manifests
│   ├── src/
│   │   └── guardian.bend              # Pure functional parallel AST tree evaluator
│   └── tests/
│       ├── test_rules.bend            # Rule engine functional unit tests
│       └── test_engine.bend           # Parallel tree reduction integration tests
├── scripts/
│   ├── culture_guard.py               # Universal CLI auditor & CI/CD gate orchestrator
│   ├── token_filter.py                # Syntactic boundary filter & pragma parser
│   ├── validate.sh                    # 8-stage end-to-end quality gate script
│   └── vcs_adapters/                  # GitHub, GitLab, and Bitbucket platform adapters
├── specs/                             # 📋 Spec-Driven Development (SDD) Specifications
│   ├── 001-devops-standards-validator/# Core Parallel HVM Engine Spec
│   ├── 002-layered-architecture-auditor/# 4-Tier Pipeline & Layer Vocabulary Spec
│   ├── 003-vcs-git-platforms-integration/# GitHub, GitLab, Bitbucket Integration Spec
│   └── 004-false-positive-suppression-engine/# False-Positive Elimination & Pragmas Spec
├── tests/                             # 🧪 Automated Python TDD Test Suite
│   ├── test_token_filter.py           # Token boundary tests
│   ├── test_suppressions.py           # Inline pragma tests
│   ├── test_false_positives.py        # False-positive scenario integration tests
│   └── vcs/                           # Multi-platform VCS adapter unit tests
├── frontend/                          # 🅰️ Angular 19 DevOps Quality Dashboard
│   ├── src/app/                       # Standalone Components, Models & Reactive Signals
│   └── package.json                   # Angular and Tailwind CSS dependencies
├── .github/workflows/guardian.yml     # GitHub Actions Quality Gate Workflow
├── .gitlab-ci.yml                     # GitLab CI/CD Quality Gate Pipeline
└── bitbucket-pipelines.yml            # Bitbucket Pipelines Quality Gate Configuration
```

---

## ⚡ Quickstart Commands

```bash
# 1. Run complete 8-stage validation suite
./scripts/validate.sh

# 2. Audit codebase via CLI
python3 scripts/culture_guard.py src/

# 3. Run in CI/CD mode with automated PR/MR commenting
python3 scripts/culture_guard.py --vcs github

# 4. Launch Angular 19 Dashboard
cd frontend && npm install && npm start
```

*For more details on CLI options and environment variables, refer to [`QUICKSTART.md`](./QUICKSTART.md).*
