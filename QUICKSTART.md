# ⚡ Quickstart & Execution Guide: Bend DevOps Guardian

This guide covers setup, prerequisites, local execution, CLI commands, dashboard launching, and CI/CD quality gate enforcement.

---

## 📋 1. Prerequisites

Ensure the following tools are installed in your environment:
- **Rust Toolchain**: `rustup default stable`
- **Bend & HVM**: 
  ```bash
  cargo install bend-lang hvm
  ```
- **Python**: 3.10+ (tested on Python 3.12)
- **Node.js & npm**: Node.js 20+ (for Angular Dashboard)

---

## 🚀 2. Universal Validation Suite

To run all 8 quality gate stages end-to-end (Bend type checks, Bend unit/integration tests, Angular test suite & production build, false-positive filters, VCS adapter tests, and CLI audits):

```bash
./scripts/validate.sh
```

---

## 🛠️ 3. CLI Audit in DevOps Pipelines

The CLI tool [`scripts/culture_guard.py`](./scripts/culture_guard.py) is the primary entry point for running audits locally or inside CI/CD pipelines.

### 3.1. Audit Codebase Directories or Files
```bash
# Audit a single file
python3 scripts/culture_guard.py src/Domain/Order.cs

# Audit entire source tree
python3 scripts/culture_guard.py src/ backend/

# Specify an architectural profile (layered_mvc, clean_architecture, microservices, cqrs, rest_api, frontend_clean)
python3 scripts/culture_guard.py src/ --architecture clean_architecture
```

### 3.2. Output Formats
```bash
# Default text terminal summary
python3 scripts/culture_guard.py src/

# Export structured JSON report
python3 scripts/culture_guard.py src/ --format json > report.json

# Export formatted Markdown summary
python3 scripts/culture_guard.py src/ --format markdown > report.md
```

### 3.3. Configurable Quality Gate Thresholds
```bash
# Require a minimum score of 90/100 to pass (default: 80)
python3 scripts/culture_guard.py src/ --min-score 90
```

### 3.4. Multi-Platform CI/CD VCS Mode
```bash
# GitHub Actions (reads GITHUB_TOKEN and PR context)
python3 scripts/culture_guard.py --vcs github

# GitLab CI/CD (reads GITLAB_TOKEN / CI_JOB_TOKEN)
python3 scripts/culture_guard.py --vcs gitlab

# Bitbucket Pipelines (reads BITBUCKET_TOKEN)
python3 scripts/culture_guard.py --vcs bitbucket
```

### 3.5. Rule Management CLI Commands (`guardian rules`)
```bash
# List all resolved rules across all tiers
python3 scripts/culture_guard.py rules list

# Inspect rule specification
python3 scripts/culture_guard.py rules show CULT01

# Search rules by keyword
python3 scripts/culture_guard.py rules search secret

# Validate a custom rule against schema and ReDoS safety
python3 scripts/culture_guard.py rules validate backend/rules/custom/my_rule.json

# Test a rule against an inline code snippet
python3 scripts/culture_guard.py rules test CULT01 --code "def fn(): pass"

# Clone an existing rule
python3 scripts/culture_guard.py rules clone ARCH-LAYER-01 ARCH-LAYER-01-CUSTOM --name "Custom Presentation Boundary"

# Export and import rule manifests
python3 scripts/culture_guard.py rules export all --out rules_backup.json
python3 scripts/culture_guard.py rules import rules_backup.json --overwrite
```

---

## 🅰️ 4. Running the Angular Web Dashboard

The Angular 19 dashboard provides visual metrics, interactive rules inspection, and real-time PR diff simulation.

```bash
# Navigate to frontend directory and install dependencies
cd frontend
npm install

# Start local dev server
npm start

# Open http://localhost:4200 in your browser
```

---

## 🧪 5. Running Test Suites Directly

```bash
# 1. Bend Rule Unit Tests
bend run-rs backend/tests/test_rules.bend

# 2. Bend Parallel Engine Integration Tests
bend run-rs backend/tests/test_engine.bend

# 3. Python Rule Registry, API, CLI & False-Positive Tests
python3 -m pytest tests/ -v

# 4. Multi-Platform VCS Adapter Tests
python3 -m pytest tests/vcs/ -v

# 5. Angular Production Build
cd frontend && npm run build
```

---

## 🔗 Related Documentation
- [Clean Architecture & System Design](./ARCHITECTURE.md)
- [4-Tier Pipeline Specification](./PIPELINE.md)
- [Extensible Custom Rules Guide](./CUSTOM-RULES.md)
- [Rule Authoring & Schema Reference](./RULE-AUTHORING.md)
- [Rule REST API Reference](./RULE-API.md)
- [Multi-Platform VCS Integrations](./INTEGRATIONS.md)
- [Engineering Standards & Rules Catalog](./RULES.md)
- [Contributor Guidelines](./CONTRIBUTING.md)
