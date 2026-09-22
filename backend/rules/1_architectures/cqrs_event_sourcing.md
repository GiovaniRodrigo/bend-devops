# Architecture Profile: CQRS & Event Sourcing

This document formalizes the **CQRS & Event Sourcing Architecture Profile** within the 4-step pipeline:
`1. Architecture ➔ 2. Rules ➔ 3. Language ➔ 4. Scan`.

---

## 1. Architectural Topology: Command & Query Segregation

```mermaid
flowchart TD
    Client["Client Application"]

    subgraph CommandPipeline ["Write / Command Pipeline"]
        Cmd["Command (e.g. PlaceOrder)"]
        CmdHandler["Command Handler"]
        Agg["Aggregate Root"]
        EventStore[("Immutable Event Store")]
        Cmd --> CmdHandler
        CmdHandler --> Agg
        Agg -->|Appends Events| EventStore
    end

    subgraph EventStream ["Asynchronous Event Stream"]
        EventBus["Event Publisher / Bus"]
        Projector["Projection Handlers"]
        EventStore -->|Stream Events| EventBus
        EventBus --> Projector
    end

    subgraph QueryPipeline ["Read / Query Pipeline"]
        ReadDB[("Read-Optimized Database")]
        Query["Query (e.g. GetOrderDetails)"]
        QueryHandler["Query Handler"]
        Projector -->|Updates Projections| ReadDB
        Query --> QueryHandler
        QueryHandler -->|Direct Query| ReadDB
    end

    Client -->|Writes| Cmd
    Client -->|Reads| Query

    QueryHandler -. "❌ FORBIDDEN: Mutations via Query" .-> EventStore
    CmdHandler -. "❌ FORBIDDEN: Direct Read DB Coupling" .-> ReadDB
```

---

## 2. Invariant Architectural Constraints

1. **Immutable Event Ledger**: Events appended to the Event Store must be strictly immutable and append-only.
2. **Side-Effect-Free Queries**: Query handlers must never mutate state or publish domain events.
3. **Optimistic Concurrency**: Aggregates must use expected version numbers to prevent conflicting concurrent writes.
