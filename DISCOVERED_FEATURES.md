# DISCOVERED_FEATURES.md: Comprehensive Feature Inventory

**Project**: Bend DevOps Guardian (CodeConform)  
**Verification Date**: 2026-09-22  
**Audit Status**: 100% Discovered, Implemented, Tested & Verified  
**Total Discovered Features**: 29

---

## 1. Feature Catalog

### [FEAT-001] Algebraic TargetFile & Violation Types
- **Module**: Backend (Bend Pure Core)
- **Location**: [`backend/src/guardian.bend`](file:///home/isabelle/projects/ai-bend-devops/backend/src/guardian.bend#L7-L23)
- **Entrypoint**: `TargetFile/TargetFile`, `Violation/Violation`
- **User Visibility**: Internal / Core Engine
- **Business Rules**: Represents file metadata (line count, spec tag, lazy code, secrets, test coverage, strict typing) and violation instances (rule_id, file_name, severity, penalty, message) without runtime mutable state.
- **API**: Functional Algebraic Data Type constructor.
- **DB**: None (in-memory purely functional immutable representations).
- **External Integrations**: HVM runtime.
- **Existing Tests**: [`backend/tests/test_rules.bend`](file:///home/isabelle/projects/ai-bend-devops/backend/tests/test_rules.bend#L5-L18) (Passed).

---

### [FEAT-002] Pure Culture Rules Evaluator (CULT01..CULT05)
- **Module**: Backend (Bend Core)
- **Location**: [`backend/src/guardian.bend`](file:///home/isabelle/projects/ai-bend-devops/backend/src/guardian.bend#L29-L72)
- **Entrypoint**: `check_cult01_lazy_code`, `check_cult02_spec_traceability`, `check_cult03_test_coverage`, `check_cult04_secrets`, `check_cult05_strict_typing`
- **User Visibility**: CLI / Quality Gate
- **Business Rules**: 
  - CULT01: Rejects placeholder code (`TODO`, `FIXME`, `pass`, etc.) - P0 (Penalty: 35).
  - CULT02: Enforces `@spec RFxx` traceability tags - P1 (Penalty: 15).
  - CULT03: Requires automated unit/integration test presence - P0 (Penalty: 35).
  - CULT04: Rejects hardcoded API keys and secrets - P0 (Penalty: 40).
  - CULT05: Enforces strict type annotations - P1 (Penalty: 10).
- **API**: Pure Bend functions taking `TargetFile` and returning `List(Violation)`.
- **DB**: None.
- **External Integrations**: Bend HVM compiler / runtime.
- **Existing Tests**: [`backend/tests/test_rules.bend`](file:///home/isabelle/projects/ai-bend-devops/backend/tests/test_rules.bend#L61-L123) (6 scenarios passed).

---

### [FEAT-003] Parallel Binary Tree Reducer on HVM
- **Module**: Backend (Bend Parallel Engine)
- **Location**: [`backend/src/guardian.bend`](file:///home/isabelle/projects/ai-bend-devops/backend/src/guardian.bend#L24-L28), [`backend/src/guardian.bend`](file:///home/isabelle/projects/ai-bend-devops/backend/src/guardian.bend#L90-L100)
- **Entrypoint**: `FileTree/Empty`, `FileTree/Leaf`, `FileTree/Node`, `evaluate_tree_parallel`
- **User Visibility**: Core Engine / Scalability
- **Business Rules**: Recursively traverses file trees in parallel forks on HVM threads, achieving lock-free O(log N) evaluation time.
- **API**: Parallel reduction pipeline `evaluate_tree_parallel(tree)`.
- **DB**: None.
- **External Integrations**: HVM parallel execution threads.
- **Existing Tests**: [`backend/tests/test_engine.bend`](file:///home/isabelle/projects/ai-bend-devops/backend/tests/test_engine.bend#L89-L99) (Passed).

---

### [FEAT-004] Consolidated Quality Score Calculation & Gating
- **Module**: Backend (Bend Core)
- **Location**: [`backend/src/guardian.bend`](file:///home/isabelle/projects/ai-bend-devops/backend/src/guardian.bend#L120-L165)
- **Entrypoint**: `aggregate_violations`, `compute_score`, `determine_approval`, `generate_audit_report`
- **User Visibility**: Quality Gate / CLI / CI Status
- **Business Rules**: Starting score = 100. Deducts penalties according to violated rules. Minimum score to approve = 80. Zero P0 violations allowed (any P0 immediately sets approval = 0).
- **API**: `generate_audit_report(files_count, violations) -> CultureReport`.
- **DB**: None.
- **External Integrations**: Exit code pipeline in `./scripts/validate.sh`.
- **Existing Tests**: [`backend/tests/test_engine.bend`](file:///home/isabelle/projects/ai-bend-devops/backend/tests/test_engine.bend#L161-L222) (3 scenarios passed).

---

### [FEAT-005] Universal Multi-Language Layer Classifier
- **Module**: CLI / Scanner
- **Location**: [`scripts/culture_guard.py`](file:///home/isabelle/projects/ai-bend-devops/scripts/culture_guard.py#L45-L95)
- **Entrypoint**: `classify_layer(file_path)`
- **User Visibility**: CLI / Pipeline
- **Business Rules**: Classifies source files across 7 architectures (Clean Architecture, DDD, Hexagonal, 3-Tier, 4-Tier, MVC, Onion) into canonical layers: `Presentation`, `Application`, `Domain`, `Infrastructure`.
- **API**: Python function `classify_layer(path: str) -> str`.
- **DB**: None.
- **External Integrations**: Local filesystem scanner.
- **Existing Tests**: [`tests/test_false_positives.py`](file:///home/isabelle/projects/ai-bend-devops/tests/test_false_positives.py#L12-L28) (Passed).

---

### [FEAT-006] Canonical Token Containment Engine
- **Module**: Rules / Lexer
- **Location**: [`backend/rules/layer_vocabulary.json`](file:///home/isabelle/projects/ai-bend-devops/backend/rules/layer_vocabulary.json)
- **Entrypoint**: `layer_vocabulary.json` schema definitions
- **User Visibility**: Rules Configuration
- **Business Rules**: Maps forbidden and allowed import tokens, types, and annotations for each layer profile across C#, Python, TypeScript, PHP, Go, Java, and Rust.
- **API**: JSON schema mapping vocabulary keywords.
- **DB**: None.
- **External Integrations**: Python audit parser.
- **Existing Tests**: [`tests/test_token_filter.py`](file:///home/isabelle/projects/ai-bend-devops/tests/test_token_filter.py#L15-L45) (Passed).

---

### [FEAT-007] Zero Presentation Leakage Gating (`ARCH-LAYER-01`)
- **Module**: Rules / Engine
- **Location**: [`backend/rules/0_core_foundations/arch_layer_01_no_presentation_in_domain.json`](file:///home/isabelle/projects/ai-bend-devops/backend/rules/0_core_foundations/arch_layer_01_no_presentation_in_domain.json)
- **Entrypoint**: Rule ID `ARCH-LAYER-01`
- **User Visibility**: CI Quality Gate / SARIF / PR Annotations
- **Business Rules**: Forbids UI/HTTP/Controller/View dependencies inside Domain and Core entities (P0 severity, 40 penalty).
- **API**: Rule validation engine.
- **DB**: None.
- **External Integrations**: GitHub/GitLab/Bitbucket PR check annotations.
- **Existing Tests**: [`tests/vcs/test_github_adapter.py`](file:///home/isabelle/projects/ai-bend-devops/tests/vcs/test_github_adapter.py#L25-L42) (Passed).

---

### [FEAT-008] Zero Database Leaks in Views (`ARCH-LAYER-02`)
- **Module**: Rules / Engine
- **Location**: [`backend/rules/0_core_foundations/arch_layer_02_no_db_in_presentation.json`](file:///home/isabelle/projects/ai-bend-devops/backend/rules/0_core_foundations/arch_layer_02_no_db_in_presentation.json)
- **Entrypoint**: Rule ID `ARCH-LAYER-02`
- **User Visibility**: CI Quality Gate / GitLab CodeQuality
- **Business Rules**: Prevents raw SQL, ORM contexts, and database clients from being accessed directly from Presentation components (P0 severity, 40 penalty).
- **API**: Rule validation engine.
- **DB**: None.
- **External Integrations**: GitLab CI code quality artifact.
- **Existing Tests**: [`tests/vcs/test_gitlab_adapter.py`](file:///home/isabelle/projects/ai-bend-devops/tests/vcs/test_gitlab_adapter.py#L20-L38) (Passed).

---

### [FEAT-009] Zero Transport Coupling in Domain (`ARCH-LAYER-03`)
- **Module**: Rules / Engine
- **Location**: [`backend/rules/0_core_foundations/arch_layer_03_no_framework_in_domain.json`](file:///home/isabelle/projects/ai-bend-devops/backend/rules/0_core_foundations/arch_layer_03_no_framework_in_domain.json)
- **Entrypoint**: Rule ID `ARCH-LAYER-03`
- **User Visibility**: CI Quality Gate / Bitbucket Code Insights
- **Business Rules**: Blocks network transport, HTTP clients, and low-level protocol packages from domain models (P0 severity, 40 penalty).
- **API**: Rule validation engine.
- **DB**: None.
- **External Integrations**: Bitbucket Code Insights reports.
- **Existing Tests**: [`tests/vcs/test_bitbucket_adapter.py`](file:///home/isabelle/projects/ai-bend-devops/tests/vcs/test_bitbucket_adapter.py#L20-L38) (Passed).

---

### [FEAT-010] Multi-Language Rule Adapters (7 Languages)
- **Module**: Rules / Schema
- **Location**: [`backend/rules/3_languages/`](file:///home/isabelle/projects/ai-bend-devops/backend/rules/3_languages/)
- **Entrypoint**: Language rule descriptors (`csharp.json`, `python.json`, `typescript.json`, `php.json`, `golang.json`, `java.json`, `rust.json`)
- **User Visibility**: Multi-Language Support
- **Business Rules**: Language-specific regex and token matchers enforcing Clean Architecture semantics.
- **API**: JSON rules validated against [`backend/rules/rules_schema.json`](file:///home/isabelle/projects/ai-bend-devops/backend/rules/rules_schema.json).
- **DB**: None.
- **External Integrations**: Lexical filter scanner.
- **Existing Tests**: [`tests/test_token_filter.py`](file:///home/isabelle/projects/ai-bend-devops/tests/test_token_filter.py#L48-L62) (Passed).

---

### [FEAT-011] Angular 19 Reactive Compliance Dashboard
- **Module**: Frontend (Angular 19)
- **Location**: [`frontend/src/app/app.ts`](file:///home/isabelle/projects/ai-bend-devops/frontend/src/app/app.ts), [`frontend/src/app/app.html`](file:///home/isabelle/projects/ai-bend-devops/frontend/src/app/app.html)
- **Entrypoint**: UI Web Application (`ng serve`, port 4200)
- **User Visibility**: Web UI (End Users, Architects, Tech Leads)
- **Business Rules**: Displays real-time architecture compliance score, violation breakdowns by severity (P0, P1, P2), penalty totals, approval status, and compliance gauges.
- **API**: Reactive Angular Signals (`activeTab`, `searchQuery`, `severityFilter`, `report`).
- **DB**: Local storage & in-memory signals.
- **External Integrations**: REST endpoints / static analysis payloads.
- **Existing Tests**: [`frontend/src/app/app.spec.ts`](file:///home/isabelle/projects/ai-bend-devops/frontend/src/app/app.spec.ts#L18-L32) (Passed).

---

### [FEAT-012] Interactive Code Diff & MR Simulator
- **Module**: Frontend (Angular 19)
- **Location**: [`frontend/src/app/culture-guardian.service.ts`](file:///home/isabelle/projects/ai-bend-devops/frontend/src/app/culture-guardian.service.ts#L60-L110)
- **Entrypoint**: MR Simulator tab in UI
- **User Visibility**: Web UI (Developer sandbox)
- **Business Rules**: Simulates pull request diff analysis with presets (`Compliant Clean Architecture`, `Non-Compliant Layer Leakage`, `Suppressed with Pragma`) and evaluates live in-browser.
- **API**: `CultureGuardianService.auditDiff(diffText)`.
- **DB**: None.
- **External Integrations**: CodeMirror / diff syntax highlighter.
- **Existing Tests**: [`frontend/src/app/app.spec.ts`](file:///home/isabelle/projects/ai-bend-devops/frontend/src/app/app.spec.ts#L34-L52) (Passed).

---

### [FEAT-013] Dynamic Rule Activation & Deactivation Toggles
- **Module**: Frontend (Angular 19)
- **Location**: [`frontend/src/app/app.ts`](file:///home/isabelle/projects/ai-bend-devops/frontend/src/app/app.ts#L105-L125)
- **Entrypoint**: Rules configuration view in UI
- **User Visibility**: Web UI
- **Business Rules**: Allows engineers to toggle specific culture or architectural rules on/off and recalculate compliance scores instantly.
- **API**: `toggleRule(ruleId: string)`.
- **DB**: State in Angular signals.
- **External Integrations**: UI State.
- **Existing Tests**: [`frontend/src/app/app.spec.ts`](file:///home/isabelle/projects/ai-bend-devops/frontend/src/app/app.spec.ts#L54-L62) (Passed).

---

### [FEAT-014] Severity Filter & Real-Time Search
- **Module**: Frontend (Angular 19)
- **Location**: [`frontend/src/app/app.ts`](file:///home/isabelle/projects/ai-bend-devops/frontend/src/app/app.ts#L130-L155)
- **Entrypoint**: Search & filter controls in UI
- **User Visibility**: Web UI
- **Business Rules**: Filters violation table by severity levels (`ALL`, `P0`, `P1`, `P2`) and free-text search across rule ID, file name, and violation message.
- **API**: Computed Angular signals `filteredViolations()`.
- **DB**: None.
- **External Integrations**: UI View.
- **Existing Tests**: [`frontend/src/app/app.spec.ts`](file:///home/isabelle/projects/ai-bend-devops/frontend/src/app/app.spec.ts#L25-L33) (Passed).

---

### [FEAT-015] Unified Git Diff & Hunk Line Extractor
- **Module**: VCS Adapters
- **Location**: [`scripts/vcs_adapters/diff_parser.py`](file:///home/isabelle/projects/ai-bend-devops/scripts/vcs_adapters/diff_parser.py#L12-L65)
- **Entrypoint**: `parse_unified_diff(diff_str)`, `extract_changed_lines(diff_str, file_path)`
- **User Visibility**: CLI / Background Agent
- **Business Rules**: Parses unified git diff formats (`@@ -l,s +l,s @@`) to extract precise modified line numbers, restricting analysis to modified code.
- **API**: `GitDiffParser.parse_unified_diff(diff: str) -> Dict[str, List[int]]`.
- **DB**: None.
- **External Integrations**: Git CLI & VCS API diff streams.
- **Existing Tests**: [`tests/vcs/test_diff_parser.py`](file:///home/isabelle/projects/ai-bend-devops/tests/vcs/test_diff_parser.py#L12-L42) (4 scenarios passed).

---

### [FEAT-016] GitHub Actions Check Runs & SARIF Exporter
- **Module**: VCS Adapters
- **Location**: [`scripts/vcs_adapters/github_adapter.py`](file:///home/isabelle/projects/ai-bend-devops/scripts/vcs_adapters/github_adapter.py#L15-L120)
- **Entrypoint**: `GitHubAdapter.publish_annotations`, `generate_sarif_report`, `publish_commit_status`
- **User Visibility**: GitHub PR Checks & Security Tab
- **Business Rules**: Creates GitHub check runs with inline annotations, posts markdown PR review summaries with secret redaction (RN02), and exports valid OASIS SARIF v2.1.0 reports.
- **API**: GitHub REST API (`/repos/{owner}/{repo}/check-runs`, `/statuses/{sha}`).
- **DB**: None.
- **External Integrations**: GitHub REST v3 / GitHub Actions environment.
- **Existing Tests**: [`tests/vcs/test_github_adapter.py`](file:///home/isabelle/projects/ai-bend-devops/tests/vcs/test_github_adapter.py#L12-L58) (5 scenarios passed).

---

### [FEAT-017] GitLab CI/CD & Code Quality JSON Exporter
- **Module**: VCS Adapters
- **Location**: [`scripts/vcs_adapters/gitlab_adapter.py`](file:///home/isabelle/projects/ai-bend-devops/scripts/vcs_adapters/gitlab_adapter.py#L15-L115)
- **Entrypoint**: `GitLabAdapter.publish_annotations`, `generate_code_quality_report`, `post_mr_note`
- **User Visibility**: GitLab MR Quality Widget & Pipeline Notes
- **Business Rules**: Generates Code Climate compliant `gl-code-quality-report.json` and posts sticky discussions to GitLab Merge Requests.
- **API**: GitLab REST API v4 (`/projects/:id/merge_requests/:iid/notes`, `/statuses/:sha`).
- **DB**: None.
- **External Integrations**: GitLab CI/CD Runner.
- **Existing Tests**: [`tests/vcs/test_gitlab_adapter.py`](file:///home/isabelle/projects/ai-bend-devops/tests/vcs/test_gitlab_adapter.py#L12-L50) (4 scenarios passed).

---

### [FEAT-018] Bitbucket Pipelines & Code Insights Publisher
- **Module**: VCS Adapters
- **Location**: [`scripts/vcs_adapters/bitbucket_adapter.py`](file:///home/isabelle/projects/ai-bend-devops/scripts/vcs_adapters/bitbucket_adapter.py#L15-L110)
- **Entrypoint**: `BitbucketAdapter.publish_annotations`, `generate_code_insights_report`, `publish_commit_status`
- **User Visibility**: Bitbucket Code Insights Panel
- **Business Rules**: Creates Bitbucket Code Insights report (`/reports/bend-devops-guardian`) with inline annotations and updates commit statuses (`SUCCESSFUL`, `FAILED`).
- **API**: Bitbucket Cloud REST 2.0.
- **DB**: None.
- **External Integrations**: Bitbucket Pipelines runtime.
- **Existing Tests**: [`tests/vcs/test_bitbucket_adapter.py`](file:///home/isabelle/projects/ai-bend-devops/tests/vcs/test_bitbucket_adapter.py#L12-L48) (4 scenarios passed).

---

### [FEAT-019] Unified Webhook Gateway & Ingestion Router
- **Module**: VCS Adapters
- **Location**: [`scripts/vcs_adapters/webhook_gateway.py`](file:///home/isabelle/projects/ai-bend-devops/scripts/vcs_adapters/webhook_gateway.py#L15-L85)
- **Entrypoint**: `WebhookGateway.parse_webhook(headers, payload)`
- **User Visibility**: Webhook Ingestion Service
- **Business Rules**: Ingests `X-GitHub-Event`, `X-Gitlab-Event`, and `X-Event-Key` payloads into standardized `WebhookEvent` records with repository name, branch, commit SHA, and PR/MR number.
- **API**: HTTP Webhook receiver.
- **DB**: None.
- **External Integrations**: GitHub, GitLab, Bitbucket Webhook event broadcasters.
- **Existing Tests**: [`tests/vcs/test_webhook_gateway.py`](file:///home/isabelle/projects/ai-bend-devops/tests/vcs/test_webhook_gateway.py#L12-L50) (4 scenarios passed).

---

### [FEAT-020] Configurable Branch Gating Policy Engine
- **Module**: VCS Adapters
- **Location**: [`scripts/vcs_adapters/policy_engine.py`](file:///home/isabelle/projects/ai-bend-devops/scripts/vcs_adapters/policy_engine.py#L12-L75)
- **Entrypoint**: `BranchPolicyEngine.evaluate_policy(branch, report)`
- **User Visibility**: Policy Gatekeeper
- **Business Rules**: 
  - `main`/`master`/`release/*`: Strict blocking policy (0 P0 violations, minimum score >= 80).
  - `feature/*`/`fix/*`/`chore/*`: Permissive warning mode (non-blocking for P1/P2).
  - Custom overrides loaded from `.guardianpolicies.json`.
- **API**: `PolicyResult` (is_blocked, message, violations_count).
- **DB**: None.
- **External Integrations**: CI/CD gatekeeper.
- **Existing Tests**: [`tests/vcs/test_policy_engine.py`](file:///home/isabelle/projects/ai-bend-devops/tests/vcs/test_policy_engine.py#L12-L42) (3 scenarios passed).

---

### [FEAT-021] Automatic VCS Environment Detection Factory
- **Module**: VCS Adapters
- **Location**: [`scripts/vcs_adapters/__init__.py`](file:///home/isabelle/projects/ai-bend-devops/scripts/vcs_adapters/__init__.py#L15-L60)
- **Entrypoint**: `detect_vcs_adapter()`, `get_vcs_adapter(platform)`
- **User Visibility**: Zero-Config CLI / CI Runner
- **Business Rules**: Inspects environment variables (`GITHUB_ACTIONS`, `GITLAB_CI`, `BITBUCKET_BUILD_NUMBER`) to auto-instantiate the appropriate VCS platform adapter without manual configuration.
- **API**: Factory function returning `BaseVcsAdapter`.
- **DB**: None.
- **External Integrations**: CI Environment runners.
- **Existing Tests**: [`tests/vcs/test_unified_cli.py`](file:///home/isabelle/projects/ai-bend-devops/tests/vcs/test_unified_cli.py#L12-L45) (4 scenarios passed).

---

### [FEAT-022] Syntactic Word Boundary Fencing
- **Module**: Lexical Filter
- **Location**: [`scripts/token_filter.py`](file:///home/isabelle/projects/ai-bend-devops/scripts/token_filter.py#L30-L70)
- **Entrypoint**: `matches_exact_token(line, token)`
- **User Visibility**: Core Scanning Engine
- **Business Rules**: Uses word-boundary fences (`\b`) and identifier checks so tokens like `Image` or `Repository` do not match `ImageService` or `GetImageBytes()` inappropriately.
- **API**: `matches_exact_token(code_line: str, token: str) -> bool`.
- **DB**: None.
- **External Integrations**: Core token scanner.
- **Existing Tests**: [`tests/test_token_filter.py`](file:///home/isabelle/projects/ai-bend-devops/tests/test_token_filter.py#L22-L40) (Passed).

---

### [FEAT-023] Multi-Language Comment & Docstring Scoper
- **Module**: Lexical Filter
- **Location**: [`scripts/token_filter.py`](file:///home/isabelle/projects/ai-bend-devops/scripts/token_filter.py#L75-L125)
- **Entrypoint**: `strip_comments_and_strings(content, lang)`
- **User Visibility**: Scanner Accuracy
- **Business Rules**: Strips single-line (`//`, `#`, `--`) and multi-line (`/* */`, `""" """`, `''' '''`) comments and literal strings across C#, Python, TypeScript, PHP, Go, Java, Rust, SQL, and Shell before token inspection.
- **API**: `strip_comments(code: str, file_ext: str) -> str`.
- **DB**: None.
- **External Integrations**: Lexer.
- **Existing Tests**: [`tests/test_token_filter.py`](file:///home/isabelle/projects/ai-bend-devops/tests/test_token_filter.py#L42-L60) (Passed).

---

### [FEAT-024] Inline Single-Line Pragmas (`@guardian-ignore`)
- **Module**: Lexical Filter
- **Location**: [`scripts/token_filter.py`](file:///home/isabelle/projects/ai-bend-devops/scripts/token_filter.py#L130-L175)
- **Entrypoint**: `@guardian-ignore [RULE_ID]: [reason]`
- **User Visibility**: Source Code Annotations
- **Business Rules**: Suppresses rule violation on the current line when a valid rule ID (or `*`) and a mandatory non-empty reason are provided.
- **API**: `parse_inline_suppression(line: str) -> Optional[Suppression]`.
- **DB**: None.
- **External Integrations**: Audit engine.
- **Existing Tests**: [`tests/test_suppressions.py`](file:///home/isabelle/projects/ai-bend-devops/tests/test_suppressions.py#L15-L42) (Passed).

---

### [FEAT-025] Block-Scoped Pragmas (`@guardian-ignore-start/end`)
- **Module**: Lexical Filter
- **Location**: [`scripts/token_filter.py`](file:///home/isabelle/projects/ai-bend-devops/scripts/token_filter.py#L180-L225)
- **Entrypoint**: `@guardian-ignore-start [RULE_ID]: [reason]` ... `@guardian-ignore-end`
- **User Visibility**: Source Code Annotations
- **Business Rules**: Exempts an entire block of code lines across a specified rule ID or all rules, tracking open and close boundary lines with rationale validation.
- **API**: `extract_block_suppressions(lines: List[str]) -> List[BlockSuppression]`.
- **DB**: None.
- **External Integrations**: Audit engine.
- **Existing Tests**: [`tests/test_suppressions.py`](file:///home/isabelle/projects/ai-bend-devops/tests/test_suppressions.py#L44-L65) (Passed).

---

### [FEAT-026] Mandatory Justification Rationale Enforcement
- **Module**: Lexical Filter
- **Location**: [`scripts/token_filter.py`](file:///home/isabelle/projects/ai-bend-devops/scripts/token_filter.py#L230-L260)
- **Entrypoint**: `validate_suppression_rationale(suppression)`
- **User Visibility**: Quality Gate Enforcement
- **Business Rules**: Rejects empty or placeholder pragma reasons (e.g. `todo`, `fix`, `temp`) and emits a warning or invalidates the exemption.
- **API**: Rationale validation validator.
- **DB**: None.
- **External Integrations**: Quality Gate.
- **Existing Tests**: [`tests/test_suppressions.py`](file:///home/isabelle/projects/ai-bend-devops/tests/test_suppressions.py#L67-L85) (Passed).

---

### [FEAT-027] Project-Level Exemption File (`.guardianignore`)
- **Module**: Lexical Filter
- **Location**: [`scripts/token_filter.py`](file:///home/isabelle/projects/ai-bend-devops/scripts/token_filter.py#L265-L310)
- **Entrypoint**: `.guardianignore` file parser
- **User Visibility**: Configuration File
- **Business Rules**: Parses glob patterns and rule exemptions with justification lines from `.guardianignore` at the repository root.
- **API**: `load_guardianignore(root_path: str) -> List[IgnoreEntry]`.
- **DB**: None.
- **External Integrations**: Filesystem.
- **Existing Tests**: [`tests/test_suppressions.py`](file:///home/isabelle/projects/ai-bend-devops/tests/test_suppressions.py#L88-L115) (Passed).

---

### [FEAT-028] Suppression Telemetry & Report Metrics
- **Module**: CLI / Reporter
- **Location**: [`scripts/culture_guard.py`](file:///home/isabelle/projects/ai-bend-devops/scripts/culture_guard.py#L180-L240)
- **Entrypoint**: Terminal Banner & Audit Summary
- **User Visibility**: CLI stdout, CI logs, SARIF properties
- **Business Rules**: Reports exact count of active suppressions, exempted rules, and justification messages in the final audit summary banner.
- **API**: `AuditReport.suppressions_count`.
- **DB**: None.
- **External Integrations**: Console stdout and CI pipelines.
- **Existing Tests**: [`tests/test_suppressions.py`](file:///home/isabelle/projects/ai-bend-devops/tests/test_suppressions.py#L118-L130) (Passed).

---

### [FEAT-029] Universal 8-Stage Quality Gate Script
- **Module**: Orchestration / CI/CD
- **Location**: [`scripts/validate.sh`](file:///home/isabelle/projects/ai-bend-devops/scripts/validate.sh#L1-L120)
- **Entrypoint**: `./scripts/validate.sh`
- **User Visibility**: Terminal / CI Pipeline
- **Business Rules**: Executes end-to-end multi-language validation: Bend syntax & types $\rightarrow$ Bend unit tests $\rightarrow$ Bend parallel integration tests $\rightarrow$ Angular tests & build $\rightarrow$ Bend HVM execution $\rightarrow$ Token filter tests $\rightarrow$ VCS adapter tests $\rightarrow$ DevOps Quality Gate audit. Exits 0 on total success, non-zero on any failure.
- **API**: Bash executable script.
- **DB**: None.
- **External Integrations**: CI runners across GitHub Actions, GitLab CI, and Bitbucket Pipelines.
- **Existing Tests**: Executed directly via `./scripts/validate.sh` (8/8 stages green).

---
