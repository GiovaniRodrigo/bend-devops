"""
==============================================================================
Git Diff Parser & Line Number Extractor
==============================================================================
@spec RF04 - Unified Diff Delta Analyzer
==============================================================================
"""

import re
from typing import Dict, Set, List

def parse_unified_diff(diff_text: str) -> Dict[str, Set[int]]:
    """
    Parses a git unified diff string and returns a dictionary mapping
    file paths to sets of added/modified line numbers in the new file.
    """
    files: Dict[str, Set[int]] = {}
    current_file: str = ""
    current_new_line: int = 0

    lines = diff_text.splitlines()
    for line in lines:
        if line.startswith("diff --git"):
            match = re.search(r"b/(.*)$", line)
            if match:
                current_file = match.group(1).strip()
                if current_file not in files:
                    files[current_file] = set()
        elif line.startswith("+++ b/"):
            current_file = line[6:].strip()
            if current_file not in files:
                files[current_file] = set()
        elif line.startswith("@@"):
            # Format: @@ -old_start,old_count +new_start,new_count @@
            hunk_match = re.search(r"\+(\d+)(?:,(\d+))?", line)
            if hunk_match:
                current_new_line = int(hunk_match.group(1))
        elif line.startswith("+") and not line.startswith("+++"):
            if current_file:
                if current_file not in files:
                    files[current_file] = set()
                files[current_file].add(current_new_line)
            current_new_line += 1
        elif line.startswith("-") and not line.startswith("---"):
            pass  # Deletion in old file, doesn't advance new file line counter
        else:
            # Context line
            current_new_line += 1

    return files

def extract_changed_lines(diff_text: str, target_file: str) -> Set[int]:
    """Returns the set of changed line numbers for a specific target file."""
    all_changes = parse_unified_diff(diff_text)
    return all_changes.get(target_file, set())
