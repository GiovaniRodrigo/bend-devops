# Interfaces e Tipos: Pipeline Flow, Architecture Profiles, Split Diff & Coverage

Este documento documenta as interfaces TypeScript e estruturas de dados utilizadas no frontend Angular (`frontend/src/app/`) e backend Python (`scripts/`).

---

## 1. Interfaces TypeScript

### `PipelineStageConfig`
```typescript
export interface PipelineStageConfig {
  id: string;
  name: string;
  description: string;
  command: string;
  environment: 'local' | 'cloud' | 'both';
  enabled: boolean;
  order: number;
}
```

### `ArchitectureProfile`
```typescript
export interface ArchitectureProfile {
  id: string;
  name: string;
  description: string;
  category: string;
  enabled: boolean;
  isDefault?: boolean;
  allowedDependencies: string[];
  forbiddenDependencies: string[];
  ruleIds?: string[];
}
```

### `SplitDiffLine` & `CodeDiff`
```typescript
export interface SplitDiffLine {
  lineNumber?: number;
  content: string;
  type: 'unchanged' | 'added' | 'removed' | 'empty';
  highlight?: boolean;
}

export interface CodeDiff {
  fileName: string;
  before: string;
  after: string;
  lines: DiffLine[];
  splitBefore: SplitDiffLine[];
  splitAfter: SplitDiffLine[];
  explanations: DiffExplanation[];
}

export interface DiffExplanation {
  ruleId: string;
  severity: string;
  message: string;
  remediation: string;
}
```

---

## 2. Tipos de Visualização de Diff

```typescript
export type DiffViewMode = 'split' | 'unified' | 'original' | 'corrected';
export type AuditScope = 'branch_analysis' | 'single_file';
export type CodeSourceMode = 'local' | 'cloud';
```
