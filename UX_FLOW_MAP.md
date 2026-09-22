# UX_FLOW_MAP.md: User Journeys & Interaction Flow Maps

**Project**: Bend DevOps Guardian (CodeConform Dashboard)  
**Audit Date**: 2026-09-22  
**Design System**: shadcn/ui Developer Theme with Dark Slate Palette  

---

## 1. Primary User Journeys

### Journey 1: Live Code Quality & Architecture Audit
```mermaid
flowchart TD
    A[Engineer opens 'Live Code & Diff Auditor' Tab] --> B[Selects Code Preset or Pastes Source / Unified Diff]
    B --> C[Selects Architecture Profile e.g. Clean Architecture]
    C --> D[Selects Target Branch Policy e.g. main vs feature]
    D --> E[Clicks 'Execute Audit & Generate Quality Gate Report']
    E --> F[Bend Parallel Evaluation executes in &lt;50ms]
    F --> G[Navigation automatically transitions to 'Audit Results']
    G --> H{Violations Detected?}
    H -- Zero Violations --> I[Displays Emerald '100% Compliant' Banner & 100/100 Score]
    H -- Has Violations --> J[Displays Red/Amber Breakdown with Code Snippets & Remediation Tips]
    J --> K[Engineer clicks 'SARIF Export' or 'Markdown Summary' to share with team]
```

### Journey 2: Rules Catalog & Taxonomy Exploration
```mermaid
flowchart TD
    A[Architect opens 'Rules Manifests' Tab] --> B[Searches rule by keyword or filters by severity]
    B --> C[Inspects Rule Rationale, Penalty Points, and Remediation Example]
    C --> D[Clicks 'Enforced / Disabled' Toggle Pill]
    D --> E[Service updates signal state and triggers immediate score recalculation]
    E --> F[Architect switches to 'Layer Taxonomy' to inspect forbidden boundaries across 7 languages]
```

### Journey 3: Multi-Platform VCS & Webhook Simulation
```mermaid
flowchart TD
    A[DevOps Lead opens 'VCS & Webhook Simulator' Tab] --> B[Selects Platform: GitHub, GitLab, or Bitbucket]
    B --> C[Configures Event Type & Target Branch]
    C --> D[Clicks 'Dispatch Webhook Event']
    D --> E[Gateway parses payload into standard WebhookEvent and evaluates Branch Policy]
    E --> F[Displays deterministic verification result and gating recommendation]
```

---

## 2. UX States Enforced Across Views

- **Initial State**: Clean, readable default inputs with pre-configured compliant/non-compliant presets.
- **Loading / Busy State**: Smooth signal transitions without layout shifting.
- **Success State**: Emerald badge pills, high-contrast compliance scores, and clear pass indicators.
- **Error / Blocked State**: High-visibility rose alerts, clear violation explanations, line numbers, and copyable remediation guidance.
- **Empty State**: Contextual explanations with clear call-to-action buttons.
- **Accessibility & Responsiveness**: Semantic HTML5 tags, ARIA labels, full keyboard focus support, and mobile/tablet collapsible layouts.
