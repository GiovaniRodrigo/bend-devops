# Architecture Profile: Microservices & Distributed Systems

This document formalizes the **Microservices Architecture Profile** within the 4-step pipeline:
`1. Architecture ➔ 2. Rules ➔ 3. Language ➔ 4. Scan`.

---

## 1. Architectural Topology & Service Boundaries

```mermaid
flowchart TD
    Client["Clients & Mobile Apps"] --> Ingress["API Gateway / Ingress"]

    subgraph ServiceA ["Order Service (Bounded Context A)"]
        OrderAPI["Order API & Handlers"]
        OrderApp["Order Saga & Services"]
        OrderDB[("Order DB (Isolated)")]
        OrderOutbox["Transactional Outbox"]
        OrderAPI --> OrderApp
        OrderApp --> OrderDB
        OrderApp --> OrderOutbox
    end

    subgraph ServiceB ["Inventory Service (Bounded Context B)"]
        InvAPI["Inventory Handlers"]
        InvApp["Inventory Services"]
        InvDB[("Inventory DB (Isolated)")]
        InvAPI --> InvApp
        InvApp --> InvDB
    end

    subgraph Broker ["Message Broker / Event Bus"]
        Kafka["Apache Kafka / RabbitMQ"]
    end

    Ingress -->|REST / gRPC| OrderAPI
    Ingress -->|REST / gRPC| InvAPI
    OrderOutbox -->|Async Events| Kafka
    Kafka -->|Subscribes to Events| InvAPI

    OrderApp -. "❌ FORBIDDEN: Direct Cross-DB Access" .-> InvDB
    InvApp -. "❌ FORBIDDEN: Direct Cross-DB Access" .-> OrderDB
```

---

## 2. Invariant Architectural Constraints

1. **Database-per-Service**: Services must never directly query or mutate another service's private database.
2. **Resilient Inter-Service Communication**: All synchronous inter-service calls must enforce strict timeouts, retries with exponential backoff, and circuit breakers.
3. **Dual-Write Consistency**: State mutations and associated published events must use the Transactional Outbox pattern or Saga orchestrators.
4. **Idempotent Message Processing**: Consumers must handle at-least-once message delivery without state corruption.
