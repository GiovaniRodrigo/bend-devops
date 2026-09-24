import { describe, it, expect, beforeEach } from 'vitest';
import { TestBed } from '@angular/core/testing';
import { App } from './app';
import { CultureGuardianService } from './services/culture-guardian.service';

describe('App (Bend DevOps Guardian Dashboard)', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [App],
      providers: [CultureGuardianService]
    }).compileComponents();
  });

  it('should create the Bend DevOps Guardian dashboard app', () => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;
    expect(app).toBeTruthy();
  });

  it('should render the Bend DevOps Guardian brand title in header', async () => {
    const fixture = TestBed.createComponent(App);
    await fixture.whenStable();
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('h1')?.textContent).toContain('Bend DevOps Guardian');
  });

  it('should switch tabs between dashboard, analyze, results, rules, vocabulary, vcs, and history', () => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;
    
    expect(app.activeTab()).toBe('dashboard');
    
    app.activeTab.set('analyze');
    expect(app.activeTab()).toBe('analyze');
    
    app.activeTab.set('results');
    expect(app.activeTab()).toBe('results');

    app.activeTab.set('rules');
    expect(app.activeTab()).toBe('rules');

    app.activeTab.set('vocabulary');
    expect(app.activeTab()).toBe('vocabulary');

    app.activeTab.set('vcs');
    expect(app.activeTab()).toBe('vcs');

    app.activeTab.set('history');
    expect(app.activeTab()).toBe('history');
  });

  it('should select preset and evaluate Clean Architecture code as 100% compliant', () => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;
    app.selectPreset(0);
    expect(app.inputFileName()).toBe('src/Domain/Entities/Order.cs');
    expect(app.currentReport().score).toBe(100);
    expect(app.currentReport().isApproved).toBe(true);
    expect(app.currentReport().p0Count).toBe(0);
  });

  it('should detect blocking violations (P0) in non-compliant code preset', () => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;
    app.selectPreset(1); // Non-compliant preset with secret and lazy code
    app.runLiveAudit();
    expect(app.activeTab()).toBe('results');
    expect(app.currentReport().isApproved).toBe(false);
    expect(app.currentReport().p0Count).toBeGreaterThan(0);
    expect(app.history().length).toBeGreaterThan(0);
  });

  it('should toggle rule active/inactive status and re-evaluate report', () => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;
    const rule = app.rules()[0];
    const initialStatus = rule.status;
    app.toggleRuleStatus(rule.id);
    const updatedRule = app.rules().find(r => r.id === rule.id);
    expect(updatedRule?.status).not.toBe(initialStatus);
  });

  it('should simulate VCS webhook event and parse payload', () => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;
    app.webhookPlatform.set('github');
    app.webhookBranch.set('main');
    app.simulateWebhook();
    expect(app.webhookResult()).toContain('Ingested Webhook [GITHUB]');
    expect(app.webhookResult()).toContain('Strict Gating Policy');
  });

  it('should generate valid SARIF v2.1.0 and GitLab JSON exports', () => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;
    app.openExport('sarif');
    expect(app.activeExportModal()).toBe('sarif');
    expect(app.exportedSarif()).toContain('https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json');

    app.openExport('gitlab');
    expect(app.activeExportModal()).toBe('gitlab');
    expect(app.exportedGitLabJson()).toBeDefined();

    app.closeExportModal();
    expect(app.activeExportModal()).toBeNull();
  });

  it('should filter layer vocabulary taxonomy by keyword', () => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;
    app.vocabularySearch.set('Domain');
    expect(app.filteredVocabulary().length).toBeGreaterThan(0);
    expect(app.filteredVocabulary()[0].layer).toBe('Domain');
  });

  it('should compute Before & After Code Diff with line alignment and rule explanations', () => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;
    
    // Preset 0 (Compliant): diff is identical
    app.selectPreset(0);
    const compliantDiff = app.currentCodeDiff();
    expect(compliantDiff.isIdentical).toBe(true);
    expect(compliantDiff.additions).toBe(0);
    expect(compliantDiff.deletions).toBe(0);

    // Preset 1 (Violations): diff contains additions, deletions and explanations
    app.selectPreset(1);
    const violationDiff = app.currentCodeDiff();
    expect(violationDiff.isIdentical).toBe(false);
    expect(violationDiff.additions).toBeGreaterThan(0);
    expect(violationDiff.deletions).toBeGreaterThan(0);
    expect(violationDiff.affectedRules).toContain('CULT04');
    expect(violationDiff.explanations.length).toBeGreaterThan(0);
    expect(violationDiff.splitBefore.length).toBeGreaterThan(0);
    expect(violationDiff.splitAfter.length).toBeGreaterThan(0);
  });

  it('should toggle diff view modes between split, unified, original, and corrected', () => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;
    expect(app.diffViewMode()).toBe('split');

    app.setDiffViewMode('unified');
    expect(app.diffViewMode()).toBe('unified');

    app.setDiffViewMode('original');
    expect(app.diffViewMode()).toBe('original');

    app.setDiffViewMode('corrected');
    expect(app.diffViewMode()).toBe('corrected');

    app.setDiffViewMode('split');
    expect(app.diffViewMode()).toBe('split');
  });

  it('should toggle scope between branch_analysis and single_file and support post-analysis file review', () => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;
    expect(app.auditScope()).toBe('branch_analysis');
    expect(app.isReviewingSpecificFile()).toBe(false);

    // Initial branch analysis
    app.analyzeBranch();
    expect(app.currentReport().totalFiles).toBe(4);
    expect(app.branchSummary().totalAdditions).toBe(327);
    expect(app.branchSummary().totalDeletions).toBe(84);

    // Start post-analysis file review on file 1
    app.startFileReview(1);
    expect(app.isReviewingSpecificFile()).toBe(true);
    expect(app.selectedBranchFileIndex()).toBe(1);
    expect(app.inputFileName()).toBe('src/Domain/Models/OrderInvoice.cs');

    // Close file review
    app.closeFileReview();
    expect(app.isReviewingSpecificFile()).toBe(false);

    // Switch to Single File Review mode
    app.setAuditScope('single_file');
    expect(app.auditScope()).toBe('single_file');
    expect(app.isReviewingSpecificFile()).toBe(false);

    // Switch back to Branch Analysis mode
    app.setAuditScope('branch_analysis');
    expect(app.auditScope()).toBe('branch_analysis');
  });

  it('should toggle progressive disclosure accordions and diff visibility', () => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;

    expect(app.showDiffView()).toBe(true);
    app.toggleDiffView();
    expect(app.showDiffView()).toBe(false);
    app.toggleDiffView();
    expect(app.showDiffView()).toBe(true);

    expect(app.isViolationsExpanded()).toBe(false);
    app.toggleViolationsExpanded();
    expect(app.isViolationsExpanded()).toBe(true);

    expect(app.isDetailsExpanded()).toBe(false);
    app.toggleDetailsExpanded();
    expect(app.isDetailsExpanded()).toBe(true);

    expect(app.isAdvancedScopeOpen()).toBe(false);
    app.toggleAdvancedScope();
    expect(app.isAdvancedScopeOpen()).toBe(true);
  });

  it('should execute in-place scope analysis on Analyze button click', () => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;
    const prevHistoryLen = app.history().length;

    app.setAuditScope('single_file');
    app.selectPreset(1);
    app.analyzeCurrentScope();

    expect(app.isAudited()).toBe(true);
    expect(app.currentReport().isApproved).toBe(false);
    expect(app.currentReport().totalViolations).toBeGreaterThan(0);
    expect(app.history().length).toBe(prevHistoryLen + 1);
  });

  it('should support Stage 1 Code Source switching between Local and GitHub repository', async () => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;

    expect(app.codeSourceMode()).toBe('local');
    expect(app.localRepoName()).toBe('ai-bend-devops');
    expect(app.activeRepoName()).toBe('ai-bend-devops');
    expect(app.availableLocalRepos()).toContain('ai-bend-devops');

    // Switch to GitHub repository
    app.setCodeSourceMode('github');
    expect(app.codeSourceMode()).toBe('github');
    // Without token, isGitHubConnected is false
    expect(app.isGitHubConnected()).toBe(false);

    // Switch back to Local repository
    app.setCodeSourceMode('local');
    expect(app.codeSourceMode()).toBe('local');
    expect(app.localRepoName()).toBe('ai-bend-devops');
  });

  it('should allow user to select and validate local repository directory path', async () => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;

    expect(app.codeSourceMode()).toBe('local');
    expect(app.customLocalPathInput()).toBe('/home/isabelle/projects/ai-bend-devops');

    // Test valid local directory path
    await app.validateAndSetCustomPath('/home/isabelle/projects/ai-bend-devops');
    expect(app.customLocalPathValidation()?.valid).toBe(true);
    expect(app.customLocalPathValidation()?.repository?.name).toBe('ai-bend-devops');
    expect(app.selectedLocalRepoId()).toBe('ai-bend-devops');

    // Test invalid local directory path
    await app.validateAndSetCustomPath('/nonexistent/random/directory/path');
    expect(app.customLocalPathValidation()?.valid).toBe(false);
    expect(app.customLocalPathValidation()?.error).toBeDefined();
  });

  it('should support Stage 2 Target Modes (Branch Comparison, Working Tree, Commit SHA)', async () => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;

    // Target 1: Branch Mode
    expect(app.analysisTargetMode()).toBe('branch');
    expect(app.availableBranches()).toContain('main');

    // Target 2: Working Tree Mode
    app.setAnalysisTargetMode('working_tree');
    expect(app.analysisTargetMode()).toBe('working_tree');
    expect(app.workingTreeInfo()).toBeDefined();

    // Target 3: Commit SHA Validation
    app.setAnalysisTargetMode('commit');
    expect(app.analysisTargetMode()).toBe('commit');

    // Validate real HEAD commit
    await app.validateCommitInput('ab28967');
    expect(app.commitValidation()?.valid).toBe(true);
    expect(app.commitValidation()?.shortSha).toBe('ab28967');

    // Validate non-existent fake commit
    await app.validateCommitInput('nonexistent999999');
    expect(app.commitValidation()?.valid).toBe(false);
    expect(app.commitValidation()?.error).toContain('Commit not found');
  });

  it('should support Stage 3 Architecture Validation scope (All, Rule Set, Custom) and dynamic rule counts', () => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;

    // Mode 1: All Architecture Rules
    expect(app.validationScopeMode()).toBe('all');
    expect(app.allActiveRulesCount()).toBe(app.rules().filter(r => r.status === 'active').length);
    expect(app.effectiveRulesCount()).toBe(app.allActiveRulesCount());
    expect(app.ctaButtonText()).toContain(`Analyze Branch (All ${app.allActiveRulesCount()} Rules)`);

    // Mode 2: Rule Set Profile
    app.setValidationScopeMode('ruleset');
    expect(app.validationScopeMode()).toBe('ruleset');
    expect(app.ctaButtonText()).toContain('Analyze Branch');

    // Mode 3: Custom Rules
    app.setValidationScopeMode('custom');
    expect(app.validationScopeMode()).toBe('custom');
    expect(app.selectedCustomRuleIds().size).toBeGreaterThan(0);

    // Toggle custom rules
    const firstRuleId = app.rules()[0].id;
    expect(app.isCustomRuleSelected(firstRuleId)).toBe(true);
    app.toggleCustomRule(firstRuleId);
    expect(app.isCustomRuleSelected(firstRuleId)).toBe(false);

    // Clear all and Select all
    app.clearAllCustomRules();
    expect(app.selectedCustomRuleIds().size).toBe(0);
    expect(app.effectiveRulesCount()).toBe(0);

    app.selectAllCustomRules();
    expect(app.selectedCustomRuleIds().size).toBe(app.rules().length);
    expect(app.effectiveRulesCount()).toBe(app.rules().length);
  });

  it('should operate in Real Data mode by default with no fabricated offsets', () => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;

    // Real Data Default check
    expect(app.isMockMode()).toBe(false);
    expect(app.mockScenario()).toBeNull();
    expect(app.localRepoName()).toBe('ai-bend-devops');
    expect(app.availableLocalRepos()).toContain('ai-bend-devops');
    expect(app.availableBranches()).toContain('main');

    // Metrics are strictly computed from real executions, not arbitrary offsets (no +842, no || 24)
    expect(app.totalAuditsExecuted()).toBe(app.history().length);
    expect(app.totalViolationsBlocked()).toBe(app.history().reduce((sum, h) => sum + h.p0Count, 0));
  });

  it('should support explicit Mock Mode scenarios and cleanly toggle back to real data', () => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;

    // Explicitly enable architecture-violations scenario
    app.enableMockScenario('architecture-violations');
    expect(app.isMockMode()).toBe(true);
    expect(app.mockScenario()).toBe('architecture-violations');
    expect(app.currentReport().isApproved).toBe(false);
    expect(app.currentReport().p0Count).toBeGreaterThan(0);

    // Explicitly enable clean-repository scenario
    app.enableMockScenario('clean-repository');
    expect(app.isMockMode()).toBe(true);
    expect(app.mockScenario()).toBe('clean-repository');
    expect(app.currentReport().isApproved).toBe(true);
    expect(app.currentReport().score).toBe(100);

    // Explicitly enable empty-repository scenario
    app.enableMockScenario('empty-repository');
    expect(app.isMockMode()).toBe(true);
    expect(app.mockScenario()).toBe('empty-repository');
    expect(app.currentAuditedFiles().length).toBe(0);
    expect(app.history().length).toBe(0);
    expect(app.currentReport().score).toBe(0);
    expect(app.currentReport().isApproved).toBe(false);

    // Exit Mock Mode back to real data
    app.disableMockMode();
    expect(app.isMockMode()).toBe(false);
    expect(app.mockScenario()).toBeNull();
  });

  it('should display honest empty states when no audit has been run in empty scenario', async () => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;

    app.enableMockScenario('empty-repository');
    app.activeTab.set('results');
    fixture.detectChanges();
    await fixture.whenStable();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.textContent).toContain('No Audit Results Available');
    expect(compiled.textContent).toContain('No repository or branch audits have been recorded in this session yet.');
  });
});

