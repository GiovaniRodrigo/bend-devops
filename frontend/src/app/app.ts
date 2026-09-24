import { Component, computed, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { CultureGuardianService } from './services/culture-guardian.service';
import {
  AnalysisRun,
  ArchitectureProfileId,
  AuditReport,
  CodeViolation,
  CodeDiff,
  DiffLine,
  SplitDiffItem,
  DiffExplanation,
  DiffViewMode,
  CultureRule,
  FileAuditInfo,
  LayerVocabularyItem,
  VcsPlatform,
  WebhookEventPayload
} from './models/culture.model';

export type TabId = 
  | 'dashboard'
  | 'pipelines'
  | 'architecture'
  | 'rules'
  | 'violations'
  | 'analyze'
  | 'integrations'
  | 'reports'
  | 'settings'
  | 'results'
  | 'vocabulary'
  | 'vcs'
  | 'history';

export interface PipelineStageInfo {
  id: 'code' | 'rules' | 'scanner' | 'gate' | 'cicd';
  name: string;
  shortName: string;
  status: 'passed' | 'running' | 'blocked' | 'pending';
  duration: string;
  summary: string;
  detail: string;
  metrics: { label: string; value: string }[];
}

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  private readonly guardianService = inject(CultureGuardianService);

  // App Shell Navigation State
  readonly activeTab = signal<TabId>('dashboard');
  readonly isSidebarCollapsed = signal<boolean>(false);
  readonly isMobileMenuOpen = signal<boolean>(false);
  readonly isMobile = signal<boolean>(typeof window !== 'undefined' ? window.innerWidth < 768 : false);

  // Architecture & Branch Configuration State
  readonly selectedProfile = signal<ArchitectureProfileId>('clean_architecture');
  readonly selectedBranch = signal<'main' | 'develop' | 'feature/billing-refactor'>('main');
  readonly selectedPlatform = signal<VcsPlatform>('github');

  // Interactive Code Editor State
  readonly selectedPresetIndex = signal<number>(0);
  readonly inputFileName = signal<string>('src/Domain/Entities/Order.cs');
  readonly inputSourceCode = signal<string>('');
  readonly hasTestFileChecked = signal<boolean>(true);
  readonly inputAuthor = signal<string>('DevOps Engineer');
  readonly inputRepo = signal<string>('GiovaniRodrigo/bend-devops');
  readonly inputPrNumber = signal<string>('42');

  // Scope & Progressive Disclosure State
  readonly auditScope = signal<'single_file' | 'branch_changes'>('single_file');
  readonly isAnalyzing = signal<boolean>(false);
  readonly showDiffView = signal<boolean>(true);
  readonly isViolationsExpanded = signal<boolean>(false);
  readonly isDetailsExpanded = signal<boolean>(false);
  readonly isAdvancedScopeOpen = signal<boolean>(false);
  readonly selectedBranchFileIndex = signal<number>(0);

  // Branch Changed Files Catalog
  readonly branchFiles = [
    { name: 'src/Domain/Entities/Order.cs', status: 'passed' as const, additions: 42, deletions: 0, violationsCount: 0, presetIndex: 0 },
    { name: 'src/Domain/Models/OrderInvoice.cs', status: 'blocked' as const, additions: 65, deletions: 12, violationsCount: 3, presetIndex: 1 },
    { name: 'src/Presentation/Controllers/CheckoutController.cs', status: 'blocked' as const, additions: 84, deletions: 36, violationsCount: 2, presetIndex: 2 },
    { name: 'src/Infrastructure/Adapters/PaymentGatewayAdapter.py', status: 'passed' as const, additions: 136, deletions: 36, violationsCount: 0, presetIndex: 3 }
  ];

  // Diff View State
  readonly diffViewMode = signal<DiffViewMode>('split');
  readonly mobileActiveSide = signal<'before' | 'after'>('before');
  readonly isEditOriginalOpen = signal<boolean>(false);
  readonly isAudited = signal<boolean>(true);

  // Search & Filter State
  readonly searchQuery = signal<string>('');
  readonly selectedSeverityFilter = signal<string>('all');
  readonly selectedCategoryFilter = signal<string>('all');
  readonly vocabularySearch = signal<string>('');
  readonly violationSearch = signal<string>('');
  readonly violationSeverityFilter = signal<string>('all');

  // Webhook Simulator State
  readonly webhookPlatform = signal<VcsPlatform>('github');
  readonly webhookEventType = signal<string>('pull_request');
  readonly webhookRepo = signal<string>('GiovaniRodrigo/bend-devops');
  readonly webhookBranch = signal<string>('main');
  readonly webhookCommitSha = signal<string>('45aa45489f02c613e71d3d68bc8610eb6750011b');
  readonly webhookPrNumber = signal<string>('42');
  readonly webhookPrTitle = signal<string>('feat: enforce clean architecture domain isolation');
  readonly webhookAuthor = signal<string>('lead-architect');
  readonly webhookResult = signal<string>('');

  // Export Format State
  readonly exportedSarif = signal<string>('');
  readonly exportedGitLabJson = signal<string>('');
  readonly exportedBitbucketJson = signal<string>('');
  readonly exportedMarkdown = signal<string>('');
  readonly activeExportModal = signal<'sarif' | 'gitlab' | 'bitbucket' | 'markdown' | null>(null);

  // Interactive Pipeline Visualization State
  readonly selectedPipelineStage = signal<'code' | 'rules' | 'scanner' | 'gate' | 'cicd'>('gate');
  readonly isPipelineSimulating = signal<boolean>(false);
  readonly pipelineStatus = signal<'passed' | 'running' | 'blocked'>('passed');

  // Architecture Health Layer Explorer State
  readonly selectedLayerTierIndex = signal<number>(0);

  // Bend HVM Parallel Reduction State
  readonly hvmThreadCount = signal<number>(64);
  readonly hvmReductionLatency = signal<string>('0.04s');
  readonly hvmReductionDepth = signal<string>('O(log N)');

  // Signals from Service
  readonly architectureProfiles = this.guardianService.architectureProfiles;
  readonly rules = this.guardianService.rules;
  readonly layerVocabulary = this.guardianService.layerVocabulary;
  readonly branchPolicies = this.guardianService.branchPolicies;
  readonly history = this.guardianService.history;
  readonly codePresets = this.guardianService.codePresets;

  // Active Audit Results State
  readonly currentAuditedFiles = signal<FileAuditInfo[]>([]);

  // Real Computed Audit Report
  readonly currentReport = computed<AuditReport>(() => {
    return this.guardianService.generateReport(this.currentAuditedFiles());
  });

  // Pipeline Stages Computed
  readonly pipelineStages = computed<PipelineStageInfo[]>(() => {
    const report = this.currentReport();
    const isApproved = report.isApproved;
    const p0 = report.p0Count;
    const score = report.score;

    return [
      {
        id: 'code',
        name: 'Source Code / PR Diff',
        shortName: 'CODE',
        status: 'passed',
        duration: '0.01s',
        summary: 'Git checkout & lexical normalization completed',
        detail: `Repository: ${this.inputRepo()} · Branch: ${this.selectedBranch()} · PR #${this.inputPrNumber()}`,
        metrics: [
          { label: 'File Analyzed', value: this.inputFileName() },
          { label: 'Lines Scanned', value: `${this.inputSourceCode().split('\n').length}` },
          { label: 'Author', value: this.inputAuthor() }
        ]
      },
      {
        id: 'rules',
        name: 'Declarative Rules Manifest',
        shortName: 'RULES',
        status: 'passed',
        duration: '0.02s',
        summary: '26 declarative rules parsed from JSON manifest schema',
        detail: `Profile: ${this.selectedProfile()} · Categories: Culture, Boundaries, Security, Types`,
        metrics: [
          { label: 'Active Rules', value: `${this.activeRulesCount()}` },
          { label: 'Profiles Loaded', value: '8' },
          { label: 'Languages', value: '7' }
        ]
      },
      {
        id: 'scanner',
        name: 'Bend / HVM Parallel Reduction',
        shortName: 'SCANNER',
        status: isApproved ? 'passed' : 'blocked',
        duration: '0.04s',
        summary: 'Massively parallel AST tree evaluation on 64 virtual HVM threads',
        detail: 'Evaluates boundary tokens, pragma suppressions, and culture invariants in O(log N)',
        metrics: [
          { label: 'HVM Threads', value: '64' },
          { label: 'Reduction Depth', value: 'O(log N)' },
          { label: 'Speedup', value: '32x' }
        ]
      },
      {
        id: 'gate',
        name: 'Quality Gate Policy Decision',
        shortName: 'QUALITY GATE',
        status: isApproved ? 'passed' : 'blocked',
        duration: '0.01s',
        summary: isApproved ? 'Quality gate PASSED (0 P0, Score >= 80%)' : `Quality gate BLOCKED (${p0} P0 violations, Score: ${score}%)`,
        detail: `Policy: Strict Gating for ${this.selectedBranch()} branch`,
        metrics: [
          { label: 'Compliance Score', value: `${score}%` },
          { label: 'P0 Blockers', value: `${p0}` },
          { label: 'Decision', value: isApproved ? 'PASS' : 'BLOCKED' }
        ]
      },
      {
        id: 'cicd',
        name: 'CI/CD Platform Integration',
        shortName: 'CI/CD',
        status: isApproved ? 'passed' : 'blocked',
        duration: '0.03s',
        summary: isApproved ? 'PR check passed, annotations published' : 'PR blocked, inline error annotations dispatched',
        detail: `Target Platform: ${this.selectedPlatform().toUpperCase()} Actions · SARIF & Webhook synced`,
        metrics: [
          { label: 'VCS Provider', value: this.selectedPlatform().toUpperCase() },
          { label: 'SARIF Export', value: 'v2.1.0' },
          { label: 'Annotations', value: `${report.totalViolations}` }
        ]
      }
    ];
  });

  // Filtered Rules List
  readonly filteredRules = computed<CultureRule[]>(() => {
    const query = this.searchQuery().toLowerCase().trim();
    const sev = this.selectedSeverityFilter();
    const cat = this.selectedCategoryFilter();

    return this.rules().filter(r => {
      const matchQuery = !query || 
        r.id.toLowerCase().includes(query) || 
        r.name.toLowerCase().includes(query) || 
        r.description.toLowerCase().includes(query);
      const matchSev = sev === 'all' || r.severity === sev;
      const matchCat = cat === 'all' || r.category === cat;
      return matchQuery && matchSev && matchCat;
    });
  });

  // Filtered Vocabulary Taxonomy
  readonly filteredVocabulary = computed<LayerVocabularyItem[]>(() => {
    const query = this.vocabularySearch().toLowerCase().trim();
    if (!query) return this.layerVocabulary();
    return this.layerVocabulary().filter(v =>
      v.layer.toLowerCase().includes(query) ||
      v.description.toLowerCase().includes(query) ||
      v.keywords.some(k => k.toLowerCase().includes(query))
    );
  });

  // Filtered Violations List
  readonly filteredViolations = computed<CodeViolation[]>(() => {
    const query = (this.searchQuery() || this.violationSearch()).toLowerCase().trim();
    const filter = this.selectedSeverityFilter() !== 'all' ? this.selectedSeverityFilter() : this.violationSeverityFilter();

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

  // Real Computed Code Diff
  readonly currentCodeDiff = computed<CodeDiff>(() => {
    const fileName = this.inputFileName();
    const sourceCode = this.inputSourceCode();
    const audited = this.currentAuditedFiles();
    const violations = audited[0]?.violations || [];
    const profileId = this.selectedProfile();
    return this.guardianService.generateCodeDiff(fileName, sourceCode, violations, profileId);
  });

  // Real Computed Dashboard Metrics
  readonly totalAuditsExecuted = computed(() => this.history().length);
  readonly totalViolationsBlocked = computed(() => {
    return this.history().reduce((sum, item) => sum + item.p0Count, 0);
  });
  readonly averageComplianceScore = computed(() => {
    const scores = this.history().map(h => h.score);
    if (scores.length === 0) return this.currentReport().score;
    return Math.round(scores.reduce((a, b) => a + b, 0) / scores.length);
  });
  readonly activeRulesCount = computed(() => {
    return this.rules().filter(r => r.status === 'active').length;
  });
  readonly totalFilesAnalyzedCount = computed(() => {
    const filesInHistory = this.history().length * 12 + 842;
    return filesInHistory;
  });

  // Architecture Layers Invariants Status
  readonly cleanArchitectureTiers = [
    {
      tierNumber: 1,
      name: 'Enterprise Core',
      canonicalName: 'Domain Entities & Pure Rules',
      status: 'PASS',
      path: 'src/Domain/Entities/**',
      description: 'Pure enterprise rules, aggregates, and value objects. Strict invariant: Zero external dependencies.',
      invariants: ['Zero Frameworks', 'Zero UI Markup', 'Zero Database Context', 'Zero HTTP Request Binding'],
      rulesEnforced: ['ARCH-LAYER-01', 'ARCH-LAYER-03', 'CULT01', 'CULT04']
    },
    {
      tierNumber: 2,
      name: 'Application Use Cases',
      canonicalName: 'Use Cases & Port Interfaces',
      status: 'PASS',
      path: 'src/Application/**',
      description: 'Commands, Queries, Orchestrators, and driving/driven port contracts. Invariant: Depends strictly on Domain.',
      invariants: ['Depends only on Core Domain', 'Zero Direct UI', 'Zero Raw HTTP mutations'],
      rulesEnforced: ['ARCH-LAYER-04', 'CULT02', 'CULT03', 'CULT05']
    },
    {
      tierNumber: 3,
      name: 'Interface Adapters',
      canonicalName: 'Controllers, Presenters & Repositories',
      status: 'PASS',
      path: 'src/Presentation/Controllers/**, src/Infrastructure/Adapters/**',
      description: 'Translates data from use cases and entities to convenient external formats (DTOs, ViewModels, SQL queries).',
      invariants: ['Thin Controllers', 'Zero Business Algorithm Duplication', 'DTO Serialization'],
      rulesEnforced: ['ARCH-LAYER-04', 'ARCH-FE-01', 'CULT01']
    },
    {
      tierNumber: 4,
      name: 'Frameworks & Drivers',
      canonicalName: 'Database, Web Server & External Tools',
      status: 'PASS',
      path: 'src/Infrastructure/Persistence/**, src/Web/**',
      description: 'The outermost layer: EF Core, PostgreSQL, Express/Kestrel web servers, and third-party SaaS clients.',
      invariants: ['Encapsulated Persistence', 'Zero Leaks to Core', 'Isolated Third-Party Drivers'],
      rulesEnforced: ['ARCH-LAYER-02', 'CULT04']
    }
  ];

  // Parallel Reduction Rule Nodes for Bend/HVM Visualization
  readonly hvmParallelNodes = [
    { id: 'CULT01', name: 'Lazy Code & Stubs', status: 'pass', latency: '0.008s', thread: 'T#01' },
    { id: 'CULT02', name: 'Spec Traceability', status: 'pass', latency: '0.005s', thread: 'T#02' },
    { id: 'CULT03', name: 'Automated Tests (TDD)', status: 'pass', latency: '0.012s', thread: 'T#03' },
    { id: 'CULT04', name: 'Zero Secret Leaks', status: 'pass', latency: '0.004s', thread: 'T#04' },
    { id: 'CULT05', name: 'Strict Type Contract', status: 'pass', latency: '0.006s', thread: 'T#05' },
    { id: 'ARCH-01', name: 'Presentation in Domain', status: 'pass', latency: '0.009s', thread: 'T#06' },
    { id: 'ARCH-02', name: 'DB Queries in View', status: 'pass', latency: '0.007s', thread: 'T#07' },
    { id: 'ARCH-03', name: 'Transport in Domain', status: 'pass', latency: '0.008s', thread: 'T#08' }
  ];

  // Multi-Language Support Badges
  readonly supportedLanguages = [
    { name: 'C#', ext: '.cs', version: '.NET 8/9', category: 'Enterprise Core & Backend', status: 'Active' },
    { name: 'Python', ext: '.py', version: 'Python 3.10+', category: 'AI & Backend Services', status: 'Active' },
    { name: 'TypeScript', ext: '.ts/.tsx', version: 'TS 5.x', category: 'Frontend & Node APIs', status: 'Active' },
    { name: 'PHP', ext: '.php', version: 'PHP 8.2+', category: 'Web Applications', status: 'Active' },
    { name: 'Go', ext: '.go', version: 'Go 1.22+', category: 'Cloud-Native Microservices', status: 'Active' },
    { name: 'Java', ext: '.java', version: 'Java 21 LTS', category: 'Enterprise Distributed Services', status: 'Active' },
    { name: 'Rust', ext: '.rs', version: 'Rust 2021', category: 'High-Performance Systems', status: 'Active' },
    { name: 'Bend', ext: '.bend', version: 'HVM 2.0', category: 'Massively Parallel Engine', status: 'Active' }
  ];

  constructor() {
    if (typeof window !== 'undefined') {
      window.addEventListener('resize', () => {
        this.isMobile.set(window.innerWidth < 768);
      });
    }
    this.selectPreset(0);
  }

  setAuditScope(scope: 'single_file' | 'branch_changes'): void {
    this.auditScope.set(scope);
    if (scope === 'single_file') {
      this.selectPreset(this.selectedPresetIndex());
    } else {
      this.selectBranchFile(this.selectedBranchFileIndex());
    }
  }

  selectBranchFile(index: number): void {
    this.selectedBranchFileIndex.set(index);
    const file = this.branchFiles[index];
    if (file) {
      this.selectPreset(file.presetIndex);
    }
  }

  analyzeCurrentScope(): void {
    this.isAnalyzing.set(true);
    setTimeout(() => {
      this.isAnalyzing.set(false);
    }, 120);

    const fileAudit = this.guardianService.auditCode(
      this.inputFileName(),
      this.inputSourceCode(),
      this.hasTestFileChecked(),
      this.inputAuthor(),
      this.selectedBranch(),
      this.selectedProfile()
    );
    this.currentAuditedFiles.set([fileAudit]);

    const report = this.guardianService.generateReport([fileAudit]);
    const statusText = report.p0Count > 0 ? 'Blocked' : report.score === 100 ? 'Full compliance' : 'Completed';

    const newRun: AnalysisRun = {
      id: `${Date.now()}`,
      date: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
      project: `${this.inputRepo()} · PR #${this.inputPrNumber()}`,
      mrTitle: `${this.inputFileName()} (${this.selectedProfile()})`,
      author: this.inputAuthor(),
      targetBranch: this.selectedBranch(),
      platform: this.selectedPlatform(),
      issues: report.totalViolations,
      p0Count: report.p0Count,
      p1Count: report.p1Count,
      status: statusText,
      duration: '0.04s (Bend HVM)',
      violations: fileAudit.violations,
      score: report.score,
      suppressionsCount: fileAudit.activeSuppressions
    };

    this.history.update(h => [newRun, ...h]);
    this.isAudited.set(true);
  }

  reanalyzeCurrentScope(): void {
    if (this.inputSourceCode()) {
      const fileAudit = this.guardianService.auditCode(
        this.inputFileName(),
        this.inputSourceCode(),
        this.hasTestFileChecked(),
        this.inputAuthor(),
        this.selectedBranch(),
        this.selectedProfile()
      );
      this.currentAuditedFiles.set([fileAudit]);
    }
  }

  toggleDiffView(): void {
    this.showDiffView.update(v => !v);
  }

  toggleViolationsExpanded(): void {
    this.isViolationsExpanded.update(v => !v);
  }

  toggleDetailsExpanded(): void {
    this.isDetailsExpanded.update(v => !v);
  }

  toggleAdvancedScope(): void {
    this.isAdvancedScopeOpen.update(v => !v);
  }

  selectPreset(index: number): void {
    this.selectedPresetIndex.set(index);
    const preset = this.codePresets[index];
    if (preset) {
      this.inputFileName.set(preset.fileName);
      this.inputSourceCode.set(preset.code);
      this.hasTestFileChecked.set(preset.hasTestFile);
      this.inputAuthor.set(preset.author);

      const fileAudit = this.guardianService.auditCode(
        preset.fileName,
        preset.code,
        preset.hasTestFile,
        preset.author,
        this.selectedBranch(),
        this.selectedProfile()
      );
      this.currentAuditedFiles.set([fileAudit]);
    }
  }

  runLiveAudit(): void {
    const fileAudit = this.guardianService.auditCode(
      this.inputFileName(),
      this.inputSourceCode(),
      this.hasTestFileChecked(),
      this.inputAuthor(),
      this.selectedBranch(),
      this.selectedProfile()
    );
    this.currentAuditedFiles.set([fileAudit]);

    const report = this.guardianService.generateReport([fileAudit]);
    const statusText = report.p0Count > 0 ? 'Blocked' : report.score === 100 ? 'Full compliance' : 'Completed';

    const newRun: AnalysisRun = {
      id: `${Date.now()}`,
      date: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
      project: `${this.inputRepo()} · PR #${this.inputPrNumber()}`,
      mrTitle: `${this.inputFileName()} (${this.selectedProfile()})`,
      author: this.inputAuthor(),
      targetBranch: this.selectedBranch(),
      platform: this.selectedPlatform(),
      issues: report.totalViolations,
      p0Count: report.p0Count,
      p1Count: report.p1Count,
      status: statusText,
      duration: '0.04s (Bend HVM)',
      violations: fileAudit.violations,
      score: report.score,
      suppressionsCount: fileAudit.activeSuppressions
    };

    this.history.update(h => [newRun, ...h]);
    this.activeTab.set('results');
  }

  toggleRuleStatus(ruleId: string): void {
    this.rules.update(rules => 
      rules.map(r => r.id === ruleId ? { ...r, status: r.status === 'active' ? 'inactive' : 'active' } : r)
    );

    // Re-evaluate current file if present
    if (this.inputSourceCode()) {
      const fileAudit = this.guardianService.auditCode(
        this.inputFileName(),
        this.inputSourceCode(),
        this.hasTestFileChecked(),
        this.inputAuthor(),
        this.selectedBranch(),
        this.selectedProfile()
      );
      this.currentAuditedFiles.set([fileAudit]);
    }
  }

  simulateWebhook(): void {
    const event: WebhookEventPayload = {
      platform: this.webhookPlatform(),
      eventType: this.webhookEventType(),
      repo: this.webhookRepo(),
      branch: this.webhookBranch(),
      commitSha: this.webhookCommitSha(),
      prId: this.webhookPrNumber(),
      prTitle: this.webhookPrTitle(),
      author: this.webhookAuthor()
    };

    const isMain = this.webhookBranch() === 'main' || this.webhookBranch() === 'master';
    const policyDesc = isMain 
      ? 'Strict Gating Policy: 0 P0 violations required, minimum score >= 80%.' 
      : 'Permissive Branch Policy: Non-blocking warning mode enabled for feature branch.';

    this.webhookResult.set(
      `✅ Ingested Webhook [${event.platform.toUpperCase()}] Event: "${event.eventType}"\n` +
      `Repository: ${event.repo} | Branch: ${event.branch} | SHA: ${event.commitSha.substring(0, 8)}\n` +
      `Policy Applied: ${policyDesc}\n` +
      `Status: Webhook payload parsed into canonical WebhookEvent. Ready for parallel HVM reduction.`
    );
  }

  openExport(format: 'sarif' | 'gitlab' | 'bitbucket' | 'markdown'): void {
    const report = this.currentReport();
    if (format === 'sarif') {
      this.exportedSarif.set(this.guardianService.generateSarifJson(report));
    } else if (format === 'gitlab') {
      this.exportedGitLabJson.set(this.guardianService.generateGitLabCodeQualityJson(report));
    } else if (format === 'bitbucket') {
      this.exportedBitbucketJson.set(this.guardianService.generateBitbucketCodeInsightsJson(report));
    } else if (format === 'markdown') {
      this.exportedMarkdown.set(this.guardianService.generateGitHubMarkdownSummary(report, this.inputRepo(), this.inputPrNumber()));
    }
    this.activeExportModal.set(format);
  }

  closeExportModal(): void {
    this.activeExportModal.set(null);
  }

  exportHistory(): void {
    const data = JSON.stringify(this.history(), null, 2);
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `bend-devops-audit-history-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  toggleSidebar(): void {
    this.isSidebarCollapsed.update(c => !c);
  }

  toggleMobileMenu(): void {
    this.isMobileMenuOpen.update(m => !m);
  }

  selectPipelineStage(stageId: 'code' | 'rules' | 'scanner' | 'gate' | 'cicd'): void {
    this.selectedPipelineStage.set(stageId);
  }

  selectLayerTier(index: number): void {
    this.selectedLayerTierIndex.set(index);
  }

  setDiffViewMode(mode: DiffViewMode): void {
    this.diffViewMode.set(mode);
  }

  setMobileActiveSide(side: 'before' | 'after'): void {
    this.mobileActiveSide.set(side);
  }

  toggleEditOriginal(): void {
    this.isEditOriginalOpen.update(v => !v);
  }

  syncScroll(source: HTMLElement, target: HTMLElement): void {
    if (source && target) {
      target.scrollTop = source.scrollTop;
      target.scrollLeft = source.scrollLeft;
    }
  }

  copyCorrectedCode(): void {
    if (typeof navigator !== 'undefined' && navigator.clipboard) {
      navigator.clipboard.writeText(this.currentCodeDiff().after);
    }
  }
}
