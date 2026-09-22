# Research & Technical References: Multi-Platform VCS Integration

---

## 1. Platform-Specific Integration APIs

### 1.1. GitHub API & Check Runs
- **Check Runs REST API**: `POST /repos/{owner}/{repo}/check-runs` allows sending structured annotations with `path`, `start_line`, `annotation_level` (`failure`, `warning`, `notice`), and `message`.
- **SARIF Standard**: GitHub natively ingests SARIF v2.1.0 (Static Analysis Results Interchange Format) into the GitHub Security / Code Scanning tab.
- **Pull Request Comments**: `POST /repos/{owner}/{repo}/issues/{issue_number}/comments`.

### 1.2. GitLab CI/CD & Code Quality
- **GitLab Code Quality Report**: Standard JSON array containing objects with `description`, `fingerprint`, `severity` (`blocker`, `critical`, `major`, `minor`, `info`), and `location: { path, lines: { begin } }`.
- **Merge Request Notes API**: `POST /projects/{id}/merge_requests/{merge_request_iid}/notes` posts markdown summaries to MR discussions.
- **Commit Status API**: `POST /projects/{id}/statuses/{sha}` sets pipeline build state.

### 1.3. Bitbucket Pipelines & Code Insights
- **Code Insights Reports**: `PUT /2.0/repositories/{workspace}/{repo_slug}/commit/{commit}/reports/{report_key}` creates a report container.
- **Code Insights Annotations**: `POST /2.0/repositories/{workspace}/{repo_slug}/commit/{commit}/reports/{report_key}/annotations` adds line-level findings.
- **Commit Status API**: `POST /2.0/repositories/{workspace}/{repo_slug}/commit/{commit}/statuses/build`.

---

## 2. Alternatives Considered

| Alternative | Evaluation | Decision |
| :--- | :--- | :--- |
| **CLI-Only Output (No API Calls)** | Only reports to stdout; maintainers must check raw CI logs. | Rejected: Fails to provide native PR comments or inline annotations. |
| **Dedicated SaaS Cloud Service** | Requires external servers, database infrastructure, and billing. | Rejected: Self-hosted script adapter running directly within runner context is faster, free, and more secure. |
| **Unified CLI Runner + Native VCS Adapters** | Direct runner integration via Python + Bend with environment variable auto-detection. | **Chosen**: Lightweight, zero-infrastructure, and runs in any CI runner. |
