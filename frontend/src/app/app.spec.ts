import { describe, it, expect, beforeEach } from 'vitest';
import { TestBed } from '@angular/core/testing';
import { App } from './app';
import { CultureGuardianService } from './services/culture-guardian.service';

describe('App (CodeConform Dashboard)', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [App],
      providers: [CultureGuardianService]
    }).compileComponents();
  });

  it('should create the CodeConform dashboard app', () => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;
    expect(app).toBeTruthy();
  });

  it('should render the CodeConform brand title in header', async () => {
    const fixture = TestBed.createComponent(App);
    await fixture.whenStable();
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('h1')?.textContent).toContain('CodeConform');
  });

  it('should switch tabs between dashboard, analyze, results, history, and rules', () => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;
    
    expect(app.activeTab()).toBe('dashboard');
    
    app.activeTab.set('analyze');
    expect(app.activeTab()).toBe('analyze');
    
    app.activeTab.set('results');
    expect(app.activeTab()).toBe('results');

    app.activeTab.set('history');
    expect(app.activeTab()).toBe('history');

    app.activeTab.set('rules');
    expect(app.activeTab()).toBe('rules');
  });

  it('should select MR preset and evaluate diff', () => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;
    app.selectMR(0);
    expect(app.selectedMRId()).toBe('142');
    expect(app.currentReport().score).toBe(100);
    expect(app.currentReport().isApproved).toBe(true);
  });

  it('should run MR analysis on non-compliant preset and detect violations', () => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;
    app.selectMR(1); // MR #87 with issues
    app.runMRAnalysis();
    expect(app.activeTab()).toBe('results');
    expect(app.currentReport().isApproved).toBe(false);
    expect(app.currentReport().p0Count).toBeGreaterThan(0);
  });

  it('should toggle rule active/inactive status', () => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;
    const rule = app.rules()[0];
    const initialStatus = rule.status;
    app.toggleRuleStatus(rule.id);
    const updatedRule = app.rules().find(r => r.id === rule.id);
    expect(updatedRule?.status).not.toBe(initialStatus);
  });
});
