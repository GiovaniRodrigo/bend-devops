# 🌐 Multi-Platform VCS Integrations

Enforce Bend DevOps Guardian quality gates on Pull Requests and commits in GitHub Actions, GitLab CI/CD, and Bitbucket Pipelines.

---

## 1. CI/CD Pipeline Configurations

### GitHub Actions ([`.github/workflows/guardian.yml`](./.github/workflows/guardian.yml))

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
      - name: Run Guardian Audit
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: python3 scripts/culture_guard.py --vcs github --min-score 80
      - name: Upload SARIF
        if: always()
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: guardian-report.sarif
```

### GitLab CI/CD ([`.gitlab-ci.yml`](./.gitlab-ci.yml))

```yaml
stages: [quality-gate]

guardian_quality_gate:
  stage: quality-gate
  image: python:3.11-slim
  script:
    - python3 scripts/culture_guard.py --vcs gitlab --min-score 80
  artifacts:
    reports:
      codequality: gl-code-quality-report.json
    when: always
```

### Bitbucket Pipelines ([`bitbucket-pipelines.yml`](./bitbucket-pipelines.yml))

```yaml
image: python:3.11
pipelines:
  pull-requests:
    '**':
      - step:
          name: Guardian Gate
          script:
            - python3 scripts/culture_guard.py --vcs bitbucket --min-score 80
```

---

## 2. Environment Variables

| Variable | Platform | Scope / Permissions |
| :--- | :--- | :--- |
| `GITHUB_TOKEN` | GitHub Actions | `checks:write`, `pull-requests:write`, `security-events:write` |
| `GITLAB_TOKEN` / `CI_JOB_TOKEN` | GitLab CI/CD | `api`, `write_discussion` |
| `BITBUCKET_TOKEN` | Bitbucket Pipelines | `repository:read`, `pullrequests:write`, `reports:write` |
