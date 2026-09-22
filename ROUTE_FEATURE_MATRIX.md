# ROUTE_FEATURE_MATRIX.md: Frontend View & Navigation Route Matrix

**Project**: Bend DevOps Guardian (CodeConform Dashboard)  
**Audit Date**: 2026-09-22  
**Navigation Model**: Angular 19 Reactive Signal-Driven Single-Page Application (SPA)  
**Total Interactive Views**: 7  

---

## 1. Route / Tab Navigation Map

| View Identifier | Tab State (`activeTab`) | Primary Feature Focus | UX Controls & Actions | Associated Services & Contracts | Status |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **View 1: Dashboard** | `'dashboard'` | Executive Quality Overview | Metric KPI cards, Profile badges, Latest audit summary card, CTA to Live Auditor | `CultureGuardianService.rules`, `architectureProfiles` | **COMPLETE** |
| **View 2: Live Auditor** | `'analyze'` | Interactive Source Code & Diff Scanner | Language presets, Architecture profile selector, Branch policy selector, Multi-line code editor, Audit execution CTA | `CultureGuardianService.auditCode`, `matchesToken`, `stripComments` | **COMPLETE** |
| **View 3: Audit Results** | `'results'` | Violation Diagnostics & Remediation | Search filter by keyword, Severity filter (All, P0, P1), Violation cards with snippets and remediation guidance, Export CTAs | `AuditReport`, `CodeViolation[]`, `generateSarifJson`, `generateGitHubMarkdownSummary` | **COMPLETE** |
| **View 4: Rules Manifests** | `'rules'` | Declarative Rules Manifest Catalog | Real-time rule search, Category and severity filters, Enforce/Disable toggle pill buttons | `CultureGuardianService.rules()`, `rules_schema.json` | **COMPLETE** |
| **View 5: Layer Taxonomy** | `'vocabulary'` | Universal Layer Vocabulary Explorer | Keyword search, Layer classification cards (Domain, Application, Infrastructure, Presentation), Forbidden boundary tags | `CultureGuardianService.layerVocabulary()`, `layer_vocabulary.json` | **COMPLETE** |
| **View 6: VCS Simulator** | `'vcs'` | Multi-Platform Webhook & Policy Tester | Platform selector (GitHub, GitLab, Bitbucket), Event header input, Webhook simulation dispatcher, Branch policy viewer | `WebhookGateway`, `BranchPolicyEngine` | **COMPLETE** |
| **View 7: Session History** | `'history'` | Audit Telemetry & Session Log | Audit run list, Score badges, Run details viewer, Export History JSON downloader | `App.history()`, `App.exportHistory()` | **COMPLETE** |

---
