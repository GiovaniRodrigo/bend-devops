# 🌐 Multi-Platform VCS Integrations (GitHub, GitLab, Bitbucket)

The **Bend DevOps Guardian** natively integrates with major Git hosting platforms to enforce quality gates on Pull Requests and Merge Requests.

---

## 🛠️ Platform Support Matrix

| Feature | GitHub Actions | GitLab CI/CD | Bitbucket Pipelines |
| :--- | :---: | :---: | :---: |
| **Commit Status Checks** | ✅ Supported | ✅ Supported | ✅ Supported |
| **PR / MR Comments** | ✅ Supported | ✅ Supported | ✅ Supported |
| **Inline Diff Annotations** | ✅ Check Runs API | ✅ Code Quality JSON | ✅ Code Insights API |
| **SARIF v2.1.0 Artifacts** | ✅ Supported | ⚠️ Converted | ⚠️ Converted |
| **Code Quality Reports** | ⚠️ SARIF | ✅ `gl-code-quality-report.json` | ⚠️ Code Insights |
| **Incremental Diff Scans** | ✅ Supported | ✅ Supported | ✅ Supported |

---

## 🐙 1. GitHub Actions Integration

### 1.1. Workflow Setup ([`.github/workflows/guardian.yml`](./.github/workflows/guardian.yml))

```yaml
name: Bend DevOps Guardian Gate

on:
  pull_request:
    branches: [ main, develop ]
  push:
    branches: [ main ]

jobs:
  guardian-gate:
    name: DevOps Standards & Architecture Quality Gate
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
      checks: write
      security-events: write

    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up Python 3.12
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Execute Guardian Gate Audit
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          python3 scripts/culture_guard.py --vcs github

      - name: Upload SARIF Report
        if: always()
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: guardian-report.sarif
```

---

## 🦊 2. GitLab CI/CD Integration

### 2.1. Pipeline Setup ([`.gitlab-ci.yml`](./.gitlab-ci.yml))

```yaml
stages:
  - quality-gate

guardian_quality_gate:
  stage: quality-gate
  image: python:3.11-slim
  variables:
    GIT_DEPTH: "0"
  script:
    - python3 scripts/culture_guard.py --vcs gitlab
  artifacts:
    reports:
      codequality: gl-code-quality-report.json
    when: always
  rules:
    - if: $CI_PIPELINE_SOURCE == 'merge_request_event'
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
```

---

## 🪣 3. Bitbucket Pipelines Integration

### 3.1. Pipeline Setup ([`bitbucket-pipelines.yml`](./bitbucket-pipelines.yml))

```yaml
image: python:3.11

pipelines:
  pull-requests:
    '**':
      - step:
          name: Bend DevOps Guardian
          script:
            - python3 scripts/culture_guard.py --vcs bitbucket
```

---

## 🔐 Environment Variables & Tokens

| Environment Variable | Target Platform | Description |
| :--- | :--- | :--- |
| `GITHUB_TOKEN` | GitHub Actions | Default workflow token with `checks:write` & `pull-requests:write` |
| `GITLAB_TOKEN` / `CI_JOB_TOKEN` | GitLab CI/CD | Pipeline token for posting MR discussion notes and commit statuses |
| `BITBUCKET_TOKEN` | Bitbucket Pipelines | Repository or workspace access token with Code Insights write access |

---

## 🔗 Related Documentation
- [Clean Architecture & System Design](./ARCHITECTURE.md)
- [Quickstart & CLI Usage](./QUICKSTART.md)
- [4-Tier Pipeline Specification](./PIPELINE.md)
- [Engineering Standards & Rules Catalog](./RULES.md)
- [Contributor Guidelines](./CONTRIBUTING.md)
