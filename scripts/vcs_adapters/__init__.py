"""
==============================================================================
VCS Platform Adapters Module
==============================================================================
"""

import os
from typing import Optional
from scripts.vcs_adapters.base_adapter import BaseVcsAdapter
from scripts.vcs_adapters.github_adapter import GitHubAdapter
from scripts.vcs_adapters.gitlab_adapter import GitLabAdapter
from scripts.vcs_adapters.bitbucket_adapter import BitbucketAdapter
from scripts.vcs_adapters.diff_parser import parse_unified_diff, extract_changed_lines

def detect_vcs_environment() -> Optional[str]:
    """Auto-detects the running CI/CD platform from standard environment variables."""
    if os.environ.get("GITHUB_ACTIONS") == "true":
        return "github"
    elif os.environ.get("GITLAB_CI") == "true":
        return "gitlab"
    elif os.environ.get("BITBUCKET_BUILD_NUMBER") is not None:
        return "bitbucket"
    return None

def get_vcs_adapter(
    platform: Optional[str] = None,
    token: Optional[str] = None,
    repo: Optional[str] = None,
    pr_number: Optional[int] = None,
    commit_sha: Optional[str] = None
) -> Optional[BaseVcsAdapter]:
    """Factory creating the appropriate VCS adapter instance."""
    resolved_platform = platform or detect_vcs_environment()
    if not resolved_platform:
        return None

    resolved_platform = resolved_platform.lower()

    if resolved_platform == "github":
        resolved_token = token or os.environ.get("GITHUB_TOKEN", "")
        resolved_repo = repo or os.environ.get("GITHUB_REPOSITORY", "")
        resolved_sha = commit_sha or os.environ.get("GITHUB_SHA", "")
        pr_str = os.environ.get("GITHUB_PR_NUMBER")
        resolved_pr = pr_number or (int(pr_str) if pr_str and pr_str.isdigit() else None)
        return GitHubAdapter(resolved_token, resolved_repo, resolved_pr, resolved_sha)

    elif resolved_platform == "gitlab":
        resolved_token = token or os.environ.get("GITLAB_TOKEN", os.environ.get("CI_JOB_TOKEN", ""))
        resolved_repo = repo or os.environ.get("CI_PROJECT_PATH", os.environ.get("CI_PROJECT_ID", ""))
        resolved_sha = commit_sha or os.environ.get("CI_COMMIT_SHA", "")
        mr_str = os.environ.get("CI_MERGE_REQUEST_IID")
        resolved_pr = pr_number or (int(mr_str) if mr_str and mr_str.isdigit() else None)
        return GitLabAdapter(resolved_token, resolved_repo, resolved_pr, resolved_sha)

    elif resolved_platform == "bitbucket":
        resolved_token = token or os.environ.get("BITBUCKET_TOKEN", "")
        resolved_repo = repo or os.environ.get("BITBUCKET_REPO_FULL_NAME", "")
        resolved_sha = commit_sha or os.environ.get("BITBUCKET_COMMIT", "")
        pr_str = os.environ.get("BITBUCKET_PR_ID")
        resolved_pr = pr_number or (int(pr_str) if pr_str and pr_str.isdigit() else None)
        return BitbucketAdapter(resolved_token, resolved_repo, resolved_pr, resolved_sha)

    return None

__all__ = [
    "BaseVcsAdapter",
    "GitHubAdapter",
    "GitLabAdapter",
    "BitbucketAdapter",
    "parse_unified_diff",
    "extract_changed_lines",
    "detect_vcs_environment",
    "get_vcs_adapter"
]
