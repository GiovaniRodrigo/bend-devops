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
});
