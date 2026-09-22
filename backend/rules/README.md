# 🏛️ Modular Rules & Catalog Architecture (`backend/rules/`)

This directory is organized into a clean 4-tier modular pipeline that decouples architecture styles, abstract rules, language adapters, layer vocabularies, and scanner reduction engines:

```
backend/rules/
├── 1_architectures/     # 1. Identify Architecture (Topologies, layers & boundaries)
├── 2_rules/             # 2. Rules (Abstract constraints, severities & penalties)
├── 3_languages/         # 3. Languages (AST tokens, syntax patterns & adapters)
├── 4_scanner/           # 4. Scanner (Execution pipeline & parallel reduction config)
├── layer_vocabulary.json# Machine-readable Token & Tag Taxonomy
├── layer_vocabulary.md  # Detailed Documentation & Token Matrix
├── rules_schema.json    # JSON Schema validating all manifests
└── README.md            # Central Catalog Index
```

---

## 🗂️ Catalog Index

### 1️⃣ Identify Architecture ([`1_architectures/`](./1_architectures/))
- [`layered_mvc.json`](./1_architectures/layered_mvc.json) / [`.md`](./1_architectures/layered_mvc.md): Multi-tier and MVC tier constraints.
- [`clean_architecture.json`](./1_architectures/clean_architecture.json) / [`.md`](./1_architectures/clean_architecture.md): Concentric layers and Ports & Adapters.
- [`microservices.json`](./1_architectures/microservices.json) / [`.md`](./1_architectures/microservices.md): Distributed boundaries and database-per-service isolation.
- [`cqrs_event_sourcing.json`](./1_architectures/cqrs_event_sourcing.json) / [`.md`](./1_architectures/cqrs_event_sourcing.md): Command/Query segregation and immutable event ledgers.
- [`rest_api.json`](./1_architectures/rest_api.json) / [`.md`](./1_architectures/rest_api.md): REST API standards and explicit DTO contracts.
- [`frontend_clean.json`](./1_architectures/frontend_clean.json) / [`.md`](./1_architectures/frontend_clean.md): Component clean architecture and dumb UI isolation.

### 2️⃣ Rules ([`2_rules/`](./2_rules/))
- [`layer_boundaries.json`](./2_rules/layer_boundaries.json): Universal layer violation rules (`ARCH-LAYER-01` to `ARCH-LAYER-04`).
- [`culture_standards.json`](./2_rules/culture_standards.json): Engineering culture standards (`CULT01` to `CULT05`).

### 3️⃣ Languages ([`3_languages/`](./3_languages/))
- [`csharp.json`](./3_languages/csharp.json): .NET 8/9 C#, Razor, DbContext, and HttpContext adapters.
- [`python.json`](./3_languages/python.json): Python 3.10+, Django, FastAPI, and Jinja adapters.
- [`typescript.json`](./3_languages/typescript.json): TypeScript, JavaScript, React, and NestJS adapters.
- [`php.json`](./3_languages/php.json): PHP, Laravel, and Blade adapters.
- [`golang.json`](./3_languages/golang.json): Go, Gin, and GORM adapters.
- [`java.json`](./3_languages/java.json): Java, Spring Boot, and Jakarta EE adapters.
- [`rust.json`](./3_languages/rust.json): Rust, Actix, Axum, and SQLx/Diesel adapters.

### 4️⃣ Scanner ([`4_scanner/`](./4_scanner/))
- [`scanner_config.json`](./4_scanner/scanner_config.json): Engine runtime settings and gate thresholds.
- [`pipeline_definition.md`](./4_scanner/pipeline_definition.md): 4-stage pipeline diagram and workflow specification.

### 📚 Layer Vocabulary & Token Taxonomy
- [`layer_vocabulary.json`](./layer_vocabulary.json): Exhaustive taxonomy mapping HTML tags, DOM APIs, SQL keywords, ORM primitives, and HTTP contexts to canonical layers.
- [`layer_vocabulary.md`](./layer_vocabulary.md): Detailed guide explaining layer classification and forbidden boundaries with diagrams.
