"""
==============================================================================
Base Abstract VCS Adapter Contract
==============================================================================
@spec RF01, RF02, RF03 - Platform Adapters
==============================================================================
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class BaseVcsAdapter(ABC):
    """Abstract contract for VCS platform integrations."""

    def __init__(self, token: str, repo: str, pr_number: Optional[int] = None, commit_sha: Optional[str] = None):
        self.token = token
        self.repo = repo
        self.pr_number = pr_number
        self.commit_sha = commit_sha

    @abstractmethod
    def publish_commit_status(self, state: str, description: str, score: int) -> bool:
        """Sets commit status check on the HEAD SHA (e.g. success, failure, pending)."""
        pass

    @abstractmethod
    def post_pr_comment(self, markdown_body: str) -> bool:
        """Posts or updates a markdown comment on the PR/MR discussion thread."""
        pass

    @abstractmethod
    def generate_report_artifact(self, violations: List[Dict[str, Any]], score: int, approved: bool) -> str:
        """Generates platform-specific report format (SARIF / CodeQuality JSON)."""
        pass

    def build_markdown_summary(self, violations: List[Dict[str, Any]], score: int, approved: bool) -> str:
        """Constructs a clean markdown summary table with secret redaction."""
        status_badge = "✅ **PASSED**" if approved else "❌ **BLOCKED**"
        lines = [
            "## 🛡️ Bend DevOps Guardian Report",
            "",
            f"**Quality Gate Status**: {status_badge} · **Compliance Score**: `{score}/100`",
            "",
            "| Rule ID | Severity | File | Line | Message |",
            "| :--- | :--- | :--- | :--- | :--- |"
        ]

        if not violations:
            lines.append("| - | - | - | - | ✨ Zero architectural infractions detected. |")
        else:
            for v in violations:
                sev = v.get("severity", "P1_WARNING")
                rule = v.get("rule_id", "GENERIC")
                file_path = v.get("path", v.get("fileName", "unknown"))
                line = v.get("line", "-")
                msg = v.get("message", "")
                
                # RN02: Zero Secret Exposure - Redact secrets in comments
                if rule == "CULT04":
                    msg = "Hardcoded API secret or token detected [***REDACTED***]"

                lines.append(f"| `{rule}` | `{sev}` | `{file_path}` | `{line}` | {msg} |")

        lines.append("")
        lines.append("---")
        lines.append("*Enforced automatically by Bend DevOps Guardian (Bend HVM Engine)*")
        return "\n".join(lines)
