# Engineering & Architecture Standards: REST API Design & Contracts

This document establishes engineering conventions for all **RESTful APIs, endpoints, and HTTP contracts** audited in the repository.

---

## REST API Request/Response Lifecycle

```mermaid
flowchart TD
    Client["HTTP Client (Web / Mobile / Third-Party)"] -->|1. Request with Version (/api/v1/...)| Gateway["API Gateway / Routing"]
    Gateway -->|2. Authentication & Rate Limiting| Controller["API Controller"]
    Controller -->|3. Validate Payload (DTO / FormRequest)| Handler["Application Service"]
    
    Handler -->|4. Process Domain Logic| DB[("Database")]
    
    Controller -->|5a. Success (200, 201, 204) + Pagination| Client
    Controller -->|5b. Error (400, 422, 500) + RFC 7807 Envelope| Client
```

---

## Rules Catalog

### `ARCH-API-01` — Mandatory Collection Pagination (P0 - Blocking)
- **Description:** Any endpoint returning collections (e.g. `/api/v1/customers`) must require limit/cursor pagination and impose a hard upper bound (e.g. maximum 100 items).
- **Rationale:** Prevents unbounded memory growth, database thread lockups, and Denial of Service incidents.
- **Remediation:** Enforce pagination query parameters on all list endpoints.

### `ARCH-API-02` — Explicit API Versioning (P1 - Warning)
- **Description:** Route paths must include a clear version segment (e.g. `/api/v1/`).
- **Rationale:** Ensures clean contract lifecycle management and non-breaking changes for clients.
- **Remediation:** Group routes under explicit version prefixes.

### `ARCH-API-03` — Standardized Error Envelope (RFC 7807) (P1 - Warning)
- **Description:** All error responses must comply with the `application/problem+json` structure (`type`, `title`, `status`, `detail`, `instance`).
- **Rationale:** Standardizes automated client parsing and structured error reporting.
- **Remediation:** Implement global exception filters formatting responses to RFC 7807.

### `ARCH-API-04` — Strict HTTP Status Code Semantics (P0 - Blocking)
- **Description:** Never return HTTP 200 OK when an error or exception has occurred.
- **Rationale:** Prevents cache corruption in reverse proxies and ensures correct alerting in monitoring tools.
- **Remediation:** Match error states with accurate status codes (400, 401, 403, 404, 422, 500).

### `ARCH-API-05` — Idempotent Mutation Verbs (PUT & DELETE) (P0 - Blocking)
- **Description:** Retrying PUT or DELETE requests must not produce differing side-effects or duplicated states.
- **Rationale:** Protects against erratic network retries and transient timeouts.
- **Remediation:** Structure PUT and DELETE operations deterministically by resource identifier.
