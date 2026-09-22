# TEST_INVENTORY.md: Complete Automated Test Catalog

**Project**: Bend DevOps Guardian (CodeConform)  
**Execution Date**: 2026-09-22  
**Total Executable Tests**: 59  
**Passing Tests**: 59 (100%)  
**Failing / Skipped Tests**: 0 (0%)  

---

## 1. Summary by Test Suite

| Test Suite | Framework / Runtime | File Location | Tests | Status | Execution Time |
| :--- | :--- | :--- | :---: | :---: | :---: |
| **Bend Unit Rules** | Bend / HVM | [`backend/tests/test_rules.bend`](file:///home/isabelle/projects/ai-bend-devops/backend/tests/test_rules.bend) | 6 | **PASS** | 0.04s |
| **Bend Integration Engine** | Bend / HVM | [`backend/tests/test_engine.bend`](file:///home/isabelle/projects/ai-bend-devops/backend/tests/test_engine.bend) | 3 | **PASS** | 0.05s |
| **Angular Vitest Suite** | Vitest / Node 20 | [`frontend/src/app/app.spec.ts`](file:///home/isabelle/projects/ai-bend-devops/frontend/src/app/app.spec.ts) | 6 | **PASS** | 0.40s |
| **False Positive Prevention** | Python 3.12 `unittest` | [`tests/test_false_positives.py`](file:///home/isabelle/projects/ai-bend-devops/tests/test_false_positives.py) | 2 | **PASS** | 0.002s |
| **Suppression Pragmas & Ignore** | Python 3.12 `unittest` | [`tests/test_suppressions.py`](file:///home/isabelle/projects/ai-bend-devops/tests/test_suppressions.py) | 8 | **PASS** | 0.005s |
| **Token Filter & Lexical Scoper** | Python 3.12 `unittest` | [`tests/test_token_filter.py`](file:///home/isabelle/projects/ai-bend-devops/tests/test_token_filter.py) | 6 | **PASS** | 0.004s |
| **Git Diff & Hunk Parser** | Python 3.12 `unittest` | [`tests/vcs/test_diff_parser.py`](file:///home/isabelle/projects/ai-bend-devops/tests/vcs/test_diff_parser.py) | 4 | **PASS** | 0.003s |
| **GitHub VCS Adapter** | Python 3.12 `unittest` | [`tests/vcs/test_github_adapter.py`](file:///home/isabelle/projects/ai-bend-devops/tests/vcs/test_github_adapter.py) | 5 | **PASS** | 0.007s |
| **GitLab VCS Adapter** | Python 3.12 `unittest` | [`tests/vcs/test_gitlab_adapter.py`](file:///home/isabelle/projects/ai-bend-devops/tests/vcs/test_gitlab_adapter.py) | 4 | **PASS** | 0.005s |
| **Bitbucket VCS Adapter** | Python 3.12 `unittest` | [`tests/vcs/test_bitbucket_adapter.py`](file:///home/isabelle/projects/ai-bend-devops/tests/vcs/test_bitbucket_adapter.py) | 4 | **PASS** | 0.005s |
| **Unified Webhook Gateway** | Python 3.12 `unittest` | [`tests/vcs/test_webhook_gateway.py`](file:///home/isabelle/projects/ai-bend-devops/tests/vcs/test_webhook_gateway.py) | 4 | **PASS** | 0.004s |
| **Branch Policy Engine** | Python 3.12 `unittest` | [`tests/vcs/test_policy_engine.py`](file:///home/isabelle/projects/ai-bend-devops/tests/vcs/test_policy_engine.py) | 3 | **PASS** | 0.003s |
| **Unified VCS CLI & Factory** | Python 3.12 `unittest` | [`tests/vcs/test_unified_cli.py`](file:///home/isabelle/projects/ai-bend-devops/tests/vcs/test_unified_cli.py) | 4 | **PASS** | 0.004s |
| **TOTAL** | | | **59** | **100% PASS** | **~0.6s** |

---

## 2. Detailed Test Catalog

### A. Bend Unit & Integration Tests (9 tests)
1. **TEST-BEND-01**: `test_all_rules_pass_on_compliant_file`
   - **File**: `backend/tests/test_rules.bend:62`
   - **Type**: Unit Test
   - **Requirement**: RF01, RF02, RF03, RF04, RF05, RF06
   - **Result**: `PASS`
2. **TEST-BEND-02**: `test_cult01_lazy_code_violation`
   - **File**: `backend/tests/test_rules.bend:72`
   - **Type**: Unit Test
   - **Requirement**: RF02
   - **Result**: `PASS`
3. **TEST-BEND-03**: `test_cult02_missing_spec_tag`
   - **File**: `backend/tests/test_rules.bend:77`
   - **Type**: Unit Test
   - **Requirement**: RF03
   - **Result**: `PASS`
4. **TEST-BEND-04**: `test_cult03_missing_tests`
   - **File**: `backend/tests/test_rules.bend:82`
   - **Type**: Unit Test
   - **Requirement**: RF04
   - **Result**: `PASS`
5. **TEST-BEND-05**: `test_cult04_secret_leak`
   - **File**: `backend/tests/test_rules.bend:87`
   - **Type**: Unit Test
   - **Requirement**: RF05
   - **Result**: `PASS`
6. **TEST-BEND-06**: `test_cult05_missing_types`
   - **File**: `backend/tests/test_rules.bend:92`
   - **Type**: Unit Test
   - **Requirement**: RF06
   - **Result**: `PASS`
7. **TEST-BEND-07**: `test_fully_compliant_codebase`
   - **File**: `backend/tests/test_engine.bend:162`
   - **Type**: Integration Test (HVM Tree Reducer)
   - **Requirement**: RF07, RF08, RF09
   - **Result**: `PASS`
8. **TEST-BEND-08**: `test_blocking_violation_rejection`
   - **File**: `backend/tests/test_engine.bend:178`
   - **Type**: Integration Test (Quality Gate)
   - **Requirement**: RF10
   - **Result**: `PASS`
9. **TEST-BEND-09**: `test_empty_tree`
   - **File**: `backend/tests/test_engine.bend:194`
   - **Type**: Integration Test (Edge Case)
   - **Requirement**: RF11
   - **Result**: `PASS`

---

### B. Angular 19 Component & Service Tests (6 tests)
10. **TEST-NG-01**: `should create the CodeConform dashboard app`
    - **File**: `frontend/src/app/app.spec.ts:18`
    - **Type**: Component Lifecycle Test
    - **Requirement**: RF23
    - **Result**: `PASS`
11. **TEST-NG-02**: `should render the CodeConform brand title in header`
    - **File**: `frontend/src/app/app.spec.ts:24`
    - **Type**: UI DOM Render Test
    - **Requirement**: RF23
    - **Result**: `PASS`
12. **TEST-NG-03**: `should switch tabs between dashboard, analyze, results, history, and rules`
    - **File**: `frontend/src/app/app.spec.ts:30`
    - **Type**: UI State / Navigation Test
    - **Requirement**: RF23, RF25
    - **Result**: `PASS`
13. **TEST-NG-04**: `should select MR preset and evaluate diff`
    - **File**: `frontend/src/app/app.spec.ts:39`
    - **Type**: Integration / Service Simulator Test
    - **Requirement**: RF24
    - **Result**: `PASS`
14. **TEST-NG-05**: `should run MR analysis on non-compliant preset and detect violations`
    - **File**: `frontend/src/app/app.spec.ts:46`
    - **Type**: Integration / Rule Evaluation Test
    - **Requirement**: RF24, RF25
    - **Result**: `PASS`
15. **TEST-NG-06**: `should toggle rule active/inactive status`
    - **File**: `frontend/src/app/app.spec.ts:54`
    - **Type**: UI Signal State Mutation Test
    - **Requirement**: RF26
    - **Result**: `PASS`

---

### C. Python False-Positive & Suppression Engine Tests (16 tests)
16. **TEST-PY-01**: `TestFalsePositiveScenarios.test_csharp_domain_model_with_image_methods_not_flagged`
    - **File**: `tests/test_false_positives.py:12`
    - **Type**: False-Positive Regression Test
    - **Requirement**: RF13, RF41
    - **Result**: `PASS`
17. **TEST-PY-02**: `TestFalsePositiveScenarios.test_inline_suppression_pragma_exempts_violation_with_reason`
    - **File**: `tests/test_false_positives.py:27`
    - **Type**: Suppression Integration Test
    - **Requirement**: RF45, RF50
    - **Result**: `PASS`
18. **TEST-PY-03**: `TestInlinePragmas.test_guardianignore_pattern_matching`
    - **File**: `tests/test_suppressions.py:15`
    - **Type**: Unit Test (`.guardianignore` matching)
    - **Requirement**: RF49
    - **Result**: `PASS`
19. **TEST-PY-04**: `TestInlinePragmas.test_guardianignore_wildcard_all_rules`
    - **File**: `tests/test_suppressions.py:30`
    - **Type**: Unit Test (Wildcard ignore)
    - **Requirement**: RF47, RF49
    - **Result**: `PASS`
20. **TEST-PY-05**: `TestInlinePragmas.test_load_guardianignore_from_file`
    - **File**: `tests/test_suppressions.py:42`
    - **Type**: Integration Test (File loader)
    - **Requirement**: RF49
    - **Result**: `PASS`
21. **TEST-PY-06**: `TestInlinePragmas.test_parse_all_rules_inline_pragma`
    - **File**: `tests/test_suppressions.py:54`
    - **Type**: Unit Test (Wildcard inline pragma)
    - **Requirement**: RF47
    - **Result**: `PASS`
22. **TEST-PY-07**: `TestInlinePragmas.test_parse_block_scoped_pragma`
    - **File**: `tests/test_suppressions.py:65`
    - **Type**: Unit Test (Block scoping)
    - **Requirement**: RF46
    - **Result**: `PASS`
23. **TEST-PY-08**: `TestInlinePragmas.test_parse_block_scoped_pragma_missing_reason_emits_warning`
    - **File**: `tests/test_suppressions.py:78`
    - **Type**: Unit Test (Rationale validation)
    - **Requirement**: RF48
    - **Result**: `PASS`
24. **TEST-PY-09**: `TestInlinePragmas.test_parse_invalid_inline_pragma_missing_reason`
    - **File**: `tests/test_suppressions.py:88`
    - **Type**: Unit Test (Missing reason rejection)
    - **Requirement**: RF48
    - **Result**: `PASS`
25. **TEST-PY-10**: `TestInlinePragmas.test_parse_valid_inline_pragma`
    - **File**: `tests/test_suppressions.py:97`
    - **Type**: Unit Test (Valid pragma parsing)
    - **Requirement**: RF45
    - **Result**: `PASS`
26. **TEST-PY-11**: `TestTokenFilter.test_matches_exact_token_detects_real_violations`
    - **File**: `tests/test_token_filter.py:15`
    - **Type**: Unit Test (Token boundary exact match)
    - **Requirement**: RF41, RF44
    - **Result**: `PASS`
27. **TEST-PY-12**: `TestTokenFilter.test_matches_exact_token_ignores_method_and_variable_substrings`
    - **File**: `tests/test_token_filter.py:28`
    - **Type**: Unit Test (Substring rejection)
    - **Requirement**: RF41
    - **Result**: `PASS`
28. **TEST-PY-13**: `TestTokenFilter.test_strip_comments_multi_languages`
    - **File**: `tests/test_token_filter.py:40`
    - **Type**: Unit Test (Multi-language comment stripper)
    - **Requirement**: RF22, RF43
    - **Result**: `PASS`
29. **TEST-PY-14**: `TestTokenFilter.test_strip_single_line_hash_comment`
    - **File**: `tests/test_token_filter.py:53`
    - **Type**: Unit Test (Hash `#` comment stripping)
    - **Requirement**: RF42
    - **Result**: `PASS`
30. **TEST-PY-15**: `TestTokenFilter.test_strip_single_line_slash_comment`
    - **File**: `tests/test_token_filter.py:62`
    - **Type**: Unit Test (Slash `//` comment stripping)
    - **Requirement**: RF42
    - **Result**: `PASS`
31. **TEST-PY-16**: `TestTokenFilter.test_token_filter_class_static_methods`
    - **File**: `tests/test_token_filter.py:71`
    - **Type**: Unit Test (Class static helper methods)
    - **Requirement**: RF18, RF41
    - **Result**: `PASS`

---

### D. Python Multi-Platform VCS Adapter Tests (28 tests)
32. **TEST-VCS-01**: `TestBitbucketAdapter.test_generate_code_insights_report_payload_structure`
    - **File**: `tests/vcs/test_bitbucket_adapter.py:15`
    - **Type**: Unit Test (Bitbucket Insight schema)
    - **Requirement**: RF21, RF34
    - **Result**: `PASS`
33. **TEST-VCS-02**: `TestBitbucketAdapter.test_get_changed_files_from_bitbucket_api`
    - **File**: `tests/vcs/test_bitbucket_adapter.py:28`
    - **Type**: Unit Test (Bitbucket diff API client)
    - **Requirement**: RF34
    - **Result**: `PASS`
34. **TEST-VCS-03**: `TestBitbucketAdapter.test_publish_annotations_puts_insight_annotation`
    - **File**: `tests/vcs/test_bitbucket_adapter.py:40`
    - **Type**: Unit Test (Bitbucket annotation PUT)
    - **Requirement**: RF34
    - **Result**: `PASS`
35. **TEST-VCS-04**: `TestBitbucketAdapter.test_publish_commit_status_makes_http_post`
    - **File**: `tests/vcs/test_bitbucket_adapter.py:55`
    - **Type**: Unit Test (Bitbucket status POST)
    - **Requirement**: RF35
    - **Result**: `PASS`
36. **TEST-VCS-05**: `TestGitDiffParser.test_extract_changed_lines_for_empty_or_missing_file`
    - **File**: `tests/vcs/test_diff_parser.py:15`
    - **Type**: Unit Test (Edge case empty diff)
    - **Requirement**: RF27
    - **Result**: `PASS`
37. **TEST-VCS-06**: `TestGitDiffParser.test_extract_changed_lines_handles_multiple_hunks`
    - **File**: `tests/vcs/test_diff_parser.py:25`
    - **Type**: Unit Test (Multi-hunk line calculation)
    - **Requirement**: RF27, RF28
    - **Result**: `PASS`
38. **TEST-VCS-07**: `TestGitDiffParser.test_extract_changed_lines_returns_correct_line_numbers`
    - **File**: `tests/vcs/test_diff_parser.py:38`
    - **Type**: Unit Test (Precise line mapping)
    - **Requirement**: RF27, RF28
    - **Result**: `PASS`
39. **TEST-VCS-08**: `TestGitDiffParser.test_parse_unified_diff_extracts_all_modified_files`
    - **File**: `tests/vcs/test_diff_parser.py:50`
    - **Type**: Unit Test (File dictionary extractor)
    - **Requirement**: RF27
    - **Result**: `PASS`
40. **TEST-VCS-09**: `TestGitHubAdapter.test_build_markdown_summary_redacts_secrets_rn02`
    - **File**: `tests/vcs/test_github_adapter.py:15`
    - **Type**: Security / Privacy Unit Test (Secret redaction)
    - **Requirement**: RF31
    - **Result**: `PASS`
41. **TEST-VCS-10**: `TestGitHubAdapter.test_generate_sarif_report_produces_valid_v2_json`
    - **File**: `tests/vcs/test_github_adapter.py:28`
    - **Type**: Integration Test (OASIS SARIF v2.1.0 schema)
    - **Requirement**: RF30
    - **Result**: `PASS`
42. **TEST-VCS-11**: `TestGitHubAdapter.test_get_changed_files_from_github_api`
    - **File**: `tests/vcs/test_github_adapter.py:45`
    - **Type**: Unit Test (GitHub API client)
    - **Requirement**: RF29
    - **Result**: `PASS`
43. **TEST-VCS-12**: `TestGitHubAdapter.test_publish_annotations_creates_check_run`
    - **File**: `tests/vcs/test_github_adapter.py:58`
    - **Type**: Integration Test (Check Run annotation POST)
    - **Requirement**: RF19, RF29
    - **Result**: `PASS`
44. **TEST-VCS-13**: `TestGitHubAdapter.test_publish_commit_status_makes_http_post`
    - **File**: `tests/vcs/test_github_adapter.py:75`
    - **Type**: Unit Test (Commit status update)
    - **Requirement**: RF29
    - **Result**: `PASS`
45. **TEST-VCS-14**: `TestGitLabAdapter.test_generate_code_quality_report_produces_valid_gl_format`
    - **File**: `tests/vcs/test_gitlab_adapter.py:15`
    - **Type**: Integration Test (Code Climate JSON)
    - **Requirement**: RF20, RF32
    - **Result**: `PASS`
46. **TEST-VCS-15**: `TestGitLabAdapter.test_get_changed_files_from_gitlab_api`
    - **File**: `tests/vcs/test_gitlab_adapter.py:30`
    - **Type**: Unit Test (GitLab API client)
    - **Requirement**: RF32
    - **Result**: `PASS`
47. **TEST-VCS-16**: `TestGitLabAdapter.test_post_mr_note_makes_http_post`
    - **File**: `tests/vcs/test_gitlab_adapter.py:44`
    - **Type**: Unit Test (MR discussion post)
    - **Requirement**: RF33
    - **Result**: `PASS`
48. **TEST-VCS-17**: `TestGitLabAdapter.test_publish_annotations_posts_note`
    - **File**: `tests/vcs/test_gitlab_adapter.py:58`
    - **Type**: Integration Test (Annotation publisher)
    - **Requirement**: RF33
    - **Result**: `PASS`
49. **TEST-VCS-18**: `TestBranchPolicyEngine.test_custom_policy_overrides`
    - **File**: `tests/vcs/test_policy_engine.py:15`
    - **Type**: Unit Test (Policy override evaluation)
    - **Requirement**: RF38
    - **Result**: `PASS`
50. **TEST-VCS-19**: `TestBranchPolicyEngine.test_feature_branch_permissive_policy`
    - **File**: `tests/vcs/test_policy_engine.py:28`
    - **Type**: Unit Test (Permissive branch rules)
    - **Requirement**: RF37
    - **Result**: `PASS`
51. **TEST-VCS-20**: `TestBranchPolicyEngine.test_main_branch_requires_strict_score_and_zero_p0`
    - **File**: `tests/vcs/test_policy_engine.py:40`
    - **Type**: Unit Test (Strict production branch gating)
    - **Requirement**: RF37
    - **Result**: `PASS`
52. **TEST-VCS-21**: `TestUnifiedVcsDispatcher.test_detect_vcs_environment_bitbucket`
    - **File**: `tests/vcs/test_unified_cli.py:15`
    - **Type**: Environment Detection Test
    - **Requirement**: RF39
    - **Result**: `PASS`
53. **TEST-VCS-22**: `TestUnifiedVcsDispatcher.test_detect_vcs_environment_github`
    - **File**: `tests/vcs/test_unified_cli.py:26`
    - **Type**: Environment Detection Test
    - **Requirement**: RF39
    - **Result**: `PASS`
54. **TEST-VCS-23**: `TestUnifiedVcsDispatcher.test_detect_vcs_environment_gitlab`
    - **File**: `tests/vcs/test_unified_cli.py:37`
    - **Type**: Environment Detection Test
    - **Requirement**: RF39
    - **Result**: `PASS`
55. **TEST-VCS-24**: `TestUnifiedVcsDispatcher.test_get_vcs_adapter_creates_correct_instance`
    - **File**: `tests/vcs/test_unified_cli.py:48`
    - **Type**: Factory Instantiation Test
    - **Requirement**: RF39, RF40
    - **Result**: `PASS`
56. **TEST-VCS-25**: `TestWebhookGateway.test_handle_unknown_webhook_returns_none`
    - **File**: `tests/vcs/test_webhook_gateway.py:15`
    - **Type**: Unit Test (Unsupported webhook fallback)
    - **Requirement**: RF36
    - **Result**: `PASS`
57. **TEST-VCS-26**: `TestWebhookGateway.test_parse_bitbucket_pullrequest_webhook`
    - **File**: `tests/vcs/test_webhook_gateway.py:25`
    - **Type**: Unit Test (Bitbucket webhook parser)
    - **Requirement**: RF36
    - **Result**: `PASS`
58. **TEST-VCS-27**: `TestWebhookGateway.test_parse_github_pull_request_webhook`
    - **File**: `tests/vcs/test_webhook_gateway.py:38`
    - **Type**: Unit Test (GitHub PR webhook parser)
    - **Requirement**: RF36
    - **Result**: `PASS`
59. **TEST-VCS-28**: `TestWebhookGateway.test_parse_gitlab_merge_request_webhook`
    - **File**: `tests/vcs/test_webhook_gateway.py:52`
    - **Type**: Unit Test (GitLab MR webhook parser)
    - **Requirement**: RF36
    - **Result**: `PASS`

---
