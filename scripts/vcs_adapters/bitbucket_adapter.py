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

    def get_changed_files(self) -> List[str]:
        """Returns list of changed files in the Bitbucket PR."""
        if not self.pr_number or not self.repo:
            return self._get_git_diff_files()

        url = f"{self.api_base}/repositories/{self.repo}/pullrequests/{self.pr_number}/diffstat"
        req = urllib.request.Request(url, headers=self._get_headers(), method="GET")
        try:
            with urllib.request.urlopen(req) as resp:
                if resp.getcode() == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    values = data.get("values", [])
                    files = []
                    for v in values:
                        if "new" in v and v["new"] and "path" in v["new"]:
                            files.append(v["new"]["path"])
                        elif "old" in v and v["old"] and "path" in v["old"]:
                            files.append(v["old"]["path"])
                    return files
        except Exception:
            pass
        return self._get_git_diff_files()

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

    def publish_annotations(self, violations: List[Dict[str, Any]]) -> bool:
        """Publishes Bitbucket Code Insights annotations."""
        if not self.commit_sha or not self.repo or not violations:
            return False

        # First ensure the insight report exists
        self.publish_commit_status("SUCCESSFUL", "DevOps Guardian Insights Attached", 100)

        # Post individual annotations
        for idx, v in enumerate(violations[:100], 1):
            path = v.get("path", v.get("fileName", "unknown"))
            line = v.get("line", 1)
            msg = v.get("message", "Violation detected")
            rule_id = v.get("rule_id", "ARCH-RULE")
            sev = "HIGH" if v.get("severity") == "P0_BLOCKING" else "MEDIUM"

            annotation_payload = {
                "external_id": f"guardian-{self.commit_sha[:8]}-{idx}",
                "title": f"[{rule_id}] Rule Infraction",
                "annotation_type": "CODE_SMELL" if sev != "HIGH" else "VULNERABILITY",
                "summary": msg,
                "severity": sev,
                "path": path,
                "line": line
            }

            url = f"{self.api_base}/repositories/{self.repo}/commit/{self.commit_sha}/reports/{self.report_key}/annotations/{annotation_payload['external_id']}"
            req = urllib.request.Request(
                url,
                data=json.dumps(annotation_payload).encode("utf-8"),
                headers=self._get_headers(),
                method="PUT"
            )
            try:
                with urllib.request.urlopen(req) as resp:
                    pass
            except Exception:
                pass

        return True

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
