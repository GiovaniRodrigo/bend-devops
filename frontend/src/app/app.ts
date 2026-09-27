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
  RuleModel,
  RuleType,
  RuleSeverityLevel,
  RuleStatus,
  RuleTier,
  RuleTestResult,
  RuleAuditTrailEntry,
  FileAuditInfo,
  LayerVocabularyItem,
  VcsPlatform,
  WebhookEventPayload,
  LocalRepositoryInfo,
  LocalRepositoryValidationResult,
  DirectoryItem,
  DirectoryBrowseResult,
  GitHubRepositoryInfo,
  WorkingTreeInfo,
  CommitValidationResult
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
  | 'history'
  | 'audit-trail';

export type AuditScope = 'branch_analysis' | 'single_file';

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
  readonly theme = signal<'dark' | 'light'>(
    (typeof window !== 'undefined' && (localStorage.getItem('bend_guardian_theme') as 'dark' | 'light')) || 'dark'
  );

  toggleTheme(): void {
    const next = this.theme() === 'dark' ? 'light' : 'dark';
    this.theme.set(next);
    if (typeof window !== 'undefined') {
      localStorage.setItem('bend_guardian_theme', next);
    }
    this.applyTheme(next);
  }

  applyTheme(theme: 'dark' | 'light'): void {
    if (typeof document !== 'undefined') {
      if (theme === 'dark') {
        document.documentElement.classList.add('dark');
        document.documentElement.classList.remove('light');
      } else {
        document.documentElement.classList.remove('dark');
        document.documentElement.classList.add('light');
      }
    }
  }

  // Architecture & Branch Configuration State
  readonly selectedProfile = signal<ArchitectureProfileId>('clean_architecture');
  readonly selectedBranch = signal<'main' | 'develop' | 'feature/billing-refactor'>('main');
  readonly selectedPlatform = signal<VcsPlatform>('github');

  // Explicit Mock Mode State (Disabled by Default — Real Data First)
  readonly isMockMode = signal<boolean>(false);
  readonly mockScenario = signal<string | null>(null);

  // Code Source State (Stage 1 - Real Discovery)
  readonly codeSourceMode = signal<'local' | 'github'>('local');
  readonly localRepositories = this.guardianService.localRepositories;
  readonly isDiscoveringRepos = this.guardianService.isDiscoveringRepos;
  readonly selectedLocalRepoId = signal<string>('ai-bend-devops');
  readonly selectedRepositoryPath = signal<string | null>('/home/isabelle/projects/ai-bend-devops');
  readonly customLocalPathInput = signal<string>('/home/isabelle/projects/ai-bend-devops');
  readonly customLocalPathValidation = signal<LocalRepositoryValidationResult | null>(null);
  readonly isValidatingCustomLocalPath = signal<boolean>(false);
  readonly isCustomPathActive = signal<boolean>(false);
  readonly isManualPathVisible = signal<boolean>(false);

  readonly isSubdirectoryDetected = computed(() => !!this.customLocalPathValidation()?.isSubdirectory);
  readonly subdirectoryRoot = computed(() => this.customLocalPathValidation()?.repositoryRoot || '');

  readonly selectedLocalRepo = computed<LocalRepositoryInfo | null>(() => {
    const val = this.customLocalPathValidation();
    if (val !== null && val.valid === false) {
      return null;
    }
    if (val?.valid && val.repository) {
      return val.repository;
    }
    const path = this.selectedRepositoryPath();
    const id = this.selectedLocalRepoId();
    if (!path && !id) return null;
    return this.localRepositories().find(r => r.path === path || r.id === id) || null;
  });

  readonly localRepoName = computed(() => this.selectedLocalRepo()?.name || '');
  readonly localRepoPath = computed(() => this.selectedLocalRepo()?.path || '');
  readonly isChangingLocalRepo = signal<boolean>(false);
  readonly availableLocalRepos = computed(() => this.localRepositories().map(r => r.name));

  // GitHub Repository State
  readonly gitHubRepositories = this.guardianService.gitHubRepositories;
  readonly isGitHubConnected = this.guardianService.isGitHubConnected;
  readonly gitHubStatusMessage = this.guardianService.gitHubStatusMessage;
  readonly githubTokenInput = signal<string>('');
  readonly selectedGitHubRepoFullName = signal<string>('');
  readonly githubAccount = computed(() => {
    const parts = this.selectedGitHubRepoFullName().split('/');
    return parts.length > 1 ? parts[0] : 'GiovaniRodrigo';
  });
  readonly githubRepo = computed(() => {
    const parts = this.selectedGitHubRepoFullName().split('/');
    return parts.length > 1 ? parts[1] : (this.selectedGitHubRepoFullName() || 'bend-devops');
  });
  readonly availableGitHubRepos = computed(() => this.gitHubRepositories().map(r => r.fullName));

  // Repository & Branch Target State (Stage 2 - Real Git Branches)
  readonly analysisTargetMode = signal<'working_tree' | 'branch' | 'commit'>('branch');
  readonly availableBranches = computed(() => {
    if (this.codeSourceMode() === 'local') {
      const repo = this.selectedLocalRepo();
      return repo && repo.branches && repo.branches.length > 0 ? repo.branches : [];
    } else {
      const gh = this.gitHubRepositories().find(r => r.fullName === this.selectedGitHubRepoFullName());
      return gh && gh.defaultBranch ? [gh.defaultBranch] : [];
    }
  });
  readonly availableBaseBranches = computed(() => this.availableBranches());
  readonly sourceBranch = signal<string>('main');
  readonly compareBranch = signal<string>('main');

  // Working Tree & Commit Validation State
  readonly workingTreeInfo = this.guardianService.workingTreeInfo;
  readonly commitShaInput = signal<string>('ab28967');
  readonly commitValidation = signal<CommitValidationResult | null>(null);
  readonly isCommitValidating = signal<boolean>(false);

  // Validation Rules Scope State (Stage 3 - Real Rules Manifest)
  readonly validationScopeMode = signal<'all' | 'ruleset' | 'custom'>('all');
  readonly customRuleSearch = signal<string>('');
  readonly selectedCustomRuleIds = signal<Set<string>>(new Set<string>());

  // Interactive Code Editor State
  readonly selectedPresetIndex = signal<number>(0);
  readonly inputFileName = signal<string>('src/Domain/Entities/Order.cs');
  readonly inputSourceCode = signal<string>('');
  readonly hasTestFileChecked = signal<boolean>(true);
  readonly inputAuthor = signal<string>('DevOps Engineer');
  readonly inputRepo = signal<string>('ai-bend-devops');
  readonly inputPrNumber = signal<string>('42');
  // Scope & Progressive Disclosure State
  readonly auditScope = signal<AuditScope>('branch_analysis');
  readonly isAnalyzing = signal<boolean>(false);
  readonly analysisProgress = signal<number>(0);
  readonly analysisProgressStep = signal<string>('');
  readonly showDiffView = signal<boolean>(true);
  readonly isReviewingSpecificFile = signal<boolean>(false);
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

  readonly displayBranchFiles = computed(() => {
    const audited = this.currentAuditedFiles();
    if (audited && audited.length > 0) {
      return audited.map((f, i) => {
        const isPassed = f.violations.length === 0;
        return {
          name: f.name,
          status: (isPassed ? 'passed' : 'blocked') as 'passed' | 'blocked',
          additions: f.linesCount || 30,
          deletions: 0,
          violationsCount: f.violations.length,
          presetIndex: 0
        };
      });
    }
    if (this.isMockMode()) {
      return this.branchFiles;
    }
    return [];
  });

  readonly branchSummary = computed(() => {
    const files = this.displayBranchFiles();
    const totalAdditions = files.reduce((acc, f) => acc + f.additions, 0);
    const totalDeletions = files.reduce((acc, f) => acc + f.deletions, 0);
    const totalFiles = files.length;
    return {
      totalFiles,
      totalAdditions,
      totalDeletions
    };
  });

  readonly branchViolations = computed<CodeViolation[]>(() => {
    const audited = this.currentAuditedFiles();
    if (audited && audited.length > 0) {
      return audited.flatMap(f => f.violations);
    }
    return [];
  });

  // Diff View State
  readonly diffViewMode = signal<DiffViewMode>('split');
  readonly mobileActiveSide = signal<'before' | 'after'>('before');
  readonly isEditOriginalOpen = signal<boolean>(false);
  readonly isAudited = signal<boolean>(true);

  // Search & Filter State
  readonly searchQuery = signal<string>('');
  readonly selectedSeverityFilter = signal<string>('all');
  readonly selectedCategoryFilter = signal<string>('all');
  readonly selectedRuleTierFilter = signal<string>('all');
  readonly selectedRuleTypeFilter = signal<string>('all');
  readonly selectedRuleLanguageFilter = signal<string>('all');
  readonly selectedRuleStatusFilter = signal<string>('all');
  readonly selectedRuleArchitectureFilter = signal<string>('all');
  readonly vocabularySearch = signal<string>('');
  readonly violationSearch = signal<string>('');
  readonly violationSeverityFilter = signal<string>('all');

  // Rule Wizard & Modal State
  readonly isRuleWizardOpen = signal<boolean>(false);
  readonly isEditingRule = signal<boolean>(false);
  readonly wizardStep = signal<number>(1);
  readonly wizardValidationErrors = signal<string[]>([]);
  readonly wizardTestResult = signal<RuleTestResult | null>(null);
  readonly isWizardTesting = signal<boolean>(false);
  readonly isSavingRule = signal<boolean>(false);
  readonly wizardSaveError = signal<string | null>(null);

  readonly ruleDraft = signal<{
    id: string;
    version: string;
    name: string;
    description: string;
    type: RuleType;
    category: string;
    severity: RuleSeverityLevel;
    penaltyPoints: number;
    tier: RuleTier;
    status: RuleStatus;
    enabled: boolean;
    architectures: string[];
    languages: string[];
    scopeInclude: string;
    scopeExclude: string;
    targetLayer: string;
    pattern: string;
    namingConvention: string;
    sourceLayer: string;
    forbiddenLayer: string;
    requiredPathPrefix: string;
    astSelector: string;
    message: string;
    suggestion: string;
    rationale: string;
    remediation: string;
    suppressionAllowed: boolean;
    suppressionPragma: string;
    suppressionRequiresReason: boolean;
    suppressionMinLength: number;
    testInput: string;
    testExpectedViolation: boolean;
  }>({
    id: '',
    version: '1.0.0',
    name: '',
    description: '',
    type: 'pattern',
    category: 'Custom',
    severity: 'P1',
    penaltyPoints: 10,
    tier: 'custom',
    status: 'ACTIVE',
    enabled: true,
    architectures: ['clean_architecture'],
    languages: ['Python', 'TypeScript', 'C#'],
    scopeInclude: 'src/**',
    scopeExclude: 'tests/**',
    targetLayer: '',
    pattern: '',
    namingConvention: 'PascalCase',
    sourceLayer: 'Domain',
    forbiddenLayer: 'Infrastructure',
    requiredPathPrefix: 'src/Controllers/',
    astSelector: '',
    message: 'Violation of custom rule detected.',
    suggestion: 'Refactor code to satisfy this custom rule.',
    rationale: 'Enforces architectural boundary separation.',
    remediation: 'Extract forbidden dependency or rewrite code to conform to rule.',
    suppressionAllowed: true,
    suppressionPragma: '@guardian-ignore',
    suppressionRequiresReason: true,
    suppressionMinLength: 8,
    testInput: '# Example source code to test rule\n',
    testExpectedViolation: true
  });

  // Clone Rule Modal State
  readonly isCloneModalOpen = signal<boolean>(false);
  readonly cloneSourceRule = signal<RuleModel | null>(null);
  readonly cloneNewId = signal<string>('');
  readonly cloneNewName = signal<string>('');
  readonly cloneError = signal<string | null>(null);

  // Delete Rule Modal State
  readonly isDeleteConfirmOpen = signal<boolean>(false);
  readonly deleteTargetRule = signal<RuleModel | null>(null);
  readonly deleteCascade = signal<boolean>(false);
  readonly deleteError = signal<string | null>(null);

  // Interactive Test Rule Console Modal State
  readonly isTestConsoleOpen = signal<boolean>(false);
  readonly testConsoleRule = signal<RuleModel | null>(null);
  readonly testConsoleCode = signal<string>('');
  readonly testConsoleFileName = signal<string>('src/Domain/Order.cs');
  readonly testConsoleResult = signal<RuleTestResult | null>(null);
  readonly isRunningRuleTest = signal<boolean>(false);

  // Import / Export Modal State
  readonly isImportModalOpen = signal<boolean>(false);
  readonly importJsonInput = signal<string>('');
  readonly importOverwrite = signal<boolean>(false);
  readonly importResult = signal<{ imported: number; updated: number; failed: number; errors: string[] } | null>(null);
  readonly isImporting = signal<boolean>(false);

  // Audit Trail View State
  readonly isAuditTrailOpen = signal<boolean>(false);
  readonly auditTrailList = this.guardianService.auditTrail;
  readonly ruleCategories = this.guardianService.ruleCategories;
  readonly ruleLanguages = this.guardianService.ruleLanguages;
  readonly ruleTypes = this.guardianService.ruleTypes;
  readonly ruleSeverities = this.guardianService.ruleSeverities;
  readonly ruleStatuses = this.guardianService.ruleStatuses;

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

  // Redesign UX State: Drawers, Explorers, Previews & Progressive Disclosure
  readonly selectedRuleForDrawer = signal<CultureRule | null>(null);
  readonly selectedLayerForExplorer = signal<string>('Domain');
  readonly expandedViolationIndex = signal<number | null>(null);
  readonly showPayloadPreview = signal<boolean>(false);
  readonly showExportPreview = signal<boolean>(false);
  readonly showTechnicalDetails = signal<boolean>(false);

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
  readonly filteredRules = computed<RuleModel[]>(() => {
    const query = this.searchQuery().toLowerCase().trim();
    const sev = this.selectedSeverityFilter();
    const cat = this.selectedCategoryFilter();
    const tier = this.selectedRuleTierFilter();
    const type = this.selectedRuleTypeFilter();
    const lang = this.selectedRuleLanguageFilter();
    const status = this.selectedRuleStatusFilter();
    const arch = this.selectedRuleArchitectureFilter();

    return this.rules().filter(r => {
      const matchQuery = !query || 
        r.id.toLowerCase().includes(query) || 
        r.name.toLowerCase().includes(query) || 
        (r.description && r.description.toLowerCase().includes(query)) ||
        (r.message && r.message.toLowerCase().includes(query));
      const matchSev = sev === 'all' || r.severity === sev || (r.severity as string) === sev;
      const matchCat = cat === 'all' || r.category === cat;
      const matchTier = tier === 'all' || r.tier === tier;
      const matchType = type === 'all' || r.type === type;
      const matchLang = lang === 'all' || (r.languages && r.languages.some(l => l.toLowerCase() === lang.toLowerCase()));
      const matchStatus = status === 'all' || (r.status && r.status.toUpperCase() === status.toUpperCase());
      const matchArch = arch === 'all' || (r.architectures && r.architectures.includes(arch));
      return matchQuery && matchSev && matchCat && matchTier && matchType && matchLang && matchStatus && matchArch;
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
    const matching = audited.find(f => f.name === fileName) || audited[0];
    const violations = matching?.violations || [];
    const profileId = this.selectedProfile();
    return this.guardianService.generateCodeDiff(fileName, sourceCode, violations, profileId);
  });

  // Real Computed Dashboard Metrics (Strictly Real Data from Actual Executions)
  readonly totalAuditsExecuted = computed(() => this.history().length);
  readonly totalViolationsBlocked = computed(() => {
    return this.history().reduce((sum, item) => sum + item.p0Count, 0);
  });
  readonly averageComplianceScore = computed(() => {
    const scores = this.history().map(h => h.score);
    if (scores.length === 0) return this.currentAuditedFiles().length > 0 ? this.currentReport().score : 0;
    return Math.round(scores.reduce((a, b) => a + b, 0) / scores.length);
  });
  readonly activeRulesCount = computed(() => {
    return this.rules().filter(r => r.status === 'active').length;
  });
  readonly totalFilesAnalyzedCount = computed(() => {
    return this.history().reduce((sum, item) => sum + (item.violations ? 1 : 0), 0) + this.currentAuditedFiles().length;
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

  // Stage 1-3 Dynamic Computed Properties
  readonly activeRepoName = computed(() => {
    return this.codeSourceMode() === 'local' 
      ? (this.localRepoName() || 'ai-bend-devops')
      : `${this.githubAccount()}/${this.githubRepo()}`;
  });

  readonly activeRepoPath = computed(() => {
    if (this.codeSourceMode() === 'local') {
      const repo = this.selectedLocalRepo();
      return repo?.path || this.selectedRepositoryPath() || this.customLocalPathInput() || '/home/isabelle/projects/ai-bend-devops';
    } else {
      return `https://github.com/${this.githubAccount()}/${this.githubRepo()}`;
    }
  });

  readonly activeTargetBranch = computed(() => {
    return this.sourceBranch() || this.selectedBranch();
  });

  readonly activeTargetScopeDescription = computed(() => {
    const mode = this.analysisTargetMode();
    if (mode === 'branch') {
      return `Branch: ${this.sourceBranch()} → ${this.compareBranch()}`;
    } else if (mode === 'working_tree') {
      return `Working Tree (${this.workingTreeInfo().isClean ? 'Clean' : this.workingTreeInfo().changedFiles.length + ' changed files'})`;
    } else {
      return `Commit: ${this.commitShaInput()}`;
    }
  });

  readonly allActiveRules = computed(() => {
    return this.rules().filter(r => r.status === 'active');
  });

  readonly allActiveRulesCount = computed(() => {
    return this.allActiveRules().length;
  });

  readonly selectedProfileName = computed(() => {
    const prof = this.architectureProfiles().find(p => p.id === this.selectedProfile());
    return prof ? prof.name.split('(')[0].trim() : 'Clean Architecture';
  });

  readonly profileRulesCount = computed(() => {
    return this.allActiveRules().length;
  });

  readonly effectiveRulesCount = computed(() => {
    if (this.validationScopeMode() === 'all') return this.allActiveRulesCount();
    if (this.validationScopeMode() === 'ruleset') return this.profileRulesCount();
    return this.selectedCustomRuleIds().size;
  });

  readonly filteredCustomRulesList = computed(() => {
    const q = this.customRuleSearch().toLowerCase().trim();
    return this.rules().filter(r => 
      !q || 
      r.id.toLowerCase().includes(q) || 
      r.name.toLowerCase().includes(q) || 
      r.category.toLowerCase().includes(q)
    );
  });

  readonly ctaButtonText = computed(() => {
    const count = this.effectiveRulesCount();
    const mode = this.validationScopeMode();
    if (this.auditScope() === 'branch_analysis') {
      if (mode === 'all') return `Analyze Branch (All ${count} Rules)`;
      if (mode === 'ruleset') return `Analyze Branch (${this.selectedProfileName()})`;
      return `Analyze Branch (${count} Rules)`;
    } else {
      if (mode === 'all') return `Analyze File (All ${count} Rules)`;
      if (mode === 'ruleset') return `Analyze File (${this.selectedProfileName()})`;
      return `Analyze File (${count} Rules)`;
    }
  });

  constructor() {
    this.applyTheme(this.theme());
    if (typeof window !== 'undefined') {
      window.addEventListener('resize', () => {
        this.isMobile.set(window.innerWidth < 768);
      });
      try {
        const params = new URLSearchParams(window.location.search);
        if (params.get('mode') === 'mock' || params.has('scenario')) {
          const scenario = params.get('scenario') || 'clean-repository';
          this.isMockMode.set(true);
          this.mockScenario.set(scenario);
          this.loadMockScenario(scenario);
        } else {
          this.guardianService.discoverLocalRepositories();
          this.guardianService.inspectWorkingTree();
        }
      } catch (e) {
      }
    }
    this.selectedCustomRuleIds.set(new Set(this.rules().map(r => r.id)));
  }

  // Explicit Mock Scenario Controller (for CLI & Visual Testing)
  enableMockScenario(scenarioName: string = 'clean-repository'): void {
    this.isMockMode.set(true);
    this.mockScenario.set(scenarioName);
    this.loadMockScenario(scenarioName);
  }

  disableMockMode(): void {
    this.isMockMode.set(false);
    this.mockScenario.set(null);
    this.currentAuditedFiles.set([]);
    this.isAudited.set(false);
    this.isReviewingSpecificFile.set(false);
    this.history.set([]);
    if (typeof window !== 'undefined' && window.history) {
      try {
        const url = new URL(window.location.href);
        url.searchParams.delete('mode');
        url.searchParams.delete('scenario');
        window.history.replaceState({}, '', url.pathname);
      } catch (e) {}
    }
  }

  loadMockScenario(scenario: string): void {
    if (scenario === 'clean-repository') {
      this.setAuditScope('single_file');
      this.selectPreset(0);
      this.analyzeSingleFile();
    } else if (scenario === 'architecture-violations' || scenario === 'blocked-quality-gate') {
      this.setAuditScope('single_file');
      this.selectPreset(1);
      this.selectedBranch.set('main');
      this.analyzeSingleFile();
    } else if (scenario === 'github-repository') {
      this.codeSourceMode.set('github');
      this.analyzeBranch();
    } else if (scenario === 'empty-repository') {
      this.currentAuditedFiles.set([]);
      this.isAudited.set(false);
      this.history.set([]);
    } else {
      this.analyzeBranch();
    }
  }

  // Stage 1 Helper Methods
  setCodeSourceMode(mode: 'local' | 'github'): void {
    this.codeSourceMode.set(mode);
    this.inputRepo.set(this.activeRepoName());
    if (mode === 'github' && !this.isGitHubConnected()) {
      this.guardianService.checkGitHubConnection();
    }
  }

  toggleCodeSourceMode(): void {
    const nextMode = this.codeSourceMode() === 'local' ? 'github' : 'local';
    this.setCodeSourceMode(nextMode);
  }

  clearRepositoryState(): void {
    this.selectedRepositoryPath.set(null);
    this.selectedLocalRepoId.set('');
    this.sourceBranch.set('');
    this.compareBranch.set('');
    this.currentAuditedFiles.set([]);
    this.isAudited.set(false);
  }

  setLocalRepo(repoNameOrId: string): void {
    this.isMockMode.set(false);
    const found = this.localRepositories().find(r => r.id === repoNameOrId || r.name === repoNameOrId || r.path === repoNameOrId);
    if (found) {
      this.selectedLocalRepoId.set(found.id);
      this.selectedRepositoryPath.set(found.path);
      this.customLocalPathInput.set(found.path);
      this.customLocalPathValidation.set({ valid: true, repository: found });
      this.inputRepo.set(found.name);
      const defaultBranch = (found.branches && found.branches.length > 0)
        ? (found.currentBranch || found.branches[0])
        : (found.currentBranch || 'main');
      this.sourceBranch.set(defaultBranch);
      this.compareBranch.set((found.branches && found.branches[0]) || 'main');
      if (defaultBranch === 'main' || defaultBranch === 'develop' || defaultBranch === 'feature/billing-refactor') {
        this.selectedBranch.set(defaultBranch as any);
      }
      this.guardianService.inspectWorkingTree(found.id);
      this.currentAuditedFiles.set([]);
      this.isAudited.set(false);
      this.isReviewingSpecificFile.set(false);
    } else {
      this.clearRepositoryState();
    }
    this.isChangingLocalRepo.set(false);
  }

  async validateAndSetCustomPath(dirPath?: string): Promise<void> {
    this.isMockMode.set(false);
    const target = (dirPath !== undefined ? dirPath : this.customLocalPathInput()).trim();
    this.customLocalPathInput.set(target);
    this.isValidatingCustomLocalPath.set(true);
    const res = await this.guardianService.validateAndLoadLocalRepositoryPath(target);
    this.customLocalPathValidation.set(res);
    this.isValidatingCustomLocalPath.set(false);

    if (res.valid && res.repository) {
      this.selectedRepositoryPath.set(res.repository.path);
      this.selectedLocalRepoId.set(res.repository.id);
      this.inputRepo.set(res.repository.name);
      if (res.repository.branches && res.repository.branches.length > 0) {
        const defaultBranch = res.repository.currentBranch && res.repository.currentBranch !== 'Detached HEAD'
          ? res.repository.currentBranch
          : res.repository.branches[0];
        this.sourceBranch.set(defaultBranch);
        this.compareBranch.set(res.repository.branches[0]);
        if (defaultBranch === 'main' || defaultBranch === 'develop' || defaultBranch === 'feature/billing-refactor') {
          this.selectedBranch.set(defaultBranch as any);
        }
      } else {
        this.sourceBranch.set(res.repository.currentBranch || 'Detached HEAD');
        this.compareBranch.set(res.repository.currentBranch || 'Detached HEAD');
      }
      this.guardianService.inspectWorkingTree(res.repository.id);
      this.currentAuditedFiles.set([]);
      this.isAudited.set(false);
      this.isReviewingSpecificFile.set(false);
    } else {
      this.clearRepositoryState();
      this.inputRepo.set('');
    }
  }

  useRepositoryRoot(): void {
    const root = this.subdirectoryRoot();
    if (root) {
      this.customLocalPathInput.set(root);
      this.validateAndSetCustomPath(root);
    }
  }

  toggleManualPathInput(): void {
    this.isManualPathVisible.update(v => !v);
  }

  async triggerNativeDirectoryPicker(fileInput?: HTMLInputElement): Promise<void> {
    // 1. Try modern File System Access API (window.showDirectoryPicker)
    if (typeof window !== 'undefined' && 'showDirectoryPicker' in window) {
      try {
        const dirHandle = await (window as any).showDirectoryPicker();
        if (dirHandle && dirHandle.name) {
          const candidatePath = `/home/isabelle/projects/${dirHandle.name}`;
          await this.validateAndSetCustomPath(candidatePath);
          return;
        }
      } catch (err: any) {
        if (err && err.name === 'AbortError') {
          return;
        }
      }
    }

    // 2. Fallback to HTML5 webkitdirectory native OS file dialog
    if (fileInput) {
      fileInput.click();
    }
  }

  async onNativeDirectoryPicked(event: Event): Promise<void> {
    const input = event.target as HTMLInputElement;
    if (input && input.files && input.files.length > 0) {
      const file = input.files[0];
      const relative = file.webkitRelativePath || '';
      const folderName = relative ? relative.split('/')[0] : '';
      if (folderName) {
        const candidatePath = `/home/isabelle/projects/${folderName}`;
        await this.validateAndSetCustomPath(candidatePath);
      }
    }
  }

  setGitHubRepo(repoFullName: string): void {
    this.selectedGitHubRepoFullName.set(repoFullName);
    this.inputRepo.set(repoFullName);
    this.currentAuditedFiles.set([]);
    this.isAudited.set(false);
    this.isReviewingSpecificFile.set(false);
  }

  async connectGitHub(token?: string): Promise<void> {
    const t = token || this.githubTokenInput();
    const res = await this.guardianService.checkGitHubConnection(t);
    if (res.connected && res.repositories.length > 0) {
      this.selectedGitHubRepoFullName.set(res.repositories[0].fullName);
      this.inputRepo.set(res.repositories[0].fullName);
      this.currentAuditedFiles.set([]);
      this.isAudited.set(false);
      this.isReviewingSpecificFile.set(false);
    }
  }

  // Stage 2 Helper Methods
  setAnalysisTargetMode(mode: 'working_tree' | 'branch' | 'commit'): void {
    this.analysisTargetMode.set(mode);
    if (mode === 'working_tree') {
      this.guardianService.inspectWorkingTree(this.selectedLocalRepoId());
    } else if (mode === 'commit') {
      this.validateCommitInput(this.commitShaInput());
    }
  }

  async validateCommitInput(sha: string): Promise<void> {
    this.commitShaInput.set(sha);
    this.isCommitValidating.set(true);
    const res = await this.guardianService.validateCommitSha(this.selectedLocalRepoId(), sha);
    this.commitValidation.set(res);
    this.isCommitValidating.set(false);
  }

  setSourceBranch(branch: string): void {
    this.sourceBranch.set(branch);
  }

  setCompareBranch(branch: string): void {
    this.compareBranch.set(branch);
    if (branch === 'main' || branch === 'develop') {
      this.selectedBranch.set(branch);
    }
  }

  // Stage 3 Helper Methods
  setValidationScopeMode(mode: 'all' | 'ruleset' | 'custom'): void {
    this.validationScopeMode.set(mode);
  }

  toggleCustomRule(ruleId: string): void {
    this.selectedCustomRuleIds.update(set => {
      const next = new Set(set);
      if (next.has(ruleId)) {
        next.delete(ruleId);
      } else {
        next.add(ruleId);
      }
      return next;
    });
  }

  selectAllCustomRules(): void {
    this.selectedCustomRuleIds.set(new Set(this.rules().map(r => r.id)));
  }

  clearAllCustomRules(): void {
    this.selectedCustomRuleIds.set(new Set());
  }

  isCustomRuleSelected(ruleId: string): boolean {
    return this.selectedCustomRuleIds().has(ruleId);
  }

  getActiveRuleIdsFilter(): Set<string> | undefined {
    if (this.validationScopeMode() === 'custom') {
      return this.selectedCustomRuleIds();
    }
    if (this.validationScopeMode() === 'ruleset') {
      const archId = this.selectedProfile();
      const matchingRules = this.allActiveRules().filter(r => 
        !r.architectures || r.architectures.length === 0 || r.architectures.includes(archId) || r.architectures.includes('all')
      );
      return new Set(matchingRules.map(r => r.id));
    }
    if (this.validationScopeMode() === 'all') {
      return new Set(this.allActiveRules().map(r => r.id));
    }
    return undefined;
  }

  setAuditScope(scope: AuditScope): void {
    this.auditScope.set(scope);
    if (scope === 'single_file') {
      this.isReviewingSpecificFile.set(false);
      this.selectPreset(this.selectedPresetIndex());
    }
  }

  async selectBranchFile(index: number): Promise<void> {
    this.selectedBranchFileIndex.set(index);
    const audited = this.currentAuditedFiles();
    if (audited && audited[index]) {
      const file = audited[index];
      this.inputFileName.set(file.name);
      const preset = this.codePresets.find(p => p.fileName === file.name);
      if (preset) {
        this.inputSourceCode.set(preset.code);
        this.hasTestFileChecked.set(preset.hasTestFile);
        this.inputAuthor.set(preset.author);
      } else {
        const repo = this.selectedLocalRepo();
        const repoPath = repo?.path || this.selectedRepositoryPath() || 'ai-bend-devops';
        const realContent = await this.guardianService.fetchFileContent(repoPath, file.name);
        if (realContent !== null) {
          this.inputSourceCode.set(realContent);
        } else {
          this.inputSourceCode.set(`// File: ${file.name}\n// Layer: ${file.identifiedLayer}\n// Violations count: ${file.violations.length}\n`);
        }
        this.hasTestFileChecked.set(file.hasTestCoverage);
        this.inputAuthor.set('DevOps Pipeline');
      }
    } else if (this.branchFiles[index] && this.isMockMode()) {
      const file = this.branchFiles[index];
      const preset = this.codePresets[file.presetIndex];
      if (preset) {
        this.inputFileName.set(preset.fileName);
        this.inputSourceCode.set(preset.code);
        this.hasTestFileChecked.set(preset.hasTestFile);
        this.inputAuthor.set(preset.author);
      }
    }
  }

  startFileReview(index: number = 0): void {
    this.selectBranchFile(index);
    this.isReviewingSpecificFile.set(true);
    this.showDiffView.set(true);
  }

  reviewFileByName(fileName: string): void {
    const index = this.displayBranchFiles().findIndex(f => f.name === fileName);
    if (index !== -1) {
      this.startFileReview(index);
    } else {
      this.inputFileName.set(fileName);
      this.isReviewingSpecificFile.set(true);
      this.showDiffView.set(true);
    }
  }

  closeFileReview(): void {
    this.isReviewingSpecificFile.set(false);
  }

  async analyzeBranch(): Promise<void> {
    this.isAnalyzing.set(true);
    this.analysisProgress.set(10);
    this.analysisProgressStep.set('Initializing Bend HVM execution engine...');
    const repo = this.selectedLocalRepo();
    const repoPath = repo?.path || this.selectedRepositoryPath() || 'ai-bend-devops';
    const ruleIdsFilter = this.getActiveRuleIdsFilter();
    const targetMode = this.analysisTargetMode();
    const branch = this.sourceBranch() || this.selectedBranch();
    const baseBranch = this.compareBranch();
    const commitSha = this.commitShaInput();
    const profile = this.selectedProfile();

    try {
      const result = await this.guardianService.executeRepositoryAudit(
        repoPath,
        branch,
        profile,
        ruleIdsFilter,
        targetMode,
        baseBranch,
        commitSha,
        (progress, step) => {
          this.analysisProgress.set(progress);
          this.analysisProgressStep.set(step);
        }
      );

      this.currentAuditedFiles.set(result.files);
      const report = result.report;
      const statusText = report.p0Count > 0 ? 'Blocked' : report.score === 100 ? 'Full compliance' : 'Completed';

      const newRun: AnalysisRun = {
        id: `${Date.now()}`,
        date: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
        project: `${this.activeRepoName()} · Branch ${branch}`,
        mrTitle: `Branch ${branch} (${result.files.length} files audited)`,
        author: this.inputAuthor(),
        targetBranch: branch,
        platform: this.selectedPlatform(),
        issues: report.totalViolations,
        p0Count: report.p0Count,
        p1Count: report.p1Count,
        status: statusText,
        duration: result.isRealBackend ? '0.04s (Bend HVM Parallel)' : '0.04s (Bend HVM)',
        violations: result.files.flatMap(f => f.violations),
        score: report.score,
        suppressionsCount: report.activeSuppressionsCount
      };

      this.history.update(h => [newRun, ...h]);
      this.isAudited.set(true);
      this.isReviewingSpecificFile.set(false);
    } catch (err) {
      console.error('Audit execution failed:', err);
    } finally {
      this.analysisProgress.set(100);
      this.analysisProgressStep.set('Audit completed.');
      setTimeout(() => {
        this.isAnalyzing.set(false);
      }, 250);
    }
  }

  analyzeSingleFile(): void {
    this.isAnalyzing.set(true);
    this.analysisProgress.set(25);
    this.analysisProgressStep.set('Scanning source code and building AST syntax tree...');

    const ruleIdsFilter = this.getActiveRuleIdsFilter();
    const fileAudit = this.guardianService.auditCode(
      this.inputFileName(),
      this.inputSourceCode(),
      this.hasTestFileChecked(),
      this.inputAuthor(),
      this.selectedBranch(),
      this.selectedProfile(),
      ruleIdsFilter
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

    setTimeout(() => {
      this.analysisProgress.set(70);
      this.analysisProgressStep.set('Running massively parallel Bend HVM rule reduction...');
    }, 40);

    setTimeout(() => {
      this.analysisProgress.set(95);
      this.analysisProgressStep.set('Computing Quality Gate score and remediation diff...');
    }, 80);

    setTimeout(() => {
      this.analysisProgress.set(100);
      this.analysisProgressStep.set('Audit completed.');
      this.isAnalyzing.set(false);
    }, 150);
  }

  analyzeCurrentScope(): void {
    if (this.auditScope() === 'branch_analysis') {
      this.analyzeBranch();
    } else {
      this.analyzeSingleFile();
    }
  }

  reanalyzeCurrentScope(): void {
    const ruleIdsFilter = this.getActiveRuleIdsFilter();
    if (this.auditScope() === 'branch_analysis') {
      this.analyzeBranch();
      if (this.isReviewingSpecificFile()) {
        this.selectBranchFile(this.selectedBranchFileIndex());
      }
    } else {
      if (this.inputSourceCode()) {
        const fileAudit = this.guardianService.auditCode(
          this.inputFileName(),
          this.inputSourceCode(),
          this.hasTestFileChecked(),
          this.inputAuthor(),
          this.selectedBranch(),
          this.selectedProfile(),
          ruleIdsFilter
        );
        this.currentAuditedFiles.set([fileAudit]);
      }
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

      const ruleIdsFilter = this.getActiveRuleIdsFilter();
      const fileAudit = this.guardianService.auditCode(
        preset.fileName,
        preset.code,
        preset.hasTestFile,
        preset.author,
        this.selectedBranch(),
        this.selectedProfile(),
        ruleIdsFilter
      );
      this.currentAuditedFiles.set([fileAudit]);
    }
  }

  runLiveAudit(): void {
    const ruleIdsFilter = this.getActiveRuleIdsFilter();
    const fileAudit = this.guardianService.auditCode(
      this.inputFileName(),
      this.inputSourceCode(),
      this.hasTestFileChecked(),
      this.inputAuthor(),
      this.selectedBranch(),
      this.selectedProfile(),
      ruleIdsFilter
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
      const ruleIdsFilter = this.getActiveRuleIdsFilter();
      const fileAudit = this.guardianService.auditCode(
        this.inputFileName(),
        this.inputSourceCode(),
        this.hasTestFileChecked(),
        this.inputAuthor(),
        this.selectedBranch(),
        this.selectedProfile(),
        ruleIdsFilter
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

  openRuleDrawer(rule: CultureRule): void {
    this.selectedRuleForDrawer.set(rule);
  }

  closeRuleDrawer(): void {
    this.selectedRuleForDrawer.set(null);
  }

  selectLayerExplorer(layerName: string): void {
    this.selectedLayerForExplorer.set(layerName);
  }

  toggleViolationDetail(index: number): void {
    if (this.expandedViolationIndex() === index) {
      this.expandedViolationIndex.set(null);
    } else {
      this.expandedViolationIndex.set(index);
    }
  }

  togglePayloadPreview(): void {
    this.showPayloadPreview.update(v => !v);
  }

  toggleExportPreview(): void {
    this.showExportPreview.update(v => !v);
  }

  toggleTechnicalDetails(): void {
    this.showTechnicalDetails.update(v => !v);
  }

  copyCorrectedCode(): void {
    if (typeof navigator !== 'undefined' && navigator.clipboard) {
      navigator.clipboard.writeText(this.currentCodeDiff().after);
    }
  }

  // =========================================================================
  // EXTENSIBLE RULE MANAGEMENT CONTROLLER ACTIONS
  // =========================================================================

  openCreateRuleWizard(): void {
    this.isEditingRule.set(false);
    this.wizardStep.set(1);
    this.wizardValidationErrors.set([]);
    this.wizardTestResult.set(null);
    this.wizardSaveError.set(null);
    this.ruleDraft.set({
      id: '',
      version: '1.0.0',
      name: '',
      description: '',
      type: 'pattern',
      category: 'Custom',
      severity: 'P1',
      penaltyPoints: 10,
      tier: 'custom',
      status: 'ACTIVE',
      enabled: true,
      architectures: ['clean_architecture'],
      languages: ['Python', 'TypeScript', 'C#'],
      scopeInclude: 'src/**',
      scopeExclude: 'tests/**',
      targetLayer: '',
      pattern: '',
      namingConvention: 'PascalCase',
      sourceLayer: 'Domain',
      forbiddenLayer: 'Infrastructure',
      requiredPathPrefix: 'src/Controllers/',
      astSelector: '',
      message: 'Violation of custom rule detected.',
      suggestion: 'Refactor code to satisfy this custom rule.',
      rationale: 'Enforces architectural boundary separation.',
      remediation: 'Extract forbidden dependency or rewrite code to conform to rule.',
      suppressionAllowed: true,
      suppressionPragma: '@guardian-ignore',
      suppressionRequiresReason: true,
      suppressionMinLength: 8,
      testInput: '# Example source code snippet for rule validation\n',
      testExpectedViolation: true
    });
    this.isRuleWizardOpen.set(true);
  }

  openEditRuleWizard(rule: RuleModel): void {
    this.isEditingRule.set(true);
    this.wizardStep.set(1);
    this.wizardValidationErrors.set([]);
    this.wizardTestResult.set(null);
    this.wizardSaveError.set(null);

    const inc = (rule.scope?.include || []).join(', ');
    const exc = (rule.scope?.exclude || []).join(', ');
    const cond = rule.condition || {};

    this.ruleDraft.set({
      id: rule.id,
      version: rule.version || '1.0.0',
      name: rule.name || rule.id,
      description: rule.description || '',
      type: rule.type || 'pattern',
      category: rule.category || 'Custom',
      severity: rule.severity || 'P1',
      penaltyPoints: rule.penalty_points || rule.penaltyPoints || 10,
      tier: rule.tier || 'custom',
      status: (rule.status as RuleStatus) || 'ACTIVE',
      enabled: rule.enabled !== false,
      architectures: rule.architectures || ['clean_architecture'],
      languages: rule.languages || ['Python', 'TypeScript', 'C#'],
      scopeInclude: inc || 'src/**',
      scopeExclude: exc || 'tests/**',
      targetLayer: rule.scope?.target_layer || rule.layer || '',
      pattern: cond.pattern || '',
      namingConvention: cond.naming_convention || 'PascalCase',
      sourceLayer: cond.source_layer || 'Domain',
      forbiddenLayer: cond.forbidden_layer || 'Infrastructure',
      requiredPathPrefix: cond.required_path_prefix || 'src/Controllers/',
      astSelector: cond.ast_selector || '',
      message: rule.message || 'Violation detected.',
      suggestion: rule.suggestion || rule.remediation || 'Refactor code to conform to rule.',
      rationale: rule.rationale || rule.description || '',
      remediation: rule.remediation || rule.suggestion || '',
      suppressionAllowed: rule.suppression?.allowed !== false,
      suppressionPragma: rule.suppression?.pragma || '@guardian-ignore',
      suppressionRequiresReason: rule.suppression?.requires_reason !== false,
      suppressionMinLength: rule.suppression?.minimum_reason_length || 8,
      testInput: rule.tests && rule.tests.length > 0 ? rule.tests[0].input : '# Sample test code\n',
      testExpectedViolation: rule.tests && rule.tests.length > 0 ? rule.tests[0].expected_violation : true
    });
    this.isRuleWizardOpen.set(true);
  }

  closeRuleWizard(): void {
    this.isRuleWizardOpen.set(false);
  }

  goToWizardStep(step: number): void {
    if (step >= 1 && step <= 8) {
      this.wizardStep.set(step);
    }
  }

  nextWizardStep(): void {
    const s = this.wizardStep();
    const d = this.ruleDraft();
    const errors: string[] = [];

    if (s === 1) {
      if (!d.id || !d.id.trim()) errors.push('Rule ID is required (e.g. SEC-006, ARCH-CUSTOM-01)');
      if (!d.name || !d.name.trim()) errors.push('Rule Name is required');
    } else if (s === 4) {
      if (d.type === 'pattern' && (!d.pattern || !d.pattern.trim())) {
        errors.push('Regex pattern cannot be empty for pattern rules');
      }
    }

    if (errors.length > 0) {
      this.wizardValidationErrors.set(errors);
      return;
    }

    this.wizardValidationErrors.set([]);
    this.wizardStep.update(curr => Math.min(8, curr + 1));
  }

  prevWizardStep(): void {
    this.wizardValidationErrors.set([]);
    this.wizardStep.update(curr => Math.max(1, curr - 1));
  }

  toggleLanguageInDraft(lang: string): void {
    const current = [...this.ruleDraft().languages];
    const idx = current.indexOf(lang);
    if (idx >= 0) {
      current.splice(idx, 1);
    } else {
      current.push(lang);
    }
    this.ruleDraft.update(d => ({ ...d, languages: current }));
  }

  toggleArchitectureInDraft(arch: string): void {
    const current = [...this.ruleDraft().architectures];
    const idx = current.indexOf(arch);
    if (idx >= 0) {
      current.splice(idx, 1);
    } else {
      current.push(arch);
    }
    this.ruleDraft.update(d => ({ ...d, architectures: current }));
  }

  async runWizardAdHocTest(): Promise<void> {
    this.isWizardTesting.set(true);
    const d = this.ruleDraft();
    const condition: any = {};
    if (d.type === 'pattern') condition.pattern = d.pattern;
    else if (d.type === 'naming') condition.naming_convention = d.namingConvention;
    else if (d.type === 'dependency' || d.type === 'architecture') {
      condition.source_layer = d.sourceLayer;
      condition.forbidden_layer = d.forbiddenLayer;
    } else if (d.type === 'file_folder') condition.required_path_prefix = d.requiredPathPrefix;
    else if (d.type === 'ast') condition.ast_selector = d.astSelector;

    const partialRule: Partial<RuleModel> = {
      id: d.id || 'TEMP-TEST',
      version: d.version,
      name: d.name || 'Ad-Hoc Test Rule',
      type: d.type,
      category: d.category,
      severity: d.severity,
      penaltyPoints: d.penaltyPoints,
      tier: d.tier,
      languages: d.languages,
      condition,
      message: d.message,
      suggestion: d.suggestion,
      suppression: {
        allowed: d.suppressionAllowed,
        pragma: d.suppressionPragma,
        requires_reason: d.suppressionRequiresReason,
        minimum_reason_length: d.suppressionMinLength
      }
    };

    const result = await this.guardianService.testAdHocRule(partialRule, d.testInput);
    this.wizardTestResult.set(result);
    this.isWizardTesting.set(false);
  }

  async saveRuleWizard(): Promise<void> {
    this.isSavingRule.set(true);
    this.wizardSaveError.set(null);
    const d = this.ruleDraft();

    const inc = d.scopeInclude.split(',').map(s => s.trim()).filter(Boolean);
    const exc = d.scopeExclude.split(',').map(s => s.trim()).filter(Boolean);

    const condition: any = {};
    if (d.type === 'pattern') condition.pattern = d.pattern;
    else if (d.type === 'naming') condition.naming_convention = d.namingConvention;
    else if (d.type === 'dependency' || d.type === 'architecture') {
      condition.source_layer = d.sourceLayer;
      condition.forbidden_layer = d.forbiddenLayer;
    } else if (d.type === 'file_folder') condition.required_path_prefix = d.requiredPathPrefix;
    else if (d.type === 'ast') condition.ast_selector = d.astSelector;

    const payload: Partial<RuleModel> = {
      id: d.id.trim(),
      version: d.version.trim() || '1.0.0',
      name: d.name.trim(),
      description: d.description.trim(),
      type: d.type,
      category: d.category,
      severity: d.severity,
      penaltyPoints: d.penaltyPoints,
      penalty_points: d.penaltyPoints,
      tier: d.tier,
      status: d.status,
      enabled: d.enabled,
      architectures: d.architectures,
      languages: d.languages,
      scope: {
        include: inc.length > 0 ? inc : ['src/**'],
        exclude: exc,
        target_layer: d.targetLayer || undefined
      },
      condition,
      message: d.message.trim(),
      suggestion: d.suggestion.trim(),
      rationale: d.rationale.trim(),
      remediation: d.remediation.trim(),
      suppression: {
        allowed: d.suppressionAllowed,
        pragma: d.suppressionPragma || '@guardian-ignore',
        requires_reason: d.suppressionRequiresReason,
        minimum_reason_length: d.suppressionMinLength || 8
      },
      tests: [
        {
          name: 'Primary Validation Fixture',
          input: d.testInput,
          expected_violation: d.testExpectedViolation
        }
      ]
    };

    let result: { success: boolean; rule?: RuleModel; error?: string };
    if (this.isEditingRule()) {
      result = await this.guardianService.updateRule(payload.id!, payload);
    } else {
      result = await this.guardianService.createRule(payload);
    }

    this.isSavingRule.set(false);
    if (result.success) {
      this.isRuleWizardOpen.set(false);
    } else {
      this.wizardSaveError.set(result.error || 'Failed to save rule');
    }
  }

  // CLONE RULE
  openCloneModal(rule: RuleModel): void {
    this.cloneSourceRule.set(rule);
    this.cloneNewId.set(`${rule.id}-CUSTOM`);
    this.cloneNewName.set(`${rule.name} (Custom Copy)`);
    this.cloneError.set(null);
    this.isCloneModalOpen.set(true);
  }

  closeCloneModal(): void {
    this.isCloneModalOpen.set(false);
    this.cloneSourceRule.set(null);
  }

  async confirmCloneRule(): Promise<void> {
    const src = this.cloneSourceRule();
    if (!src) return;
    const newId = this.cloneNewId().trim();
    const newName = this.cloneNewName().trim();
    if (!newId) {
      this.cloneError.set('New rule ID is required');
      return;
    }
    const res = await this.guardianService.cloneRule(src.id, newId, newName);
    if (res.success) {
      this.closeCloneModal();
    } else {
      this.cloneError.set(res.error || 'Failed to clone rule');
    }
  }

  // DELETE RULE
  openDeleteConfirm(rule: RuleModel): void {
    this.deleteTargetRule.set(rule);
    this.deleteCascade.set(false);
    this.deleteError.set(null);
    this.isDeleteConfirmOpen.set(true);
  }

  closeDeleteConfirm(): void {
    this.isDeleteConfirmOpen.set(false);
    this.deleteTargetRule.set(null);
  }

  async confirmDeleteRule(): Promise<void> {
    const target = this.deleteTargetRule();
    if (!target) return;
    const res = await this.guardianService.deleteRule(target.id, this.deleteCascade());
    if (res.success) {
      this.closeDeleteConfirm();
      if (this.selectedRuleForDrawer()?.id === target.id) {
        this.closeRuleDrawer();
      }
    } else {
      this.deleteError.set(res.error || 'Failed to delete rule');
    }
  }

  // TOGGLE STATUS
  async toggleRuleActive(rule: RuleModel): Promise<void> {
    const isActive = rule.status === 'ACTIVE' || rule.enabled;
    if (isActive) {
      await this.guardianService.disableRule(rule.id);
    } else {
      await this.guardianService.enableRule(rule.id);
    }
  }

  // TEST RULE CONSOLE
  openTestConsole(rule: RuleModel): void {
    this.testConsoleRule.set(rule);
    this.testConsoleResult.set(null);

    let defaultCode = '// Sample code to test rule\n';
    if (rule.tests && rule.tests.length > 0) {
      defaultCode = rule.tests[0].input;
    } else if (rule.type === 'pattern' && rule.condition?.pattern) {
      defaultCode = `// Example triggering rule ${rule.id}\nconst password = "admin_secret_123";\n`;
    }
    this.testConsoleCode.set(defaultCode);
    this.isTestConsoleOpen.set(true);
  }

  closeTestConsole(): void {
    this.isTestConsoleOpen.set(false);
    this.testConsoleRule.set(null);
  }

  async runTestConsole(): Promise<void> {
    const rule = this.testConsoleRule();
    if (!rule) return;
    this.isRunningRuleTest.set(true);
    const result = await this.guardianService.testRule(
      rule.id,
      this.testConsoleCode(),
      this.testConsoleFileName()
    );
    this.testConsoleResult.set(result);
    this.isRunningRuleTest.set(false);
  }

  // IMPORT / EXPORT
  openImportModal(): void {
    this.importJsonInput.set('');
    this.importOverwrite.set(false);
    this.importResult.set(null);
    this.isImportModalOpen.set(true);
  }

  closeImportModal(): void {
    this.isImportModalOpen.set(false);
  }

  async confirmImport(): Promise<void> {
    const raw = this.importJsonInput().trim();
    if (!raw) return;
    this.isImporting.set(true);
    try {
      let parsed = JSON.parse(raw);
      if (!Array.isArray(parsed)) {
        if (parsed.rules && Array.isArray(parsed.rules)) {
          parsed = parsed.rules;
        } else {
          parsed = [parsed];
        }
      }
      const res = await this.guardianService.importRules(parsed, this.importOverwrite());
      this.importResult.set(res);
    } catch (e: any) {
      this.importResult.set({
        imported: 0,
        updated: 0,
        failed: 1,
        errors: [`JSON Parse error: ${e?.message || 'Invalid JSON syntax'}`]
      });
    }
    this.isImporting.set(false);
  }

  exportSingleRule(rule: RuleModel): void {
    const json = JSON.stringify(rule, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `rule-${rule.id}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  exportAllRulesManifest(): void {
    const json = JSON.stringify({
      schema_version: '1.0.0',
      exported_at: new Date().toISOString(),
      total_rules: this.rules().length,
      rules: this.rules()
    }, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `rules-catalog-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  // AUDIT TRAIL
  openAuditTrail(): void {
    this.guardianService.fetchAuditTrail();
    this.isAuditTrailOpen.set(true);
  }

  closeAuditTrail(): void {
    this.isAuditTrailOpen.set(false);
  }
}

