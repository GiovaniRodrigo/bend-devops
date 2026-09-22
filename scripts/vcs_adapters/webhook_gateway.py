"""
==============================================================================
Unified Webhook Gateway & Payload Ingestion Router
==============================================================================
@spec RF05 - Unified Webhook Gateway
==============================================================================
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

@dataclass
class VcsPullRequestEvent:
    """Represents an incoming PR or MR review event across VCS platforms."""
    platform: str
    repo_id: str
    pr_number: int
    commit_sha: str
    base_sha: str
    author: str
    title: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class WebhookGateway:
    """Ingests and normalizes webhook events from GitHub, GitLab, and Bitbucket."""

    @staticmethod
    def parse_github_event(payload: Dict[str, Any]) -> Optional[VcsPullRequestEvent]:
        """Parses GitHub pull_request webhook payload."""
        if "pull_request" not in payload:
            return None

        pr = payload["pull_request"]
        repo = payload.get("repository", {})
        
        return VcsPullRequestEvent(
            platform="github",
            repo_id=repo.get("full_name", ""),
            pr_number=payload.get("number", pr.get("number", 0)),
            commit_sha=pr.get("head", {}).get("sha", ""),
            base_sha=pr.get("base", {}).get("sha", ""),
            author=pr.get("user", {}).get("login", ""),
            title=pr.get("title", "")
        )

    @staticmethod
    def parse_gitlab_event(payload: Dict[str, Any]) -> Optional[VcsPullRequestEvent]:
        """Parses GitLab merge_request webhook payload."""
        if payload.get("object_kind") != "merge_request" and "object_attributes" not in payload:
            return None

        attrs = payload.get("object_attributes", {})
        project = payload.get("project", {})
        user = payload.get("user", {})

        return VcsPullRequestEvent(
            platform="gitlab",
            repo_id=str(project.get("path_with_namespace") or project.get("id", "")),
            pr_number=attrs.get("iid", 0),
            commit_sha=attrs.get("last_commit", {}).get("id", ""),
            base_sha=attrs.get("target_branch", "main"),
            author=user.get("username", ""),
            title=attrs.get("title", "")
        )

    @staticmethod
    def parse_bitbucket_event(payload: Dict[str, Any]) -> Optional[VcsPullRequestEvent]:
        """Parses Bitbucket pullrequest webhook payload."""
        if "pullrequest" not in payload and not payload.get("event_key", "").startswith("pullrequest"):
            return None

        pr = payload.get("pullrequest", {})
        repo = payload.get("repository", {})
        actor = payload.get("actor", {})

        source_commit = pr.get("source", {}).get("commit", {}).get("hash", "")
        dest_branch = pr.get("destination", {}).get("branch", {}).get("name", "main")

        return VcsPullRequestEvent(
            platform="bitbucket",
            repo_id=repo.get("full_name", ""),
            pr_number=pr.get("id", 0),
            commit_sha=source_commit,
            base_sha=dest_branch,
            author=actor.get("username") or actor.get("display_name", ""),
            title=pr.get("title", "")
        )

    @classmethod
    def handle_webhook(cls, payload: Dict[str, Any], platform_hint: Optional[str] = None) -> Optional[VcsPullRequestEvent]:
        """Auto-detects or uses platform_hint to parse incoming webhook payload."""
        if platform_hint:
            hint = platform_hint.lower()
            if hint == "github":
                return cls.parse_github_event(payload)
            elif hint == "gitlab":
                return cls.parse_gitlab_event(payload)
            elif hint == "bitbucket":
                return cls.parse_bitbucket_event(payload)

        # Auto-detection heuristic
        if "pull_request" in payload:
            return cls.parse_github_event(payload)
        elif payload.get("object_kind") == "merge_request" or "object_attributes" in payload:
            return cls.parse_gitlab_event(payload)
        elif "pullrequest" in payload or payload.get("event_key", "").startswith("pullrequest"):
            return cls.parse_bitbucket_event(payload)

        return None
