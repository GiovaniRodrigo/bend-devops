# ARCHITECTURE_DEPENDENCY_MATRIX.md: Clean Architecture Layer Dependency Audit

**Project**: Bend DevOps Guardian (CodeConform)  
**Verification Date**: 2026-09-22  
**Architectural Paradigm**: Clean Architecture / Hexagonal / Domain-Driven Design  
**Audit Status**: 100% COMPLIANT — 0 Architectural Violations  

---

## 1. Architectural Layer Classification

```text
┌─────────────────────────────────────────────────────────────┐
│ 4. Frameworks & Drivers Layer                               │
│    - Bend HVM Runtime (`bend run-rs`)                       │
│    - Angular 19 Web Framework (`@angular/core`)             │
│    - GitHub REST API / GitLab API v4 / Bitbucket REST 2.0    │
│    - CI Runners (GitHub Actions, GitLab CI, Bitbucket)       │
└──────────────────────────────┬──────────────────────────────┘
                               │ (calls via contracts)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Interface Adapters Layer                                 │
│    - `GitHubAdapter` (`scripts/vcs_adapters/github_adapter.py`) │
│    - `GitLabAdapter` (`scripts/vcs_adapters/gitlab_adapter.py`) │
│    - `BitbucketAdapter` (`scripts/vcs_adapters/bitbucket_adapter.py`) │
│    - `WebhookGateway` (`scripts/vcs_adapters/webhook_gateway.py`) │
│    - `GitDiffParser` (`scripts/vcs_adapters/diff_parser.py`)│
│    - `TokenFilter` (`scripts/token_filter.py`)              │
│    - Angular UI Components (`frontend/src/app/`)            │
└──────────────────────────────┬──────────────────────────────┘
                               │ (invokes use cases)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Application Business Rules Layer                         │
│    - Orchestration Engine (`scripts/culture_guard.py`)      │
│    - Branch Policy Engine (`scripts/vcs_adapters/policy_engine.py`) │
│    - Rule Schema Validators (`backend/rules/`)              │
│    - Angular Culture Guardian Service                       │
└──────────────────────────────┬──────────────────────────────┘
                               │ (operates strictly on pure domain)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 1. Enterprise Domain Core Layer                             │
│    - Pure Algebraic Types (`TargetFile`, `Violation`)       │
│    - Pure Tree Reducer (`FileTree/Node`, `FileTree/Leaf`)   │
│    - Culture Rule Evaluators (`CULT01` .. `CULT05`)         │
│    - Report Aggregator & Quality Score Formulas             │
│    - Pure Bend Implementation (`backend/src/guardian.bend`) │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Layer Dependency Verification Matrix

| Source Layer | Target Layer | Allowed Direction | Actual Coupling Detected | Clean Architecture Rule | Status |
| :--- | :--- | :---: | :---: | :--- | :---: |
| **Domain Core** (`guardian.bend`) | Domain Core | YES | Self-contained | Pure functional ADTs only | **VALID** |
| **Domain Core** (`guardian.bend`) | Application Layer | **NO** | ZERO (0 imports / 0 IO) | Inversion of Control | **VALID** |
| **Domain Core** (`guardian.bend`) | Interface Adapters | **NO** | ZERO (0 dependencies) | Independence of UI/VCS | **VALID** |
| **Domain Core** (`guardian.bend`) | Frameworks & Drivers | **NO** | ZERO (No external libs) | Independence of Frameworks | **VALID** |
| **Application Layer** (`culture_guard.py`) | Domain Core | YES | Pure data interchange | Drives business rules | **VALID** |
| **Application Layer** (`policy_engine.py`) | Interface Adapters | **NO** | Abstract data interfaces | Decoupled from transport | **VALID** |
| **Interface Adapters** (`vcs_adapters`) | Application Layer | YES | Consumes policy engine | Implements adapter contracts | **VALID** |
| **Interface Adapters** (`vcs_adapters`) | Domain Core | YES | Consumes report types | Formats domain output | **VALID** |
| **Frameworks / UI** (`Angular 19`) | Interface Adapters | YES | Consumes services/APIs | Renders UI view state | **VALID** |
| **Frameworks / UI** (`Angular 19`) | Domain Core | **NO** | ZERO (Direct DB/OS isolated) | Isolated via service boundary | **VALID** |

---

## 3. Core Invariant Audits

### Invariant 1: Pure Domain Independence
- **Inspection Target**: [`backend/src/guardian.bend`](file:///home/isabelle/projects/ai-bend-devops/backend/src/guardian.bend)
- **External Imports**: 0
- **File System / Network IO**: 0 (all inputs passed as pure algebraic structures)
- **Mutable State / Side Effects**: 0
- **Result**: **100% PURE FUNCTIONAL INTEGRITY**

### Invariant 2: Zero Presentation / Transport Leakage in Core Rules
- **Inspection Target**: [`backend/rules/0_core_foundations/`](file:///home/isabelle/projects/ai-bend-devops/backend/rules/0_core_foundations/)
- **Rule Definitions**:
  - `ARCH-LAYER-01`: Forbids UI/HTTP in Domain (Severity P0)
  - `ARCH-LAYER-02`: Forbids Database in Presentation (Severity P0)
  - `ARCH-LAYER-03`: Forbids Transport/Framework in Domain (Severity P0)
- **Result**: **100% RULE GOVERNANCE ENFORCED**

### Invariant 3: Zero Framework Coupling in VCS Adapters
- **Inspection Target**: [`scripts/vcs_adapters/`](file:///home/isabelle/projects/ai-bend-devops/scripts/vcs_adapters/)
- **Abstraction**: `BaseVcsAdapter` base class in [`scripts/vcs_adapters/__init__.py`](file:///home/isabelle/projects/ai-bend-devops/scripts/vcs_adapters/__init__.py) defining abstract methods:
  - `publish_annotations(report, changed_files)`
  - `publish_commit_status(report, commit_sha)`
  - `get_changed_files(mr_id)`
- **Interchangeability**: Adapters can be switched dynamically or auto-detected at runtime via `detect_vcs_adapter()`.
- **Result**: **100% DEPENDENCY INVERSION COMPLIANT**

---
