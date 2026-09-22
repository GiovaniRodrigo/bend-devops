# FRONTEND_COVERAGE_MATRIX.md: Backend vs Frontend Capability Coverage Matrix

**Project**: Bend DevOps Guardian (CodeConform Dashboard)  
**Audit Date**: 2026-09-22  
**Total User-Facing Capabilities**: 10  
**Frontend Representation Coverage**: 100% (10/10)  
**Real Data Integration**: 100% (10/10)  
**Automated Test Coverage**: 100% (10/10 Covered by Vitest)  

---

## 1. Feature Coverage Matrix

| Feature Domain | Backend Real Capability | Frontend UI Representation | Real Data Source | Automated Test | Status |
| :--- | :--- | :--- | :---: | :---: | :---: |
| **Culture Quality Standards** | Rules `CULT01`..`CULT05` | Rules Manifests & Results View | `culture_standards.json` | `app.spec.ts` (Tests 4, 5, 6) | **COMPLETE** |
| **Layer Boundary Invariants** | Rules `ARCH-LAYER-01`..`04`, `ARCH-FE-01` | Rules Manifests & Live Auditor | `layer_boundaries.json` | `app.spec.ts` (Tests 4, 5) | **COMPLETE** |
| **Architecture Profiles** | 8 Manifest Profiles | Dashboard & Auditor Dropdown | `1_architectures/*.json` | `app.spec.ts` (Tests 1, 4) | **COMPLETE** |
| **Layer Vocabulary Taxonomy** | Universal Token Taxonomy | Layer Taxonomy Explorer Tab | `layer_vocabulary.json` | `app.spec.ts` (Test 9) | **COMPLETE** |
| **Multi-Language Lexing** | C#, Python, TS, PHP, Go, Java, Rust | Multi-Language Code Editor | `token_filter.py` logic | `app.spec.ts` (Test 4) | **COMPLETE** |
| **Inline Pragma Suppressions** | `@guardian-ignore [RULE]: [reason]` | Live Auditor & Diagnostics | `token_filter.py` logic | `app.spec.ts` (Test 4) | **COMPLETE** |
| **VCS Webhook Gateway** | Unified Webhook Ingestion | VCS & Webhook Simulator Tab | `webhook_gateway.py` logic | `app.spec.ts` (Test 7) | **COMPLETE** |
| **Branch Gating Policies** | Strict main vs Permissive feature | Policy Selector & Gating Matrix | `policy_engine.py` logic | `app.spec.ts` (Test 7) | **COMPLETE** |
| **SARIF & Quality Exports** | OASIS SARIF v2.1.0 & CodeQuality | Header & Modal Export Viewers | `github_adapter.py` logic | `app.spec.ts` (Test 8) | **COMPLETE** |
| **Session Audit Telemetry** | Session audit log & Score metrics | History Tab & Metric KPI Cards | Reactive Angular Signals | `app.spec.ts` (Tests 3, 5) | **COMPLETE** |

---
