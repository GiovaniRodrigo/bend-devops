"""
==============================================================================
Git Diff Parser & Line Number Extractor
==============================================================================
@spec RF04 - Unified Diff Delta Analyzer
@spec RF05 - Unified Diff Multi-Mode Support (Added, Deleted, Renamed)
@spec RF06 - Strict Changed-Line Semantic Isolation
==============================================================================
"""

import re
from dataclasses import dataclass, field
from typing import Dict, Set, List, Optional

@dataclass
class ParsedDiffFile:
    """
    Structured representation of a file modification within a Git diff patch.
    """
    new_path: str
    old_path: Optional[str] = None
    status: str = "modified"  # 'modified', 'added', 'deleted', 'renamed'
    changed_lines: Set[int] = field(default_factory=set)
    additions_count: int = 0
    deletions_count: int = 0


def parse_unified_diff(diff_text: str) -> Dict[str, Set[int]]:
    """
    Parses a git unified diff string and returns a dictionary mapping
    file paths to sets of added/modified line numbers in the new file.
    Maintains 100% backward compatibility with VCS adapters.
    """
    if not diff_text or not diff_text.strip():
        return {}

    structured_files = parse_unified_diff_structured(diff_text)
    result: Dict[str, Set[int]] = {}
    for f in structured_files:
        if f.status != "deleted":
            result[f.new_path] = f.changed_lines
    return result


def parse_unified_diff_structured(diff_text: str) -> List[ParsedDiffFile]:
    """
    Parses a unified diff string into structured ParsedDiffFile objects,
    accurately detecting added, deleted, renamed, and modified files.
    """
    if not diff_text or not diff_text.strip():
        return []

    files: List[ParsedDiffFile] = []
    current_file: Optional[ParsedDiffFile] = None
    current_new_line: int = 0
    is_new_file = False
    is_deleted_file = False
    rename_from: Optional[str] = None
    rename_to: Optional[str] = None

    lines = diff_text.splitlines()
    for line in lines:
        if line.startswith("diff --git"):
            # If we had a previous file in progress, flush or finalize it
            if current_file:
                if is_new_file:
                    current_file.status = "added"
                elif is_deleted_file:
                    current_file.status = "deleted"
                elif rename_from and rename_to:
                    current_file.status = "renamed"
                    current_file.old_path = rename_from
                    current_file.new_path = rename_to

            is_new_file = False
            is_deleted_file = False
            rename_from = None
            rename_to = None

            match = re.search(r"a/(.*?)\s+b/(.*)$", line)
            if match:
                old_p = match.group(1).strip()
                new_p = match.group(2).strip()
                current_file = ParsedDiffFile(new_path=new_p, old_path=old_p, status="modified")
                files.append(current_file)
            else:
                match_b = re.search(r"b/(.*)$", line)
                if match_b:
                    new_p = match_b.group(1).strip()
                    current_file = ParsedDiffFile(new_path=new_p, status="modified")
                    files.append(current_file)
                else:
                    current_file = None

        elif line.startswith("new file mode"):
            is_new_file = True
            if current_file:
                current_file.status = "added"

        elif line.startswith("deleted file mode"):
            is_deleted_file = True
            if current_file:
                current_file.status = "deleted"

        elif line.startswith("rename from"):
            rename_from = line.replace("rename from", "").strip()
            if current_file:
                current_file.old_path = rename_from
                current_file.status = "renamed"

        elif line.startswith("rename to"):
            rename_to = line.replace("rename to", "").strip()
            if current_file:
                current_file.new_path = rename_to
                current_file.status = "renamed"

        elif line.startswith("--- "):
            old_p = line[4:].strip()
            if old_p == "/dev/null":
                is_new_file = True
                if current_file:
                    current_file.status = "added"
            elif old_p.startswith("a/"):
                if current_file:
                    current_file.old_path = old_p[2:]

        elif line.startswith("+++ "):
            new_p = line[4:].strip()
            if new_p == "/dev/null":
                is_deleted_file = True
                if current_file:
                    current_file.status = "deleted"
            elif new_p.startswith("b/"):
                if current_file:
                    current_file.new_path = new_p[2:]

        elif line.startswith("@@"):
            # Format: @@ -old_start,old_count +new_start,new_count @@
            hunk_match = re.search(r"\+(\d+)(?:,(\d+))?", line)
            if hunk_match:
                current_new_line = int(hunk_match.group(1))

        elif line.startswith("+") and not line.startswith("+++"):
            if current_file:
                current_file.changed_lines.add(current_new_line)
                current_file.additions_count += 1
            current_new_line += 1

        elif line.startswith("-") and not line.startswith("---"):
            if current_file:
                current_file.deletions_count += 1
            # Deletion in old file, does not advance new file line counter

        else:
            # Context line (starts with space ' ')
            current_new_line += 1

    # Finalize the last file in the loop
    if current_file:
        if is_new_file:
            current_file.status = "added"
        elif is_deleted_file:
            current_file.status = "deleted"
        elif rename_from and rename_to:
            current_file.status = "renamed"
            current_file.old_path = rename_from
            current_file.new_path = rename_to

    return files


def extract_changed_lines(diff_text: str, target_file: str) -> Set[int]:
    """
    Returns the set of changed line numbers for a specific target file.
    """
    all_changes = parse_unified_diff(diff_text)
    return all_changes.get(target_file, set())
