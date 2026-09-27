# CLI Specification: Rule Management Commands

**Spec ID**: `SPEC-006-CLI`  
**Parent**: `SPEC-006`  
**Binary / Entrypoint**: `python3 scripts/culture_guard.py rules` (or `guardian rules`)  

---

## 1. Subcommands Syntax

```bash
# 1. List rules with multi-dimensional filtering
guardian rules list [--category <CAT>] [--severity <SEV>] [--language <LANG>] [--status <STAT>] [--type <TYPE>] [--search <QUERY>] [--json]

# 2. Inspect a specific rule in detail
guardian rules show <RULE_ID> [--json]

# 3. Create a new rule from a JSON manifest file
guardian rules create <FILE_PATH.json>

# 4. Edit an existing rule
guardian rules edit <RULE_ID> <FILE_PATH.json>

# 5. Clone a rule to a new identifier
guardian rules clone <RULE_ID> <NEW_RULE_ID> [--name <NEW_NAME>]

# 6. Delete or archive a custom rule
guardian rules delete <RULE_ID> [--force]

# 7. Enable or activate a rule in the Quality Gate
guardian rules enable <RULE_ID>

# 8. Disable or deactivate a rule
guardian rules disable <RULE_ID>

# 9. Validate rule manifest syntax and security checks
guardian rules validate <FILE_PATH.json>

# 10. Test a rule against code snippet or fixture file
guardian rules test <RULE_ID_OR_FILE> --code "let token = '12345';" [--file <TEST_FILE>]

# 11. Import rules from a directory or JSON pack
guardian rules import <DIRECTORY_OR_FILE>

# 12. Export a rule to JSON
guardian rules export <RULE_ID> [--out <OUTPUT_PATH.json>]

# 13. Search rules by keyword
guardian rules search <QUERY>
```

---

## 2. Examples

```bash
# Search all security P0 rules
python3 scripts/culture_guard.py rules list --category security --severity P0

# Test custom rule against sample input
python3 scripts/culture_guard.py rules test SEC-006 --code "apiKey = 'secret_test_token_12345'"

# Clone an architecture rule
python3 scripts/culture_guard.py rules clone ARCH-LAYER-01 ARCH-LAYER-01-ENTERPRISE --name "Enterprise Domain Guard"
```
