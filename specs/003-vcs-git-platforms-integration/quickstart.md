# Quickstart: Multi-Platform VCS Integration

Guide to configuring and executing the **AI Culture & Architecture Guardian** in GitHub Actions, GitLab CI/CD, and Bitbucket Pipelines.

---

## 1. Environment Variables

| Variable | Platform | Description |
| :--- | :--- | :--- |
| `GITHUB_TOKEN` | GitHub | GitHub Actions default token (`secrets.GITHUB_TOKEN`) |
| `GITLAB_TOKEN` | GitLab | GitLab CI job token or Project Access Token (`$CI_JOB_TOKEN` / `$GITLAB_TOKEN`) |
| `BITBUCKET_TOKEN` | Bitbucket | Bitbucket App Password or Repository Access Token (`$BITBUCKET_TOKEN`) |

---

## 2. Platform Pipeline Execution Examples

### 2.1. GitHub Actions (`.github/workflows/guardian.yml`)

```yaml
name: Architecture & Culture Guardian Gate

on:
  pull_request:
    branches: [ main, develop ]

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Run Guardian CI Gate
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          python3 scripts/culture_guard.py --vcs github
```

---

### 2.2. GitLab CI/CD (`.gitlab-ci.yml`)

```yaml
stages:
  - test
  - quality-gate

guardian_audit:
  stage: quality-gate
  image: python:3.11-slim
  script:
    - python3 scripts/culture_guard.py --vcs gitlab
  artifacts:
    reports:
      codequality: gl-code-quality-report.json
    when: always
```

---

### 2.3. Bitbucket Pipelines (`bitbucket-pipelines.yml`)

```yaml
image: python:3.11

pipelines:
  pull-requests:
    '**':
      - step:
          name: AI Culture & Architecture Guardian
          script:
            - python3 scripts/culture_guard.py --vcs bitbucket
```
