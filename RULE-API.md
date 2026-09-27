# Guardian Rule Engine REST API Reference

The **Bend DevOps Guardian** REST server (`scripts/guardian_server.py`) provides full CRUD, validation, testing, cloning, lifecycle management, import/export, and audit trail endpoints for rules.

Base URL: `http://localhost:8080/api`

---

## Summary of Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/rules` | List all resolved rules with multi-criteria filtering |
| `GET` | `/api/rules/{id}` | Get detailed rule definition by ID |
| `POST` | `/api/rules` | Create a new custom rule |
| `PUT` | `/api/rules/{id}` | Update an existing rule (supports partial updates) |
| `DELETE` | `/api/rules/{id}` | Delete or archive a rule (`?cascade=true` for hard delete) |
| `POST` | `/api/rules/{id}/validate` | Validate a specific rule against schema and ReDoS checks |
| `POST` | `/api/rules/{id}/test` | Test an existing rule against source code input |
| `POST` | `/api/rules/test` | Test an ad-hoc inline rule definition against code |
| `POST` | `/api/rules/{id}/enable` | Activate a rule in the Quality Gate |
| `POST` | `/api/rules/{id}/disable` | Disable a rule in the Quality Gate |
| `POST` | `/api/rules/{id}/clone` | Clone an existing rule to a new ID |
| `POST` | `/api/rules/import` | Import rules from JSON payload |
| `GET` | `/api/rules/{id}/export` | Export a specific rule as JSON |
| `GET` | `/api/rules/export/all` | Export all active rules as a JSON manifest |
| `GET` | `/api/rules/audit-trail` | Retrieve governance mutation audit trail |
| `GET` | `/api/rules/categories` | List unique rule categories |
| `GET` | `/api/rules/languages` | List supported programming languages |
| `GET` | `/api/rules/types` | List rule evaluation types |
| `GET` | `/api/rules/severities` | List standardized severity levels |
| `GET` | `/api/rules/statuses` | List lifecycle statuses |

---

## Example Requests & Responses

### 1. List Rules
`GET /api/rules?tier=custom&severity=P0`

**Response (`200 OK`):**
```json
{
  "total": 1,
  "rules": [
    {
      "id": "SEC-006",
      "name": "No Hardcoded Credentials",
      "type": "pattern",
      "category": "security",
      "severity": "P0",
      "penaltyPoints": 35,
      "tier": "custom",
      "status": "ACTIVE",
      "enabled": true
    }
  ]
}
```

### 2. Test Rule Against Code
`POST /api/rules/SEC-006/test`

**Request Body:**
```json
{
  "code": "password = \"supersecret123\"\n",
  "file_name": "src/auth.py"
}
```

**Response (`200 OK`):**
```json
{
  "test_result": {
    "ruleId": "SEC-006",
    "passed": false,
    "hasViolation": true,
    "isSuppressed": false,
    "matchedLines": [1],
    "violations": [
      {
        "ruleId": "SEC-006",
        "line": 1,
        "message": "Hardcoded credentials detected.",
        "snippet": "password = \"supersecret123\"",
        "suggestion": "Use environment variables."
      }
    ],
    "durationMs": 0.42
  }
}
```

### 3. Clone Rule
`POST /api/rules/ARCH-LAYER-01/clone`

**Request Body:**
```json
{
  "new_id": "ARCH-LAYER-01-CUSTOM",
  "new_name": "Custom Presentation Layer Check"
}
```

**Response (`201 Created`):**
```json
{
  "success": true,
  "rule": {
    "id": "ARCH-LAYER-01-CUSTOM",
    "name": "Custom Presentation Layer Check",
    "tier": "custom",
    "status": "DRAFT"
  },
  "message": "Rule 'ARCH-LAYER-01' cloned to 'ARCH-LAYER-01-CUSTOM'"
}
```
