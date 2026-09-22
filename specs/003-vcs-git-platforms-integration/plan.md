# Implementation Plan: Multi-Platform VCS Integration (GitHub, GitLab, Bitbucket)

This document details the technical strategy and file roadmap for integrating GitHub Actions, GitLab CI/CD, and Bitbucket Pipelines with the **Bend DevOps Guardian**.

---

## 1. Files and Components

### 1.1. Core VCS Adapters (`scripts/vcs_adapters/`)
* **`scripts/vcs_adapters/__init__.py`**: Adapter registry and common abstract base class.
* **`scripts/vcs_adapters/base_adapter.py`**: Base contract for commit status posting, PR commenting, and annotation parsing.
* **`scripts/vcs_adapters/github_adapter.py`**: GitHub REST & Check Runs API client, inline PR annotations, and SARIF exporter.
* **`scripts/vcs_adapters/gitlab_adapter.py`**: GitLab MR Notes API client and `gl-code-quality-report.json` exporter.
* **`scripts/vcs_adapters/bitbucket_adapter.py`**: Bitbucket Code Insights and Commit Status API client.
* **`scripts/vcs_adapters/diff_parser.py`**: Unified Git diff parser extracting modified line ranges.

### 1.2. CI/CD Pipeline Workflow Templates (`contracts/` and `.github/`, `.gitlab-ci.yml`, `bitbucket-pipelines.yml`)
* **`.github/workflows/guardian.yml`**: Official GitHub Action workflow.
* **`.gitlab-ci.yml`**: Official GitLab CI template.
* **`bitbucket-pipelines.yml`**: Official Bitbucket Pipelines template.

### 1.3. Automated TDD Test Suite (`tests/vcs/`)
* **`tests/vcs/test_diff_parser.py`**: Tests for patch hunk and changed lines extraction.
* **`tests/vcs/test_github_adapter.py`**: Unit tests with mocked GitHub REST/Check Runs API.
* **`tests/vcs/test_gitlab_adapter.py`**: Unit tests with mocked GitLab MR API and Code Quality generator.
* **`tests/vcs/test_bitbucket_adapter.py`**: Unit tests with mocked Bitbucket Code Insights API.
* **`tests/vcs/test_unified_cli.py`**: Integration tests for `--vcs [github|gitlab|bitbucket]`.

---

## 2. Technical Strategy (Test-Driven Development)

1. **Step 1 — Write Failing Tests**: Implement test fixtures in `tests/vcs/` for git diff parsing and platform payload serialization.
2. **Step 2 — Implement Base & Adapters**: Implement `BaseVcsAdapter`, `GitHubAdapter`, `GitLabAdapter`, and `BitbucketAdapter`.
3. **Step 3 — Wire into CLI Scanner**: Connect `scripts/culture_guard.py` to auto-detect CI environments or accept `--vcs`.
4. **Step 4 — Verify Green CI Suite**: Execute `./scripts/validate.sh` and ensure all unit tests pass with exit code 0.

---

## 3. Risks & Mitigations

| Risk | Impact | Mitigation |
| :--- | :--- | :--- |
| VCS API rate limiting | Medium | Implement exponential retry with jitter on HTTP 429/503. |
| Large monorepo diff overhead | Medium | Use `git diff --name-only` and stream hunk line ranges. |
| Secret leakage in PR comments | High | Strictly redact matched token patterns (`CULT04`) before generating markdown tables. |
