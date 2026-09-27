# Interfaces e Tipos: Escopo e Regras Arquiteturais do Usuário

---

## Tipos TypeScript (Frontend)

```typescript
export type ScopeMode = 'full_branch' | 'working_tree_diff' | 'subdirectory' | 'single_file';

export interface RepositoryScopeConfig {
  id?: string;
  repositoryId: string;
  scopeMode: ScopeMode;
  targetPath?: string | null;
  branch: string;
  includePatterns?: string[];
  excludePatterns?: string[];
}

export interface RuleSelectionItem {
  ruleId: string;
  enabled: boolean;
  customSeverity?: 'P0_BLOCKING' | 'P1_WARNING' | 'P2_INFO' | null;
  category?: string;
}

export interface CustomEvaluationRequest {
  repositoryPath: string;
  scope: RepositoryScopeConfig;
  rules: RuleSelectionItem[];
  triggeredBy?: 'user' | 'cli' | 'webhook';
}

export interface ScopeEvaluationReport {
  reportId: string;
  timestamp: string;
  score: number;
  isApproved: boolean;
  scope: {
    mode: ScopeMode;
    targetPath?: string;
    filesEvaluatedCount: number;
  };
  totalViolations: number;
  violations: Array<{
    ruleId: string;
    filePath: string;
    lineNumber: number;
    severity: string;
    message: string;
    snippet?: string;
    suggestion?: string;
  }>;
}
```

---

## Tipos Python (Backend / Scripts)

```python
from dataclasses import dataclass
from typing import List, Optional, Literal

ScopeMode = Literal['full_branch', 'working_tree_diff', 'subdirectory', 'single_file']

@dataclass
class RepositoryScopeConfig:
    repository_id: str
    scope_mode: ScopeMode
    branch: str = 'main'
    target_path: Optional[str] = None
    include_patterns: Optional[List[str]] = None
    exclude_patterns: Optional[List[str]] = None

@dataclass
class RuleSelectionItem:
    rule_id: str
    enabled: bool = True
    custom_severity: Optional[str] = None
    category: Optional[str] = None

@dataclass
class CustomEvaluationRequest:
    repository_path: str
    scope: RepositoryScopeConfig
    rules: List[RuleSelectionItem]
    triggered_by: str = 'user'
```
