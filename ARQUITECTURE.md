# 🏛️ Architecture & System Design

For the complete **Clean Architecture**, runtime characteristics, parallel reduction model, and component topology documentation, please refer to:

👉 **[`ARCHITECTURE.md`](./ARCHITECTURE.md)**

---

## ⚡ Clean Architecture Summary

The **Bend DevOps Guardian** is structured according to **Clean Architecture** concentric layers:
- **Layer 1 (Enterprise Core)**: Pure algebraic types and functional rule evaluators in [`backend/src/guardian.bend`](./backend/src/guardian.bend) and [`backend/rules/layer_vocabulary.json`](./backend/rules/layer_vocabulary.json).
- **Layer 2 (Application Use Cases)**: Dynamic AST harness synthesis, parallel binary tree reduction, and DevOps quality score calculation.
- **Layer 3 (Interface Adapters)**: Multi-platform VCS adapters for GitHub, GitLab, Bitbucket in [`scripts/vcs_adapters/`](./scripts/vcs_adapters/), syntactic token boundary filter in [`scripts/token_filter.py`](./scripts/token_filter.py), and SARIF exporters.
- **Layer 4 (Frameworks & Drivers)**: CLI gate runner [`scripts/culture_guard.py`](./scripts/culture_guard.py), CI/CD pipelines, and Angular 19 dashboard in [`frontend/`](./frontend/).

See [`ARCHITECTURE.md`](./ARCHITECTURE.md) for detailed diagrams and full specifications.
