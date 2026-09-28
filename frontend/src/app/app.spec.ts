import { describe, it, expect, beforeEach } from 'vitest';
import { TestBed } from '@angular/core/testing';
import { App } from './app';
import { CultureGuardianService } from './services/culture-guardian.service';

describe('App (Bend DevOps Guardian Dashboard)', () => {
  beforeEach(async () => {
    if (typeof window !== 'undefined' && window.history) {
      window.history.replaceState({}, '', '/');
    }
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

  it('should toggle scope between branch_analysis and single_file and support post-analysis file review', async () => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;
    expect(app.auditScope()).toBe('branch_analysis');
    expect(app.isReviewingSpecificFile()).toBe(false);

    // Initial branch analysis
    await app.analyzeBranch();
    expect(app.currentReport().totalFiles).toBe(4);
    expect(app.branchSummary().totalFiles).toBe(4);

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

  it('should support Stage 1 Code Source switching between Local and Nuvem repository with turn on/off switch', async () => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;
    app.activeTab.set('analyze');
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;

    expect(app.codeSourceMode()).toBe('local');
    expect(app.localRepoName()).toBe('ai-bend-devops');
    expect(app.activeRepoName()).toBe('ai-bend-devops');
    expect(app.availableLocalRepos()).toContain('ai-bend-devops');

    // Verify DOM contains Local and Nuvem switch options and toggle switch
    const localOption = compiled.querySelector('[data-testid="code-source-local"]') as HTMLButtonElement;
    const nuvemOption = compiled.querySelector('[data-testid="code-source-nuvem"]') as HTMLButtonElement;
    const toggleSwitch = compiled.querySelector('[data-testid="code-source-toggle-switch"]') as HTMLButtonElement;
    expect(localOption).toBeTruthy();
    expect(nuvemOption).toBeTruthy();
    expect(toggleSwitch).toBeTruthy();
    expect(localOption?.textContent).toContain('Local');
    expect(localOption?.textContent).toContain('ON');
    expect(nuvemOption?.textContent).toContain('Nuvem');
    expect(nuvemOption?.textContent).toContain('OFF');

    // Click toggle switch to switch to Nuvem
    toggleSwitch.click();
    fixture.detectChanges();
    expect(app.codeSourceMode()).toBe('github');
    expect(app.isGitHubConnected()).toBe(false);
    expect(localOption?.textContent).toContain('OFF');
    expect(nuvemOption?.textContent).toContain('ON');

    // Click toggle switch again to switch back to Local
    toggleSwitch.click();
    fixture.detectChanges();
    expect(app.codeSourceMode()).toBe('local');
    expect(app.localRepoName()).toBe('ai-bend-devops');
    expect(localOption?.textContent).toContain('ON');
    expect(nuvemOption?.textContent).toContain('OFF');

    // Click Nuvem button directly
    nuvemOption.click();
    fixture.detectChanges();
    expect(app.codeSourceMode()).toBe('github');
    expect(localOption?.textContent).toContain('OFF');
    expect(nuvemOption?.textContent).toContain('ON');

    // Click Local button directly
    localOption.click();
    fixture.detectChanges();
    expect(app.codeSourceMode()).toBe('local');
    expect(localOption?.textContent).toContain('ON');
    expect(nuvemOption?.textContent).toContain('OFF');
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
    expect(app.selectedLocalRepo()).toBeNull();
    expect(app.availableBranches()).toEqual([]);
    expect(app.inputRepo()).toBe('');
  });

  it('should detect subdirectory of a git repository and allow using repository root', async () => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;

    // Simulate validation result for a subdirectory
    app.customLocalPathValidation.set({
      valid: true,
      selectedPath: '/home/isabelle/projects/ai-bend-devops/frontend',
      isSubdirectory: true,
      repositoryRoot: '/home/isabelle/projects/ai-bend-devops',
      repository: {
        id: 'ai-bend-devops',
        name: 'ai-bend-devops',
        path: '/home/isabelle/projects/ai-bend-devops',
        remoteUrl: '',
        currentBranch: 'main',
        branches: ['main'],
        headCommit: 'ab28967',
        isClean: true
      }
    });

    expect(app.isSubdirectoryDetected()).toBe(true);
    expect(app.subdirectoryRoot()).toBe('/home/isabelle/projects/ai-bend-devops');

    // Call useRepositoryRoot
    app.useRepositoryRoot();
    expect(app.customLocalPathInput()).toBe('/home/isabelle/projects/ai-bend-devops');
  });

  it('should trigger native directory picker and update card with real repository information', async () => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;

    // Verify initial clean state with active real repository
    expect(app.codeSourceMode()).toBe('local');
    expect(app.selectedLocalRepo()?.name).toBe('ai-bend-devops');
    expect(app.selectedLocalRepo()?.path).toBe('/home/isabelle/projects/ai-bend-devops');
    expect(app.selectedLocalRepo()?.currentBranch).toBe('main');

    // Trigger directory picker with native input
    const mockInput = document.createElement('input');
    mockInput.type = 'file';
    let clicked = false;
    mockInput.click = () => { clicked = true; };

    await app.triggerNativeDirectoryPicker(mockInput);
    expect(clicked).toBe(true);

    // Mock native directory picked event
    const mockFile = { webkitRelativePath: 'ai-bend-devops/README.md' } as File;
    const mockEvent = { target: { files: [mockFile] } } as unknown as Event;
    await app.onNativeDirectoryPicked(mockEvent);

    expect(app.selectedLocalRepo()?.name).toBe('ai-bend-devops');
    expect(app.customLocalPathValidation()?.valid).toBe(true);
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
    expect(app.hasExecutedAudit()).toBe(false);
    expect(app.currentReport().score).toBe(100);
    expect(app.currentReport().isApproved).toBe(true);

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

  it('should list detected violations in Branch Analysis Result and allow file review by violation file name', async () => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;

    await app.analyzeBranch();
    expect(app.auditScope()).toBe('branch_analysis');
    expect(app.branchViolations().length).toBeGreaterThan(0);
    expect(app.currentReport().totalViolations).toBeGreaterThan(0);

    const firstViolation = app.branchViolations()[0];
    expect(firstViolation.ruleId).toBeDefined();
    expect(firstViolation.fileName).toBeDefined();

    // Review file by violation file name
    app.reviewFileByName(firstViolation.fileName);
    expect(app.isReviewingSpecificFile()).toBe(true);
    expect(app.inputFileName()).toBe(firstViolation.fileName);

    app.closeFileReview();
    expect(app.isReviewingSpecificFile()).toBe(false);
  });

  it('should toggle light and dark themes with correct document classes', () => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;

    const initial = app.theme();
    app.toggleTheme();
    const next = app.theme();
    expect(next).not.toBe(initial);

    app.applyTheme('light');
    expect(document.documentElement.classList.contains('light')).toBe(true);
    expect(document.documentElement.classList.contains('dark')).toBe(false);

    app.applyTheme('dark');
    expect(document.documentElement.classList.contains('dark')).toBe(true);
    expect(document.documentElement.classList.contains('light')).toBe(false);
  });

  it('should synchronize active repository path and only execute evaluation when Analyze Branch is clicked', async () => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;

    // Initial default repo
    expect(app.activeRepoPath()).toBe('/home/isabelle/projects/ai-bend-devops');

    // Switch to another path or validate custom path -> should update selection WITHOUT auto-running audit
    await app.validateAndSetCustomPath('/home/isabelle/projects/ai-bend-devops');
    expect(app.selectedRepositoryPath()).toBe('/home/isabelle/projects/ai-bend-devops');
    expect(app.activeRepoPath()).toBe('/home/isabelle/projects/ai-bend-devops');
    expect(app.activeRepoName()).toBe('ai-bend-devops');
    expect(app.activeTargetScopeDescription()).toContain('Branch:');
    expect(app.currentAuditedFiles().length).toBe(0);

    // Explicitly click/run Analyze Branch
    await app.analyzeBranch();
    expect(app.currentAuditedFiles().length).toBeGreaterThan(0);
    expect(app.currentReport()).toBeDefined();

    // Verify Audit Results view reflects the path and audited files
    app.activeTab.set('results');
    await fixture.whenStable();
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.textContent).toContain('/home/isabelle/projects/ai-bend-devops');
  });

  it('should faithfully update progress bar percentage and step descriptions during analysis', async () => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;
    app.activeTab.set('analyze');
    await fixture.whenStable();
    fixture.detectChanges();

    expect(app.isAnalyzing()).toBe(false);
    expect(app.analysisProgress()).toBe(0);

    // Launch audit
    const analyzePromise = app.analyzeBranch();
    
    // Check that analyzing state is active
    expect(app.isAnalyzing()).toBe(true);
    expect(app.analysisProgress()).toBeGreaterThanOrEqual(10);
    expect(app.analysisProgressStep()).toBeTruthy();

    await analyzePromise;
    expect(app.analysisProgress()).toBe(100);
    expect(app.analysisProgressStep()).toContain('completed');
  });

  it('should produce 0 violations and 100% score when all custom rules are unselected', async () => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;
    app.activeTab.set('analyze');
    await fixture.whenStable();

    // Switch to custom rules mode and clear all rules
    app.setValidationScopeMode('custom');
    app.clearAllCustomRules();
    expect(app.selectedCustomRuleIds().size).toBe(0);
    expect(app.effectiveRulesCount()).toBe(0);

    // Execute audit with 0 selected rules
    await app.analyzeBranch();
    expect(app.currentReport().totalViolations).toBe(0);
    expect(app.currentReport().p0Count).toBe(0);
    expect(app.currentReport().score).toBe(100);
    expect(app.currentReport().isApproved).toBe(true);
    expect(app.branchViolations().length).toBe(0);
    expect(app.displayBranchFiles().every(f => f.status === 'passed')).toBe(true);
  });

  it('should support whole repository validation mode (full_repo) with active scope description', async () => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;
    app.activeTab.set('analyze');
    await fixture.whenStable();

    // Select full_repo target mode
    app.setAnalysisTargetMode('full_repo');
    expect(app.analysisTargetMode()).toBe('full_repo');
    expect(app.activeTargetScopeDescription()).toContain('Whole Repository');

    // Run audit in full_repo mode
    await app.analyzeBranch();
    expect(app.currentAuditedFiles().length).toBeGreaterThan(0);
    expect(app.history()[0].project).toContain('Whole Repository');
  });

  it('should trigger warning confirmation modal when attempting to validate build folders and allow confirm or cancel', async () => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;
    app.activeTab.set('analyze');
    await fixture.whenStable();

    app.setAnalysisTargetMode('full_repo');
    expect(app.includeBuildDirs()).toBe(false);
    expect(app.showBuildDirsWarningModal()).toBe(false);

    // User checks "Validar pastas de build" -> triggers warning modal
    app.onIncludeBuildDirsChange(true);
    expect(app.showBuildDirsWarningModal()).toBe(true);
    expect(app.includeBuildDirs()).toBe(false); // not confirmed yet

    // User cancels
    app.cancelIncludeBuildDirs();
    expect(app.showBuildDirsWarningModal()).toBe(false);
    expect(app.includeBuildDirs()).toBe(false);

    // User checks again and confirms
    app.onIncludeBuildDirsChange(true);
    expect(app.showBuildDirsWarningModal()).toBe(true);
    app.confirmIncludeBuildDirs();
    expect(app.showBuildDirsWarningModal()).toBe(false);
    expect(app.includeBuildDirs()).toBe(true);
    expect(app.activeTargetScopeDescription()).toContain('+ Build Dirs');

    // User unchecks directly -> turns off without modal
    app.onIncludeBuildDirsChange(false);
    expect(app.includeBuildDirs()).toBe(false);
    expect(app.showBuildDirsWarningModal()).toBe(false);
  });

  it('should filter findings across text search, rule dropdown, file dropdown, and severity buttons', () => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;
    app.selectPreset(1); // Non-compliant preset with multiple findings
    app.runLiveAudit();

    expect(app.allFindings().length).toBeGreaterThan(0);
    const initialCount = app.filteredViolations().length;
    expect(initialCount).toBeGreaterThan(0);
    expect(app.isFindingFiltered()).toBe(false);

    // 1. Text search
    app.violationSearch.set('Secret');
    expect(app.isFindingFiltered()).toBe(true);
    const searchFilteredCount = app.filteredViolations().length;
    expect(searchFilteredCount).toBeLessThanOrEqual(initialCount);

    // 2. Rule filter
    app.clearFindingFilters();
    expect(app.isFindingFiltered()).toBe(false);
    if (app.uniqueFindingRules().length > 0) {
      const targetRule = app.uniqueFindingRules()[0];
      app.findingRuleFilter.set(targetRule);
      expect(app.isFindingFiltered()).toBe(true);
      expect(app.filteredViolations().every((f: any) => f.ruleId === targetRule)).toBe(true);
    }

    // 3. Severity filter
    app.clearFindingFilters();
    app.selectedSeverityFilter.set('P0');
    expect(app.isFindingFiltered()).toBe(true);
    expect(app.filteredViolations().every((f: any) => f.severity === 'P0')).toBe(true);

    // 4. Reset filters
    app.clearFindingFilters();
    expect(app.isFindingFiltered()).toBe(false);
    expect(app.violationSearch()).toBe('');
    expect(app.findingRuleFilter()).toBe('all');
    expect(app.findingFileFilter()).toBe('all');
    expect(app.selectedSeverityFilter()).toBe('all');
    expect(app.filteredViolations().length).toBe(initialCount);
  });

  it('should manage SPA browser navigation history stack and forward/backward controls', () => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;

    // Initial state: dashboard
    expect(app.activeTab()).toBe('dashboard');
    expect(app.canGoBack()).toBe(false);
    expect(app.canGoForward()).toBe(false);
    expect(app.navHistory()).toEqual(['dashboard']);
    expect(app.navHistoryIndex()).toBe(0);

    // Navigate to analyze
    app.navigateToTab('analyze');
    expect(app.activeTab()).toBe('analyze');
    expect(app.canGoBack()).toBe(true);
    expect(app.canGoForward()).toBe(false);
    expect(app.navHistory()).toEqual(['dashboard', 'analyze']);
    expect(app.navHistoryIndex()).toBe(1);

    // Navigate to results
    app.navigateToTab('results');
    expect(app.activeTab()).toBe('results');
    expect(app.canGoBack()).toBe(true);
    expect(app.canGoForward()).toBe(false);
    expect(app.navHistory()).toEqual(['dashboard', 'analyze', 'results']);
    expect(app.navHistoryIndex()).toBe(2);

    // Go Back -> analyze
    app.goBack();
    expect(app.activeTab()).toBe('analyze');
    expect(app.canGoBack()).toBe(true);
    expect(app.canGoForward()).toBe(true);
    expect(app.navHistoryIndex()).toBe(1);

    // Go Back -> dashboard
    app.goBack();
    expect(app.activeTab()).toBe('dashboard');
    expect(app.canGoBack()).toBe(false);
    expect(app.canGoForward()).toBe(true);
    expect(app.navHistoryIndex()).toBe(0);

    // Go Forward -> analyze
    app.goForward();
    expect(app.activeTab()).toBe('analyze');
    expect(app.canGoBack()).toBe(true);
    expect(app.canGoForward()).toBe(true);
    expect(app.navHistoryIndex()).toBe(1);

    // Go Forward -> results
    app.goForward();
    expect(app.activeTab()).toBe('results');
    expect(app.canGoBack()).toBe(true);
    expect(app.canGoForward()).toBe(false);
    expect(app.navHistoryIndex()).toBe(2);

    // Branching navigation: Go back to analyze, then navigate to rules
    app.goBack();
    expect(app.activeTab()).toBe('analyze');
    app.navigateToTab('rules');
    expect(app.activeTab()).toBe('rules');
    expect(app.navHistory()).toEqual(['dashboard', 'analyze', 'rules']);
    expect(app.navHistoryIndex()).toBe(2);
    expect(app.canGoForward()).toBe(false);
  });

  it('should not falsely display BLOCKED when no audit has been executed or when 0 violations exist', async () => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;
    await fixture.whenStable();

    // Initial state: No audit executed
    expect(app.hasExecutedAudit()).toBe(false);
    expect(app.history().length).toBe(0);
    expect(app.currentAuditedFiles().length).toBe(0);
    // Report score is 100% and isApproved is true when 0 violations exist
    expect(app.currentReport().isApproved).toBe(true);
    expect(app.currentReport().score).toBe(100);
    expect(app.currentReport().p0Count).toBe(0);

    // After compliant audit: Approved
    app.selectPreset(0);
    expect(app.hasExecutedAudit()).toBe(true);
    expect(app.currentReport().isApproved).toBe(true);
    expect(app.currentReport().score).toBe(100);

    // Only non-compliant audit with P0 blockers triggers BLOCKED
    app.selectPreset(1);
    expect(app.currentReport().isApproved).toBe(false);
    expect(app.currentReport().p0Count).toBeGreaterThan(0);
  });

  it('should allow interactive configuration of Settings & Branch Policies', async () => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;
    await fixture.whenStable();

    // Navigate to settings tab
    app.navigateToTab('settings');
    expect(app.activeTab()).toBe('settings');

    // Switch subtabs
    app.setSettingsSubTab('engine');
    expect(app.settingsSubTab()).toBe('engine');

    // Update engine settings
    app.updateEngineSettingField('minGlobalPassingScore', 85);
    app.updateEngineSettingField('hvmWorkerThreads', 128);
    app.updateEngineSettingField('strictQualityGate', false);
    expect(app.engineSettings().minGlobalPassingScore).toBe(85);
    expect(app.engineSettings().hvmWorkerThreads).toBe(128);
    expect(app.engineSettings().strictQualityGate).toBe(false);

    // Switch to policies subtab
    app.setSettingsSubTab('policies');
    expect(app.settingsSubTab()).toBe('policies');
    const initialPoliciesCount = app.branchPolicies().length;

    // Add a new branch policy
    app.openAddPolicyModal();
    expect(app.isAddingPolicy()).toBe(true);
    app.newPolicyForm.set({
      id: 'policy-hotfix',
      name: 'Hotfix Emergency Policy',
      branchPattern: 'hotfix/*',
      minScore: 90,
      allowP0: false,
      allowP1: false,
      requireCleanBuild: true,
      requireCiApproval: true,
      blockOnPragmaWithoutReason: true,
      enabled: true,
      description: 'Emergency hotfix branches require zero warnings'
    });
    app.submitNewPolicy();
    expect(app.isAddingPolicy()).toBe(false);
    expect(app.branchPolicies().length).toBe(initialPoliciesCount + 1);

    const added = app.branchPolicies().find(p => p.id === 'policy-hotfix');
    expect(added).toBeDefined();
    expect(added?.branchPattern).toBe('hotfix/*');
    expect(added?.minScore).toBe(90);

    // Toggle and update policy
    const hotfixIdx = app.branchPolicies().findIndex(p => p.id === 'policy-hotfix');
    app.togglePolicy(hotfixIdx);
    expect(app.branchPolicies()[hotfixIdx].enabled).toBe(false);

    app.updatePolicyField(hotfixIdx, 'minScore', 95);
    expect(app.branchPolicies()[hotfixIdx].minScore).toBe(95);

    // Delete policy
    app.deletePolicy(hotfixIdx);
    expect(app.branchPolicies().length).toBe(initialPoliciesCount);

    // Reset settings
    app.resetEngineSettingsToDefault();
    expect(app.engineSettings().minGlobalPassingScore).toBe(80);
    expect(app.engineSettings().strictQualityGate).toBe(true);
  });

  it('should trigger framework detection prompt when selecting a repository and adapt rules upon confirmation', async () => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;
    await fixture.whenStable();

    // Ensure auto-scan setting is enabled
    app.updateEngineSettingField('autoScanFrameworkOnRepoSelect', true);
    expect(app.engineSettings().autoScanFrameworkOnRepoSelect).toBe(true);

    // Select local repository
    app.setLocalRepo('ai-bend-devops');
    expect(app.showFrameworkDetectionModal()).toBe(true);
    expect(app.pendingRepoForFrameworkScan()).toBeDefined();

    // Confirm framework scan
    await app.confirmFrameworkScan();
    expect(app.showFrameworkDetectionModal()).toBe(false);
    expect(app.lastFrameworkDetectionResult()).not.toBeNull();
    expect(app.lastFrameworkDetectionResult()?.valid).toBe(true);

    // Check that CancellationToken rule is active in rules catalog
    const rules = app.rules();
    const dotnetRule = rules.find(r => r.id === 'DOTNET-ASYNC-01');
    expect(dotnetRule).toBeDefined();
    expect(dotnetRule?.status).toBe('active');

    // Check toast feedback message was displayed
    expect(app.frameworkToastMessage()).toContain('configurado com sucesso');

    // Test quick preset application
    app.quickApplyFrameworkPreset('dotnet');
    expect(app.selectedProfile()).toBe('clean_architecture');
    expect(app.rules().find(r => r.id === 'DOTNET-ASYNC-01')?.status).toBe('active');

    app.quickApplyFrameworkPreset('angular');
    expect(app.selectedProfile()).toBe('frontend_clean');
    expect(app.rules().find(r => r.id === 'ARCH-FE-01')?.status).toBe('active');
  });

  it('should render and maintain always-visible applied rules panel on Live Auditor screen with search and severity filters', async () => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;
    await fixture.whenStable();

    app.navigateToTab('analyze');
    expect(app.activeTab()).toBe('analyze');

    // Default: panel is expanded and lists all active applied rules
    expect(app.isAppliedRulesPanelCollapsed()).toBe(false);
    expect(app.appliedRulesList().length).toBeGreaterThan(0);
    expect(app.appliedP0Count()).toBeGreaterThan(0);

    // Filter by text search
    app.appliedRulesFilter.set('DOTNET');
    const filtered = app.appliedRulesList();
    expect(filtered.length).toBeGreaterThan(0);
    expect(filtered.every(r => r.id.includes('DOTNET') || r.name.includes('DOTNET') || (r.category || '').includes('DOTNET') || (r.languages || []).includes('C#'))).toBe(true);

    // Clear text filter
    app.appliedRulesFilter.set('');

    // Filter by severity P0
    app.setAppliedRulesSeverityFilter('P0');
    expect(app.appliedRulesSeverityFilter()).toBe('P0');
    expect(app.appliedRulesList().every(r => r.severity.startsWith('P0'))).toBe(true);

    // Filter by severity P1
    app.setAppliedRulesSeverityFilter('P1');
    expect(app.appliedRulesSeverityFilter()).toBe('P1');
    expect(app.appliedRulesList().every(r => r.severity.startsWith('P1'))).toBe(true);

    // Reset severity filter
    app.setAppliedRulesSeverityFilter('ALL');
    expect(app.appliedRulesSeverityFilter()).toBe('ALL');

    // Toggle collapse
    app.toggleAppliedRulesPanel();
    expect(app.isAppliedRulesPanelCollapsed()).toBe(true);
    app.toggleAppliedRulesPanel();
    expect(app.isAppliedRulesPanelCollapsed()).toBe(false);
  });

  it('should open rule details modal when clicking on an applied rule card and support closing it', async () => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;
    await fixture.whenStable();

    app.navigateToTab('analyze');
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;

    expect(app.selectedRuleForDrawer()).toBeNull();
    expect(compiled.querySelector('[data-testid="rule-detail-modal"]')).toBeNull();

    // Find the first rule card and click it
    const firstRule = app.appliedRulesList()[0];
    expect(firstRule).toBeDefined();

    const ruleCard = compiled.querySelector(`[data-testid="applied-rule-card-${firstRule.id}"]`) as HTMLElement;
    expect(ruleCard).toBeTruthy();
    ruleCard.click();
    fixture.detectChanges();

    // Verify modal is open and has correct rule details
    expect(app.selectedRuleForDrawer()).not.toBeNull();
    expect(app.selectedRuleForDrawer()?.id).toBe(firstRule.id);

    const modal = compiled.querySelector('[data-testid="rule-detail-modal"]') as HTMLElement;
    expect(modal).toBeTruthy();
    expect(modal.textContent).toContain(firstRule.id);
    expect(modal.textContent).toContain(firstRule.name);

    // Close the modal via close button
    const closeBtn = modal.querySelector('[data-testid="close-rule-detail-modal-btn"]') as HTMLElement;
    expect(closeBtn).toBeTruthy();
    closeBtn.click();
    fixture.detectChanges();

    expect(app.selectedRuleForDrawer()).toBeNull();
    expect(compiled.querySelector('[data-testid="rule-detail-modal"]')).toBeNull();
  });

  it('should render pipeline flowchart with nodes and support node selection, creation, editing, cloning, and deletion', () => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;

    expect(app.pipelineNodes().length).toBeGreaterThanOrEqual(5);

    // Select a node
    app.selectPipelineNode('node_bend');
    expect(app.selectedNodeId()).toBe('node_bend');
    expect(app.selectedPipelineNode()?.name).toContain('Bend HVM');

    // Add a custom node
    const initialCount = app.pipelineNodes().length;
    app.openAddNodeModal('node_gate');
    expect(app.isAddingNode()).toBe(true);
    app.nodeForm.update(form => ({
      ...form,
      id: 'node_custom_smoke_test',
      name: 'Smoke Test & Health Check',
      shortName: 'SMOKE',
      type: 'test',
      command: './scripts/smoke-test.sh',
      runner: 'ubuntu-latest'
    }));
    app.saveNodeForm();
    expect(app.isAddingNode()).toBe(false);
    expect(app.pipelineNodes().length).toBe(initialCount + 1);
    expect(app.pipelineNodes().some(n => n.id === 'node_custom_smoke_test')).toBe(true);

    // Edit the created node
    const createdNode = app.pipelineNodes().find(n => n.id === 'node_custom_smoke_test')!;
    app.openEditNodeModal(createdNode);
    expect(app.isEditingNode()).toBe(true);
    app.nodeForm.update(form => ({
      ...form,
      name: 'Smoke Test & Health Check (Updated)'
    }));
    app.saveNodeForm();
    expect(app.isEditingNode()).toBe(false);
    expect(app.pipelineNodes().find(n => n.id === 'node_custom_smoke_test')?.name).toBe('Smoke Test & Health Check (Updated)');

    // Duplicate node
    app.duplicatePipelineNode('node_custom_smoke_test');
    expect(app.pipelineNodes().length).toBe(initialCount + 2);

    // Move node
    app.movePipelineNode('node_custom_smoke_test', 'left');

    // Toggle node status and allowFailure
    app.toggleNodeStatus('node_custom_smoke_test');
    app.toggleNodeAllowFailure('node_custom_smoke_test');
    const updated = app.pipelineNodes().find(n => n.id === 'node_custom_smoke_test');
    expect(updated?.allowFailure).toBe(true);

    // Delete nodes
    app.deletePipelineNode('node_custom_smoke_test');
    expect(app.pipelineNodes().some(n => n.id === 'node_custom_smoke_test')).toBe(false);
  });

  it('should generate valid synchronized Mermaid diagram flowchart code and CI/CD YAML configurations', () => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;

    // Mermaid code generation
    const mermaid = app.generatedMermaidCode();
    expect(mermaid).toContain('flowchart LR');
    expect(mermaid).toContain('classDef passed');
    expect(mermaid).toContain('node_trigger');
    expect(mermaid).toContain('node_bend');
    expect(mermaid).toContain('-->');

    // GitHub Actions YAML
    app.setPipelineTargetPlatform('github');
    const githubYaml = app.generatedPipelineYaml();
    expect(githubYaml).toContain('name: Bend DevOps Guardian Quality Gate');
    expect(githubYaml).toContain('runs-on:');
    expect(githubYaml).toContain('actions/checkout@v4');

    // GitLab CI YAML
    app.setPipelineTargetPlatform('gitlab');
    const gitlabYaml = app.generatedPipelineYaml();
    expect(gitlabYaml).toContain('stages:');
    expect(gitlabYaml).toContain('script:');

    // Azure Pipelines YAML
    app.setPipelineTargetPlatform('azure');
    const azureYaml = app.generatedPipelineYaml();
    expect(azureYaml).toContain('vmImage:');
    expect(azureYaml).toContain('displayName:');

    // Bitbucket Pipelines YAML
    app.setPipelineTargetPlatform('bitbucket');
    const bitbucketYaml = app.generatedPipelineYaml();
    expect(bitbucketYaml).toContain('pipelines:');
  });

  it('should switch pipeline blueprints/templates and simulate execution step by step', async () => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;

    // Switch blueprint to Clean Architecture GitOps
    app.applyPipelineBlueprint('clean_arch_gitops');
    expect(app.selectedPipelineBlueprint()).toBe('clean_arch_gitops');
    expect(app.pipelineTargetPlatform()).toBe('gitlab');
    expect(app.pipelineNodes().some(n => n.id === 'node_build_oci')).toBe(true);

    // Switch blueprint to Fast Feedback CI
    app.applyPipelineBlueprint('fast_feedback_ci');
    expect(app.selectedPipelineBlueprint()).toBe('fast_feedback_ci');
    expect(app.pipelineNodes().some(n => n.id === 'node_notify')).toBe(true);

    // Switch back to Bend Strict and simulate
    app.applyPipelineBlueprint('bend_strict');
    expect(app.selectedPipelineBlueprint()).toBe('bend_strict');

    // Run simulation (with 0ms delay for instant test execution)
    const simPromise = app.runPipelineSimulation(0);
    await simPromise;
    expect(app.isPipelineSimulating()).toBe(false);
    expect(app.pipelineSimulationProgress()).toBe(100);
    expect(app.pipelineSimulationLog().length).toBeGreaterThan(0);

    // Reset simulation
    app.resetPipelineSimulation();
    expect(app.pipelineSimulationProgress()).toBe(0);
    expect(app.pipelineSimulationLog().length).toBe(0);

    // Zoom controls
    app.setPipelineZoom(120);
    expect(app.pipelineZoom()).toBe(120);
    app.zoomInPipeline();
    expect(app.pipelineZoom()).toBe(135);
    app.zoomOutPipeline();
    expect(app.pipelineZoom()).toBe(120);
    app.resetPipelineZoom();
    expect(app.pipelineZoom()).toBe(100);
  });
});


