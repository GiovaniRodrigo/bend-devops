# Contratos de API: Pipeline Flow, Architecture Profiles, Split Diff & Coverage

Este documento formaliza os contratos de endpoints HTTP da API do Guardian Server (`scripts/guardian_server.py`) consumidos pelo frontend Angular.

---

## 1. Endpoints

### `GET /api/profiles`
Retorna todos os perfis arquiteturais cadastrados na plataforma.

**Response 200:**
```json
{
  "profiles": [
    {
      "id": "profile_clean_arch",
      "name": "Clean Architecture (Strict)",
      "description": "Enforces strict domain boundaries and zero external dependencies in core entities.",
      "category": "Layered Architecture",
      "enabled": true,
      "isDefault": true,
      "allowedDependencies": ["Domain.*", "Application.*"],
      "forbiddenDependencies": ["Presentation.*", "Infrastructure.*"],
      "ruleIds": ["ARCH-LAYER-01", "ARCH-LAYER-03", "CULT01"]
    }
  ],
  "total": 1
}
```

---

### `PUT /api/profiles/:id/status`
Atualiza o status de ativação (turnover Ativo/Inativo) de um perfil arquitetural.

**Request:**
```json
{
  "enabled": false
}
```

**Response 200:**
```json
{
  "success": true,
  "id": "profile_clean_arch",
  "enabled": false,
  "updatedAt": "2026-09-28T09:30:00Z"
}
```

---

### `POST /api/audit`
Executa a avaliação arquitetural com escopo customizado e perfil selecionado.

**Request:**
```json
{
  "repoPath": "ai-bend-devops",
  "branch": "feature/checkout-flow",
  "profile": "profile_clean_arch",
  "ruleIds": ["CULT01", "ARCH-LAYER-01"],
  "targetMode": "diff_only"
}
```

**Response 200:**
```json
{
  "report": {
    "isApproved": false,
    "score": 68,
    "totalViolations": 3,
    "p0Count": 1,
    "p1Count": 2,
    "p2Count": 0,
    "totalFiles": 4
  },
  "files": [
    {
      "name": "src/Domain/Models/OrderInvoice.cs",
      "identifiedLayer": "Domain",
      "hasTestCoverage": false,
      "violations": [
        {
          "ruleId": "CULT01",
          "severity": "P0_BLOCKING",
          "message": "Domain entities must not import presentation models.",
          "remediation": "Move DTO binding to Application/Presentation layer.",
          "line": 14
        }
      ]
    }
  ]
}
```
