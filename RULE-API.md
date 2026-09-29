# 🔌 Guardian Rule Engine REST API Reference

REST server (`scripts/guardian_server.py`) provides rule lifecycle, CRUD, testing, cloning, and audit trail endpoints.

**Base URL**: `http://localhost:4200/api` (or custom `--port`)

---

## Endpoint Summary

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/healthz` | Health check and active rule count. |
| `GET` | `/api/rules` | List resolved rules (query: `?tier=`, `?severity=`, `?status=`). |
| `GET` | `/api/rules/{id}` | Get rule definition by ID. |
| `POST` | `/api/rules` | Create custom rule from JSON payload. |
| `PUT` | `/api/rules/{id}` | Update existing rule. |
| `DELETE` | `/api/rules/{id}` | Delete or archive rule (`?force=true` for hard delete). |
| `POST` | `/api/rules/{id}/validate` | Validate rule against schema and ReDoS checks. |
| `POST` | `/api/rules/{id}/test` | Test rule against source code input payload (`{"code": "..."}`). |
| `POST` | `/api/rules/{id}/clone` | Clone rule (`{"new_id": "...", "new_name": "..."}`). |
| `POST` | `/api/rules/{id}/enable` | Enable rule. |
| `POST` | `/api/rules/{id}/disable` | Disable rule. |
| `GET` | `/api/rules/export/all` | Export all active rules as JSON manifest. |
| `POST` | `/api/rules/import` | Import rules from JSON payload. |
| `GET` | `/api/rules/audit-trail` | Retrieve rule mutation audit logs. |

---

## Quick Examples

### Test Rule Against Code
```bash
curl -X POST http://localhost:4200/api/rules/CULT01/test \
  -H "Content-Type: application/json" \
  -d '{"code": "def fn(): pass\n", "file_name": "app.py"}'
```

### Clone Rule
```bash
curl -X POST http://localhost:4200/api/rules/ARCH-LAYER-01/clone \
  -H "Content-Type: application/json" \
  -d '{"new_id": "ARCH-LAYER-01-CUSTOM", "new_name": "Custom Presentation Layer"}'
```
