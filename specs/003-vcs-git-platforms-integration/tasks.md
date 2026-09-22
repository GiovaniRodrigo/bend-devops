# Tasks: Multi-Platform VCS Integration (TDD Workflow)

---

## Task List

### Phase 1: Git Diff & Delta Analysis (TDD)
- [x] 1. Create Unit Tests for Git Diff Parser (`tests/vcs/test_diff_parser.py`)
- [x] 2. Implement Git Diff Parser & Hunk Line Extractor (`scripts/vcs_adapters/diff_parser.py`)

### Phase 2: GitHub Actions & Check Runs Integration (TDD)
- [x] 3. Create Unit Tests for GitHub Adapter & SARIF Exporter (`tests/vcs/test_github_adapter.py`)
- [x] 4. Implement GitHub Adapter & Inline Annotations (`scripts/vcs_adapters/github_adapter.py`)
- [x] 5. Create GitHub Action Workflow Configuration (`.github/workflows/guardian.yml`)

### Phase 3: GitLab CI/CD & Code Quality Integration (TDD)
- [x] 6. Create Unit Tests for GitLab Adapter & Code Quality JSON (`tests/vcs/test_gitlab_adapter.py`)
- [x] 7. Implement GitLab Adapter & MR Notes Notifier (`scripts/vcs_adapters/gitlab_adapter.py`)
- [x] 8. Create GitLab CI Template Configuration (`.gitlab-ci.yml`)

### Phase 4: Bitbucket Pipelines & Code Insights (TDD)
- [x] 9. Create Unit Tests for Bitbucket Adapter & Insights Report (`tests/vcs/test_bitbucket_adapter.py`)
- [x] 10. Implement Bitbucket Adapter & Status Check Publisher (`scripts/vcs_adapters/bitbucket_adapter.py`)
- [x] 11. Create Bitbucket Pipelines Template Configuration (`bitbucket-pipelines.yml`)

### Phase 5: Unified CLI & Orchestrator Integration (TDD)
- [x] 12. Create Integration Tests for `--vcs` CLI Flag (`tests/vcs/test_unified_cli.py`)
- [x] 13. Connect VCS Adapters to `scripts/culture_guard.py` CLI Dispatcher
- [x] 14. Run Full Quality Gate Suite (`./scripts/validate.sh`)
