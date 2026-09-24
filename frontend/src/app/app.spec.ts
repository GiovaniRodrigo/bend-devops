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

  it('should toggle scope between single_file and branch_changes and select branch files', () => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;
    expect(app.auditScope()).toBe('single_file');

    app.setAuditScope('branch_changes');
    expect(app.auditScope()).toBe('branch_changes');

    app.selectBranchFile(1);
    expect(app.selectedBranchFileIndex()).toBe(1);
    expect(app.inputFileName()).toBe('src/Domain/Models/OrderInvoice.cs');

    app.setAuditScope('single_file');
    expect(app.auditScope()).toBe('single_file');
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

    app.selectPreset(1);
    app.analyzeCurrentScope();

    expect(app.isAudited()).toBe(true);
    expect(app.currentReport().isApproved).toBe(false);
    expect(app.currentReport().totalViolations).toBeGreaterThan(0);
    expect(app.history().length).toBe(prevHistoryLen + 1);
  });
});
