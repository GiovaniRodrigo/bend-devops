# Rules Schema Contract: Universal 4-Tier Architecture

This document describes the schema contract for JSON manifests in `backend/rules/`, validated against [`rules_schema.json`](../../../backend/rules/rules_schema.json).

---

## 1. 4-Tier Manifest Contract Structure

The configuration files adhere to three contract formats:

### 1.1. Architecture Profile Contract (`1_architectures/*.json`)

```json
{
  "$schema": "../rules_schema.json",
  "version": "1.0.0",
  "architecture_id": "ARCH_PROFILE_LAYERED_MVC",
  "name": "Layered & MVC Architecture Profile",
  "description": "Defines canonical tiers, responsibilities, and directional constraints.",
  "layers": [
    {
      "name": "Domain",
      "aliases": ["models", "entities", "domain", "core"],
      "allowed_dependencies": [],
      "description": "Pure business models and state. Zero presentation or transport awareness."
    }
  ]
}
```

### 1.2. Abstract Rules Manifest (`2_rules/*.json`)

```json
{
  "$schema": "../rules_schema.json",
  "version": "1.0.0",
  "manifesto_name": "Universal Layer Boundary Rules",
  "category": "Architecture - Layer Boundaries",
  "description": "Abstract layer isolation rules defining forbidden concerns between tiers.",
  "rules": [
    {
      "id": "ARCH-LAYER-01",
      "name": "Zero Presentation Code in Domain, Models & Controllers",
      "layer": "Domain, Model, Controller, Service",
      "severity": "P0_BLOCKING",
      "penalty_points": 40,
      "description": "Prohibits raw UI markup (HTML, JSX, client scripts, styles) inside Domain, Model, Service, or Controller classes.",
      "rationale": "Separation of Concerns across multi-tier software systems.",
      "remediation": "Move presentation code to dedicated View templates or return ViewModels/DTOs."
    }
  ]
}
```

### 1.3. Language Adapter Contract (`3_languages/*.json`)

```json
{
  "$schema": "../rules_schema.json",
  "version": "1.0.0",
  "language": "C# (.NET 8 / 9)",
  "file_extensions": [".cs", ".cshtml", ".razor"],
  "layer_detection": {
    "Domain": ["/Domain/", "/Models/", "/Entities/"],
    "Presentation": ["/Views/", "/Pages/", "/Components/"]
  },
  "forbidden_patterns": {
    "Domain": [
      {
        "pattern": "<html|<div|<span|<p>|<script>|<style>|Response\\.Write",
        "maps_to_rule": "ARCH-LAYER-01",
        "message": "Raw HTML/presentation markup detected in C# Domain Entity"
      }
    ]
  }
}
```

### 1.4. Layer Vocabulary Contract ([`layer_vocabulary.json`](../../../backend/rules/layer_vocabulary.json))

```json
{
  "$schema": "./rules_schema.json",
  "version": "1.0.0",
  "title": "Layer Vocabulary & Token Taxonomy",
  "layers": {
    "Presentation": {
      "layer_id": "LAYER_PRESENTATION",
      "tokens": {
        "html_tags": ["<img>", "<div>", "<span>", "<form>", "<button>"],
        "dom_apis": ["document.getElementById", "window.location"],
        "template_directives": ["{{", "}}", "*ngIf", "v-model"]
      },
      "forbidden_in": ["Domain", "Model", "Application", "Service", "Infrastructure"]
    }
  }
}
```
