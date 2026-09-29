# 📜 Engineering Standards & Rules Catalog

Active quality gate rules, severities, penalty points, and inline suppressions.

---

## 🏛️ 1. Culture & Standards (`CULT01` - `CULT05`)

| Rule ID | Name | Severity | Penalty | Description |
| :--- | :--- | :---: | :---: | :--- |
| **`CULT01`** | **Zero Lazy Code** | `P0_BLOCKING` | 35 pts | Prohibits `TODO`, `FIXME`, empty `pass`, and unimplemented stubs in PRs. |
| **`CULT02`** | **Spec Traceability** | `P1_WARNING` | 15 pts | Requires specification requirement tag (e.g. `@spec RF01`). |
| **`CULT03`** | **Automated Tests** | `P0_BLOCKING` | 35 pts | Requires automated test coverage for functional modules. |
| **`CULT04`** | **Zero Hardcoded Secrets** | `P0_BLOCKING` | 40 pts | Detects API keys, passwords, bearer tokens, or credentials in source. |
| **`CULT05`** | **Strict Typing** | `P1_WARNING` | 10 pts | Requires explicit type annotations on public signatures. |

---

## 🏗️ 2. Architectural Layer Boundary Rules

| Rule ID | Name | Severity | Penalty | Description |
| :--- | :--- | :---: | :---: | :--- |
| **`ARCH-LAYER-01`** | **No UI in Domain / Controllers** | `P0_BLOCKING` | 40 pts | Prohibits HTML, JSX, DOM in Domain, Models, Services, or Controllers. |
| **`ARCH-LAYER-02`** | **No Direct DB Queries in Views** | `P0_BLOCKING` | 35 pts | Prohibits SQL queries (`SELECT`, `INSERT`), `DbContext` in views. |
| **`ARCH-LAYER-03`** | **No Transport Coupling in Domain** | `P0_BLOCKING` | 30 pts | Prohibits HTTP request objects (`HttpContext`, `$_POST`) in Domain. |
| **`ARCH-LAYER-04`** | **Thin Controllers** | `P1_WARNING` | 20 pts | Controllers must delegate logic to Application / Domain services. |
| **`ARCH-FE-01`** | **No Direct API Calls in Dumb UI** | `P0_BLOCKING` | 35 pts | Prohibits `fetch` / `axios` calls inside dumb presentational UI components. |

---

## 🛡️ 3. Inline Suppression Pragma (`@guardian-ignore`)

```csharp
// @guardian-ignore ARCH-LAYER-01: Legacy email template migration adapter
public string RenderHeader() => "<div class='header'></div>";
```

```python
# @guardian-ignore ARCH-LAYER-02: Test database seeding helper
def seed_test_database(): db.execute("SELECT * FROM seeds")
```

> [!IMPORTANT]
> A non-empty reason after `:` is mandatory. Undocumented pragmas trigger `P1_WARNING`.
