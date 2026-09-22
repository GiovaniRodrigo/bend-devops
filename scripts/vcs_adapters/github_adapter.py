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
