# Contratos de API: Escopo e Regras Arquiteturais do Usuário

---

## Endpoints

### `POST /api/audit/evaluate`

**Descrição**: Executa a auditoria arquitetural sobre o repositório aplicando estritamente o escopo delimitado e o conjunto de regras complementares ativadas pelo usuário.

**Request:**
```json
{
  "repositoryPath": "/home/isabelle/projects/ai-bend-devops",
  "scope": {
    "mode": "subdirectory",
    "targetPath": "backend/domain",
    "branch": "main",
    "includePatterns": ["*.py", "*.bend"],
    "excludePatterns": ["tests/**"]
  },
  "rules": [
    {
      "ruleId": "ARCH-LAYER-01",
      "enabled": true,
      "customSeverity": "P0_BLOCKING"
    },
    {
      "ruleId": "SEC-001",
      "enabled": true,
      "customSeverity": "P0_BLOCKING"
    }
  ],
  "triggeredBy": "user"
}
```

**Response 200 (OK):**
```json
{
  "reportId": "rep-892f3a",
  "timestamp": "2026-09-27T18:00:00Z",
  "score": 95,
  "isApproved": true,
  "scope": {
    "mode": "subdirectory",
    "targetPath": "backend/domain",
    "filesEvaluatedCount": 14
  },
  "totalViolations": 0,
  "violations": [],
  "rulesEvaluated": [
    { "ruleId": "ARCH-LAYER-01", "status": "PASSED" },
    { "ruleId": "SEC-001", "status": "PASSED" }
  ]
}
```

**Erros:**
| Status | Código | Mensagem |
| :--- | :--- | :--- |
| `400` | `INVALID_SCOPE` | O escopo informado não é válido ou o caminho não existe. |
| `422` | `NO_RULES_SELECTED` | É necessário selecionar ao menos uma regra ativa para avaliação. |
| `500` | `ENGINE_ERROR` | Falha interna no motor de redução paralela. |
