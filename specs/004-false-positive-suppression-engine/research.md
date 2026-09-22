# Research & Technical References: False-Positive Elimination

---

## 1. Industry Suppression Patterns

Static analysis engines handle inline pragmas and false positives via established patterns:

| Tool | Suppression Syntax | Mandatory Justification |
| :--- | :--- | :--- |
| **ESLint** | `// eslint-disable-next-line rule-id -- justification` | Optional |
| **SonarQube** | `// NOSONAR justification` | Optional |
| **Rust / Clippy** | `#[allow(clippy::rule_name)]` | Optional |
| **Guardian Gate** | `// @guardian-ignore RULE_ID: Justification rationale` | **Mandatory** (`RN01`) |

---

## 2. Syntactic Token Isolation Strategies

To eliminate false positives where method/variable names collide with prohibited tags:
1. **Word Boundary Fences (`\b`)**: Ensure keywords like `SELECT` match only as standalone tokens (`\bSELECT\b`), not inside identifiers (`selected_item`, `select_box`).
2. **HTML Tag Open Fencing (`<tag(?:\s|>|/|$)`)**: Ensure `<img` matches only when followed by whitespace or attributes (`<img src=...`), never when part of an identifier or generic type `Entity<Image>`.
3. **Comment Stripping**: Regular expression and lexer stripping of single-line (`//`, `#`) and multi-line (`/* ... */`, `<!-- ... -->`, `"""..."""`) comments.
