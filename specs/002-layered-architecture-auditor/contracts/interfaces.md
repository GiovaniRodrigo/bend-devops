# Interfaces & Contracts: Layered Architecture Validator

This document defines code contracts, TypeScript interfaces, and Bend algebraic types for the layered architecture validator.

---

## 1. TypeScript Interfaces (`frontend/src/app/models/culture.model.ts`)

```typescript
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
```

---

## 2. Bend Algebraic Types (`backend/src/guardian.bend`)

```bend
type TargetFile:
  TargetFile {
    name,
    lines_count,
    has_spec_tag,
    has_lazy_code,
    has_secrets,
    has_test_coverage,
    has_type_annotations
  }

type Violation:
  Violation {
    rule_id,
    file_name,
    severity,
    penalty,
    message
  }
```
