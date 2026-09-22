"""
==============================================================================
Bitbucket Pipelines & Code Insights Adapter
==============================================================================
@spec RF03 - Bitbucket Integration
==============================================================================
"""

import json
import urllib.request
from typing import List, Dict, Any, Optional
from scripts.vcs_adapters.base_adapter import BaseVcsAdapter

class BitbucketAdapter(BaseVcsAdapter):
    """Adapter for Bitbucket REST API, Code Insights, and Build Statuses."""

    def __init__(self, token: str, repo: str, pr_number: Optional[int] = None, commit_sha: Optional[str] = None):
        super().__init__(token, repo, pr_number, commit_sha)
        self.api_base = "https://api.bitbucket.org/2.0"
        self.report_key = "guardian-quality-gate"

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "User-Agent": "Bend-DevOps-Guardian-Gate"
        }

    def publish_commit_status(self, state: str, description: str, score: int) -> bool:
        """Sets commit build status via Bitbucket Commit Status API."""
        if not self.commit_sha or not self.repo:
            return False

        bb_state = "SUCCESSFUL" if state.upper() in ["SUCCESS", "SUCCESSFUL"] else "FAILED"
        payload = {
            "key": "guardian-devops-gate",
            "state": bb_state,
            "description": description[:255],
            "url": "https://github.com/oasis-tcs/sarif-spec"
        }

        url = f"{self.api_base}/repositories/{self.repo}/commit/{self.commit_sha}/statuses/build"
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
        """Posts a comment on the Bitbucket PR."""
        if not self.pr_number or not self.repo:
            return False

        url = f"{self.api_base}/repositories/{self.repo}/pullrequests/{self.pr_number}/comments"
        payload = {
            "content": {
                "raw": markdown_body
            }
        }
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
        """Generates Bitbucket Code Insights Report payload."""
        payload = {
            "title": "Bend DevOps Guardian",
            "details": f"Quality Gate Compliance Score: {score}/100. Total violations: {len(violations)}.",
            "report_type": "SECURITY",
            "reporter": "Guardian HVM Engine",
            "result": "PASSED" if approved else "FAILED",
            "data": [
                {
                    "title": "DevOps Quality Score",
                    "type": "NUMBER",
                    "value": score
                },
                {
                    "title": "Total Violations",
                    "type": "NUMBER",
                    "value": len(violations)
                }
            ]
        }
        return json.dumps(payload, indent=2)
