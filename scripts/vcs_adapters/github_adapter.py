"""
==============================================================================
GitHub Actions & Check Runs Adapter
==============================================================================
@spec RF01 - GitHub Integration
==============================================================================
"""

import json
import urllib.request
import urllib.error
from typing import List, Dict, Any, Optional
from scripts.vcs_adapters.base_adapter import BaseVcsAdapter

class GitHubAdapter(BaseVcsAdapter):
    """Adapter for GitHub REST API, Check Runs, and SARIF output."""

    def __init__(self, token: str, repo: str, pr_number: Optional[int] = None, commit_sha: Optional[str] = None):
        super().__init__(token, repo, pr_number, commit_sha)
        self.api_base = "https://api.github.com"

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Bend-DevOps-Guardian-Gate"
        }

    def get_changed_files(self) -> List[str]:
        """Returns list of modified or added files in the GitHub PR."""
        if not self.pr_number or not self.repo:
            return self._get_git_diff_files()

        url = f"{self.api_base}/repos/{self.repo}/pulls/{self.pr_number}/files"
        req = urllib.request.Request(url, headers=self._get_headers(), method="GET")
        try:
            with urllib.request.urlopen(req) as resp:
                if resp.getcode() == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    return [item.get("filename") for item in data if "filename" in item]
        except Exception:
            pass
        return self._get_git_diff_files()

    def publish_commit_status(self, state: str, description: str, score: int) -> bool:
        """Sets commit status check via GitHub Statuses API."""
        if not self.commit_sha or not self.repo:
            return False

        gh_state = "success" if state == "success" else "failure"
        payload = {
            "state": gh_state,
            "description": description[:140],
            "context": "guardian/devops-architecture-gate"
        }

        url = f"{self.api_base}/repos/{self.repo}/statuses/{self.commit_sha}"
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
        """Posts a review comment to the GitHub PR discussion."""
        if not self.pr_number or not self.repo:
            return False

        url = f"{self.api_base}/repos/{self.repo}/issues/{self.pr_number}/comments"
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
        """Publishes inline Check Run annotations to GitHub."""
        if not self.commit_sha or not self.repo:
            return False

        annotations = []
        for v in violations:
            path = v.get("path", v.get("fileName", "unknown"))
            line = v.get("line", 1)
            msg = v.get("message", "Violation detected")
            rule_id = v.get("rule_id", "ARCH-RULE")
            sev_level = "failure" if v.get("severity") == "P0_BLOCKING" else "warning"

            annotations.append({
                "path": path,
                "start_line": line,
                "end_line": line,
                "annotation_level": sev_level,
                "message": msg,
                "title": f"DevOps Guardian: {rule_id}"
            })

        payload = {
            "name": "Bend DevOps Guardian",
            "head_sha": self.commit_sha,
            "status": "completed",
            "conclusion": "failure" if any(v.get("severity") == "P0_BLOCKING" for v in violations) else "success",
            "output": {
                "title": "Architecture & Engineering Standards Audit",
                "summary": f"Audited {len(violations)} infractions.",
                "annotations": annotations[:50]  # GitHub Check API limit: 50 per call
            }
        }

        url = f"{self.api_base}/repos/{self.repo}/check-runs"
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

    def generate_report_artifact(self, violations: List[Dict[str, Any]], score: int, approved: bool) -> str:
        """Generates a valid SARIF v2.1.0 document."""
        sarif_results = []
        for v in violations:
            sarif_results.append({
                "ruleId": v.get("rule_id", "ARCH-LAYER-01"),
                "level": "error" if v.get("severity") == "P0_BLOCKING" else "warning",
                "message": {
                    "text": v.get("message", "Architectural violation")
                },
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {
                                "uri": v.get("path", v.get("fileName", "unknown"))
                            },
                            "region": {
                                "startLine": v.get("line", 1)
                            }
                        }
                    }
                ]
            })

        sarif_doc = {
            "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
            "version": "2.1.0",
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": "Bend DevOps Guardian",
                            "version": "1.0.0",
                            "informationUri": "https://github.com/oasis-tcs/sarif-spec",
                            "rules": [
                                {
                                    "id": "ARCH-LAYER-01",
                                    "shortDescription": {"text": "Zero Presentation Code in Domain, Models & Controllers"}
                                },
                                {
                                    "id": "ARCH-LAYER-02",
                                    "shortDescription": {"text": "Zero Direct Database Queries in Presentation & Views"}
                                },
                                {
                                    "id": "ARCH-LAYER-03",
                                    "shortDescription": {"text": "Zero Transport Protocol Coupling in Domain Models"}
                                },
                                {
                                    "id": "CULT01",
                                    "shortDescription": {"text": "Zero Lazy Code (TODO/FIXME/pass)"}
                                },
                                {
                                    "id": "CULT04",
                                    "shortDescription": {"text": "Zero Hardcoded Secrets"}
                                }
                            ]
                        }
                    },
                    "results": sarif_results
                }
            ]
        }
        return json.dumps(sarif_doc, indent=2)
