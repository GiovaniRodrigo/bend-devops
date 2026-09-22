# Interfaces: False-Positive Suppression & Lexical Filtering

---

## 1. Token Filter Module Contract (`scripts/token_filter.py`)

```python
from typing import Dict, List, Set, Tuple, Optional

class TokenFilter:
    """Filters comments, docstrings, and validates inline suppression pragmas."""

    @staticmethod
    def strip_comments(line: str, extension: str) -> str:
        """Strips single-line comments from the code line."""
        pass

    @staticmethod
    def parse_inline_pragmas(lines: List[str]) -> Tuple[Dict[int, Set[str]], List[Dict[str, Any]]]:
        """
        Parses all lines for `@guardian-ignore RULE_ID: Reason`.
        Returns:
            - Map of line_number -> Set of ignored rule IDs
            - List of invalid pragma warning violations
        """
        pass

    @staticmethod
    def matches_exact_token(token: str, line: str) -> bool:
        """
        Ensures token matches with word boundaries or tag fences,
        preventing false positives on identifier names (e.g. get_img() vs <img).
        """
        pass
```
