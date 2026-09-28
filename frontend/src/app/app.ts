import { Component, computed, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { CultureGuardianService } from './services/culture-guardian.service';
import {
  AnalysisRun,
  ArchitectureProfileId,
  AuditReport,
  BranchPolicy,
  GuardianEngineSettings,
  DetectedFrameworkItem,
  FrameworkDetectionResult,
  FrameworkApplicationSummary,
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
  CommitValidationResult,
  PipelineNodeType,
  PipelineNodeStatus,
  PipelineNode,
  PipelineBlueprint
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

  // SPA Browser Navigation & History Stack State
  readonly navHistory = signal<TabId[]>(['dashboard']);
  readonly navHistoryIndex = signal<number>(0);
  readonly canGoBack = computed<boolean>(() => this.navHistoryIndex() > 0);
  readonly canGoForward = computed<boolean>(() => this.navHistoryIndex() < this.navHistory().length - 1);
  private isNavigatingFromHistory = false;

  readonly tabDisplayNames: Record<TabId, string> = {
    dashboard: 'Dashboard',
    analyze: 'Live Code & Diff Auditor',
    results: 'Audit Results',
    rules: 'Rules Manifests',
    vocabulary: 'Layer Taxonomy',
    vcs: 'VCS & Webhook Simulator',
    history: 'Session History',
    pipelines: 'Pipelines',
    architecture: 'Architecture Health',
    violations: 'Violations Matrix',
    integrations: 'CI/CD Integrations',
    reports: 'Artifact Reports',
    settings: 'Settings & Policy Gates',
    'audit-trail': 'Audit Trail Log'
  };

  readonly activeTabTitle = computed(() => {
    return this.tabDisplayNames[this.activeTab()] || this.activeTab();
  });

  isValidTab(tab: string | null | undefined): tab is TabId {
    if (!tab) return false;
    return [
      'dashboard',
      'pipelines',
      'architecture',
      'rules',
      'violations',
      'analyze',
      'integrations',
      'reports',
      'settings',
      'results',
      'vocabulary',
      'vcs',
      'history',
      'audit-trail'
    ].includes(tab);
  }

  navigateToTab(tab: TabId, updateHistory: boolean = true): void {
    if (!this.isValidTab(tab)) return;
    
    this.activeTab.set(tab);
    if (this.isMobileMenuOpen()) {
      this.isMobileMenuOpen.set(false);
    }

    if (updateHistory && !this.isNavigatingFromHistory) {
      const currentHistory = this.navHistory();
      const currentIdx = this.navHistoryIndex();
      
      if (currentHistory[currentIdx] !== tab) {
        const newHistory = [...currentHistory.slice(0, currentIdx + 1), tab];
        this.navHistory.set(newHistory);
        this.navHistoryIndex.set(newHistory.length - 1);
        
        if (typeof window !== 'undefined' && window.history) {
          try {
            const url = new URL(window.location.href);
            url.searchParams.set('tab', tab);
            window.history.pushState({ tab, index: newHistory.length - 1 }, '', url.toString());
          } catch (e) {}
        }
      }
    }

    if (typeof document !== 'undefined') {
      document.title = `Bend DevOps Guardian - ${this.tabDisplayNames[tab] || tab}`;
    }
  }

  goBack(): void {
    if (!this.canGoBack()) return;
    const newIdx = this.navHistoryIndex() - 1;
    this.navHistoryIndex.set(newIdx);
    const targetTab = this.navHistory()[newIdx];
    this.isNavigatingFromHistory = true;
    this.activeTab.set(targetTab);
    this.isNavigatingFromHistory = false;
    if (typeof window !== 'undefined' && window.history) {
      try {
        const url = new URL(window.location.href);
        url.searchParams.set('tab', targetTab);
        window.history.replaceState({ tab: targetTab, index: newIdx }, '', url.toString());
      } catch (e) {}
    }
    if (typeof document !== 'undefined') {
      document.title = `Bend DevOps Guardian - ${this.tabDisplayNames[targetTab] || targetTab}`;
    }
  }

  goForward(): void {
    if (!this.canGoForward()) return;
    const newIdx = this.navHistoryIndex() + 1;
    this.navHistoryIndex.set(newIdx);
    const targetTab = this.navHistory()[newIdx];
    this.isNavigatingFromHistory = true;
    this.activeTab.set(targetTab);
    this.isNavigatingFromHistory = false;
    if (typeof window !== 'undefined' && window.history) {
      try {
        const url = new URL(window.location.href);
        url.searchParams.set('tab', targetTab);
        window.history.replaceState({ tab: targetTab, index: newIdx }, '', url.toString());
      } catch (e) {}
    }
    if (typeof document !== 'undefined') {
      document.title = `Bend DevOps Guardian - ${this.tabDisplayNames[targetTab] || targetTab}`;
    }
  }

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

  // Repository & Branch Target State (Stage 2 - Real Git Branches & Repo Scope)
  readonly analysisTargetMode = signal<'working_tree' | 'branch' | 'commit' | 'full_repo'>('branch');
  readonly includeBuildDirs = signal<boolean>(false);
  readonly showBuildDirsWarningModal = signal<boolean>(false);
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
  readonly findingRuleFilter = signal<string>('all');
  readonly findingFileFilter = signal<string>('all');

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

  // Webhook Simulator & Real API Connection State
  readonly webhookPlatform = signal<VcsPlatform>('github');
  readonly webhookEventType = signal<string>('pull_request');
  readonly webhookRepo = signal<string>('GiovaniRodrigo/bend-devops');
  readonly webhookBranch = signal<string>('main');
  readonly webhookCommitSha = signal<string>('45aa45489f02c613e71d3d68bc8610eb6750011b');
  readonly webhookPrNumber = signal<string>('42');
  readonly webhookPrTitle = signal<string>('feat: enforce clean architecture domain isolation');
  readonly webhookAuthor = signal<string>('lead-architect');
  readonly webhookResult = signal<string>('');
  readonly webhookApiUrl = signal<string>('/api/v1/webhook');
  readonly webhookPingUrl = signal<string>('/api/v1/vcs/ping');
  readonly webhookSecretToken = signal<string>('ghp_guardian_secret_token_123');
  readonly isTestingApiConnection = signal<boolean>(false);
  readonly apiConnectionResult = signal<{ success: boolean; latency: string; message: string; version?: string } | null>(null);
  readonly isDispatchingWebhook = signal<boolean>(false);
  readonly webhookHttpResponse = signal<{ statusCode: number; latency: string; data?: any; headers?: Record<string, string>; error?: string } | null>(null);
  readonly activeWebhookTab = signal<'result' | 'headers' | 'curl' | 'payload'>('result');

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

  // Interactive Pipeline Visualization & Flowchart Editor State
  readonly selectedPipelineStage = signal<'code' | 'rules' | 'scanner' | 'gate' | 'cicd'>('gate');
  readonly isPipelineSimulating = signal<boolean>(false);
  readonly pipelineStatus = signal<'passed' | 'running' | 'blocked'>('passed');

  // Pipeline Flowchart & DAG Designer State
  readonly pipelineSubTab = signal<'flowchart' | 'editor' | 'mermaid' | 'yaml' | 'simulator'>('flowchart');
  readonly selectedPipelineBlueprint = signal<string>('bend_strict');
  readonly selectedNodeId = signal<string | null>('node_bend');
  readonly isEditingNode = signal<boolean>(false);
  readonly isAddingNode = signal<boolean>(false);
  readonly isEditingSequence = signal<boolean>(false);
  readonly tempSequenceNodes = signal<PipelineNode[]>([]);
  readonly syncDependenciesOnReorder = signal<boolean>(true);
  readonly draggedSequenceIndex = signal<number | null>(null);
  readonly dragOverSequenceIndex = signal<number | null>(null);
  readonly isDraggingSequence = signal<boolean>(false);
  readonly pipelineZoom = signal<number>(100);
  readonly pipelineLayoutMode = signal<'horizontal' | 'grid'>('horizontal');
  readonly pipelineTargetPlatform = signal<'github' | 'gitlab' | 'azure' | 'bitbucket'>('github');
  readonly pipelineSimulationProgress = signal<number>(0);
  readonly pipelineSimulationLog = signal<string[]>([]);
  readonly pipelineSimulationActiveStep = signal<string | null>(null);
  readonly pipelineToastMessage = signal<string | null>(null);

  readonly nodeForm = signal<PipelineNode>({
    id: 'node_custom',
    name: 'Nova Etapa do Pipeline',
    shortName: 'CUSTOM',
    type: 'custom',
    status: 'pending',
    duration: '0.02s',
    summary: 'Execução de tarefa customizada de CI/CD',
    detail: 'Ambiente de execução automatizado',
    command: 'echo "Executando etapa"',
    runner: 'ubuntu-latest',
    dependsOn: ['node_gate'],
    allowFailure: false,
    timeoutMinutes: 10,
    condition: 'on_success',
    metrics: [{ label: 'Tempo Limite', value: '10m' }],
    icon: '⚡'
  });

  readonly pipelineBlueprints: PipelineBlueprint[] = [
    {
      id: 'bend_strict',
      name: 'Bend HVM Strict Architecture Gate',
      description: 'Pipeline completo de 9 estágios com redução HVM em 64 threads, varredura SAST e Quality Gate estrito.',
      category: 'Architecture & DevOps',
      platform: 'github',
      nodes: [
        {
          id: 'node_trigger',
          name: 'VCS Trigger & Webhook Event',
          shortName: 'TRIGGER',
          type: 'trigger',
          status: 'passed',
          duration: '0.01s',
          summary: 'Gatilho de Push e Pull Request no repositório',
          detail: 'Branches monitoradas: main, release/*, develop',
          command: 'on: [push, pull_request]',
          runner: 'github-webhook-agent',
          dependsOn: [],
          allowFailure: false,
          timeoutMinutes: 5,
          condition: 'always',
          metrics: [{ label: 'Event', value: 'pull_request' }, { label: 'Action', value: 'synchronize' }],
          icon: '⚡'
        },
        {
          id: 'node_checkout',
          name: 'Git Checkout & Diff Normalizer',
          shortName: 'CHECKOUT',
          type: 'checkout',
          status: 'passed',
          duration: '0.02s',
          summary: 'Clonagem rasa e normalização de diffs de arquivos',
          detail: 'Fetch depth completo para análise determinística de histórico',
          command: 'actions/checkout@v4 --fetch-depth=0',
          runner: 'ubuntu-latest',
          dependsOn: ['node_trigger'],
          allowFailure: false,
          timeoutMinutes: 5,
          condition: 'on_success',
          metrics: [{ label: 'Commit', value: 'HEAD' }, { label: 'Depth', value: 'Full' }],
          icon: '📥'
        },
        {
          id: 'node_security',
          name: 'SAST & Secret Scanner',
          shortName: 'SECURITY',
          type: 'security',
          status: 'passed',
          duration: '0.03s',
          summary: 'Detecção estática de segredos vazados e vulnerabilidades',
          detail: 'Varredura com regras de tokens sensíveis, chaves AWS/Azure e certificados',
          command: 'gitleaks detect --verbose && trivy fs .',
          runner: 'ubuntu-latest',
          dependsOn: ['node_checkout'],
          allowFailure: false,
          timeoutMinutes: 10,
          condition: 'on_success',
          metrics: [{ label: 'Scanner', value: 'Gitleaks v8' }, { label: 'Severidade', value: 'Zero-Leaking' }],
          icon: '🔒'
        },
        {
          id: 'node_manifest',
          name: 'Lexer & AST Rule Manifest Matcher',
          shortName: 'LEXER',
          type: 'lint',
          status: 'passed',
          duration: '0.02s',
          summary: 'Tokenização e mapeamento de vocabulário de camadas',
          detail: 'Validação de sintaxe Bend e manifesto JSON de regras arquiteturais',
          command: 'bend check backend/src/guardian.bend && python3 -m unittest discover tests',
          runner: 'ubuntu-latest',
          dependsOn: ['node_checkout'],
          allowFailure: false,
          timeoutMinutes: 10,
          condition: 'on_success',
          metrics: [{ label: 'Tokens', value: 'Normalized' }, { label: 'Manifests', value: '26 Regras' }],
          icon: '🧹'
        },
        {
          id: 'node_bend',
          name: 'Bend HVM Parallel Reduction',
          shortName: 'BEND HVM',
          type: 'bend_analyzer',
          status: 'passed',
          duration: '0.04s',
          summary: 'Redução funcional massivamente paralela em 64 threads virtuais',
          detail: 'Avalia árvores de sintaxe e violações de fronteiras em complexidade O(log N)',
          command: 'bend run-rs backend/src/guardian.bend --threads 64',
          runner: 'hvm-accelerated-64x',
          dependsOn: ['node_security', 'node_manifest'],
          allowFailure: false,
          timeoutMinutes: 15,
          condition: 'on_success',
          metrics: [{ label: 'Threads', value: '64 HVM' }, { label: 'Depth', value: 'O(log N)' }, { label: 'Speedup', value: '32x' }],
          icon: '🧬'
        },
        {
          id: 'node_test',
          name: 'Unit & Contract Quality Tests',
          shortName: 'TESTS',
          type: 'test',
          status: 'passed',
          duration: '0.03s',
          summary: 'Execução de testes de regressão de regras e contratos',
          detail: 'Suíte de testes atômicos e validações de pirâmide de testes',
          command: 'npm run test -- --watch=false && dotnet test --configuration Release',
          runner: 'ubuntu-latest',
          dependsOn: ['node_manifest'],
          allowFailure: false,
          timeoutMinutes: 15,
          condition: 'on_success',
          metrics: [{ label: 'Unit Tests', value: '43 Passed' }, { label: 'Coverage', value: '98.5%' }],
          icon: '🧪'
        },
        {
          id: 'node_gate',
          name: 'Quality Gate & Branch Policy Decision',
          shortName: 'GATE',
          type: 'quality_gate',
          status: 'passed',
          duration: '0.01s',
          summary: 'Avaliação estrita de pontuação mínima e zero violações P0',
          detail: 'Decisão de bloqueio ou aprovação com cálculo de penalidade acumulada',
          command: 'python3 scripts/culture_guard.py --enforce-gate --branch main',
          runner: 'guardian-engine',
          dependsOn: ['node_bend', 'node_test'],
          allowFailure: false,
          timeoutMinutes: 5,
          condition: 'on_success',
          metrics: [{ label: 'Gate Policy', value: 'Strict' }, { label: 'P0 Blocker Threshold', value: '0' }],
          icon: '🛡️'
        },
        {
          id: 'node_sarif',
          name: 'SARIF Telemetry & PR Annotations',
          shortName: 'SARIF / CI',
          type: 'sarif_export',
          status: 'passed',
          duration: '0.02s',
          summary: 'Publicação de anotações no Pull Request e artefatos SARIF v2.1.0',
          detail: 'Integração bidirecional com GitHub Security Code Scanning e GitLab SAST',
          command: 'github/codeql-action/upload-sarif --sarif-file=report.sarif',
          runner: 'ubuntu-latest',
          dependsOn: ['node_gate'],
          allowFailure: true,
          timeoutMinutes: 5,
          condition: 'always',
          metrics: [{ label: 'Format', value: 'SARIF v2.1.0' }, { label: 'Annotations', value: 'Synced' }],
          icon: '📊'
        },
        {
          id: 'node_deploy',
          name: 'Staging Deployment & Release Gate',
          shortName: 'DEPLOY',
          type: 'deploy',
          status: 'passed',
          duration: '0.05s',
          summary: 'Deploy automático para ambiente de validação contínua',
          detail: 'Executa migrações idempotentes e deploy em cluster Kubernetes',
          command: 'kubectl apply -k k8s/overlays/staging && ./scripts/smoke-test.sh',
          runner: 'production-runner',
          dependsOn: ['node_gate'],
          allowFailure: false,
          timeoutMinutes: 20,
          condition: 'on_success',
          metrics: [{ label: 'Environment', value: 'Staging' }, { label: 'Rollback', value: 'Automated' }],
          icon: '🚀'
        }
      ]
    },
    {
      id: 'clean_arch_gitops',
      name: 'Clean Architecture GitOps & CD',
      description: 'Pipeline orientado a microsserviços com validação de camadas, build de contêiner OCI e promoção GitOps.',
      category: 'GitOps & Cloud Native',
      platform: 'gitlab',
      nodes: [
        {
          id: 'node_trigger',
          name: 'GitLab Push / MR Hook',
          shortName: 'TRIGGER',
          type: 'trigger',
          status: 'passed',
          duration: '0.01s',
          summary: 'Trigger automático em Merge Requests',
          detail: 'Pipeline multi-branch para branches de feature e main',
          command: 'workflow: rules: [if: $CI_PIPELINE_SOURCE == "merge_request_event"]',
          runner: 'gitlab-runner',
          dependsOn: [],
          allowFailure: false,
          timeoutMinutes: 5,
          condition: 'always',
          metrics: [{ label: 'Runner', value: 'GitLab SaaS' }],
          icon: '⚡'
        },
        {
          id: 'node_checkout',
          name: 'Source Checkout',
          shortName: 'CHECKOUT',
          type: 'checkout',
          status: 'passed',
          duration: '0.02s',
          summary: 'Download do workspace com cache de pacotes',
          detail: 'Cache centralizado para npm e NuGet',
          command: 'git checkout $CI_COMMIT_SHA',
          runner: 'ubuntu-latest',
          dependsOn: ['node_trigger'],
          allowFailure: false,
          timeoutMinutes: 5,
          condition: 'on_success',
          metrics: [{ label: 'Cache', value: 'Hit' }],
          icon: '📥'
        },
        {
          id: 'node_bend',
          name: 'Clean Layer Rule Engine',
          shortName: 'CLEAN ARCH',
          type: 'bend_analyzer',
          status: 'passed',
          duration: '0.03s',
          summary: 'Verificação de isolamento do Domain e proibição de dependências cíclicas',
          detail: 'Garante que Domain não referencia Infraestrutura nem Apresentação',
          command: 'bend run-rs backend/src/guardian.bend --profile clean_architecture',
          runner: 'hvm-accelerated-64x',
          dependsOn: ['node_checkout'],
          allowFailure: false,
          timeoutMinutes: 10,
          condition: 'on_success',
          metrics: [{ label: 'Layer Rule', value: 'Strict Isolation' }],
          icon: '🧬'
        },
        {
          id: 'node_test',
          name: 'Automated Test Matrix',
          shortName: 'TESTS',
          type: 'test',
          status: 'passed',
          duration: '0.04s',
          summary: 'Execução de testes de unidade e contratos de API',
          detail: 'Cobertura de testes com threshold de 80%',
          command: 'dotnet test --collect:"XPlat Code Coverage"',
          runner: 'ubuntu-latest',
          dependsOn: ['node_checkout'],
          allowFailure: false,
          timeoutMinutes: 10,
          condition: 'on_success',
          metrics: [{ label: 'Test Suite', value: 'Passing' }],
          icon: '🧪'
        },
        {
          id: 'node_gate',
          name: 'GitOps Policy Gate',
          shortName: 'GATE',
          type: 'quality_gate',
          status: 'passed',
          duration: '0.01s',
          summary: 'Checagem de conformidade GitOps e branch protection',
          detail: 'Exige pontuação 100% para prosseguir com o build de release',
          command: 'python3 scripts/culture_guard.py --gitops-mode',
          runner: 'guardian-engine',
          dependsOn: ['node_bend', 'node_test'],
          allowFailure: false,
          timeoutMinutes: 5,
          condition: 'on_success',
          metrics: [{ label: 'GitOps Gate', value: 'Approved' }],
          icon: '🛡️'
        },
        {
          id: 'node_build_oci',
          name: 'OCI Container Image Build',
          shortName: 'BUILD OCI',
          type: 'build',
          status: 'passed',
          duration: '0.06s',
          summary: 'Build de imagem Docker multi-stage sem root',
          detail: 'Publicação de imagem assinada no container registry com Cosign',
          command: 'docker buildx build --platform linux/amd64,linux/arm64 -t registry/app:$CI_COMMIT_SHORT_SHA .',
          runner: 'docker-dind-runner',
          dependsOn: ['node_gate'],
          allowFailure: false,
          timeoutMinutes: 15,
          condition: 'on_success',
          metrics: [{ label: 'Image', value: 'Distroless' }, { label: 'Signature', value: 'Cosign Signed' }],
          icon: '📦'
        },
        {
          id: 'node_deploy',
          name: 'GitOps Manifest Sync (ArgoCD)',
          shortName: 'ARGOCD SYNC',
          type: 'deploy',
          status: 'passed',
          duration: '0.03s',
          summary: 'Commit automatizado no repositório de configuração ArgoCD',
          detail: 'Sincronização contínua com cluster de produção',
          command: 'argocd app sync guardian-app --prune',
          runner: 'gitops-agent',
          dependsOn: ['node_build_oci'],
          allowFailure: false,
          timeoutMinutes: 10,
          condition: 'on_success',
          metrics: [{ label: 'Sync Status', value: 'Synced' }, { label: 'Health', value: 'Healthy' }],
          icon: '🚀'
        }
      ]
    },
    {
      id: 'fast_feedback_ci',
      name: 'Microservices Fast Feedback CI',
      description: 'Pipeline ultra-rápido otimizado para feedback em menos de 10 segundos com paralelismo máximo.',
      category: 'Developer Experience',
      platform: 'github',
      nodes: [
        {
          id: 'node_trigger',
          name: 'PR Quick Hook',
          shortName: 'HOOK',
          type: 'trigger',
          status: 'passed',
          duration: '0.01s',
          summary: 'Gatilho de abertura de PR',
          detail: 'Fail-fast instantâneo',
          command: 'on: pull_request',
          runner: 'fast-runner',
          dependsOn: [],
          allowFailure: false,
          timeoutMinutes: 3,
          condition: 'always',
          metrics: [{ label: 'Trigger', value: 'FastHook' }],
          icon: '⚡'
        },
        {
          id: 'node_bend',
          name: 'HVM Rapid Audit',
          shortName: 'FAST HVM',
          type: 'bend_analyzer',
          status: 'passed',
          duration: '0.02s',
          summary: 'Avaliação instantânea de regras arquiteturais',
          detail: 'Execução direta em memória sem I/O de disco',
          command: 'bend run-rs backend/src/guardian.bend --fast-mode',
          runner: 'hvm-in-memory',
          dependsOn: ['node_trigger'],
          allowFailure: false,
          timeoutMinutes: 3,
          condition: 'on_success',
          metrics: [{ label: 'Time', value: '0.02s' }],
          icon: '🧬'
        },
        {
          id: 'node_gate',
          name: 'Instant Quality Feedback',
          shortName: 'GATE',
          type: 'quality_gate',
          status: 'passed',
          duration: '0.01s',
          summary: 'Aprovação expressa de PR',
          detail: 'Bloqueia se houver P0s e libera em caso de zero violações',
          command: 'python3 scripts/culture_guard.py --fast',
          runner: 'guardian-engine',
          dependsOn: ['node_bend'],
          allowFailure: false,
          timeoutMinutes: 2,
          condition: 'on_success',
          metrics: [{ label: 'Status', value: 'PASS' }],
          icon: '🛡️'
        },
        {
          id: 'node_notify',
          name: 'PR Inline Comment Bot',
          shortName: 'NOTIFY',
          type: 'notify',
          status: 'passed',
          duration: '0.01s',
          summary: 'Comenta resumo diretamente no PR',
          detail: 'Tabela de conformidade e sugestões de correção',
          command: 'gh pr comment $PR_NUMBER --body-file=summary.md',
          runner: 'github-actions',
          dependsOn: ['node_gate'],
          allowFailure: true,
          timeoutMinutes: 2,
          condition: 'always',
          metrics: [{ label: 'Bot', value: 'Active' }],
          icon: '📡'
        }
      ]
    }
  ];

  readonly pipelineNodes = signal<PipelineNode[]>(
    JSON.parse(JSON.stringify(this.pipelineBlueprints[0].nodes))
  );

  readonly selectedPipelineNode = computed<PipelineNode | undefined>(() => {
    const id = this.selectedNodeId();
    if (!id) return undefined;
    return this.pipelineNodes().find(n => n.id === id);
  });

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
  readonly engineSettings = this.guardianService.engineSettings;
  readonly history = this.guardianService.history;
  readonly codePresets = this.guardianService.codePresets;

  // Settings & Branch Policy Sub-tab and Form State
  readonly settingsSubTab = signal<'policies' | 'engine' | 'framework' | 'raw_json'>('policies');
  readonly isAddingPolicy = signal<boolean>(false);
  readonly editingPolicyIndex = signal<number | null>(null);
  readonly newPolicyForm = signal<BranchPolicy>({
    branchPattern: 'release/*',
    minScore: 80,
    allowP0: false,
    allowP1: true,
    requireCleanBuild: true,
    requireCiApproval: true,
    blockOnPragmaWithoutReason: true,
    enabled: true,
    description: 'Release stabilization gate'
  });
  readonly settingsSavedToast = signal<string | null>(null);

  // Framework Detection Modal & State
  readonly showFrameworkDetectionModal = signal<boolean>(false);
  readonly pendingRepoForFrameworkScan = signal<LocalRepositoryInfo | null>(null);
  readonly isScanningFramework = signal<boolean>(false);
  readonly lastFrameworkDetectionResult = signal<FrameworkDetectionResult | null>(null);
  readonly frameworkToastMessage = signal<string | null>(null);
  readonly rememberFrameworkScanChoice = signal<boolean>(false);

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

  // Pipeline Flowchart Computed: Total Estimated Duration
  readonly pipelineTotalDuration = computed<string>(() => {
    let totalSec = 0;
    this.pipelineNodes().forEach(n => {
      const match = n.duration.match(/([0-9.]+)/);
      if (match) totalSec += parseFloat(match[1]);
    });
    return `${totalSec.toFixed(2)}s`;
  });

  // Pipeline Flowchart Computed: Status Summary Count
  readonly pipelineStatusSummary = computed(() => {
    const nodes = this.pipelineNodes();
    const passed = nodes.filter(n => n.status === 'passed').length;
    const blocked = nodes.filter(n => n.status === 'blocked').length;
    const running = nodes.filter(n => n.status === 'running').length;
    const pending = nodes.filter(n => n.status === 'pending').length;
    const skipped = nodes.filter(n => n.status === 'skipped').length;
    const overallStatus: PipelineNodeStatus = blocked > 0 ? 'blocked' : (running > 0 ? 'running' : 'passed');
    return { passed, blocked, running, pending, skipped, total: nodes.length, overallStatus };
  });

  // Generated Mermaid Diagram Code (Real-Time Synchronized)
  readonly generatedMermaidCode = computed<string>(() => {
    const nodes = this.pipelineNodes();
    let code = 'flowchart LR\n';
    code += '  %% Styling classes for pipeline status\n';
    code += '  classDef passed fill:#064e3b,stroke:#10b981,stroke-width:2px,color:#f8fafc;\n';
    code += '  classDef blocked fill:#881337,stroke:#f43f5e,stroke-width:2px,color:#f8fafc;\n';
    code += '  classDef running fill:#164e63,stroke:#06b6d4,stroke-width:2px,color:#f8fafc;\n';
    code += '  classDef pending fill:#1e293b,stroke:#64748b,stroke-width:1px,color:#94a3b8;\n';
    code += '  classDef skipped fill:#78350f,stroke:#f59e0b,stroke-width:1px,color:#f8fafc;\n\n';

    nodes.forEach(n => {
      const icon = n.icon || this.getNodeTypeIcon(n.type);
      const shapeStart = n.type === 'quality_gate' ? '{"' : '["';
      const shapeEnd = n.type === 'quality_gate' ? '}"' : '"]';
      code += `  ${n.id}${shapeStart}${icon} ${n.name}${shapeEnd}:::${n.status}\n`;
    });

    code += '\n  %% Connections & Dependencies\n';
    let hasConnections = false;
    nodes.forEach(n => {
      if (n.dependsOn && n.dependsOn.length > 0) {
        n.dependsOn.forEach(parentId => {
          if (nodes.some(x => x.id === parentId)) {
            code += `  ${parentId} --> ${n.id}\n`;
            hasConnections = true;
          }
        });
      }
    });

    if (!hasConnections && nodes.length > 1) {
      for (let i = 0; i < nodes.length - 1; i++) {
        code += `  ${nodes[i].id} --> ${nodes[i + 1].id}\n`;
      }
    }

    return code;
  });

  // Generated CI/CD Platform YAML (GitHub Actions, GitLab CI, Azure Pipelines, Bitbucket)
  readonly generatedPipelineYaml = computed<string>(() => {
    const platform = this.pipelineTargetPlatform();
    const nodes = this.pipelineNodes();
    const repo = this.inputRepo();
    const branch = this.selectedBranch();

    if (platform === 'github') {
      let y = `# ==============================================================================\n`;
      y += `# Bend DevOps Guardian - GitHub Actions Workflow\n`;
      y += `# Repository: ${repo} | Target Branch: ${branch}\n`;
      y += `# Generated automatically by Pipeline Flowchart Designer\n`;
      y += `# ==============================================================================\n`;
      y += `name: Bend DevOps Guardian Quality Gate\n\n`;
      y += `on:\n`;
      y += `  push:\n`;
      y += `    branches: [ ${branch}, release/*, develop ]\n`;
      y += `  pull_request:\n`;
      y += `    branches: [ ${branch}, release/* ]\n\n`;
      y += `permissions:\n`;
      y += `  contents: read\n`;
      y += `  pull-requests: write\n`;
      y += `  security-events: write\n\n`;
      y += `jobs:\n`;

      nodes.forEach(n => {
        const jobId = n.id.replace(/[^a-zA-Z0-9_]/g, '_');
        y += `  ${jobId}:\n`;
        y += `    name: "${n.name}"\n`;
        y += `    runs-on: ${n.runner || 'ubuntu-latest'}\n`;
        y += `    timeout-minutes: ${n.timeoutMinutes || 10}\n`;
        if (n.allowFailure) {
          y += `    continue-on-error: true\n`;
        }
        if (n.dependsOn && n.dependsOn.length > 0) {
          const parentJobIds = n.dependsOn.map(p => p.replace(/[^a-zA-Z0-9_]/g, '_'));
          y += `    needs: [ ${parentJobIds.join(', ')} ]\n`;
        }
        y += `    steps:\n`;
        if (n.type === 'checkout') {
          y += `      - name: Checkout repository\n`;
          y += `        uses: actions/checkout@v4\n`;
          y += `        with:\n`;
          y += `          fetch-depth: 0\n`;
        } else if (n.type === 'sarif_export') {
          y += `      - name: Upload SARIF report\n`;
          y += `        uses: github/codeql-action/upload-sarif@v3\n`;
          y += `        with:\n`;
          y += `          sarif_file: guardian-report.sarif\n`;
        } else {
          y += `      - name: Execute ${n.shortName}\n`;
          y += `        run: |\n`;
          y += `          ${n.command || 'echo "Step executed"'}\n`;
        }
        y += `\n`;
      });
      return y;
    } else if (platform === 'gitlab') {
      let y = `# ==============================================================================\n`;
      y += `# Bend DevOps Guardian - GitLab CI/CD Configuration (.gitlab-ci.yml)\n`;
      y += `# ==============================================================================\n`;
      y += `stages:\n`;
      const stageSet = Array.from(new Set(nodes.map(n => n.type)));
      stageSet.forEach(st => {
        y += `  - ${st}\n`;
      });
      y += `\n`;
      nodes.forEach(n => {
        y += `${n.id}:\n`;
        y += `  stage: ${n.type}\n`;
        y += `  image: ${n.runner.includes('hvm') ? 'bendlang/bend:latest' : 'ubuntu:22.04'}\n`;
        if (n.allowFailure) y += `  allow_failure: true\n`;
        if (n.dependsOn && n.dependsOn.length > 0) {
          y += `  needs: [ ${n.dependsOn.join(', ')} ]\n`;
        }
        y += `  script:\n`;
        y += `    - ${n.command || 'echo "Step executed"'}\n\n`;
      });
      return y;
    } else if (platform === 'azure') {
      let y = `# ==============================================================================\n`;
      y += `# Bend DevOps Guardian - Azure Pipelines Configuration (azure-pipelines.yml)\n`;
      y += `# ==============================================================================\n`;
      y += `trigger:\n  - ${branch}\n\npool:\n  vmImage: 'ubuntu-latest'\n\nstages:\n`;
      y += `  - stage: GuardianPipeline\n    displayName: 'Bend DevOps Guardian Quality Gate'\n    jobs:\n`;
      nodes.forEach(n => {
        y += `      - job: ${n.id.replace(/[^a-zA-Z0-9_]/g, '_')}\n`;
        y += `        displayName: '${n.name}'\n`;
        if (n.dependsOn && n.dependsOn.length > 0) {
          y += `        dependsOn: [ ${n.dependsOn.map(p => p.replace(/[^a-zA-Z0-9_]/g, '_')).join(', ')} ]\n`;
        }
        y += `        steps:\n`;
        y += `          - script: |\n              ${n.command || 'echo "Running"'}\n            displayName: '${n.shortName}'\n\n`;
      });
      return y;
    } else {
      let y = `# ==============================================================================\n`;
      y += `# Bitbucket Pipelines Configuration (bitbucket-pipelines.yml)\n`;
      y += `# ==============================================================================\n`;
      y += `pipelines:\n  default:\n`;
      nodes.forEach(n => {
        y += `    - step:\n`;
        y += `        name: ${n.name}\n`;
        y += `        script:\n`;
        y += `          - ${n.command || 'echo "Running"'}\n`;
      });
      return y;
    }
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

  // All Raw Findings/Violations
  readonly allFindings = computed<CodeViolation[]>(() => {
    let list: CodeViolation[] = [];
    if (this.currentAuditedFiles().length > 0) {
      this.currentAuditedFiles().forEach(f => list.push(...f.violations));
    } else {
      this.history().forEach(h => list.push(...h.violations));
    }
    return list;
  });

  // Unique Rule IDs in Findings for Dropdown Filtering
  readonly uniqueFindingRules = computed<string[]>(() => {
    const set = new Set<string>();
    this.allFindings().forEach(v => {
      if (v.ruleId) set.add(v.ruleId);
    });
    return Array.from(set).sort();
  });

  // Unique Files in Findings for Dropdown Filtering
  readonly uniqueFindingFiles = computed<string[]>(() => {
    const set = new Set<string>();
    this.allFindings().forEach(v => {
      if (v.fileName) set.add(v.fileName);
    });
    return Array.from(set).sort();
  });

  // Computed Boolean to Check if Any Filter is Active
  readonly isFindingFiltered = computed<boolean>(() => {
    return (
      this.violationSearch().trim() !== '' ||
      this.selectedSeverityFilter() !== 'all' ||
      this.findingRuleFilter() !== 'all' ||
      this.findingFileFilter() !== 'all'
    );
  });

  // Filtered Violations / Findings List (Multi-criteria Search, Rule, File & Severity)
  readonly filteredViolations = computed<CodeViolation[]>(() => {
    const query = this.violationSearch().toLowerCase().trim();
    const sevFilter = this.selectedSeverityFilter();
    const ruleFilter = this.findingRuleFilter();
    const fileFilter = this.findingFileFilter();

    let list = this.allFindings();

    if (query) {
      list = list.filter(v => 
        (v.message && v.message.toLowerCase().includes(query)) ||
        (v.fileName && v.fileName.toLowerCase().includes(query)) ||
        (v.ruleId && v.ruleId.toLowerCase().includes(query)) ||
        (v.astNode && v.astNode.toLowerCase().includes(query)) ||
        (v.snippet && v.snippet.toLowerCase().includes(query)) ||
        (v.remediation && v.remediation.toLowerCase().includes(query)) ||
        (v.author && v.author.toLowerCase().includes(query))
      );
    }

    if (sevFilter !== 'all') {
      list = list.filter(v => 
        v.severity === sevFilter || 
        (sevFilter === 'P0_BLOCKING' && v.severity === 'P0') || 
        (sevFilter === 'P1_WARNING' && v.severity === 'P1') || 
        (sevFilter === 'P2_INFO' && (v.severity === 'P2' || v.severity === 'P3' || v.severity === 'INFO'))
      );
    }

    if (ruleFilter !== 'all') {
      list = list.filter(v => v.ruleId === ruleFilter);
    }

    if (fileFilter !== 'all') {
      list = list.filter(v => v.fileName === fileFilter);
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
    return this.rules().filter(r => (r.status || '').toLowerCase() === 'active' || (r.enabled !== false && (r.status || '').toLowerCase() !== 'inactive')).length;
  });
  readonly hasExecutedAudit = computed(() => {
    return this.history().length > 0 || this.currentAuditedFiles().length > 0;
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
    } else if (mode === 'full_repo') {
      return `Whole Repository (All Source Files${this.includeBuildDirs() ? ' + Build Dirs' : ''})`;
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

  // Always-Visible Applied Rules State on Live Auditor Screen
  readonly appliedRulesFilter = signal<string>('');
  readonly appliedRulesSeverityFilter = signal<'ALL' | 'P0' | 'P1' | 'P2'>('ALL');
  readonly isAppliedRulesPanelCollapsed = signal<boolean>(false);

  readonly appliedRulesList = computed<CultureRule[]>(() => {
    const all = this.rules();
    const mode = this.validationScopeMode();
    const customIds = this.selectedCustomRuleIds();
    const filterText = this.appliedRulesFilter().toLowerCase().trim();
    const sevFilter = this.appliedRulesSeverityFilter();

    let list: CultureRule[];
    if (mode === 'custom') {
      list = all.filter(r => customIds.has(r.id));
    } else {
      list = all.filter(r => (r.status || '').toLowerCase() === 'active' || (r.enabled !== false && (r.status || '').toLowerCase() !== 'inactive'));
    }

    if (sevFilter !== 'ALL') {
      list = list.filter(r => (r.severity || '').toUpperCase().startsWith(sevFilter));
    }

    if (filterText) {
      list = list.filter(r =>
        r.id.toLowerCase().includes(filterText) ||
        r.name.toLowerCase().includes(filterText) ||
        (r.category || '').toLowerCase().includes(filterText) ||
        (r.description || '').toLowerCase().includes(filterText) ||
        (r.layer || '').toLowerCase().includes(filterText) ||
        (r.languages || []).some(l => l.toLowerCase().includes(filterText))
      );
    }

    return list;
  });

  readonly appliedP0Count = computed<number>(() => {
    return this.appliedRulesList().filter(r => (r.severity || '').toUpperCase().startsWith('P0')).length;
  });

  readonly appliedP1Count = computed<number>(() => {
    return this.appliedRulesList().filter(r => (r.severity || '').toUpperCase().startsWith('P1')).length;
  });

  toggleAppliedRulesPanel(): void {
    this.isAppliedRulesPanelCollapsed.update(v => !v);
  }

  setAppliedRulesSeverityFilter(filter: 'ALL' | 'P0' | 'P1' | 'P2'): void {
    this.appliedRulesSeverityFilter.set(filter);
  }

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

      // Browser popstate listener for Back / Forward buttons
      window.addEventListener('popstate', (event: PopStateEvent) => {
        let targetTab: TabId | null = null;
        if (event.state && event.state.tab && this.isValidTab(event.state.tab)) {
          targetTab = event.state.tab;
        } else {
          const params = new URLSearchParams(window.location.search);
          const urlTab = params.get('tab');
          if (urlTab && this.isValidTab(urlTab)) {
            targetTab = urlTab;
          }
        }

        if (targetTab && this.isValidTab(targetTab)) {
          this.isNavigatingFromHistory = true;
          this.activeTab.set(targetTab);
          
          if (event.state && typeof event.state.index === 'number') {
            this.navHistoryIndex.set(event.state.index);
          } else {
            const lastIdx = this.navHistory().lastIndexOf(targetTab);
            if (lastIdx !== -1) {
              this.navHistoryIndex.set(lastIdx);
            } else {
              this.navHistory.update(h => [...h, targetTab]);
              this.navHistoryIndex.set(this.navHistory().length - 1);
            }
          }
          this.isNavigatingFromHistory = false;
          if (typeof document !== 'undefined') {
            document.title = `Bend DevOps Guardian - ${this.tabDisplayNames[targetTab] || targetTab}`;
          }
        }
      });

      // Keyboard shortcuts: Alt + ArrowLeft (Back), Alt + ArrowRight (Forward)
      window.addEventListener('keydown', (e: KeyboardEvent) => {
        if (e.altKey && e.key === 'ArrowLeft') {
          if (this.canGoBack()) {
            e.preventDefault();
            this.goBack();
          }
        } else if (e.altKey && e.key === 'ArrowRight') {
          if (this.canGoForward()) {
            e.preventDefault();
            this.goForward();
          }
        }
      });

      try {
        const params = new URLSearchParams(window.location.search);
        const urlTab = params.get('tab');
        if (urlTab && this.isValidTab(urlTab)) {
          this.activeTab.set(urlTab);
          this.navHistory.set([urlTab]);
          this.navHistoryIndex.set(0);
          if (window.history) {
            window.history.replaceState({ tab: urlTab, index: 0 }, '', window.location.href);
          }
        } else if (window.history) {
          window.history.replaceState({ tab: 'dashboard', index: 0 }, '', window.location.href);
        }

        if (params.get('mode') === 'mock' || params.has('scenario')) {
          const scenario = params.get('scenario') || 'clean-repository';
          this.isMockMode.set(true);
          this.mockScenario.set(scenario);
          this.loadMockScenario(scenario);
        } else {
          this.guardianService.discoverLocalRepositories();
          this.guardianService.inspectWorkingTree();
          this.guardianService.fetchRules().then(loadedRules => {
            if (loadedRules && loadedRules.length > 0) {
              this.selectedCustomRuleIds.set(new Set(loadedRules.map(r => r.id)));
            }
          });
          this.guardianService.fetchRuleMetadata();
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

      if (this.engineSettings().autoScanFrameworkOnRepoSelect) {
        this.pendingRepoForFrameworkScan.set(found);
        this.showFrameworkDetectionModal.set(true);
      }
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

      if (this.engineSettings().autoScanFrameworkOnRepoSelect) {
        this.pendingRepoForFrameworkScan.set(res.repository);
        this.showFrameworkDetectionModal.set(true);
      }
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
  setAnalysisTargetMode(mode: 'working_tree' | 'branch' | 'commit' | 'full_repo'): void {
    this.analysisTargetMode.set(mode);
    if (mode === 'working_tree') {
      this.guardianService.inspectWorkingTree(this.selectedLocalRepoId());
    } else if (mode === 'commit') {
      this.validateCommitInput(this.commitShaInput());
    }
  }

  onIncludeBuildDirsChange(checked: boolean): void {
    if (checked) {
      this.showBuildDirsWarningModal.set(true);
    } else {
      this.includeBuildDirs.set(false);
    }
  }

  confirmIncludeBuildDirs(): void {
    this.includeBuildDirs.set(true);
    this.showBuildDirsWarningModal.set(false);
  }

  cancelIncludeBuildDirs(): void {
    this.includeBuildDirs.set(false);
    this.showBuildDirsWarningModal.set(false);
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
        this.includeBuildDirs(),
        (progress, step) => {
          this.analysisProgress.set(progress);
          this.analysisProgressStep.set(step);
        }
      );

      this.currentAuditedFiles.set(result.files);
      const report = result.report;
      const statusText = report.p0Count > 0 ? 'Blocked' : report.score === 100 ? 'Full compliance' : 'Completed';

      const isFullRepo = targetMode === 'full_repo';
      const projectLabel = isFullRepo
        ? `${this.activeRepoName()} · Whole Repository`
        : `${this.activeRepoName()} · Branch ${branch}`;
      const mrTitleLabel = isFullRepo
        ? `Whole Repository Audit (${result.files.length} files audited${this.includeBuildDirs() ? ' + builds' : ''})`
        : `Branch ${branch} (${result.files.length} files audited)`;

      const newRun: AnalysisRun = {
        id: `${Date.now()}`,
        date: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
        project: projectLabel,
        mrTitle: mrTitleLabel,
        author: this.inputAuthor(),
        targetBranch: isFullRepo ? 'all' : branch,
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
    this.navigateToTab('results');
  }

  openRulesTab(): void {
    this.navigateToTab('rules');
    this.guardianService.fetchRules();
  }

  clearFindingFilters(): void {
    this.violationSearch.set('');
    this.selectedSeverityFilter.set('all');
    this.findingRuleFilter.set('all');
    this.findingFileFilter.set('all');
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

  // Real VCS Webhook API Connection & Live Ingestion Methods
  readonly generatedCurlSnippet = computed<string>(() => {
    const payload = {
      platform: this.webhookPlatform(),
      event: this.webhookEventType(),
      repo: this.webhookRepo(),
      branch: this.webhookBranch(),
      commitSha: this.webhookCommitSha(),
      prNumber: this.webhookPrNumber(),
      prTitle: this.webhookPrTitle(),
      author: this.webhookAuthor()
    };
    const token = this.webhookSecretToken();
    const tokenHeader = token ? ` \\\n  -H "X-Hub-Signature-256: sha256=${token}" \\\n  -H "Authorization: Bearer ${token}"` : '';
    return `curl -X POST http://localhost:8000${this.webhookApiUrl()} \\\n  -H "Content-Type: application/json"${tokenHeader} \\\n  -d '${JSON.stringify(payload, null, 2)}'`;
  });

  async testWebhookApiConnection(): Promise<void> {
    this.isTestingApiConnection.set(true);
    this.apiConnectionResult.set(null);
    try {
      const res = await this.guardianService.testVcsApiConnection(this.webhookPingUrl());
      if (res.success) {
        this.apiConnectionResult.set({
          success: true,
          latency: res.latency,
          message: `Conectado com sucesso ao servidor VCS Guardian (${res.data?.service || 'API Online'})`,
          version: res.data?.version || '2.0.0'
        });
      } else {
        this.apiConnectionResult.set({
          success: false,
          latency: res.latency,
          message: `Falha na conexão: ${res.error || 'Endpoint inacessível'}`
        });
      }
    } finally {
      this.isTestingApiConnection.set(false);
    }
  }

  async dispatchWebhookViaApi(): Promise<void> {
    this.isDispatchingWebhook.set(true);
    const payload = {
      platform: this.webhookPlatform(),
      event: this.webhookEventType(),
      repo: this.webhookRepo(),
      branch: this.webhookBranch(),
      commitSha: this.webhookCommitSha(),
      prNumber: this.webhookPrNumber(),
      prTitle: this.webhookPrTitle(),
      author: this.webhookAuthor()
    };

    try {
      const res = await this.guardianService.dispatchVcsWebhook(
        this.webhookApiUrl(),
        payload,
        this.webhookSecretToken()
      );
      this.webhookHttpResponse.set({
        statusCode: res.statusCode,
        latency: res.latency,
        data: res.responseBody,
        headers: res.headers,
        error: res.error
      });

      const isMain = this.webhookBranch() === 'main' || this.webhookBranch() === 'master';
      const policyDesc = isMain 
        ? 'Strict Gating Policy: 0 P0 violations required, minimum score >= 80%.' 
        : 'Permissive Branch Policy: Non-blocking warning mode enabled for feature branch.';

      const httpStatusBadge = res.statusCode === 200 ? 'HTTP 200 OK' : `HTTP ${res.statusCode || 'ERROR'}`;
      this.webhookResult.set(
        `📡 [API DISPATCH - ${httpStatusBadge} in ${res.latency}]\n` +
        `✅ Ingested Webhook [${payload.platform.toUpperCase()}] Event: "${payload.event}" via API\n` +
        `Repository: ${payload.repo} | Branch: ${payload.branch} | SHA: ${payload.commitSha.substring(0, 8)}\n` +
        `Policy Applied: ${policyDesc}\n` +
        `Decision: ${res.responseBody?.decision || (res.statusCode === 200 ? 'PASS' : 'BLOCKED')} | Latency: ${res.latency} (Bend HVM API)`
      );
    } finally {
      this.isDispatchingWebhook.set(false);
    }
  }

  // Architecture Profile Status Management
  readonly activeArchitectureProfilesCount = computed(() => {
    return this.architectureProfiles().filter(p => p.enabled !== false).length;
  });

  toggleArchitectureProfile(profileId: ArchitectureProfileId): void {
    this.guardianService.toggleArchitectureProfile(profileId);
  }

  enableAllProfiles(): void {
    this.architectureProfiles().forEach(p => this.guardianService.setArchitectureProfileStatus(p.id, true));
  }

  disableAllProfiles(): void {
    this.architectureProfiles().forEach(p => this.guardianService.setArchitectureProfileStatus(p.id, false));
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
    const nodeMap: Record<string, string> = {
      code: 'node_checkout',
      rules: 'node_manifest',
      scanner: 'node_bend',
      gate: 'node_gate',
      cicd: 'node_sarif'
    };
    if (nodeMap[stageId]) {
      this.selectedNodeId.set(nodeMap[stageId]);
    }
  }

  selectPipelineNode(nodeId: string): void {
    this.selectedNodeId.set(nodeId);
    const node = this.pipelineNodes().find(n => n.id === nodeId);
    if (node) {
      this.nodeForm.set({ ...node, dependsOn: [...node.dependsOn], metrics: [...node.metrics] });
    }
  }

  openAddNodeModal(parentId?: string): void {
    const newId = `node_${Date.now().toString(36)}`;
    const depends = parentId ? [parentId] : (this.selectedNodeId() ? [this.selectedNodeId()!] : []);
    this.nodeForm.set({
      id: newId,
      name: 'Nova Etapa do Pipeline',
      shortName: 'CUSTOM',
      type: 'custom',
      status: 'pending',
      duration: '0.02s',
      summary: 'Execução de tarefa customizada',
      detail: 'Passo adicionado pelo usuário',
      command: 'echo "Executando passo customizado"',
      runner: 'ubuntu-latest',
      dependsOn: depends,
      allowFailure: false,
      timeoutMinutes: 10,
      condition: 'on_success',
      metrics: [{ label: 'Ambiente', value: 'ubuntu-latest' }],
      icon: '⚡'
    });
    this.isAddingNode.set(true);
    this.isEditingNode.set(false);
  }

  openEditNodeModal(node: PipelineNode): void {
    this.selectedNodeId.set(node.id);
    this.nodeForm.set({ ...node, dependsOn: [...node.dependsOn], metrics: [...node.metrics] });
    this.isEditingNode.set(true);
    this.isAddingNode.set(false);
  }

  closeNodeModal(): void {
    this.isAddingNode.set(false);
    this.isEditingNode.set(false);
  }

  toggleNodeDependency(depId: string): void {
    const current = this.nodeForm();
    const currentDeps = current.dependsOn || [];
    let updatedDeps: string[];
    if (currentDeps.includes(depId)) {
      updatedDeps = currentDeps.filter(id => id !== depId);
    } else {
      updatedDeps = [...currentDeps, depId];
    }
    this.nodeForm.set({ ...current, dependsOn: updatedDeps });
  }

  saveNodeForm(): void {
    const form = this.nodeForm();
    if (!form.name.trim()) return;

    const icon = form.icon || this.getNodeTypeIcon(form.type);
    const nodeToSave: PipelineNode = {
      ...form,
      icon,
      shortName: form.shortName || form.name.substring(0, 8).toUpperCase()
    };

    if (this.isAddingNode()) {
      this.pipelineNodes.update(nodes => [...nodes, nodeToSave]);
      this.selectedNodeId.set(nodeToSave.id);
      this.pipelineToastMessage.set(`Etapa "${nodeToSave.name}" adicionada ao fluxo com sucesso!`);
    } else {
      this.pipelineNodes.update(nodes =>
        nodes.map(n => (n.id === nodeToSave.id ? nodeToSave : n))
      );
      this.pipelineToastMessage.set(`Etapa "${nodeToSave.name}" atualizada com sucesso!`);
    }

    this.closeNodeModal();
    setTimeout(() => this.pipelineToastMessage.set(null), 4000);
  }

  deletePipelineNode(nodeId: string): void {
    const node = this.pipelineNodes().find(n => n.id === nodeId);
    const nodeName = node?.name || nodeId;
    
    this.pipelineNodes.update(nodes => {
      return nodes
        .filter(n => n.id !== nodeId)
        .map(n => ({
          ...n,
          dependsOn: n.dependsOn.filter(d => d !== nodeId)
        }));
    });

    if (this.selectedNodeId() === nodeId) {
      const remaining = this.pipelineNodes();
      this.selectedNodeId.set(remaining.length > 0 ? remaining[0].id : null);
    }

    this.pipelineToastMessage.set(`Etapa "${nodeName}" removida do pipeline.`);
    setTimeout(() => this.pipelineToastMessage.set(null), 4000);
  }

  duplicatePipelineNode(nodeId: string): void {
    const original = this.pipelineNodes().find(n => n.id === nodeId);
    if (!original) return;

    const newId = `${original.id}_copy_${Date.now().toString(36).substring(4)}`;
    const cloned: PipelineNode = {
      ...original,
      id: newId,
      name: `${original.name} (Cópia)`,
      shortName: `${original.shortName}_CP`,
      status: 'pending',
      dependsOn: [...original.dependsOn],
      metrics: [...original.metrics]
    };

    this.pipelineNodes.update(nodes => {
      const idx = nodes.findIndex(n => n.id === nodeId);
      const updated = [...nodes];
      updated.splice(idx + 1, 0, cloned);
      return updated;
    });

    this.selectedNodeId.set(newId);
    this.pipelineToastMessage.set(`Etapa duplicada como "${cloned.name}".`);
    setTimeout(() => this.pipelineToastMessage.set(null), 4000);
  }

  movePipelineNode(nodeId: string, direction: 'up' | 'down' | 'left' | 'right'): void {
    this.pipelineNodes.update(nodes => {
      const idx = nodes.findIndex(n => n.id === nodeId);
      if (idx === -1) return nodes;

      const targetIdx = (direction === 'up' || direction === 'left') ? idx - 1 : idx + 1;
      if (targetIdx < 0 || targetIdx >= nodes.length) return nodes;

      const updated = [...nodes];
      const temp = updated[idx];
      updated[idx] = updated[targetIdx];
      updated[targetIdx] = temp;
      return updated;
    });
  }

  openEditSequenceModal(): void {
    this.tempSequenceNodes.set(JSON.parse(JSON.stringify(this.pipelineNodes())));
    this.draggedSequenceIndex.set(null);
    this.dragOverSequenceIndex.set(null);
    this.isDraggingSequence.set(false);
    this.isEditingSequence.set(true);
  }

  closeEditSequenceModal(): void {
    this.isEditingSequence.set(false);
    this.tempSequenceNodes.set([]);
    this.draggedSequenceIndex.set(null);
    this.dragOverSequenceIndex.set(null);
    this.isDraggingSequence.set(false);
  }

  toggleSyncDependenciesOnReorder(): void {
    this.syncDependenciesOnReorder.update(v => !v);
  }

  moveSequenceItem(index: number, direction: 'up' | 'down' | 'top' | 'bottom'): void {
    const list = [...this.tempSequenceNodes()];
    if (index < 0 || index >= list.length) return;

    let targetIndex = index;
    if (direction === 'up') targetIndex = index - 1;
    else if (direction === 'down') targetIndex = index + 1;
    else if (direction === 'top') targetIndex = 0;
    else if (direction === 'bottom') targetIndex = list.length - 1;

    if (targetIndex < 0 || targetIndex >= list.length || targetIndex === index) return;

    const [item] = list.splice(index, 1);
    list.splice(targetIndex, 0, item);
    this.tempSequenceNodes.set(list);
  }

  onSequenceDragStart(event: DragEvent, index: number): void {
    this.draggedSequenceIndex.set(index);
    this.isDraggingSequence.set(true);
    if (event.dataTransfer) {
      event.dataTransfer.effectAllowed = 'move';
      event.dataTransfer.setData('text/plain', index.toString());
    }
  }

  onSequenceDragOver(event: DragEvent, index: number): void {
    event.preventDefault();
    if (event.dataTransfer) {
      event.dataTransfer.dropEffect = 'move';
    }
    if (this.dragOverSequenceIndex() !== index) {
      this.dragOverSequenceIndex.set(index);
    }
  }

  onSequenceDragLeave(event: DragEvent, index: number): void {
    if (this.dragOverSequenceIndex() === index) {
      this.dragOverSequenceIndex.set(null);
    }
  }

  onSequenceDrop(event: DragEvent, dropIndex: number): void {
    event.preventDefault();
    const sourceIndex = this.draggedSequenceIndex();
    if (sourceIndex !== null && sourceIndex !== dropIndex) {
      const list = [...this.tempSequenceNodes()];
      if (sourceIndex >= 0 && sourceIndex < list.length && dropIndex >= 0 && dropIndex < list.length) {
        const [movedItem] = list.splice(sourceIndex, 1);
        list.splice(dropIndex, 0, movedItem);
        this.tempSequenceNodes.set(list);
      }
    }
    this.draggedSequenceIndex.set(null);
    this.dragOverSequenceIndex.set(null);
    this.isDraggingSequence.set(false);
  }

  onSequenceDragEnd(): void {
    this.draggedSequenceIndex.set(null);
    this.dragOverSequenceIndex.set(null);
    this.isDraggingSequence.set(false);
  }

  saveSequenceChanges(): void {
    let reordered = [...this.tempSequenceNodes()];
    if (this.syncDependenciesOnReorder() && reordered.length > 0) {
      reordered = reordered.map((node, idx) => {
        if (idx === 0) {
          return { ...node, dependsOn: [] };
        }
        return { ...node, dependsOn: [reordered[idx - 1].id] };
      });
    }

    this.pipelineNodes.set(reordered);
    this.isEditingSequence.set(false);
    this.tempSequenceNodes.set([]);
    this.draggedSequenceIndex.set(null);
    this.dragOverSequenceIndex.set(null);
    this.isDraggingSequence.set(false);
    this.pipelineToastMessage.set('Sequência de etapas do pipeline atualizada com sucesso!');
    setTimeout(() => this.pipelineToastMessage.set(null), 4000);
  }

  toggleNodeStatus(nodeId: string): void {
    this.pipelineNodes.update(nodes =>
      nodes.map(n => {
        if (n.id === nodeId) {
          const nextStatus: PipelineNodeStatus = n.status === 'passed' ? 'blocked' : (n.status === 'blocked' ? 'running' : 'passed');
          return { ...n, status: nextStatus };
        }
        return n;
      })
    );
  }

  toggleNodeAllowFailure(nodeId: string): void {
    this.pipelineNodes.update(nodes =>
      nodes.map(n => (n.id === nodeId ? { ...n, allowFailure: !n.allowFailure } : n))
    );
  }

  applyPipelineBlueprint(blueprintId: string): void {
    const bp = this.pipelineBlueprints.find(b => b.id === blueprintId);
    if (!bp) return;

    this.selectedPipelineBlueprint.set(blueprintId);
    this.pipelineTargetPlatform.set(bp.platform);
    this.pipelineNodes.set(JSON.parse(JSON.stringify(bp.nodes)));
    if (bp.nodes.length > 0) {
      this.selectedNodeId.set(bp.nodes[0].id);
    }
    this.pipelineToastMessage.set(`Template "${bp.name}" carregado no editor de fluxo!`);
    setTimeout(() => this.pipelineToastMessage.set(null), 4000);
  }

  setPipelineSubTab(tab: 'flowchart' | 'editor' | 'mermaid' | 'yaml' | 'simulator'): void {
    this.pipelineSubTab.set(tab);
  }

  setPipelineTargetPlatform(platform: 'github' | 'gitlab' | 'azure' | 'bitbucket'): void {
    this.pipelineTargetPlatform.set(platform);
  }

  setPipelineZoom(zoom: number): void {
    this.pipelineZoom.set(zoom);
  }

  zoomInPipeline(): void {
    this.pipelineZoom.update(z => Math.min(150, z + 15));
  }

  zoomOutPipeline(): void {
    this.pipelineZoom.update(z => Math.max(60, z - 15));
  }

  resetPipelineZoom(): void {
    this.pipelineZoom.set(100);
  }

  async runPipelineSimulation(delayMs: number = 300): Promise<void> {
    if (this.isPipelineSimulating()) return;

    this.isPipelineSimulating.set(true);
    this.pipelineSimulationProgress.set(0);
    this.pipelineSimulationLog.set(['[00:00.00] 🚀 Iniciando simulação de execução do pipeline...']);
    
    // Set all nodes to pending
    this.pipelineNodes.update(nodes => nodes.map(n => ({ ...n, status: 'pending' })));

    const nodes = this.pipelineNodes();
    const total = nodes.length;

    for (let i = 0; i < total; i++) {
      const node = nodes[i];
      this.pipelineSimulationActiveStep.set(node.name);
      
      this.pipelineNodes.update(curr =>
        curr.map(n => (n.id === node.id ? { ...n, status: 'running' } : n))
      );

      const progress = Math.round(((i + 0.5) / total) * 100);
      this.pipelineSimulationProgress.set(progress);
      this.pipelineSimulationLog.update(logs => [
        ...logs,
        `[00:0${i + 1}.20] ⏳ Executando etapa [${node.shortName}]: ${node.name} no runner (${node.runner})...`,
        `[00:0${i + 1}.35] $ ${node.command}`
      ]);

      if (delayMs > 0) {
        await new Promise(r => setTimeout(r, delayMs));
      }

      const isBlocked = node.type === 'quality_gate' && this.currentReport().p0Count > 0 && !node.allowFailure;
      const finalStatus: PipelineNodeStatus = isBlocked ? 'blocked' : 'passed';

      this.pipelineNodes.update(curr =>
        curr.map(n => (n.id === node.id ? { ...n, status: finalStatus } : n))
      );

      this.pipelineSimulationLog.update(logs => [
        ...logs,
        `[00:0${i + 1}.80] ${finalStatus === 'passed' ? '✅' : '❌'} Etapa [${node.shortName}] finalizada com status: ${finalStatus.toUpperCase()} (${node.duration})`
      ]);

      if (isBlocked) {
        this.pipelineSimulationLog.update(logs => [
          ...logs,
          `[00:0${i + 1}.90] 🚫 Pipeline interrompido devido a bloqueio arquitetural no Quality Gate!`
        ]);
        break;
      }
    }

    this.pipelineSimulationProgress.set(100);
    this.pipelineSimulationActiveStep.set(null);
    this.isPipelineSimulating.set(false);
    this.pipelineSimulationLog.update(logs => [
      ...logs,
      `[00:09.99] 🎉 Simulação concluída com sucesso! Telemetria gerada.`
    ]);
  }

  resetPipelineSimulation(): void {
    const bp = this.pipelineBlueprints.find(b => b.id === this.selectedPipelineBlueprint()) || this.pipelineBlueprints[0];
    this.pipelineNodes.set(JSON.parse(JSON.stringify(bp.nodes)));
    this.pipelineSimulationProgress.set(0);
    this.pipelineSimulationLog.set([]);
    this.pipelineSimulationActiveStep.set(null);
    this.isPipelineSimulating.set(false);
    this.pipelineToastMessage.set('Status de execução do pipeline restaurado.');
    setTimeout(() => this.pipelineToastMessage.set(null), 3000);
  }

  copyMermaidToClipboard(): void {
    if (typeof navigator !== 'undefined' && navigator.clipboard) {
      navigator.clipboard.writeText(this.generatedMermaidCode());
      this.pipelineToastMessage.set('Código do diagrama Mermaid copiado para a área de transferência!');
      setTimeout(() => this.pipelineToastMessage.set(null), 3000);
    }
  }

  copyYamlToClipboard(): void {
    if (typeof navigator !== 'undefined' && navigator.clipboard) {
      navigator.clipboard.writeText(this.generatedPipelineYaml());
      this.pipelineToastMessage.set(`Configuração YAML (${this.pipelineTargetPlatform().toUpperCase()}) copiada com sucesso!`);
      setTimeout(() => this.pipelineToastMessage.set(null), 3000);
    }
  }

  downloadPipelineYaml(): void {
    const yaml = this.generatedPipelineYaml();
    const platform = this.pipelineTargetPlatform();
    const filename = platform === 'github' ? 'guardian.yml' : (platform === 'gitlab' ? '.gitlab-ci.yml' : 'azure-pipelines.yml');
    const blob = new Blob([yaml], { type: 'text/yaml' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  }

  getNodeTypeIcon(type: PipelineNodeType): string {
    const icons: Record<PipelineNodeType, string> = {
      trigger: '⚡',
      checkout: '📥',
      lint: '🧹',
      security: '🔒',
      bend_analyzer: '🧬',
      test: '🧪',
      quality_gate: '🛡️',
      build: '📦',
      deploy: '🚀',
      sarif_export: '📊',
      notify: '📡',
      custom: '⚙️'
    };
    return icons[type] || '⚙️';
  }

  getNodeTypeColor(type: PipelineNodeType): { bg: string; text: string; border: string; badge: string } {
    const colors: Record<PipelineNodeType, { bg: string; text: string; border: string; badge: string }> = {
      trigger: { bg: 'bg-amber-500/10', text: 'text-amber-400', border: 'border-amber-500/30', badge: 'bg-amber-500/20 text-amber-300' },
      checkout: { bg: 'bg-blue-500/10', text: 'text-blue-400', border: 'border-blue-500/30', badge: 'bg-blue-500/20 text-blue-300' },
      lint: { bg: 'bg-slate-500/10', text: 'text-slate-300', border: 'border-slate-500/30', badge: 'bg-slate-500/20 text-slate-300' },
      security: { bg: 'bg-rose-500/10', text: 'text-rose-400', border: 'border-rose-500/30', badge: 'bg-rose-500/20 text-rose-300' },
      bend_analyzer: { bg: 'bg-purple-500/15', text: 'text-purple-300', border: 'border-purple-500/40 shadow-[0_0_15px_rgba(168,85,247,0.15)]', badge: 'bg-purple-500/20 text-purple-300' },
      test: { bg: 'bg-emerald-500/10', text: 'text-emerald-400', border: 'border-emerald-500/30', badge: 'bg-emerald-500/20 text-emerald-300' },
      quality_gate: { bg: 'bg-cyan-500/15', text: 'text-cyan-300', border: 'border-cyan-500/50 shadow-[0_0_20px_rgba(6,182,212,0.15)]', badge: 'bg-cyan-500/20 text-cyan-300' },
      build: { bg: 'bg-indigo-500/10', text: 'text-indigo-400', border: 'border-indigo-500/30', badge: 'bg-indigo-500/20 text-indigo-300' },
      deploy: { bg: 'bg-emerald-500/15', text: 'text-emerald-300', border: 'border-emerald-500/40', badge: 'bg-emerald-500/20 text-emerald-300' },
      sarif_export: { bg: 'bg-cyan-500/10', text: 'text-cyan-400', border: 'border-cyan-500/30', badge: 'bg-cyan-500/20 text-cyan-300' },
      notify: { bg: 'bg-purple-500/10', text: 'text-purple-400', border: 'border-purple-500/30', badge: 'bg-purple-500/20 text-purple-300' },
      custom: { bg: 'bg-slate-500/10', text: 'text-slate-400', border: 'border-slate-500/30', badge: 'bg-slate-500/20 text-slate-300' }
    };
    return colors[type] || colors.custom;
  }

  getNodeStatusBadgeClass(status: PipelineNodeStatus): string {
    switch (status) {
      case 'passed':
        return 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40';
      case 'blocked':
        return 'bg-rose-500/20 text-rose-300 border-rose-500/40';
      case 'running':
        return 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40 animate-pulse';
      case 'skipped':
        return 'bg-amber-500/20 text-amber-300 border-amber-500/40';
      case 'pending':
      default:
        return 'bg-slate-800 text-slate-400 border-slate-700';
    }
  }

  getNodeDependsOnNames(node: PipelineNode): string[] {
    const nodes = this.pipelineNodes();
    return (node.dependsOn || []).map(id => {
      const found = nodes.find(n => n.id === id);
      return found ? found.shortName : id;
    });
  }

  closePipelineToast(): void {
    this.pipelineToastMessage.set(null);
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

  openRuleDrawerById(ruleId: string): void {
    const found = this.rules().find(r => r.id === ruleId);
    if (found) {
      this.selectedRuleForDrawer.set(found);
    }
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

  // SETTINGS & BRANCH POLICIES METHODS
  setSettingsSubTab(tab: 'policies' | 'engine' | 'framework' | 'raw_json'): void {
    this.settingsSubTab.set(tab);
  }

  openAddPolicyModal(): void {
    this.newPolicyForm.set({
      id: `policy-${Date.now()}`,
      name: 'Custom Branch Policy',
      branchPattern: 'staging | release/*',
      minScore: 80,
      allowP0: false,
      allowP1: true,
      requireCleanBuild: true,
      requireCiApproval: true,
      blockOnPragmaWithoutReason: true,
      enabled: true,
      description: 'Enforces quality gates before merging into release branches.'
    });
    this.isAddingPolicy.set(true);
  }

  closeAddPolicyModal(): void {
    this.isAddingPolicy.set(false);
  }

  submitNewPolicy(): void {
    const policy = this.newPolicyForm();
    if (!policy.branchPattern.trim()) return;
    this.guardianService.addBranchPolicy(policy);
    this.isAddingPolicy.set(false);
    this.showSettingsToast('Nova Branch Policy adicionada com sucesso!');
  }

  deletePolicy(index: number): void {
    this.guardianService.removeBranchPolicy(index);
    this.showSettingsToast('Branch Policy removida.');
  }

  togglePolicy(index: number): void {
    this.guardianService.toggleBranchPolicy(index);
  }

  updatePolicyField<K extends keyof BranchPolicy>(index: number, key: K, value: BranchPolicy[K]): void {
    this.guardianService.updateBranchPolicy(index, { [key]: value });
  }

  updateEngineSettingField<K extends keyof GuardianEngineSettings>(key: K, value: GuardianEngineSettings[K]): void {
    this.guardianService.updateEngineSettings({ [key]: value });
  }

  saveEngineSettings(): void {
    this.showSettingsToast('Configurações do Guardian e Políticas de Branch salvas com sucesso!');
  }

  resetEngineSettingsToDefault(): void {
    this.guardianService.resetEngineSettingsToDefault();
    this.guardianService.resetBranchPoliciesToDefault();
    this.showSettingsToast('Configurações restauradas para os padrões recomendados.');
  }

  showSettingsToast(msg: string): void {
    this.settingsSavedToast.set(msg);
    setTimeout(() => {
      if (this.settingsSavedToast() === msg) {
        this.settingsSavedToast.set(null);
      }
    }, 4000);
  }

  closeSettingsToast(): void {
    this.settingsSavedToast.set(null);
  }

  exportSettingsJson(): string {
    return JSON.stringify({
      engineSettings: this.engineSettings(),
      branchPolicies: this.branchPolicies()
    }, null, 2);
  }

  importSettingsJson(jsonStr: string): boolean {
    try {
      const parsed = JSON.parse(jsonStr);
      if (parsed.engineSettings) {
        this.guardianService.updateEngineSettings(parsed.engineSettings);
      }
      if (Array.isArray(parsed.branchPolicies)) {
        this.guardianService.branchPolicies.set(parsed.branchPolicies);
      }
      this.showSettingsToast('Configurações importadas com sucesso via JSON.');
      return true;
    } catch (e) {
      this.showSettingsToast('Erro ao importar JSON de configurações.');
      return false;
    }
  }

  // FRAMEWORK DETECTION MODAL & CUSTOMIZATION
  async confirmFrameworkScan(): Promise<void> {
    const repo = this.pendingRepoForFrameworkScan() || this.selectedLocalRepo();
    const targetPath = repo?.path || this.selectedRepositoryPath() || this.customLocalPathInput() || 'ai-bend-devops';
    this.isScanningFramework.set(true);
    try {
      const result = await this.guardianService.detectRepositoryFramework(targetPath);
      this.lastFrameworkDetectionResult.set(result);
      const appSummary = this.guardianService.applyFrameworkProfileAndRules(result);
      this.selectedProfile.set(result.recommendedProfile);

      const activeIds = this.rules().filter(r => r.status === 'active' || r.enabled !== false).map(r => r.id);
      this.selectedCustomRuleIds.set(new Set(activeIds));

      this.frameworkToastMessage.set(appSummary.message);
      setTimeout(() => {
        if (this.frameworkToastMessage() === appSummary.message) {
          this.frameworkToastMessage.set(null);
        }
      }, 7000);
    } catch (e) {
      console.error('Framework detection error', e);
    } finally {
      this.isScanningFramework.set(false);
      this.showFrameworkDetectionModal.set(false);
      this.pendingRepoForFrameworkScan.set(null);
    }
  }

  cancelFrameworkScan(): void {
    this.showFrameworkDetectionModal.set(false);
    this.pendingRepoForFrameworkScan.set(null);
  }

  async triggerManualFrameworkScan(): Promise<void> {
    const repo = this.selectedLocalRepo();
    const repoIdOrPath = repo?.path || this.selectedRepositoryPath() || this.customLocalPathInput() || 'ai-bend-devops';
    this.isScanningFramework.set(true);
    try {
      const result = await this.guardianService.detectRepositoryFramework(repoIdOrPath);
      this.lastFrameworkDetectionResult.set(result);
      const appSummary = this.guardianService.applyFrameworkProfileAndRules(result);
      this.selectedProfile.set(result.recommendedProfile);

      const activeIds = this.rules().filter(r => r.status === 'active' || r.enabled !== false).map(r => r.id);
      this.selectedCustomRuleIds.set(new Set(activeIds));

      this.frameworkToastMessage.set(appSummary.message);
      setTimeout(() => {
        if (this.frameworkToastMessage() === appSummary.message) {
          this.frameworkToastMessage.set(null);
        }
      }, 7000);
    } catch (e) {
      console.error('Manual framework scan error', e);
    } finally {
      this.isScanningFramework.set(false);
    }
  }

  closeFrameworkToast(): void {
    this.frameworkToastMessage.set(null);
  }

  quickApplyFrameworkPreset(preset: 'dotnet' | 'angular' | 'fullstack' | 'python'): void {
    let mockResult: FrameworkDetectionResult;
    if (preset === 'dotnet') {
      mockResult = {
        valid: true,
        repositoryPath: this.localRepoPath() || '/project',
        detectedFrameworks: [{ name: '.NET 8 / C# Web API', category: 'backend', language: 'C#', version: '8.0', confidence: 1.0, indicators: ['Controllers/.NET 8 detected'] }],
        primaryFramework: '.NET 8 / C# Web API',
        recommendedProfile: 'clean_architecture',
        matchingRuleIds: ['CULT01', 'CULT02', 'CULT03', 'CULT04', 'CULT05', 'ARCH-LAYER-01', 'ARCH-LAYER-02', 'ARCH-LAYER-03', 'ARCH-LAYER-04', 'DOTNET-ASYNC-01'],
        disabledRuleIds: ['ARCH-FE-01'],
        suggestedTiers: ['Domain', 'Application', 'Infrastructure', 'Presentation'],
        summary: 'Perfil e regras ajustados para .NET 8 (CancellationToken e Clean Architecture ativados).'
      };
    } else if (preset === 'angular') {
      mockResult = {
        valid: true,
        repositoryPath: this.localRepoPath() || '/project',
        detectedFrameworks: [{ name: 'Angular / TypeScript SPA', category: 'frontend', language: 'TypeScript', version: '18.0', confidence: 1.0, indicators: ['angular.json detected'] }],
        primaryFramework: 'Angular / TypeScript SPA',
        recommendedProfile: 'frontend_clean',
        matchingRuleIds: ['CULT01', 'CULT02', 'CULT03', 'CULT04', 'CULT05', 'ARCH-FE-01', 'ARCH-LAYER-01'],
        disabledRuleIds: ['DOTNET-ASYNC-01'],
        suggestedTiers: ['Presentational UI', 'Container Components', 'State/Services', 'API Adapters'],
        summary: 'Perfil e regras ajustados para Angular / TypeScript (Pureza de componentes e tipagem estrita ativadas).'
      };
    } else if (preset === 'python') {
      mockResult = {
        valid: true,
        repositoryPath: this.localRepoPath() || '/project',
        detectedFrameworks: [{ name: 'Python (FastAPI / Backend)', category: 'backend', language: 'Python', version: '3.11+', confidence: 1.0, indicators: ['pyproject.toml detected'] }],
        primaryFramework: 'Python (FastAPI / Backend)',
        recommendedProfile: 'layered_mvc',
        matchingRuleIds: ['CULT01', 'CULT02', 'CULT03', 'CULT04', 'CULT05', 'ARCH-LAYER-01', 'ARCH-LAYER-02', 'ARCH-LAYER-03', 'ARCH-LAYER-04'],
        disabledRuleIds: ['DOTNET-ASYNC-01', 'ARCH-FE-01'],
        suggestedTiers: ['Model', 'Service', 'Controller', 'Infrastructure'],
        summary: 'Perfil e regras ajustados para Python Backend.'
      };
    } else {
      mockResult = {
        valid: true,
        repositoryPath: this.localRepoPath() || '/project',
        detectedFrameworks: [
          { name: '.NET 8 / C# Web API', category: 'backend', language: 'C#', version: '8.0', confidence: 0.98, indicators: ['C# Controllers'] },
          { name: 'Angular / TypeScript SPA', category: 'frontend', language: 'TypeScript', version: '18.0', confidence: 0.99, indicators: ['Angular components'] }
        ],
        primaryFramework: 'Full-Stack Enterprise (.NET 8 + Angular)',
        recommendedProfile: 'clean_architecture',
        matchingRuleIds: ['CULT01', 'CULT02', 'CULT03', 'CULT04', 'CULT05', 'ARCH-LAYER-01', 'ARCH-LAYER-02', 'ARCH-LAYER-03', 'ARCH-LAYER-04', 'DOTNET-ASYNC-01', 'ARCH-FE-01'],
        disabledRuleIds: [],
        suggestedTiers: ['Domain', 'Application', 'Infrastructure', 'Presentation'],
        summary: 'Perfil e regras ajustados para Full-Stack (.NET 8 + Angular).'
      };
    }

    const appSummary = this.guardianService.applyFrameworkProfileAndRules(mockResult);
    this.selectedProfile.set(mockResult.recommendedProfile);
    const activeIds = this.rules().filter(r => r.status === 'active' || r.enabled !== false).map(r => r.id);
    this.selectedCustomRuleIds.set(new Set(activeIds));
    this.showSettingsToast(appSummary.message);
  }
}

