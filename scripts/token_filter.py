"""
==============================================================================
Token Filter & Inline Suppression Engine
==============================================================================
@spec RF01, RF02, RF03, RF05 - False-Positive Reduction & Pragmas
==============================================================================
"""

import re
from typing import Dict, List, Set, Tuple, Any

PRAGMA_REGEX = re.compile(
    r"(?i)(?://|#|/\*|<!--)\s*@guardian-ignore\s+([A-Z0-9_-]+|ALL)(?:\s*:\s*(.+))?"
)

def strip_comments(line: str, extension: str) -> str:
    """Strips single line comments depending on the file extension."""
    ext = extension.lower()
    if ext in [".py", ".sh", ".rb", ".yaml", ".yml"]:
        # Hash comments
        parts = line.split("#", 1)
        return parts[0].rstrip()
    elif ext in [".cs", ".ts", ".js", ".tsx", ".jsx", ".php", ".go", ".java", ".rs", ".cpp", ".c"]:
        # Slash comments
        parts = line.split("//", 1)
        return parts[0].rstrip()
    return line

def parse_inline_pragmas(lines: List[str]) -> Tuple[Dict[int, Set[str]], List[Dict[str, Any]]]:
    """
    Parses all lines for `@guardian-ignore <RULE_ID>: <reason>`.
    Returns:
        - suppressed_map: Dict mapping 1-indexed target line number to a set of ignored rule IDs
        - warnings: List of violation dictionaries for invalid/undocumented pragmas
    """
    suppressed_map: Dict[int, Set[str]] = {}
    warnings: List[Dict[str, Any]] = []

    for idx, line in enumerate(lines, 1):
        match = PRAGMA_REGEX.search(line)
        if match:
            rule_id = match.group(1).upper()
            reason = match.group(2)
            target_line = idx + 1  # Applies to next line

            if reason and reason.strip():
                if target_line not in suppressed_map:
                    suppressed_map[target_line] = set()
                suppressed_map[target_line].add(rule_id)
            else:
                # RN01: Mandatory Justification
                warnings.append({
                    "rule_id": "PRAGMA-INVALID",
                    "severity": "P1_WARNING",
                    "penalty": 10,
                    "line": idx,
                    "snippet": line.strip(),
                    "message": f"Inline suppression pragma '@guardian-ignore {rule_id}' is missing mandatory justification/reason."
                })

    return suppressed_map, warnings

def matches_exact_token(token: str, line: str) -> bool:
    """
    Ensures token matches with word boundaries or tag opening fences,
    preventing false positives on identifier names (e.g. get_img() vs <img).
    """
    token_str = token.strip()
    
    # HTML tag checks: <img, <div>, <form, <button, etc.
    if token_str.startswith("<"):
        # Match '<tag' when followed by space, '>', '/', or end of string
        tag_name = re.escape(token_str.lstrip("<").rstrip(">"))
        pattern = rf"(?i)<\s*{tag_name}(?:\s|>|/|$)"
        return bool(re.search(pattern, line))

    # Standalone SQL keywords: SELECT, INSERT INTO, UPDATE, DELETE FROM
    if token_str.isupper() and len(token_str) > 2:
        pattern = rf"(?i)\b{re.escape(token_str)}\b"
        return bool(re.search(pattern, line))

    # Standard identifier / class / method names (e.g. HttpContext, DbContext)
    pattern = rf"(?i)\b{re.escape(token_str)}"
    return bool(re.search(pattern, line))
