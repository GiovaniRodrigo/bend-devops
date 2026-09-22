# Engineering & Architecture Standards: Frontend Clean Architecture

This document establishes architectural boundaries and state management standards for **Frontend Applications (Angular, React, Vue, Vite)**.

---

## Component Hierarchy & Data Flow

```mermaid
flowchart TD
    subgraph ContainerLayer["Smart / Container Components & Pages"]
        Page["DashboardPage / UserContainer"]
        Service["State Service / TanStack Query / Signals"]
    end

    subgraph PresentationalLayer["Presentational / Dumb UI Components"]
        Card["MetricCard Component"]
        Table["DataTable Component"]
        Button["ActionButton Component"]
    end

    subgraph BackendAPI["Backend API Layer"]
        Endpoints["REST / GraphQL Endpoints"]
    end

    Page -->|Injects / Calls| Service
    Service -->|HTTP Requests| Endpoints
    Page -->|Passes Props / Signals Down| PresentationalLayer
    PresentationalLayer -->|Emits Events Up (onClick, onSelect)| Page

    PresentationalLayer -. "❌ FORBIDDEN: Direct HTTP / Fetch Call" .-> Endpoints
    PresentationalLayer -. "❌ FORBIDDEN: Direct State Mutation" .-> Service
```

---

## Rules Catalog

### `ARCH-FE-01` — Zero Direct API Calls in Presentational Components (P0 - Blocking)
- **Description:** Pure presentational/dumb components must never call `fetch()`, `axios`, or direct HTTP clients.
- **Rationale:** Preserves UI testability, Storybook isolation, and high visual reusability.
- **Remediation:** Lift network logic into Services or Smart Containers, passing pure data into presentational components.

### `ARCH-FE-02` — Strict State Immutability (P0 - Blocking)
- **Description:** Modifying state arrays or objects in-place is prohibited.
- **Rationale:** Prevents missed UI render cycles and difficult-to-debug state inconsistencies.
- **Remediation:** Use immutable updates (`[...state, item]`, `{...state, prop: value}`).

### `ARCH-FE-03` — No Deep Prop Drilling (P1 - Warning)
- **Description:** Limit passing props down through no more than two intermediate component layers.
- **Rationale:** Reduces boilerplate and avoids rigid component coupling.
- **Remediation:** Introduce state services, Context, or Signals.

### `ARCH-FE-04` — Mandatory Semantic HTML & Accessibility (P1 - Warning)
- **Description:** Use semantic elements (`<button>`, `<nav>`, `<main>`) and appropriate ARIA attributes for interactive controls.
- **Rationale:** Guarantees universal accessibility (a11y) and keyboard navigation.
- **Remediation:** Replace non-semantic clickable tags with native button/anchor elements.
