# Rules Schema Contract: Suppression & Exemptions

---

## 1. Inline Pragma Syntax Specification

```regex
(?i)(?://|#|/\*|<!--)\s*@guardian-ignore\s+([A-Z0-9_-]+|ALL)(?:\s*:\s*(.+))?
```

- **Capture Group 1**: Rule ID (`ARCH-LAYER-01`, `CULT01`, `ALL`)
- **Capture Group 2**: Justification rationale (Mandatory)

If Group 2 is empty or whitespace-only, the pragma is flagged with `PRAGMA-INVALID` (`P1_WARNING`).
