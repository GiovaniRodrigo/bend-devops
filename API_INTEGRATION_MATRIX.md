# API_INTEGRATION_MATRIX.md: Service Contracts & API Integration Matrix

**Project**: Bend DevOps Guardian (CodeConform Dashboard)  
**Audit Date**: 2026-09-22  
**Integration Paradigm**: High-Performance Direct In-Memory Service & Ingested VCS Adapters  

---

## 1. System Integration Points

| Integration Endpoint / Contract | Protocol / Format | Request Payload | Response / Output | Frontend Consumer | Status |
| :--- | :--- | :--- | :--- | :--- | :---: |
| `CultureGuardianService.auditCode` | In-Memory Functional AST | `(fileName, code, hasTestFile, author, branch, profile)` | `FileAuditInfo` with `CodeViolation[]` and `activeSuppressions` | Live Code & Diff Auditor (`app.ts:133`) | **CONNECTED** |
| `CultureGuardianService.generateReport` | In-Memory Reduction Engine | `FileAuditInfo[]` | `AuditReport` (score, p0Count, p1Count, isApproved) | Computed Signal `currentReport` | **CONNECTED** |
| `CultureGuardianService.generateSarifJson` | OASIS SARIF v2.1.0 Standard | `AuditReport` | Compliant SARIF JSON string | Export Modal / SARIF Exporter | **CONNECTED** |
| `CultureGuardianService.generateGitLabCodeQualityJson` | Code Climate JSON Standard | `AuditReport` | `gl-code-quality-report.json` array | Export Modal / GitLab Exporter | **CONNECTED** |
| `CultureGuardianService.generateBitbucketCodeInsightsJson` | Bitbucket Code Insights REST 2.0 | `AuditReport` | Bitbucket Insight report payload | Export Modal / Bitbucket Exporter | **CONNECTED** |
| `CultureGuardianService.generateGitHubMarkdownSummary` | GitHub REST v3 PR Reviews | `(report, repo, prNumber)` | Markdown string with Secret Masking (RN02) | Export Modal / PR Reviewer | **CONNECTED** |
| `WebhookGateway.parse_webhook` | HTTP Ingestion Headers & Body | `(headers, payload)` | Standardized `WebhookEventPayload` | VCS Simulator (`app.ts:182`) | **CONNECTED** |
| `BranchPolicyEngine.evaluate_policy` | Policy Invariant Rules | `(branch, report)` | `PolicyResult` (`isBlocked`, `violationsCount`) | Policy Engine Simulator | **CONNECTED** |

---
