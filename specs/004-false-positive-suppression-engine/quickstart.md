# Quickstart: False-Positive Suppression & Exemptions

Guide to using inline suppression pragmas (`@guardian-ignore`) and project-level `.guardianignore` configurations.

---

## 1. Inline Suppression Syntax (`@guardian-ignore`)

To exempt a specific line from an architectural or culture rule, add a comment on the preceding line with the rule ID and a mandatory justification:

### C# / TypeScript / Java / PHP / Go / Rust
```csharp
// @guardian-ignore ARCH-LAYER-01: Legitimate domain avatar serialization requirement
public string AvatarHtml => "<img src='/avatars/" + Username + ".png' />";
```

### Python / Shell
```python
# @guardian-ignore ARCH-LAYER-03: CLI export utility needs request context metadata
def serialize_account(context: HttpContext) -> dict:
    ...
```

---

## 2. Project-Level Exemption File (`.guardianignore`)

Create a `.guardianignore` file in the root of the project to ignore specific paths:

```ini
# Ignore legacy modules
legacy/**

# Ignore database migrations from layer boundary checks
src/Infrastructure/Migrations/**

# Specific rule suppression for test fixtures
test_fixtures/**: ARCH-LAYER-01, ARCH-LAYER-02
```
