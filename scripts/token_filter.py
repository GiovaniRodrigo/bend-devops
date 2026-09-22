"""
==============================================================================
Token Filter & Inline Suppression Engine
==============================================================================
@spec RF01, RF02, RF03, RF04, RF05, RF06 - False-Positive Reduction & Pragmas
==============================================================================
"""

import re
import fnmatch
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any, Optional

PRAGMA_SINGLE_REGEX = re.compile(
    r"(?i)(?://|#|/\*|<!--)\s*@guardian-ignore\s+([A-Z0-9_-]+|ALL)(?:\s*:\s*(.+))?"
)

PRAGMA_START_REGEX = re.compile(
    r"(?i)(?://|#|/\*|<!--)\s*@guardian-ignore-start\s+([A-Z0-9_-]+|ALL)(?:\s*:\s*(.+))?"
)

PRAGMA_END_REGEX = re.compile(
    r"(?i)(?://|#|/\*|<!--)\s*@guardian-ignore-end(?:\s+([A-Z0-9_-]+|ALL))?"
)


class IgnoredFilePattern:
    """Represents a .guardianignore or project-level file/rule exemption."""

    def __init__(self, glob_pattern: str, exempted_rules: Optional[List[str]] = None, reason: str = ""):
        self.glob_pattern = glob_pattern.strip()
        self.exempted_rules = [r.upper() for r in exempted_rules] if exempted_rules else []
        self.reason = reason.strip()

    def matches(self, file_path: str, rule_id: Optional[str] = None) -> bool:
        normalized_path = file_path.replace("\\", "/").lstrip("./")
        pattern = self.glob_pattern.replace("\\", "/").lstrip("./")
        
        # Match glob pattern
        if not (fnmatch.fnmatch(normalized_path, pattern) or fnmatch.fnmatch(normalized_path, f"*/{pattern}") or fnmatch.fnmatch(normalized_path, f"{pattern}/*")):
            # Also check if pattern matches directory prefix
            if not normalized_path.startswith(pattern.rstrip("*")):
                return False

        # If specific rules defined, check if rule_id is exempt or if ALL is exempt
        if self.exempted_rules and rule_id:
            rule_upper = rule_id.upper()
            if "ALL" not in self.exempted_rules and rule_upper not in self.exempted_rules:
                return False

        return True


class TokenFilter:
    """Filters comments, docstrings, and validates inline suppression pragmas."""

    @staticmethod
    def strip_comments(line: str, extension: str) -> str:
        """Strips single line comments depending on the file extension."""
        ext = extension.lower()
        if ext in [".py", ".sh", ".rb", ".yaml", ".yml"]:
            parts = line.split("#", 1)
            return parts[0].rstrip()
        elif ext in [".cs", ".ts", ".js", ".tsx", ".jsx", ".php", ".go", ".java", ".rs", ".cpp", ".c"]:
            parts = line.split("//", 1)
            return parts[0].rstrip()
        return line

    @staticmethod
    def parse_inline_pragmas(lines: List[str]) -> Tuple[Dict[int, Set[str]], List[Dict[str, Any]]]:
        """
        Parses all lines for:
          - Single-line: `@guardian-ignore <RULE_ID>: <reason>` (applies to next line)
          - Block-scoped: `@guardian-ignore-start <RULE_ID>: <reason>` ... `@guardian-ignore-end`
        Returns:
            - suppressed_map: Dict mapping 1-indexed target line number to a set of ignored rule IDs
            - warnings: List of violation dictionaries for invalid/undocumented pragmas
        """
        suppressed_map: Dict[int, Set[str]] = {}
        warnings: List[Dict[str, Any]] = []

        # Active block suppressions: map of rule_id -> set of active rules
        active_block_rules: Set[str] = set()

        for idx, line in enumerate(lines, 1):
            # 1. Check for block start: @guardian-ignore-start
            start_match = PRAGMA_START_REGEX.search(line)
            if start_match:
                rule_id = start_match.group(1).upper()
                reason = start_match.group(2)
                if reason and reason.strip():
                    active_block_rules.add(rule_id)
                else:
                    warnings.append({
                        "rule_id": "PRAGMA-INVALID",
                        "severity": "P1_WARNING",
                        "penalty": 10,
                        "line": idx,
                        "snippet": line.strip(),
                        "message": f"Block suppression pragma '@guardian-ignore-start {rule_id}' is missing mandatory justification/reason."
                    })
                continue

            # 2. Check for block end: @guardian-ignore-end
            end_match = PRAGMA_END_REGEX.search(line)
            if end_match:
                target_rule = end_match.group(1)
                if target_rule:
                    active_block_rules.discard(target_rule.upper())
                else:
                    active_block_rules.clear()
                continue

            # 3. Check for single line pragma: @guardian-ignore
            single_match = PRAGMA_SINGLE_REGEX.search(line)
            if single_match and not start_match and not end_match:
                rule_id = single_match.group(1).upper()
                reason = single_match.group(2)
                target_line = idx + 1  # Applies to next line

                if reason and reason.strip():
                    if target_line not in suppressed_map:
                        suppressed_map[target_line] = set()
                    suppressed_map[target_line].add(rule_id)
                else:
                    warnings.append({
                        "rule_id": "PRAGMA-INVALID",
                        "severity": "P1_WARNING",
                        "penalty": 10,
                        "line": idx,
                        "snippet": line.strip(),
                        "message": f"Inline suppression pragma '@guardian-ignore {rule_id}' is missing mandatory justification/reason."
                    })
                continue

            # 4. If within an active block, suppress the current line
            if active_block_rules:
                if idx not in suppressed_map:
                    suppressed_map[idx] = set()
                suppressed_map[idx].update(active_block_rules)

        return suppressed_map, warnings

    @staticmethod
    def matches_exact_token(token: str, line: str) -> bool:
        """
        Ensures token matches with word boundaries or tag opening fences,
        preventing false positives on identifier names (e.g. get_img() vs <img).
        """
        token_str = token.strip()
        
        # HTML tag checks: <img, <div>, <form, <button, etc.
        if token_str.startswith("<"):
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

    @staticmethod
    def load_guardianignore(ignore_file_path: Optional[Path] = None) -> List[IgnoredFilePattern]:
        """
        Parses .guardianignore or exemptions config file if present.
        Format in .guardianignore:
          # Comments
          legacy/**                    # Excludes all rules for matching files
          migrations/* [ARCH-LAYER-02] # Excludes specific rule with optional reason
        """
        patterns: List[IgnoredFilePattern] = []
        path = ignore_file_path or (Path.cwd() / ".guardianignore")
        if not path or not path.exists():
            return patterns

        try:
            content = path.read_text(encoding="utf-8")
            for line in content.splitlines():
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue

                # Parse pattern with optional rule specification: pattern [RULE1, RULE2] # Reason
                reason = ""
                if "#" in stripped:
                    parts = stripped.split("#", 1)
                    stripped = parts[0].strip()
                    reason = parts[1].strip()

                rule_match = re.search(r"\[([A-Z0-9_,\s-]+)\]", stripped)
                exempted_rules = []
                if rule_match:
                    rule_text = rule_match.group(1)
                    exempted_rules = [r.strip().upper() for r in rule_text.split(",") if r.strip()]
                    glob_pat = stripped[:rule_match.start()].strip()
                else:
                    glob_pat = stripped

                if glob_pat:
                    patterns.append(IgnoredFilePattern(glob_pat, exempted_rules, reason))
        except Exception:
            pass

        return patterns

    @staticmethod
    def is_file_or_rule_exempt(file_path: str, rule_id: str, exemptions: List[IgnoredFilePattern]) -> bool:
        """Checks if a file and rule are covered by any project-level exemption."""
        for ex in exemptions:
            if ex.matches(file_path, rule_id):
                return True
        return False


# Top-level helper functions for direct import and backwards compatibility
strip_comments = TokenFilter.strip_comments
parse_inline_pragmas = TokenFilter.parse_inline_pragmas
matches_exact_token = TokenFilter.matches_exact_token
load_guardianignore = TokenFilter.load_guardianignore
is_file_or_rule_exempt = TokenFilter.is_file_or_rule_exempt
