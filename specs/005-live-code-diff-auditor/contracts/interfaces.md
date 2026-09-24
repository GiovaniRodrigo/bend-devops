# Interfaces: Live Code & Diff Auditor

Formal interface contracts between the Interface Adapters, Application Layer, and Frontend Presentation.

---

## 1. TypeScript Interfaces (`frontend/src/app/`)

```typescript
export type AuditScope = 'branch_analysis' | 'single_file';

export type DiffViewMode = 'split' | 'unified' | 'original' | 'corrected';

export type FileStatus = 'modified' | 'added' | 'deleted' | 'renamed';

export interface DiffLine {
  lineNum: number | null;
  content: string;
  type: 'addition' | 'deletion' | 'context' | 'header' | 'empty';
  isViolation?: boolean;
  violationCode?: string;
  violationMessage?: string;
  remediation?: string;
}

export interface FileDiff {
  oldPath?: string;
  newPath: string;
  status: FileStatus;
  additions: number;
  deletions: number;
  changedLines: number[];
  violationsCount: number;
  blockingViolationsCount: number;
  layerProfile: string;
  originalCode: string;
  correctedCode: string;
}

export interface BranchSummary {
  currentBranch: string;
  baseBranch: string;
  filesChanged: number;
  additions: number;
  deletions: number;
  complianceScore: number;
  verdict: 'APPROVED' | 'BLOCKED' | 'WARNING';
  blockingViolations: number;
  warningViolations: number;
  files: FileDiff[];
}
```

---

## 2. Python Backend Data Classes (`scripts/vcs_adapters/diff_parser.py`)

```python
from dataclasses import dataclass, field
from typing import List, Set, Optional

@dataclass
class ParsedDiffFile:
    new_path: str
    old_path: Optional[str] = None
    status: str = "modified"  # 'modified', 'added', 'deleted', 'renamed'
    changed_lines: Set[int] = field(default_factory=set)
    additions_count: int = 0
    deletions_count: int = 0
```
