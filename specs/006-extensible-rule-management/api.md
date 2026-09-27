# REST API Specification: Rule Management

**Spec ID**: `SPEC-006-API`  
**Parent**: `SPEC-006`  
**Base Path**: `/api/rules`  

---

## 1. Endpoints Overview

| Method | Path | Description | Status Codes |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/rules` | List all rules with optional filters | `200` |
| `GET` | `/api/rules/{id}` | Retrieve full details of a specific rule | `200`, `404` |
| `POST` | `/api/rules` | Create a new custom rule | `201`, `400`, `409`, `422` |
| `PUT` | `/api/rules/{id}` | Update an existing rule | `200`, `400`, `404`, `422` |
| `DELETE` | `/api/rules/{id}` | Delete or archive a custom rule | `204`, `403`, `404` |
| `POST` | `/api/rules/{id}/validate` | Validate rule against JSON schema & ReDoS checks | `200`, `422` |
| `POST` | `/api/rules/{id}/test` | Test an existing rule against source code input | `200`, `404`, `422` |
| `POST` | `/api/rules/test` | Test an ad-hoc unpersisted rule definition | `200`, `400`, `422` |
| `POST` | `/api/rules/{id}/enable` | Transition rule status to `ACTIVE` | `200`, `404` |
| `POST` | `/api/rules/{id}/disable` | Transition rule status to `INACTIVE` / `DEPRECATED` | `200`, `404` |
| `POST` | `/api/rules/{id}/clone` | Clone rule to a new unique ID | `201`, `400`, `404`, `409` |
| `POST` | `/api/rules/import` | Import rule(s) from JSON payload or directory | `200`, `400`, `422` |
| `GET` | `/api/rules/{id}/export` | Export a rule as standalone JSON manifest | `200`, `404` |
| `GET` | `/api/rules/export/all` | Export all effective rules as a consolidated pack | `200` |
| `GET` | `/api/rules/categories` | List available rule categories | `200` |
| `GET` | `/api/rules/languages` | List supported programming languages | `200` |
| `GET` | `/api/rules/types` | List supported rule types | `200` |
| `GET` | `/api/rules/severities` | List supported severity levels | `200` |
| `GET` | `/api/rules/statuses` | List lifecycle statuses | `200` |
| `GET` | `/api/rules/audit-trail` | Retrieve immutable audit event log | `200` |
| `GET` | `/api/healthz` | System health and HVM runtime status | `200` |

---

## 2. Request & Response Schemas

### 2.1 List Rules (`GET /api/rules`)
**Query Parameters**:
- `search`: String matching id, name, or description.
- `category`: Filter by `culture`, `architecture`, `security`, `quality`, `performance`, `custom`.
- `severity`: Filter by `P0`, `P1`, `P2`, `P3`, `INFO`.
- `language`: Filter by `csharp`, `python`, `typescript`, `php`, `golang`, `java`, `rust`.
- `status`: Filter by `ACTIVE`, `DRAFT`, `TESTING`, `VALIDATED`, `DEPRECATED`, `ARCHIVED`.
- `type`: Filter by `pattern`, `naming`, `dependency`, `architecture`, `file_folder`, `ast`, `language_specific`.
- `tier`: Filter by `builtin`, `organization`, `project`, `custom`.

**Response Body (200 OK)**:
```json
{
  "total": 28,
  "count": 28,
  "rules": [
    {
      "id": "SEC-006",
      "version": "1.0.0",
      "name": "No Hardcoded Credentials",
      "description": "Detects hardcoded secrets, tokens, or passwords",
      "type": "pattern",
      "category": "security",
      "severity": "P0",
      "status": "ACTIVE",
      "enabled": true,
      "tier": "custom",
      "languages": ["python", "typescript", "csharp"],
      "penaltyPoints": 40,
      "updatedAt": "2026-09-25T12:00:00Z"
    }
  ]
}
```

### 2.2 Test Rule (`POST /api/rules/{id}/test` or `POST /api/rules/test`)
**Request Body**:
```json
{
  "rule": { ... },
  "sourceCode": "password = 'super_secret_admin_token_12345'",
  "fileName": "src/auth/service.py"
}
```

**Response Body (200 OK)**:
```json
{
  "ruleId": "SEC-006",
  "passed": false,
  "hasViolation": true,
  "isSuppressed": false,
  "matchedLines": [1],
  "violations": [
    {
      "ruleId": "SEC-006",
      "severity": "P0",
      "penalty": 40,
      "line": 1,
      "snippet": "password = 'super_secret_admin_token_12345'",
      "message": "Hardcoded credential detected in source code",
      "suggestion": "Use environment variables or secret vaults"
    }
  ]
}
```

### 2.3 Clone Rule (`POST /api/rules/{id}/clone`)
**Request Body**:
```json
{
  "newId": "SEC-006-CUSTOM",
  "newName": "Custom Hardcoded Credential Scanner",
  "version": "1.0.0"
}
```
