# Architecture Profile: Clean & Hexagonal Architecture

---

## 1. Concentric Dependency Boundaries

```mermaid
flowchart TD
    subgraph Frameworks ["4. Frameworks & Infrastructure"]
        DB[("Database & ORM")]
        Web["Web Framework & UI"]
    end

    subgraph Adapters ["3. Interface Adapters"]
        Controllers["Controllers & Gateways"]
        Presenters["Presenters & ViewModels"]
    end

    subgraph Application ["2. Application Core"]
        UseCases["Use Cases & Handlers"]
        Ports["Output Ports (Interfaces)"]
    end

    subgraph Domain ["1. Enterprise Domain"]
        Entities["Domain Entities & Value Objects"]
    end

    Frameworks --> Adapters
    Adapters --> Application
    Application --> Domain

    Domain -. "❌ FORBIDDEN: Domain depending outward" .-> Frameworks
```

---

## 2. Invariant Rules
- **Dependency Rule**: Code dependencies point exclusively inward towards the Domain.
- **Port Inversion**: Infrastructure implements interfaces (Ports) declared in Application/Domain.
