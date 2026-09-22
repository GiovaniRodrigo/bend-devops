import { Component, computed, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { CultureGuardianService } from './services/culture-guardian.service';
import { AnalysisRun, AuditReport, CodeViolation, CultureRule, FileAuditInfo } from './models/culture.model';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  private readonly guardianService = inject(CultureGuardianService);

  // Navigation
  readonly activeTab = signal<'dashboard' | 'analyze' | 'results' | 'history' | 'rules'>('dashboard');

  // MR/PR Analysis Form State
  readonly selectedMRIndex = signal<number>(0);
  readonly selectedRepo = signal<string>('acme/core-engine');
  readonly selectedMRId = signal<string>('142');
  readonly selectedDestBranch = signal<string>('main');

  // Standards and Languages Checklist
  readonly checkNaming = signal<boolean>(true);
  readonly checkIndentation = signal<boolean>(true);
  readonly checkOOP = signal<boolean>(true);
  readonly checkLazyCode = signal<boolean>(true);
  readonly checkSecrets = signal<boolean>(true);

  readonly langBend = signal<boolean>(true);
  readonly langPython = signal<boolean>(true);
  readonly langCpp = signal<boolean>(true);
  readonly langCSharp = signal<boolean>(true);

  // Search & Filter State
  readonly searchQuery = signal<string>('');
  readonly selectedSeverityFilter = signal<string>('all');

  // Service Data Signals
  readonly rules = this.guardianService.rules;
  readonly history = this.guardianService.history;
  readonly mrPresets = this.guardianService.mrPresets;

  // Currently Audited Files
  readonly currentAuditedFiles = signal<FileAuditInfo[]>([]);

  // Consolidated Audit Report
  readonly currentReport = computed<AuditReport>(() => {
    return this.guardianService.generateReport(this.currentAuditedFiles());
  });

  // Filtered Violations List
  readonly filteredViolations = computed<CodeViolation[]>(() => {
    const query = this.searchQuery().toLowerCase().trim();
    const filter = this.selectedSeverityFilter();

    let list: CodeViolation[] = [];
    if (this.currentAuditedFiles().length > 0) {
      this.currentAuditedFiles().forEach(f => list.push(...f.violations));
    } else {
      this.history().forEach(h => list.push(...h.violations));
    }

    if (query) {
      list = list.filter(v => 
        v.message.toLowerCase().includes(query) ||
        v.fileName.toLowerCase().includes(query) ||
        v.ruleId.toLowerCase().includes(query) ||
        (v.author && v.author.toLowerCase().includes(query))
      );
    }

    if (filter !== 'all') {
      list = list.filter(v => v.severity === filter);
    }

    return list;
  });

  // Dashboard Aggregated Metrics
  readonly totalMRsAnalyzed = computed(() => this.history().length + 20);
  readonly totalIssuesCount = computed(() => {
    return this.history().reduce((sum, item) => sum + item.issues, 0) + 135;
  });
  readonly averageScore = computed(() => {
    const scores = this.history().map(h => h.score);
    if (scores.length === 0) return 92;
    return Math.round(scores.reduce((a, b) => a + b, 0) / scores.length);
  });
  readonly totalRulesMonitored = computed(() => this.rules().length);

  constructor() {
    this.selectMR(0);
  }

  selectMR(index: number): void {
    this.selectedMRIndex.set(index);
    const preset = this.mrPresets[index];
    if (preset) {
      this.selectedRepo.set(preset.repo);
      this.selectedMRId.set(preset.mrId);
      this.selectedDestBranch.set(preset.targetBranch);

      const fileAudit = this.guardianService.auditCode(
        preset.fileName,
        preset.fullCode,
        preset.hasTestFile,
        preset.author
      );
      this.currentAuditedFiles.set([fileAudit]);
    }
  }

  runMRAnalysis(): void {
    const preset = this.mrPresets[this.selectedMRIndex()];
    if (!preset) return;

    const fileAudit = this.guardianService.auditCode(
      preset.fileName,
      preset.fullCode,
      preset.hasTestFile,
      preset.author
    );
    this.currentAuditedFiles.set([fileAudit]);

    const report = this.guardianService.generateReport([fileAudit]);
    const statusText = report.p0Count > 0 ? 'Blocked' : report.score === 100 ? 'Full compliance' : 'Completed';

    const newRun: AnalysisRun = {
      id: `${Date.now()}`,
      date: 'Just now',
      project: `${preset.repo} · #${preset.mrId}`,
      mrTitle: preset.mrTitle,
      author: preset.author,
      targetBranch: preset.targetBranch,
      issues: report.totalViolations,
      status: statusText,
      duration: '0.4s (Bend HVM)',
      violations: fileAudit.violations,
      score: report.score
    };

    this.history.update(h => [newRun, ...h]);
    this.activeTab.set('results');
  }

  toggleRuleStatus(ruleId: string): void {
    this.rules.update(rules => 
      rules.map(r => r.id === ruleId ? { ...r, status: r.status === 'active' ? 'inactive' : 'active' } : r)
    );
  }

  exportHistory(): void {
    const data = JSON.stringify(this.history(), null, 2);
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `compliance-history-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }
}
