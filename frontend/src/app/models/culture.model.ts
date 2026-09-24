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

export type SeverityLevel = 'P0_BLOCKING' | 'P1_WARNING' | 'P2_INFO';

export type VcsPlatform = 'github' | 'gitlab' | 'bitbucket' | 'local';

export interface LocalRepositoryInfo {
  id: string;
  name: string;
  path: string;
  remoteUrl: string;
  currentBranch: string;
  branches: string[];
  headCommit: string;
  headCommitMessage?: string;
  isClean: boolean;
  isCurrent?: boolean;
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
  tiers: {
    name: string;
    description: string;
    allowedDependencies: string[];
    forbiddenDependencies: string[];
  }[];
}

export interface CultureRule {
  id: string;
  name: string;
  category: 'Culture & Quality' | 'Architecture - Layer Boundaries' | 'Language Adapter' | 'Security';
  severity: SeverityLevel;
  penaltyPoints: number;
  description: string;
  rationale: string;
  remediation: string;
  layer?: string;
  languages: string[];
  status: 'active' | 'inactive';
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

export interface BranchPolicy {
  branchPattern: string;
  minScore: number;
  allowP0: boolean;
  allowP1: boolean;
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

