# Architecture Specification: Extensible Rule Engine

**Spec ID**: `SPEC-006-ARCH`  
**Parent**: `SPEC-006`  
**Layer**: Clean Architecture Concentric Layers  

---

## 1. Concentric Layer Separation

The Extensible Rule Management engine follows the existing 4 concentric layers:

```mermaid
flowchart TD
    subgraph Layer4["Layer 4: Frameworks, Drivers & Interfaces"]
        UI["Angular 19 Standalone Rule Manager"]
        CLI["CLI Command Parser (culture_guard.py rules)"]
        REST["HTTP Server (guardian_server.py)"]
        CI["CI/CD Workflows (GitHub / GitLab / Bitbucket)"]
    end

    subgraph Layer3["Layer 3: Interface Adapters & Registry"]
        REG["Rule Registry (scripts/rule_registry.py)"]
        TEST["Rule Test Engine (scripts/rule_test_engine.py)"]
        NORM["Rule Normalizer (scripts/rule_normalizer.py)"]
        SAFE["Regex Safety & Sandboxing Engine"]
    end

    subgraph Layer2["Layer 2: Application Use Cases & Synthesis"]
        RESOLVE["Deterministic Precedence Resolver"]
        SYNTH["Dynamic Bend Harness Synthesizer"]
        CALC["Penalty & Score Engine (0-100)"]
        AUDIT["Audit Trail Logger (JSONL / Memory)"]
    end

    subgraph Layer1["Layer 1: Enterprise Core & HVM Engine"]
        HVM["Bend HVM Virtual Machine (guardian.bend)"]
        TREE["Binary Tree Parallel Reduction"]
        SCHEMA["Canonical Rules JSON Schema (rules_schema.json)"]
    end

    UI --> REST
    CLI --> REG
    REST --> REG
    CI --> REG
    REG --> NORM
    REG --> SAFE
    NORM --> TEST
    NORM --> RESOLVE
    RESOLVE --> SYNTH
    SYNTH --> HVM
    HVM --> CALC
    REG --> AUDIT
    REG --> SCHEMA
```

---

## 2. Rule Resolution & Precedence Architecture

The Rule Registry resolves the **Effective Rule Set** using deterministic bottom-up precedence:

```mermaid
flowchart TD
    B["1. Built-in Rules\n(backend/rules/builtin/, 2_rules/)"]
    O["2. Organization Rules\n(backend/rules/organization/)"]
    P["3. Project Rules\n(backend/rules/projects/)"]
    R["4. Repository / Custom Rules\n(backend/rules/custom/, .guardian/rules.json)"]

    B -->|Base Defaults| E["Effective Rule Set (Normalized)"]
    O -->|Override by ID / Severity / Status| E
    P -->|Override by ID / Scope| E
    R -->|Highest Precedence Override| E

    E --> NORM["Rule Normalizer"]
    NORM --> SYNTH["Harness Synthesizer"]
    SYNTH --> HVM["Bend HVM Parallel Evaluator"]
```

### Precedence Resolution Algorithm
1. Base definitions are loaded from **Built-in** manifests (`backend/rules/2_rules/` and `backend/rules/builtin/`).
2. **Organization-level** rules augment or override Built-in rules by exact `id` match.
3. **Project-level** rules augment or override Organization rules.
4. **Repository/Custom-level** rules possess highest precedence, allowing local teams to adjust severity, regex patterns, or disabled status.

---

## 3. Rule Lifecycle State Machine

```mermaid
stateDiagram-v2
    [*] --> DRAFT : Create Rule
    DRAFT --> TESTING : Provide Test Fixtures
    TESTING --> VALIDATED : Pass Rule Test Engine
    TESTING --> DRAFT : Fail Test Cases
    VALIDATED --> ACTIVE : Enable in Quality Gate
    ACTIVE --> DEPRECATED : Mark Obsolete
    ACTIVE --> TESTING : Update Pattern / Scope
    DEPRECATED --> ARCHIVED : Archive Rule
    ARCHIVED --> [*]
```

### Lifecycle State Policies:
- **DRAFT**: Rule under creation or editing. Excluded from CI/CD Quality Gate.
- **TESTING**: Rule with attached test fixtures. Can run within the isolated Rule Test Engine.
- **VALIDATED**: Schema-valid and passed 100% of test fixtures. Eligible for activation.
- **ACTIVE**: Fully active in the CI/CD Quality Gate, CLI audits, and dashboard live diff inspections.
- **DEPRECATED**: Emits advisory warning without failing the Quality Gate build.
- **ARCHIVED**: Stored for audit trail / history; never evaluated during audits.
