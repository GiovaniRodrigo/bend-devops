# 🛡️ Custom Rules Engine & Authoring Guide

Extensible declarative rules, multi-tier precedence, JSON schema, and ReDoS safety validation for Bend DevOps Guardian.

---

## 1. Multi-Tier Governance & Precedence

Guardian resolves rule conflicts deterministically: **Custom > Project > Organization > Builtin**.

| Tier | Precedence | Path | Purpose |
| :--- | :---: | :--- | :--- |
| **Builtin** | 1 (Base) | `backend/rules/builtin/` & `2_rules/` | Base rules (`CULT01..05`, `ARCH-*`). |
| **Organization** | 2 | `backend/rules/organization/` | Company-wide policies. |
| **Project** | 3 | `backend/rules/projects/` | Repository-specific standards. |
| **Custom** | 4 (Highest) | `backend/rules/custom/` | Custom overrides and ad-hoc rules. |

---

## 2. Rule Schema Specification

All rule JSON manifests conform to `backend/rules/rules_schema.json`:

```json
{
  "id": "SEC-CUSTOM-001",
  "version": "1.0.0",
  "name": "No Plaintext Password Assignments",
  "type": "pattern",
  "category": "security",
  "severity": "P0",
  "penaltyPoints": 35,
  "status": "ACTIVE",
  "enabled": true,
  "tier": "custom",
  "languages": ["python", "typescript", "csharp"],
  "architectures": ["clean_architecture", "layered_mvc"],
  "condition": {
    "pattern": "(password|secret)\\s*=\\s*['\"][A-Za-z0-9_\\-\\.\\@]{6,}['\"]"
  },
  "message": "Plaintext credential detected.",
  "suggestion": "Read from environment variables or secrets manager."
}
```

### Supported Rule Types
- `pattern`: Regex matching with automated ReDoS protection.
- `naming`: Symbol casing checks (`PascalCase`, `camelCase`, `snake_case`).
- `dependency`: Inward Clean Architecture boundary validation.
- `architecture`: Cross-tier pattern validation.
- `file_folder`: File and path placement conventions.
- `ast`: Syntactic tree structure evaluation.
- `language_specific`: Targeted checks for specific languages.

---

## 3. ReDoS Safety Guidelines

1. **Avoid Nested Quantifiers**: Never use `(a+)+` or `(\w+)+`.
2. **Anchor Patterns**: Prefer `\b` or `^` where appropriate.
3. **Use Character Classes**: Use `[^'"]+` instead of `.*` inside quotes.

---

## 4. CLI Workflow

```bash
# 1. Validate rule schema and regex safety
python3 scripts/culture_guard.py rules validate backend/rules/custom/SEC-CUSTOM-001.json

# 2. Test rule against code snippet
python3 scripts/culture_guard.py rules test SEC-CUSTOM-001 --code "password = 'secret_pass_123'"

# 3. Register rule in Quality Gate
python3 scripts/culture_guard.py rules create backend/rules/custom/SEC-CUSTOM-001.json
```
