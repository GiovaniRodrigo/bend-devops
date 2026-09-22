# Research & Technical References: Layered Architecture Guardian

---

## 1. 4-Tier Pipeline Design

The system implements a decoupled 4-stage pipeline:
1. **Identify Architecture**: Topologies and layer hierarchies defined in declarative JSON files (`backend/rules/1_architectures/`).
2. **Rules**: Abstract architectural rules with severities and penalty point weights (`backend/rules/2_rules/`).
3. **Languages**: File extensions and token mapping adapters (`backend/rules/3_languages/`).
4. **Scanner & Report**: Static file analysis linked to high-performance Bend/HVM tree evaluation (`backend/rules/4_scanner/`).

---

## 2. Layer Token Taxonomy

By classifying concrete tokens (e.g. `<img>`, `<div>`, `<form>`, `document.*` into **Presentation**; `HttpContext`, `express.Request` into **Interface**; `SELECT * FROM`, `DbContext` into **Infrastructure**; `AggregateRoot`, `Entity<T>` into **Domain**), boundary verification reduces to checking whether a forbidden token appears in a file classified under a restricted layer.

---

## 3. Parallel Reduction via Bend HVM

Bend programs compile to Interaction Combinators evaluated concurrently across CPU cores on the High-Order Virtual Machine (HVM). Files are modeled as a binary tree:

```bend
type FileTree:
  Empty
  Leaf { file }
  Node { ~left, ~right }
```

Evaluating `evaluate_tree_parallel(tree)` reduces subtrees in parallel without lock contention.
