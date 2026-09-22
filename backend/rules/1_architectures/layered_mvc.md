# Architecture Profile: Layered & MVC Architecture

This document formalizes the **Layered & MVC Architecture Profile** within the 4-step pipeline:
`1. Architecture ➔ 2. Rules ➔ 3. Language ➔ 4. Scan`.

---

## 1. Architectural Layers & Topologies

```mermaid
flowchart TD
    subgraph PresentationTier ["1. Presentation Tier"]
        Views["Views & Templates (Razor / Blade / Jinja / JSX)"]
    end

    subgraph InterfaceTier ["2. Interface & Transport Tier"]
        Controllers["Controllers & Request Handlers"]
    end

    subgraph ApplicationTier ["3. Application Tier"]
        Services["Application Services & Use Cases"]
    end

    subgraph DomainTier ["4. Domain Tier (Core)"]
        Models["Domain Models & Entities"]
    end

    subgraph InfrastructureTier ["5. Infrastructure Tier"]
        Database[("Database")]
        Repositories["Repository Implementations"]
    end

    PresentationTier -->|HTTP / Action Request| InterfaceTier
    InterfaceTier -->|Delegates execution| ApplicationTier
    ApplicationTier --> Models
    ApplicationTier --> Repositories
    Repositories --> Database
    InterfaceTier -->|Returns ViewModel / DTO| PresentationTier

    Views -. "❌ FORBIDDEN: Direct DB Query" .-> Database
    Models -. "❌ FORBIDDEN: UI Markup in Model" .-> PresentationTier
    Controllers -. "❌ FORBIDDEN: Raw HTML in Controller" .-> PresentationTier
```

---

## 2. Invariant Layer Constraints

1. **Presentation Isolation**: UI templates must only render data received via ViewModels/DTOs; direct DB calls are prohibited.
2. **Domain Purity**: Domain models must never contain HTML, client scripts, or transport context (`HttpContext`, `request()`).
3. **Thin Controllers**: Controllers orchestrate input/output without holding business logic.
