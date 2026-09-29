# 📖 Bend DevOps Guardian — Usage Guide

> Complete CLI, Web Dashboard, rule management, and CI/CD operations reference for Bend DevOps Guardian.

---

## 🧭 Table of Contents

- [1. Prerequisites & Installation](#1-prerequisites--installation)
- [2. CLI Auditor (`culture_guard.py`)](#2-cli-auditor-culture_guardpy)
- [3. Rule Management CLI (`rules`)](#3-rule-management-cli-rules)
- [4. Web Dashboard & Server](#4-web-dashboard--server)
- [5. CI/CD Pipeline Gates](#5-cicd-pipeline-gates)
- [6. Suppression Pragmas (`@guardian-ignore`)](#6-suppression-pragmas-guardian-ignore)
- [7. Practical Recipes](#7-practical-recipes)
- [8. Exit Codes & Troubleshooting](#8-exit-codes--troubleshooting)

---

## 1. Prerequisites & Installation

### Toolchains
- **Rust & Bend**: `cargo install bend-lang hvm`
- **Python**: `3.10+` (`pip install -r requirements.txt`)
- **Node.js**: `20+` (`cd frontend && npm install`)

### Validation
```bash
# Run full 8-stage test suite
./scripts/validate.sh
```

---

## 2. CLI Auditor (`culture_guard.py`)

### Synopsis
```bash
python3 scripts/culture_guard.py [paths...] [OPTIONS]
```

### Options Reference

| Flag | Values / Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `paths` | Positional | `.` | Target files or directories to audit. |
| `--architecture` | `layered_mvc`, `clean_architecture`, `microservices`, `cqrs`, `rest_api`, `frontend_clean` | `layered_mvc` | Architectural profile. |
| `--branch` | String | `None` | Target git branch for branch gating policy (`main`, `develop`, etc.). |
| `--format` | `text`, `json`, `markdown` | `text` | Output format. |
| `--min-score` | Integer (`0-100`) | `80` | Minimum score required to pass quality gate. |
| `--vcs` | `github`, `gitlab`, `bitbucket` | `None` | VCS provider for CI/CD status posting and annotations. |
| `--include-build-dirs` | Flag | `False` | Include `bin`, `obj`, `dist`, `node_modules` in scan. |
| `--mock-scenario` | `clean-repository`, `architecture-violations`, `blocked-quality-gate`, etc. | `None` | Run deterministic fixture scenario. |

### Common Examples
```bash
# Audit repository with Clean Architecture
python3 scripts/culture_guard.py src/ --architecture clean_architecture

# Export JSON report
python3 scripts/culture_guard.py src/ --format json > report.json

# Export Markdown summary for PR comment
python3 scripts/culture_guard.py src/ --format markdown > report.md

# Enforce strict score of 90 on main branch
python3 scripts/culture_guard.py src/ --branch main --min-score 90
```

---

## 3. Rule Management CLI (`rules`)

### Subcommands

| Command | Usage | Description |
| :--- | :--- | :--- |
| `list` | `rules list [--severity P0] [--tier custom] [--json]` | List resolved rules. |
| `show` | `rules show <RULE-ID> [--json]` | Show full rule definition. |
| `search` | `rules search <query>` | Search rules by keyword. |
| `validate` | `rules validate <file.json>` | Validate schema & ReDoS safety. |
| `test` | `rules test <RULE-ID> --code "..." [--json]` | Test rule against code snippet. |
| `create` | `rules create <file.json>` | Register new custom rule. |
| `edit` | `rules edit <RULE-ID> <file.json>` | Update existing rule. |
| `clone` | `rules clone <SRC> <NEW-ID> [--name "..."]` | Clone rule to new ID. |
| `delete` | `rules delete <RULE-ID> [--force]` | Remove rule. |
| `enable` / `disable` | `rules enable <RULE-ID>` / `rules disable <RULE-ID>` | Toggle rule status. |
| `export` | `rules export [all\|RULE-ID] [--out file.json]` | Export rule(s) to JSON. |
| `import` | `rules import <file.json> [--overwrite]` | Import rules manifest. |

### Examples
```bash
# List all active P0 rules
python3 scripts/culture_guard.py rules list --severity P0 --active-only

# Validate and test a rule
python3 scripts/culture_guard.py rules validate backend/rules/custom/my_rule.json
python3 scripts/culture_guard.py rules test CULT01 --code "def fn(): pass"

# Clone and customize a built-in rule
python3 scripts/culture_guard.py rules clone ARCH-LAYER-01 ARCH-LAYER-01-CUSTOM --name "Custom Layer Rule"
```

---

## 4. Web Dashboard & Server

### Unified Server (`guardian_server.py`)
Serves the REST API and compiled Angular frontend:
```bash
# Start server (default: port 4200)
python3 scripts/guardian_server.py --port 4200

# Start in mock scenario mode
python3 scripts/guardian_server.py --port 4200 --mock --scenario clean-repository
```

### Frontend Development
```bash
# Run Angular dev server with hot reload
npm run dev
# Dashboard available at http://localhost:4200
```

### Build Production Assets
```bash
npm run build
```

---

## 5. CI/CD Pipeline Gates

### GitHub Actions (`.github/workflows/guardian.yml`)
```yaml
name: Bend DevOps Guardian Gate
on: [push, pull_request]

jobs:
  guardian-gate:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
      checks: write
      security-events: write
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Run Guardian Gate
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: python3 scripts/culture_guard.py --vcs github --min-score 80
      - name: Upload SARIF
        if: always()
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: guardian-report.sarif
```

### GitLab CI/CD (`.gitlab-ci.yml`)
```yaml
stages: [quality-gate]

guardian_gate:
  stage: quality-gate
  image: python:3.11-slim
  script:
    - python3 scripts/culture_guard.py --vcs gitlab --min-score 80
  artifacts:
    reports:
      codequality: gl-code-quality-report.json
    when: always
```

### Bitbucket Pipelines (`bitbucket-pipelines.yml`)
```yaml
image: python:3.11
pipelines:
  pull-requests:
    '**':
      - step:
          name: Guardian Quality Gate
          script:
            - python3 scripts/culture_guard.py --vcs bitbucket --min-score 80
```

---

## 6. Suppression Pragmas (`@guardian-ignore`)

To exempt a line from a rule, prefix it with a documented inline pragma:

```csharp
// @guardian-ignore ARCH-LAYER-01: Legacy email template migration helper
public string RenderHeader() => "<div class='header'></div>";
```

```python
# @guardian-ignore ARCH-LAYER-02: Test database seeding script
def seed(): db.execute("SELECT * FROM seeds")
```

```typescript
// @guardian-ignore ARCH-FE-01: Canvas DOM manipulation utility
const canvas = document.createElement("canvas");
```

> [!IMPORTANT]
> A descriptive justification after `:` is **mandatory**. Undocumented suppressions trigger a `P1_WARNING`.

### File Exemption (`.guardianignore`)
Create `.guardianignore` in the project root:
```gitignore
fixtures/**
tests/mocks/**
[ARCH-LAYER-02] src/Database/Migrations/**
```

---

## 7. Practical Recipes

### Recipe 1: Pre-Commit Hook
```bash
#!/usr/bin/env bash
# .git/hooks/pre-commit
python3 scripts/culture_guard.py --min-score 85 || exit 1
```

### Recipe 2: Create Custom Rule
```bash
# 1. Create rule manifest
cat << 'EOF' > backend/rules/custom/SEC-CUSTOM-01.json
{
  "id": "SEC-CUSTOM-01",
  "name": "No Hardcoded DB Password",
  "category": "security",
  "type": "pattern",
  "severity": "P0",
  "tier": "custom",
  "status": "ACTIVE",
  "enabled": true,
  "condition": { "pattern": "db_password\\s*=\\s*['\"][^'\"]+['\"]" },
  "message": "Hardcoded database password found.",
  "suggestion": "Use os.environ.get('DB_PASSWORD')."
}
EOF

# 2. Validate and test
python3 scripts/culture_guard.py rules validate backend/rules/custom/SEC-CUSTOM-01.json
python3 scripts/culture_guard.py rules test SEC-CUSTOM-01 --code "db_password = 'secret'"

# 3. Register
python3 scripts/culture_guard.py rules create backend/rules/custom/SEC-CUSTOM-01.json
```

---

## 8. Exit Codes & Troubleshooting

| Exit Code | Meaning | Cause |
| :---: | :--- | :--- |
| `0` | **PASSED** | Quality Gate Approved (No P0 violations and score >= `--min-score`). |
| `1` | **FAILED** | Quality Gate Blocked (P0 violation detected OR score < `--min-score`). |
| `2` | **ERROR** | Configuration or runtime argument error. |

### Troubleshooting
- `bend: command not found`: Run `cargo install bend-lang hvm` and verify `$PATH`.
- `Undocumented pragma`: Add a reason after `:` in `@guardian-ignore RULE: <reason>`.
- `ReDoS warning`: Remove nested regex quantifiers (e.g. `(a+)+`) from rule patterns.
