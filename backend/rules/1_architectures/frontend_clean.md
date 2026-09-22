# Architecture Profile: Frontend Clean Architecture

This document formalizes the **Frontend Clean Architecture Profile** within the 4-step pipeline:
`1. Architecture ➔ 2. Rules ➔ 3. Language ➔ 4. Scan`.

---

## 1. Architectural Topology: Component Tiering

```mermaid
flowchart TD
    subgraph PresentationTier ["1. Presentational UI (Dumb Components)"]
        Buttons["Button, Modal, Table, Card"]
        Typography["Heading, Paragraph, Badge"]
    end

    subgraph ContainerTier ["2. Smart Containers & Pages"]
        Pages["UserDashboardPage, CheckoutView"]
    end

    subgraph StateTier ["3. State Management & Hooks"]
        Hooks["useUserAuth(), useShoppingCart()"]
        Store["NgRx / Redux / Pinia / Signals Store"]
    end

    subgraph InfrastructureTier ["4. API Clients & Gateways"]
        ApiClient["UserHttpGateway, OrderService"]
    end

    Pages --> PresentationTier
    Pages --> Hooks
    Hooks --> Store
    Hooks --> ApiClient
    ApiClient -->|HTTP| BackendAPI[("Backend API")]

    PresentationTier -. "❌ FORBIDDEN: Direct API Fetch" .-> ApiClient
    PresentationTier -. "❌ FORBIDDEN: Direct Store Dispatch" .-> Store
```

---

## 2. Invariant Architectural Constraints

1. **Pure Presentational Components**: UI components under `components/ui/` must receive data via props/inputs and emit events via callbacks; zero direct API calls.
2. **Encapsulated Network Calls**: API calls must be wrapped in gateway services or custom hooks.
3. **Immutable State**: State mutations must be immutable.
