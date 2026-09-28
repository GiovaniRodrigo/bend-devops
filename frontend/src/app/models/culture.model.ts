export type ArchitecturalLayer = 
  | 'Domain'
  | 'Application'
  | 'Infrastructure'
  | 'Presentation'
  | 'Core'
  | 'Model'
  | 'Controller'
  | 'View'
  | 'Service'
  | 'Unknown';

export type SeverityLevel = 
  | 'P0_BLOCKING' 
  | 'P1_WARNING' 
  | 'P2_INFO' 
  | 'P0' 
  | 'P1' 
  | 'P2' 
  | 'P3' 
  | 'INFO';

export type VcsPlatform = 'github' | 'gitlab' | 'bitbucket' | 'local';

export interface LocalRepositoryInfo {
  id: string;
  name: string;
  path: string;
  selectedPath?: string;
  repositoryRoot?: string;
  isSubdirectory?: boolean;
  remoteUrl: string;
  currentBranch: string;
  branches: string[];
  headCommit: string;
  headCommitMessage?: string;
  isClean: boolean;
  isCurrent?: boolean;
}

export interface LocalRepositoryValidationResult {
  valid: boolean;
  selectedPath?: string;
  isSubdirectory?: boolean;
  repositoryRoot?: string;
  errorType?: 'EMPTY_PATH' | 'NOT_FOUND' | 'NOT_DIR' | 'NOT_GIT' | 'GIT_UNAVAILABLE' | 'GIT_ERROR' | string;
  repository?: LocalRepositoryInfo;
  error?: string;
}

export interface DirectoryItem {
  name: string;
  path: string;
  isGit: boolean;
  gitInfo?: {
    branch: string;
    headCommit: string;
    isClean: boolean;
  };
}

export interface DirectoryBrowseResult {
  currentPath: string;
  parentPath: string | null;
  isCurrentPathGit: boolean;
  directories: DirectoryItem[];
}

export interface GitHubRepositoryInfo {
  id: string;
  name: string;
  fullName: string;
  owner: string;
  defaultBranch: string;
  url: string;
}

export interface WorkingTreeInfo {
  isClean: boolean;
  changedFiles: {
    name: string;
    status: 'modified' | 'added' | 'deleted' | 'untracked';
    additions: number;
    deletions: number;
  }[];
  totalAdditions: number;
  totalDeletions: number;
  diff: string;
  error?: string;
}

export interface CommitValidationResult {
  valid: boolean;
  sha?: string;
  shortSha?: string;
  author?: string;
  date?: string;
  message?: string;
  error?: string;
}

export type ArchitectureProfileId = 
  | 'clean_architecture'
  | 'layered_mvc'
  | 'domain_driven_design'
  | 'hexagonal'
  | 'microservices'
  | 'cqrs_event_sourcing'
  | 'rest_api'
  | 'frontend_clean';

export interface ArchitectureProfile {
  id: ArchitectureProfileId;
  name: string;
  category: string;
  description: string;
  enabled?: boolean;
  tiers: {
    name: string;
    description: string;
    allowedDependencies: string[];
    forbiddenDependencies: string[];
  }[];
}

export type RuleType = 
  | 'pattern'
  | 'naming'
  | 'dependency'
  | 'architecture'
  | 'file_folder'
  | 'ast'
  | 'language_specific';

export type RuleSeverityLevel = 
  | 'P0' 
  | 'P1' 
  | 'P2' 
  | 'P3' 
  | 'INFO' 
  | 'P0_BLOCKING' 
  | 'P1_WARNING' 
  | 'P2_INFO';

export type RuleStatus = 
  | 'DRAFT' 
  | 'TESTING' 
  | 'VALIDATED' 
  | 'ACTIVE' 
  | 'DEPRECATED' 
  | 'ARCHIVED';

export type RuleTier = 
  | 'builtin' 
  | 'organization' 
  | 'project' 
  | 'custom';

export interface RuleScopeConfig {
  include: string[];
  exclude: string[];
  target_layer?: string;
}

export interface RuleConditionConfig {
  pattern?: string;
  patterns?: string[];
  naming_convention?: 'PascalCase' | 'camelCase' | 'snake_case' | 'kebab-case' | 'UPPER_CASE' | string;
  source_layer?: string;
  forbidden_layer?: string;
  forbidden_targets?: string[];
  required_path_prefix?: string;
  ast_selector?: string;
}

export interface RuleSuppressionConfig {
  allowed: boolean;
  pragma: string;
  requires_reason: boolean;
  minimum_reason_length: number;
}

export interface RuleTestFixture {
  name: string;
  input: string;
  expected_violation: boolean;
  expected_line?: number;
  expected_message?: string;
}

export interface RuleModel {
  id: string;
  name: string;
  category: string;
  severity: SeverityLevel;
  penaltyPoints: number;
  penalty_points?: number;
  description: string;
  rationale?: string;
  remediation?: string;
  languages: string[];
  status: RuleStatus | 'active' | 'inactive';
  version?: string;
  type?: RuleType;
  enabled?: boolean;
  tier?: RuleTier;
  layer?: string;
  architectures?: string[];
  scope?: RuleScopeConfig;
  condition?: RuleConditionConfig;
  message?: string;
  suggestion?: string;
  suppression?: RuleSuppressionConfig;
  tests?: RuleTestFixture[];
  metadata?: {
    author?: string;
    created_at?: string;
    updated_at?: string;
    executions_count?: number;
    violations_count?: number;
  };
}

export interface CultureRule extends RuleModel {}

export interface RuleTestResult {
  ruleId: string;
  passed: boolean;
  hasViolation: boolean;
  isSuppressed: boolean;
  suppressionReason?: string | null;
  matchedLines: number[];
  violations: {
    ruleId: string;
    fileName?: string;
    severity: string;
    penalty: number;
    line?: number;
    snippet?: string;
    message: string;
    suggestion?: string;
    remediation?: string;
  }[];
  error?: string | null;
  durationMs: number;
}

export interface RuleAuditTrailEntry {
  timestamp: string;
  action: string;
  actor: string;
  ruleId: string;
  version: string;
  details?: Record<string, any>;
}

export interface LayerVocabularyItem {
  layer: ArchitecturalLayer;
  description: string;
  keywords: string[];
  forbiddenInOtherLayers: string[];
  languages: Record<string, string[]>;
}

export interface CodeViolation {
  ruleId: string;
  fileName: string;
  severity: SeverityLevel;
  penalty: number;
  line?: number;
  message: string;
  author?: string;
  astNode?: string;
  snippet?: string;
  remediation?: string;
  isSuppressed?: boolean;
  suppressionReason?: string;
}

export interface FileAuditInfo {
  name: string;
  linesCount: number;
  language: string;
  identifiedLayer: ArchitecturalLayer;
  hasSpecTag: boolean;
  hasLazyCode: boolean;
  hasSecrets: boolean;
  hasTestCoverage: boolean;
  hasTypeAnnotations: boolean;
  violations: CodeViolation[];
  activeSuppressions: number;
}

export interface AuditReport {
  totalFiles: number;
  totalViolations: number;
  p0Count: number;
  p1Count: number;
  p2Count: number;
  totalPenalty: number;
  activeSuppressionsCount: number;
  score: number;
  isApproved: boolean;
  files: FileAuditInfo[];
  timestamp: string;
}

export interface AnalysisRun {
  id: string;
  date: string;
  project: string;
  mrTitle: string;
  author: string;
  targetBranch: string;
  platform: VcsPlatform;
  issues: number;
  p0Count: number;
  p1Count: number;
  status: 'Full compliance' | 'Completed' | 'Blocked';
  duration: string;
  violations: CodeViolation[];
  score: number;
  suppressionsCount: number;
}

export interface WebhookEventPayload {
  platform: VcsPlatform;
  eventType: string;
  repo: string;
  branch: string;
  commitSha: string;
  prId?: string;
  prTitle?: string;
  author: string;
  diffSummary?: string;
}

export interface GuardianEngineSettings {
  strictQualityGate: boolean;
  minGlobalPassingScore: number;
  maxP0BlockingThreshold: number;
  maxP1WarningsThreshold: number;
  autoRollbackOnFailure: boolean;
  hvmWorkerThreads: number;
  hvmReductionMode: 'high_performance' | 'balanced' | 'deep_verification';
  strictFrameworkEnforcement: boolean;
  autoScanFrameworkOnRepoSelect: boolean;
  requireSuppressionReason: boolean;
  minSuppressionReasonLength: number;
  notificationWebhookUrl: string;
  includeBuildDirsDefault: boolean;
}

export interface DetectedFrameworkItem {
  name: string;
  category: 'backend' | 'frontend' | 'fullstack' | 'database' | 'system';
  language: string;
  version?: string;
  confidence: number;
  indicators: string[];
}

export interface FrameworkDetectionResult {
  valid: boolean;
  repositoryId?: string;
  repositoryPath: string;
  detectedFrameworks: DetectedFrameworkItem[];
  primaryFramework: string;
  recommendedProfile: ArchitectureProfileId;
  matchingRuleIds: string[];
  disabledRuleIds: string[];
  suggestedTiers: string[];
  summary: string;
  error?: string;
}

export interface FrameworkApplicationSummary {
  appliedProfile: ArchitectureProfileId;
  activatedRulesCount: number;
  deactivatedRulesCount: number;
  activatedRuleIds: string[];
  message: string;
}

export interface BranchPolicy {
  id?: string;
  name?: string;
  branchPattern: string;
  minScore: number;
  allowP0: boolean;
  allowP1: boolean;
  requireCleanBuild?: boolean;
  requireCiApproval?: boolean;
  blockOnPragmaWithoutReason?: boolean;
  enabled?: boolean;
  description: string;
}

export type DiffViewMode = 'split' | 'unified' | 'original' | 'corrected';

export interface DiffLine {
  type: 'same' | 'added' | 'removed';
  beforeLineNumber?: number;
  afterLineNumber?: number;
  content: string;
  ruleId?: string;
}

export interface SplitDiffItem {
  lineNumber?: number;
  content: string;
  type: 'same' | 'added' | 'removed' | 'empty';
  ruleId?: string;
  highlight?: boolean;
}

export interface DiffExplanation {
  ruleId: string;
  title: string;
  description: string;
  remediation: string;
  severity: SeverityLevel;
}

export interface CodeDiff {
  filePath: string;
  before: string;
  after: string;
  additions: number;
  deletions: number;
  modifiedSections: number;
  affectedRules: string[];
  lines: DiffLine[];
  splitBefore: SplitDiffItem[];
  splitAfter: SplitDiffItem[];
  isIdentical: boolean;
  explanations: DiffExplanation[];
}

