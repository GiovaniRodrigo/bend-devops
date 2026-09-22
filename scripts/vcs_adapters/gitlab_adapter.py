"""
=============================================================================
GitLab CI/CD & Code Quality Adapter
=============================================================================
@spec RF02 - GitLab Integration
=============================================================================
"""

import json
import hashlib
import urllib.request
import urllib.parse
from typing import List, Dict, Any, Optional
from scripts.vcs_adapters.base_adapter import BaseVcsAdapter

class GitLabAdapter(BaseVcsAdapter):
    """Adapter for GitLab REST API, MR Notes, and Code Quality JSON."""

    def __init__(self, token: str, repo: str, pr_number: Optional[int] = None, commit_sha: Optional[str] = None):
        super().__init__(token, repo, pr_number, commit_sha)
        self.api_base = "https://gitlab.com/api/v4"
        self.project_id = urllib.parse.quote_plus(repo) if repo else ""

    def _get_headers(self) -> Dict[str, str]:
        return {
            "PRIVATE-TOKEN": self.token,
            "Content-Type": "application/json",
            "User-Agent": "Bend-DevOps-Guardian-Gate"
        }

    def get_changed_files(self) -> List[str]:
        """Returns list of changed files in the GitLab MR."""
        if not self.pr_number or not self.project_id:
            return self._get_git_diff_files()

        url = f"{self.api_base}/projects/{self.project_id}/merge_requests/{self.pr_number}/changes"
        req = urllib.request.Request(url, headers=self._get_headers(), method="GET")
        try:
            with urllib.request.urlopen(req) as resp:
                if resp.getcode() == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    changes = data.get("changes", [])
                    return [c.get("new_path", c.get("old_path")) for c in changes if "new_path" in c or "old_path" in c]
        except Exception:
            pass
        return self._get_git_diff_files()

    def publish_commit_status(self, state: str, description: str, score: int) -> bool:
        """Sets commit build status via GitLab Statuses API."""
        if not self.commit_sha or not self.project_id:
            return False

        gl_state = "success" if state == "success" else "failed"
        payload = {
            "state": gl_state,
            "description": description[:140],
            "name": "guardian/devops-architecture-gate"
        }

        url = f"{self.api_base}/projects/{self.project_id}/statuses/{self.commit_sha}"
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=self._get_headers(),
            method="POST"
        )
        try:
            with urllib.request.urlopen(req) as resp:
                return resp.getcode() in [200, 201]
        except Exception:
            return False

    def post_pr_comment(self, markdown_body: str) -> bool:
        """Posts or updates an MR discussion note."""
        if not self.pr_number or not self.project_id:
            return False

        url = f"{self.api_base}/projects/{self.project_id}/merge_requests/{self.pr_number}/notes"
        payload = {"body": markdown_body}
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=self._get_headers(),
            method="POST"
        )
        try:
            with urllib.request.urlopen(req) as resp:
                return resp.getcode() in [200, 201]
        except Exception:
            return False

    def publish_annotations(self, violations: List[Dict[str, Any]]) -> bool:
        """Publishes MR discussions / notes for infractions in GitLab."""
        if not self.pr_number or not self.project_id or not violations:
            return False

        summary_note = self.build_markdown_summary(violations, score=0, approved=False)
        return self.post_pr_comment(summary_note)

    def generate_report_artifact(self, violations: List[Dict[str, Any]], score: int, approved: bool) -> str:
        """Generates standard GitLab Code Quality JSON (gl-code-quality-report.json)."""
        gl_issues = []
        for v in violations:
            path = v.get("path", v.get("fileName", "unknown"))
            line = v.get("line", 1)
            msg = v.get("message", "Architectural Violation")
            sev = "blocker" if v.get("severity") == "P0_BLOCKING" else "major"
            
            fingerprint = hashlib.md5(f"{path}:{line}:{v.get('rule_id')}".encode("utf-8")).hexdigest()
            gl_issues.append({
                "description": f"[{v.get('rule_id')}] {msg}",
                "fingerprint": fingerprint,
                "severity": sev,
                "location": {
                    "path": path,
                    "lines": {
                        "begin": line
                    }
                }
            })
        return json.dumps(gl_issues, indent=2)
