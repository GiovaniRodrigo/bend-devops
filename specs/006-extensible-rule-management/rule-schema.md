# Rule Schema Specification: Rules Manifest JSON Schema

**Spec ID**: `SPEC-006-SCHEMA`  
**Parent**: `SPEC-006`  
**Target Schema File**: `backend/rules/rules_schema.json`  

---

## 1. Core Rule Definition Schema

The schema supports both standalone rule objects and manifest collections while ensuring backward compatibility with existing rules.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Bend DevOps Guardian Rule Schema",
  "description": "Validation schema for extensible engineering, architecture, culture, and security rules.",
  "type": "object",
  "required": ["id", "version", "name", "type", "category", "severity", "condition", "message"],
  "properties": {
    "id": {
      "type": "string",
      "pattern": "^[A-Z0-9_-]+$",
      "description": "Unique rule identifier (e.g. SEC-006, ARCH-LAYER-01)"
    },
    "version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+\\.\\d+$",
      "description": "Semantic version of the rule"
    },
    "name": {
      "type": "string",
      "minLength": 3,
      "maxLength": 120
    },
    "description": {
      "type": "string"
    },
    "type": {
      "type": "string",
      "enum": ["pattern", "naming", "dependency", "architecture", "file_folder", "ast", "language_specific"]
    },
    "category": {
      "type": "string",
      "enum": ["culture", "architecture", "security", "quality", "performance", "custom", "Culture & Quality", "Architecture - Layer Boundaries", "Language Adapter", "Security"]
    },
    "severity": {
      "type": "string",
      "enum": ["P0", "P1", "P2", "P3", "INFO", "P0_BLOCKING", "P1_WARNING", "P2_INFO"]
    },
    "penalty_points": {
      "type": "integer",
      "minimum": 0,
      "maximum": 100
    },
    "status": {
      "type": "string",
      "enum": ["DRAFT", "TESTING", "VALIDATED", "ACTIVE", "DEPRECATED", "ARCHIVED", "active", "inactive"]
    },
    "enabled": {
      "type": "boolean"
    },
    "tier": {
      "type": "string",
      "enum": ["builtin", "organization", "project", "custom"]
    },
    "architectures": {
      "type": "array",
      "items": { "type": "string" }
    },
    "languages": {
      "type": "array",
      "items": { "type": "string" }
    },
    "scope": {
      "type": "object",
      "properties": {
        "include": { "type": "array", "items": { "type": "string" } },
        "exclude": { "type": "array", "items": { "type": "string" } },
        "target_layer": { "type": "string" }
      }
    },
    "condition": {
      "type": "object",
      "properties": {
        "pattern": { "type": "string" },
        "patterns": { "type": "array", "items": { "type": "string" } },
        "naming_convention": { "type": "string", "enum": ["PascalCase", "camelCase", "snake_case", "kebab-case", "UPPER_CASE"] },
        "source_layer": { "type": "string" },
        "forbidden_layer": { "type": "string" },
        "forbidden_targets": { "type": "array", "items": { "type": "string" } },
        "required_path_prefix": { "type": "string" },
        "ast_selector": { "type": "string" }
      }
    },
    "message": {
      "type": "string"
    },
    "suggestion": {
      "type": "string"
    },
    "rationale": {
      "type": "string"
    },
    "remediation": {
      "type": "string"
    },
    "suppression": {
      "type": "object",
      "properties": {
        "allowed": { "type": "boolean" },
        "pragma": { "type": "string" },
        "requires_reason": { "type": "boolean" },
        "minimum_reason_length": { "type": "integer" }
      }
    },
    "metadata": {
      "type": "object",
      "properties": {
        "author": { "type": "string" },
        "created_at": { "type": "string" },
        "updated_at": { "type": "string" }
      }
    }
  }
}
```
