export type ArchitecturalLayer = 
  | 'Model'
  | 'Controller'
  | 'View'
  | 'Service'
  | 'DomainEntity'
  | 'RequestValidator'
  | 'Infrastructure'
  | 'PresentationalUI'
  | 'Unknown';

export type SeverityLevel = 'P0_BLOCKING' | 'P1_WARNING' | 'P2_INFO';

export interface CultureRule {
  id: string;
  name: string;
  category: string;
  severity: SeverityLevel;
  penaltyPoints: number;
  description: string;
  rationale: string;
  remediation: string;
  languages: string[];
  status: 'active' | 'inactive';
}

export interface LayerRule {
  id: string;
  name: string;
  category: string;
  layer?: string;
  severity: SeverityLevel;
  penaltyPoints: number;
  description: string;
  rationale: string;
  remediation: string;
  detectionPatterns?: string[];
  forbiddenTargets?: string[];
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
}

export interface LayerViolation {
  ruleId: string;
  fileName: string;
  identifiedLayer: ArchitecturalLayer;
  severity: SeverityLevel;
  penalty: number;
  line?: number;
  snippet?: string;
  message: string;
  remediation?: string;
}

export interface FileAuditInfo {
  name: string;
  linesCount: number;
  hasSpecTag: boolean;
  hasLazyCode: boolean;
  hasSecrets: boolean;
  hasTestCoverage: boolean;
  hasTypeAnnotations: boolean;
  violations: CodeViolation[];
}

export interface AuditReport {
  totalFiles: number;
  totalViolations: number;
  p0Count: number;
  p1Count: number;
  p2Count: number;
  totalPenalty: number;
  score: number;
  isApproved: boolean;
  files: FileAuditInfo[];
}

export interface ConsolidatedArchitectureReport {
  totalFiles: number;
  totalViolations: number;
  p0Count: number;
  p1Count: number;
  p2Count: number;
  penaltyTotal: number;
  architectureScore: number;
  isApproved: boolean;
  auditedFiles: LayerViolation[];
}

export interface AnalysisRun {
  id: string;
  date: string;
  project: string;
  mrTitle: string;
  author: string;
  targetBranch: string;
  issues: number;
  status: 'Completed' | 'Full compliance' | 'Blocked';
  duration: string;
  violations: CodeViolation[];
  score: number;
}
