# Engineering & Architecture Standards: Zero-Trust Security Architecture

This document establishes foundational rules for **Zero-Trust Security, Defense-in-Depth, and Cryptographic Hygiene**.

---

## Zero-Trust Verification Architecture

```mermaid
flowchart TD
    Client["Client / External Service"] -->|1. HTTPS + JWT / OAuth2| Gateway["Edge API Gateway"]
    Gateway -->|2. Verify Token & Rate Limit| Gateway
    Gateway -->|3. Forward with Signed Context + mTLS| InternalService["Internal Service"]
    
    InternalService -->|4. Re-verify Claims & Permissions (RBAC/ABAC)| AuthGuard["Authorization Guard"]
    AuthGuard -->|5. Authorized| Logic["Domain Logic Execution"]
    AuthGuard -->|6. Unauthorized| Reject["403 Forbidden Response"]
    
    Logic -->|7. Emit Immutable Audit Event| AuditLog[("Audit Log Stream")]
    Logic -->|8. Query / Mutate (Parameterized Queries)| DB[("Secure Data Store")]
```

---

## Rules Catalog

### `ARCH-SEC-01` — Zero-Trust Perimeter Verification (P0 - Blocking)
- **Description:** Never trust private or internal networks implicitly. Every inter-service endpoint must validate incoming caller identity and authorization scopes.
- **Rationale:** Protects against internal lateral movement if a perimeter container or pod is breached.
- **Remediation:** Enforce mTLS and JWT authorization checks on all internal service controllers.

### `ARCH-SEC-02` — Mandatory Input Validation & Stripping (P0 - Blocking)
- **Description:** Strip unknown payload fields and validate types strictly against explicit DTO schemas prior to domain invocation.
- **Rationale:** Prevents mass-assignment vulnerabilities, prototype pollution, and injection attacks.
- **Remediation:** Apply schema validation middleware (Zod, Class-Validator, FluentValidation).

### `ARCH-SEC-03` — Audit Logging for All Mutation Operations (P1 - Warning)
- **Description:** All data-modifying actions must produce an immutable audit log record.
- **Rationale:** Crucial for incident response, forensic auditing, and compliance certifications.
- **Remediation:** Publish audit log events upon committing entity mutations.

### `ARCH-SEC-04` — No Insecure Cryptographic Primitives (P0 - Blocking)
- **Description:** Using MD5, SHA1, DES, RC4, or Math.random() for security tokens or password hashing is strictly prohibited.
- **Rationale:** Weak cryptography leaves data vulnerable to collision and brute-force attacks.
- **Remediation:** Utilize Argon2id, bcrypt, AES-256-GCM, and CSPRNG primitives.
