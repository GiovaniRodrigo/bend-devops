# 📜 Engineering Standards, Architecture Rules & Suppression Pragmas

This catalog details all active quality gate rules, severities, penalty calculations, and inline suppression mechanisms in the **Bend DevOps Guardian**.

---

## 🏛️ 1. Engineering Culture & Standards (`CULT01` - `CULT05`)

| Rule ID | Name | Severity | Penalty | Description & Rationale |
| :--- | :--- | :--- | :---: | :--- |
| **`CULT01`** | **Zero Lazy Code & Complete Implementation** | `P0_BLOCKING` | 35 pts | Prohibits `TODO`, `FIXME`, empty `pass` blocks, and unimplemented functional stubs in pull requests. All code must be delivered complete. |
| **`CULT02`** | **Spec Traceability Obligation** | `P1_WARNING` | 15 pts | Requires an explicit requirement link annotation (e.g. `@spec RF01`) to maintain traceability between technical specifications and source code. |
| **`CULT03`** | **Mandatory Automated Test Coverage** | `P0_BLOCKING` | 35 pts | Requires every functional component/module to be accompanied by automated unit or integration tests. |
| **`CULT04`** | **Zero Hardcoded Secrets & Credentials** | `P0_BLOCKING` | 40 pts | Detects hardcoded API keys, private keys, passwords, bearer tokens, or sensitive credentials in source files. Secrets are automatically redacted in PR logs (`***REDACTED***`). |
| **`CULT05`** | **Strict Typing & Contract Clarity** | `P1_WARNING` | 10 pts | Requires explicit type annotations on public function parameters and return types. |

---

## 🏗️ 2. Architectural Layer Boundary Rules (`ARCH-LAYER-01` - `ARCH-LAYER-04`)

| Rule ID | Name | Severity | Penalty | Description & Rationale |
| :--- | :--- | :--- | :---: | :--- |
| **`ARCH-LAYER-01`** | **Zero Presentation Code in Domain, Models & Controllers** | `P0_BLOCKING` | 40 pts | Strictly prohibits embedding raw HTML tags (`<img>`, `<div>`, `<span>`), JSX, CSS, or DOM APIs inside Domain, Model, Service, or Controller classes. |
| **`ARCH-LAYER-02`** | **Zero Direct Database Queries in Presentation & Views** | `P0_BLOCKING` | 35 pts | Prohibits raw SQL queries (`SELECT`, `INSERT`), `DbContext` calls, or ORM queries inside presentation templates and views. |
| **`ARCH-LAYER-03`** | **Zero Transport Protocol Coupling in Domain Models** | `P0_BLOCKING` | 30 pts | Prohibits binding HTTP request objects or transport superglobals (`HttpContext`, `express.Request`, `$_POST`) inside core domain entities. |
| **`ARCH-LAYER-04`** | **Thin Controllers (Delegation to Application / Domain Services)** | `P1_WARNING` | 20 pts | Controllers must act as lightweight coordinators without containing heavy business algorithms or direct data access logic. |
| **`ARCH-FE-01`** | **Zero Direct Network Calls in Presentational UI Components** | `P0_BLOCKING` | 35 pts | Prohibits direct network calls (`fetch`, `axios`, `http.get`) inside dumb presentational UI components. |

---

## 🛡️ 3. False-Positive Elimination & Inline Pragmas

To prevent false alarms without degrading quality gates, the Guardian employs a 3-layer filtering system:

### 3.1. Syntactic Word Boundary Fencing
Tokens are matched only at exact boundary delimiters, preventing variable and method identifiers (e.g. `GetImageUrl()`, `selected_items`, `input_stream`) from being falsely flagged as markup tags or SQL statements.

### 3.2. Comment & Docstring Scoping
Code comments (`//`, `#`, `/* */`) and docstrings (`"""`) explaining SQL or HTML concepts are isolated and excluded from triggering layer boundary violations.

### 3.3. Documented Inline Suppression Pragma (`@guardian-ignore`)
When an architectural exception is legitimately required, developers may place an inline suppression pragma on the line preceding the code.

**Syntax**:
```csharp
// @guardian-ignore ARCH-LAYER-01: Legacy migration adapter for email templating
public string RenderLegacyHeader() {
    return "<div class='header'></div>";
}
```

```python
# @guardian-ignore ARCH-LAYER-02: Test database seeding helper
def seed_test_database():
    db.execute("SELECT * FROM seed_fixtures")
```

> [!IMPORTANT]
> Every `@guardian-ignore` pragma **MUST** include a non-empty human rationale after the colon. Pragmas lacking documentation are rejected with a `P1_WARNING`.

### 3.4. Repository-Level Exemption File (`.guardianignore`)
Files and directories can be excluded globally or for specific rules via `.guardianignore`:
```gitignore
# Exclude mock data fixtures from rule checks
fixtures/**
tests/mocks/**
```

---

## 🔗 Related Documentation
- [Clean Architecture & System Design](./ARCHITECTURE.md)
- [Quickstart & CLI Usage](./QUICKSTART.md)
- [4-Tier Pipeline Specification](./PIPELINE.md)
- [Multi-Platform VCS Integrations](./INTEGRATIONS.md)
- [Contributor Guidelines](./CONTRIBUTING.md)
