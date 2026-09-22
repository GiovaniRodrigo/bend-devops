# CI Workflow Templates: Multi-Platform CI/CD Pipelines

---

## 1. GitHub Actions (`.github/workflows/guardian.yml`)

```yaml
name: Architecture & Culture Guardian Gate

on:
  pull_request:
    branches: [ main, master, develop ]
  push:
    branches: [ main ]

jobs:
  guardian-gate:
    name: Culture & Layer Quality Gate
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

      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install Dependencies
        run: |
          python -m pip install --upgrade pip

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

## 2. GitLab CI/CD (`.gitlab-ci.yml`)

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

## 3. Bitbucket Pipelines (`bitbucket-pipelines.yml`)

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
