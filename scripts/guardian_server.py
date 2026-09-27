#!/usr/bin/env python3
"""
==============================================================================
Bend DevOps Guardian — Unified Backend API & Static Web Server
==============================================================================
Provides the single source of truth for:
1. Real Local Git Repository Discovery & Inspection
2. Real GitHub Repository & Branch Integration
3. Real Working Tree & Branch Diff Extraction
4. Real Architecture Rules & Profiles Discovery
5. Real Parallel AST Audit Execution (Bend HVM)
6. Explicit Mock Scenario Controller (when flag is set)
==============================================================================
"""

import sys
import os
import json
import re
import argparse
import subprocess
import urllib.request
import urllib.parse
import datetime
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from typing import Dict, Any, List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.token_filter import load_guardianignore
from scripts.guardian_mock import generate_scenario_data
from scripts.rule_model import (
    RuleDefinition,
    RuleType,
    RuleSeverity,
    RuleStatus,
    RuleTier
)
from scripts.rule_normalizer import RuleNormalizer
from scripts.rule_test_engine import RuleTestEngine, RegexSafetyValidator
from scripts.rule_registry import RuleRegistry

RULES_BASE_DIR = REPO_ROOT / "backend" / "rules"
FRONTEND_DIST_DIRS = [
    REPO_ROOT / "frontend" / "dist" / "frontend" / "browser",
    REPO_ROOT / "frontend" / "dist" / "frontend"
]

def get_frontend_root() -> Path:
    for d in FRONTEND_DIST_DIRS:
        if d.exists() and (d / "index.html").exists():
            return d
    return FRONTEND_DIST_DIRS[0]

def discover_local_repositories() -> List[Dict[str, Any]]:
    """Discovers all real Git repositories in current workspace and parent projects directory."""
    repos = []
    checked_paths = set()

    # 1. Current workspace repository
    try:
        is_git = subprocess.run(
            ["git", "-C", str(REPO_ROOT), "rev-parse", "--is-inside-work-tree"],
            capture_output=True, text=True, timeout=2
        ).stdout.strip()
        if is_git == "true":
            top_level = subprocess.run(
                ["git", "-C", str(REPO_ROOT), "rev-parse", "--show-toplevel"],
                capture_output=True, text=True, timeout=2
            ).stdout.strip()
            top_path = Path(top_level)
            checked_paths.add(str(top_path))
            
            remote = subprocess.run(
                ["git", "-C", str(top_path), "config", "--get", "remote.origin.url"],
                capture_output=True, text=True, timeout=2
            ).stdout.strip()
            branch = subprocess.run(
                ["git", "-C", str(top_path), "branch", "--show-current"],
                capture_output=True, text=True, timeout=2
            ).stdout.strip() or "main"
            
            raw_branches = subprocess.run(
                ["git", "-C", str(top_path), "branch", "--list"],
                capture_output=True, text=True, timeout=2
            ).stdout.splitlines()
            branches = [b.strip().lstrip("* ") for b in raw_branches if b.strip()]
            if not branches:
                branches = [branch]
                
            head = subprocess.run(
                ["git", "-C", str(top_path), "rev-parse", "--short", "HEAD"],
                capture_output=True, text=True, timeout=2
            ).stdout.strip()
            head_msg = subprocess.run(
                ["git", "-C", str(top_path), "log", "-1", "--format=%s"],
                capture_output=True, text=True, timeout=2
            ).stdout.strip()
            status = subprocess.run(
                ["git", "-C", str(top_path), "status", "--porcelain"],
                capture_output=True, text=True, timeout=2
            ).stdout.strip()

            repos.append({
                "id": top_path.name,
                "name": top_path.name,
                "path": str(top_path),
                "remoteUrl": remote,
                "currentBranch": branch,
                "branches": branches,
                "headCommit": head,
                "headCommitMessage": head_msg,
                "isClean": len(status) == 0,
                "isCurrent": True
            })
    except Exception:
        pass

    # 2. Check sibling repositories in parent directory (/home/isabelle/projects)
    parent = REPO_ROOT.parent
    if parent.exists() and parent.is_dir():
        for item in sorted(parent.iterdir()):
            if item.is_dir() and str(item) not in checked_paths and (item / ".git").exists():
                try:
                    remote = subprocess.run(
                        ["git", "-C", str(item), "config", "--get", "remote.origin.url"],
                        capture_output=True, text=True, timeout=1
                    ).stdout.strip()
                    branch = subprocess.run(
                        ["git", "-C", str(item), "branch", "--show-current"],
                        capture_output=True, text=True, timeout=1
                    ).stdout.strip() or "main"
                    raw_branches = subprocess.run(
                        ["git", "-C", str(item), "branch", "--list"],
                        capture_output=True, text=True, timeout=1
                    ).stdout.splitlines()
                    branches = [b.strip().lstrip("* ") for b in raw_branches if b.strip()]
                    head = subprocess.run(
                        ["git", "-C", str(item), "rev-parse", "--short", "HEAD"],
                        capture_output=True, text=True, timeout=1
                    ).stdout.strip()
                    head_msg = subprocess.run(
                        ["git", "-C", str(item), "log", "-1", "--format=%s"],
                        capture_output=True, text=True, timeout=1
                    ).stdout.strip()
                    status = subprocess.run(
                        ["git", "-C", str(item), "status", "--porcelain"],
                        capture_output=True, text=True, timeout=1
                    ).stdout.strip()

                    repos.append({
                        "id": item.name,
                        "name": item.name,
                        "path": str(item),
                        "remoteUrl": remote,
                        "currentBranch": branch,
                        "branches": branches or [branch],
                        "headCommit": head,
                        "headCommitMessage": head_msg,
                        "isClean": len(status) == 0,
                        "isCurrent": False
                    })
                except Exception:
                    pass

    return repos

CUSTOM_REPOSITORIES: Dict[str, Dict[str, Any]] = {}

def inspect_local_repository_path(path_str: str) -> Dict[str, Any]:
    """Validates if path_str is an existing Git repository and extracts full metadata."""
    if not path_str or not path_str.strip():
        return {
            "valid": False,
            "errorType": "EMPTY_PATH",
            "error": "Directory path cannot be empty"
        }
    
    clean_str = os.path.expanduser(path_str.strip())
    p = Path(clean_str).resolve()
    
    if not p.exists():
        return {
            "valid": False,
            "errorType": "NOT_FOUND",
            "error": f"Directory does not exist: {clean_str}",
            "selectedPath": str(p)
        }
    if not p.is_dir():
        return {
            "valid": False,
            "errorType": "NOT_DIR",
            "error": f"Path is not a directory: {clean_str}",
            "selectedPath": str(p)
        }
        
    try:
        is_git_res = subprocess.run(
            ["git", "-C", str(p), "rev-parse", "--is-inside-work-tree"],
            capture_output=True, text=True, timeout=3
        )
        if is_git_res.returncode != 0 or is_git_res.stdout.strip() != "true":
            return {
                "valid": False,
                "errorType": "NOT_GIT",
                "error": f"Directory is not a Git repository (no .git found): {clean_str}",
                "selectedPath": str(p)
            }
            
        top_level_res = subprocess.run(
            ["git", "-C", str(p), "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=3
        )
        if top_level_res.returncode != 0 or not top_level_res.stdout.strip():
            return {
                "valid": False,
                "errorType": "GIT_ERROR",
                "error": f"Could not determine Git repository root for: {clean_str}",
                "selectedPath": str(p)
            }
            
        top_path = Path(top_level_res.stdout.strip()).resolve()
        is_subdir = (top_path != p)
        
        # Remote URL
        remote = subprocess.run(
            ["git", "-C", str(top_path), "config", "--get", "remote.origin.url"],
            capture_output=True, text=True, timeout=2
        ).stdout.strip()
        if not remote:
            remote = subprocess.run(
                ["git", "-C", str(top_path), "remote", "get-url", "origin"],
                capture_output=True, text=True, timeout=2
            ).stdout.strip()

        # Branch (Detached HEAD aware)
        branch = subprocess.run(
            ["git", "-C", str(top_path), "branch", "--show-current"],
            capture_output=True, text=True, timeout=2
        ).stdout.strip()
        if not branch:
            detached_check = subprocess.run(
                ["git", "-C", str(top_path), "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True, text=True, timeout=2
            ).stdout.strip()
            if detached_check == "HEAD":
                branch = "Detached HEAD"
            else:
                branch = detached_check or "Detached HEAD"
        
        # Real local branches
        raw_branches = subprocess.run(
            ["git", "-C", str(top_path), "for-each-ref", "--format=%(refname:short)", "refs/heads/"],
            capture_output=True, text=True, timeout=2
        ).stdout.splitlines()
        branches = [b.strip() for b in raw_branches if b.strip()]
        if not branches:
            raw_branches_fallback = subprocess.run(
                ["git", "-C", str(top_path), "branch", "--list"],
                capture_output=True, text=True, timeout=2
            ).stdout.splitlines()
            branches = [b.strip().lstrip("* ") for b in raw_branches_fallback if b.strip()]
        if not branches and branch and branch != "Detached HEAD":
            branches = [branch]
            
        head = subprocess.run(
            ["git", "-C", str(top_path), "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=2
        ).stdout.strip()
        head_msg = subprocess.run(
            ["git", "-C", str(top_path), "log", "-1", "--format=%s"],
            capture_output=True, text=True, timeout=2
        ).stdout.strip()
        status = subprocess.run(
            ["git", "-C", str(top_path), "status", "--porcelain"],
            capture_output=True, text=True, timeout=2
        ).stdout.strip()

        repo_obj = {
            "id": top_path.name,
            "name": top_path.name,
            "path": str(top_path),
            "selectedPath": str(p),
            "repositoryRoot": str(top_path),
            "isSubdirectory": is_subdir,
            "remoteUrl": remote,
            "currentBranch": branch,
            "branches": branches,
            "headCommit": head,
            "headCommitMessage": head_msg,
            "isClean": len(status) == 0,
            "isCurrent": str(top_path) == str(REPO_ROOT.resolve())
        }
        return {
            "valid": True,
            "selectedPath": str(p),
            "isSubdirectory": is_subdir,
            "repositoryRoot": str(top_path),
            "repository": repo_obj
        }
    except Exception as e:
        return {
            "valid": False,
            "errorType": "GIT_ERROR",
            "error": f"Git inspection failed: {str(e)}",
            "selectedPath": str(p)
        }

def browse_local_directories(base_path: Optional[str] = None) -> Dict[str, Any]:
    """Browses directories at base_path and identifies Git repositories."""
    if not base_path or not base_path.strip():
        target = REPO_ROOT.parent if REPO_ROOT.parent.exists() else REPO_ROOT
    else:
        target = Path(os.path.expanduser(base_path.strip())).resolve()
    
    if not target.exists() or not target.is_dir():
        target = REPO_ROOT.parent if REPO_ROOT.parent.exists() else REPO_ROOT

    parent_dir = str(target.parent) if target.parent != target else None
    
    # Check if target itself is a git repository
    target_git = False
    try:
        is_git = subprocess.run(
            ["git", "-C", str(target), "rev-parse", "--is-inside-work-tree"],
            capture_output=True, text=True, timeout=1
        ).stdout.strip()
        target_git = is_git == "true"
    except Exception:
        pass

    dirs = []
    try:
        for item in sorted(target.iterdir()):
            if item.is_dir() and not item.name.startswith("."):
                is_item_git = (item / ".git").exists()
                git_info = None
                if is_item_git:
                    try:
                        branch = subprocess.run(
                            ["git", "-C", str(item), "branch", "--show-current"],
                            capture_output=True, text=True, timeout=1
                        ).stdout.strip() or "main"
                        head = subprocess.run(
                            ["git", "-C", str(item), "rev-parse", "--short", "HEAD"],
                            capture_output=True, text=True, timeout=1
                        ).stdout.strip()
                        status = subprocess.run(
                            ["git", "-C", str(item), "status", "--porcelain"],
                            capture_output=True, text=True, timeout=1
                        ).stdout.strip()
                        git_info = {
                            "branch": branch,
                            "headCommit": head,
                            "isClean": len(status) == 0
                        }
                    except Exception:
                        pass

                dirs.append({
                    "name": item.name,
                    "path": str(item),
                    "isGit": is_item_git,
                    "gitInfo": git_info
                })
    except Exception:
        pass

    return {
        "currentPath": str(target),
        "parentPath": parent_dir,
        "isCurrentPathGit": target_git,
        "directories": dirs
    }

def get_repository_by_id(repo_id: str) -> Optional[Dict[str, Any]]:
    # Check custom registry first
    if repo_id in CUSTOM_REPOSITORIES:
        return CUSTOM_REPOSITORIES[repo_id]

    # Check if repo_id is a direct path
    if "/" in repo_id or repo_id.startswith("~"):
        res = inspect_local_repository_path(repo_id)
        if res.get("valid") and "repository" in res:
            repo_obj = res["repository"]
            CUSTOM_REPOSITORIES[repo_obj["id"]] = repo_obj
            CUSTOM_REPOSITORIES[repo_obj["path"]] = repo_obj
            return repo_obj

    repos = discover_local_repositories()
    for r in repos:
        if r["id"] == repo_id or r["name"] == repo_id or r["path"] == repo_id:
            return r
    return None

def get_working_tree_info(repo_path: str) -> Dict[str, Any]:
    """Inspects real git working tree status and diff."""
    p = Path(repo_path)
    if not p.exists():
        return {"error": "Repository path not found", "isClean": True, "changedFiles": [], "totalAdditions": 0, "totalDeletions": 0, "diff": ""}
    
    try:
        status_out = subprocess.run(
            ["git", "-C", str(p), "status", "--porcelain"],
            capture_output=True, text=True, timeout=2
        ).stdout.strip()

        if not status_out:
            return {
                "isClean": True,
                "changedFiles": [],
                "totalAdditions": 0,
                "totalDeletions": 0,
                "diff": ""
            }

        diff_out = subprocess.run(
            ["git", "-C", str(p), "diff", "HEAD"],
            capture_output=True, text=True, timeout=3
        ).stdout

        changed_files = []
        total_add = 0
        total_del = 0

        for line in status_out.splitlines():
            if len(line) >= 3:
                st = line[:2].strip()
                fname = line[3:].strip()
                status_type = "modified"
                if "A" in st or "?" in st:
                    status_type = "added"
                elif "D" in st:
                    status_type = "deleted"

                # Estimate file additions/deletions from diff
                f_add = 0
                f_del = 0
                for dline in diff_out.splitlines():
                    if dline.startswith("+") and not dline.startswith("+++"):
                        f_add += 1
                    elif dline.startswith("-") and not dline.startswith("---"):
                        f_del += 1
                
                changed_files.append({
                    "name": fname,
                    "status": status_type,
                    "additions": f_add,
                    "deletions": f_del
                })
                total_add += f_add
                total_del += f_del

        return {
            "isClean": False,
            "changedFiles": changed_files,
            "totalAdditions": total_add,
            "totalDeletions": total_del,
            "diff": diff_out
        }
    except Exception as e:
        return {"error": str(e), "isClean": True, "changedFiles": [], "totalAdditions": 0, "totalDeletions": 0, "diff": ""}

def validate_commit_sha(repo_path: str, sha: str) -> Dict[str, Any]:
    """Validates if commit SHA really exists in Git repository."""
    p = Path(repo_path)
    if not p.exists() or not sha or len(sha.strip()) < 4:
        return {"valid": False, "error": "Commit not found"}

    try:
        full_sha = subprocess.run(
            ["git", "-C", str(p), "rev-parse", "--verify", f"{sha.strip()}^{{commit}}"],
            capture_output=True, text=True, timeout=2
        ).stdout.strip()

        if not full_sha:
            return {"valid": False, "error": "Commit not found"}

        info = subprocess.run(
            ["git", "-C", str(p), "log", "-1", "--format=%h|%an|%ad|%s", full_sha],
            capture_output=True, text=True, timeout=2
        ).stdout.strip().split("|")

        return {
            "valid": True,
            "sha": full_sha,
            "shortSha": info[0] if len(info) > 0 else full_sha[:7],
            "author": info[1] if len(info) > 1 else "",
            "date": info[2] if len(info) > 2 else "",
            "message": info[3] if len(info) > 3 else ""
        }
    except Exception:
        return {"valid": False, "error": "Commit not found"}

def get_github_repositories() -> Dict[str, Any]:
    """Checks GitHub connection and lists repositories if token is configured."""
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        # Check git credential or config
        try:
            token = subprocess.run(
                ["git", "config", "--get", "github.token"],
                capture_output=True, text=True, timeout=1
            ).stdout.strip()
        except Exception:
            token = None

    if not token:
        return {
            "connected": False,
            "error": "GitHub connection required",
            "message": "GitHub API integration is not authenticated. Please set GITHUB_TOKEN or authenticate via GitHub CLI to query remote repositories.",
            "repositories": []
        }

    try:
        req = urllib.request.Request(
            "https://api.github.com/user/repos?per_page=30&sort=updated",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "Bend-DevOps-Guardian"
            }
        )
        with urllib.request.urlopen(req, timeout=4) as resp:
            if resp.getcode() == 200:
                data = json.loads(resp.read().decode("utf-8"))
                repos = []
                for item in data:
                    repos.append({
                        "id": item.get("name"),
                        "name": item.get("name"),
                        "fullName": item.get("full_name"),
                        "owner": item.get("owner", {}).get("login"),
                        "defaultBranch": item.get("default_branch", "main"),
                        "url": item.get("html_url")
                    })
                return {
                    "connected": True,
                    "repositories": repos
                }
    except Exception as e:
        return {
            "connected": False,
            "error": f"GitHub API request failed: {e}",
            "repositories": []
        }

def load_real_rules_manifest() -> List[Dict[str, Any]]:
    """Loads all real declarative rules from backend/rules/."""
    rules_map = {}
    
    # 1. 2_rules/ directory
    rules_dir = RULES_BASE_DIR / "2_rules"
    if rules_dir.exists():
        for p in rules_dir.glob("*.json"):
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                for r in data.get("rules", []):
                    rules_map[r["id"]] = r
            except Exception:
                pass

    # 2. backend/rules/architecture_*.json
    for p in RULES_BASE_DIR.glob("architecture_*.json"):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            for r in data.get("rules", []):
                rules_map[r["id"]] = r
        except Exception:
            pass

    # 3. culture_manifesto.json
    culture_path = RULES_BASE_DIR / "culture_manifesto.json"
    if culture_path.exists():
        try:
            data = json.loads(culture_path.read_text(encoding="utf-8"))
            for r in data.get("rules", []):
                rules_map[r["id"]] = r
        except Exception:
            pass

    return list(rules_map.values())

def load_real_architecture_profiles() -> List[Dict[str, Any]]:
    """Loads all real architecture profiles from backend/rules/1_architectures/."""
    profiles = []
    arch_dir = RULES_BASE_DIR / "1_architectures"
    if arch_dir.exists():
        for p in sorted(arch_dir.glob("*.json")):
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                profiles.append(data)
            except Exception:
                pass
    return profiles

class GuardianRequestHandler(SimpleHTTPRequestHandler):
    """Handles both static frontend assets and REST API endpoints."""

    is_mock_mode: bool = False
    mock_scenario: Optional[str] = None

    def __init__(self, *args, **kwargs):
        frontend_root = get_frontend_root()
        super().__init__(*args, directory=str(frontend_root), **kwargs)

    def _send_json(self, data: Any, status: int = 200):
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        # 0. API: Health Check
        if path == "/api/healthz":
            reg = RuleRegistry.get_instance()
            self._send_json({
                "status": "UP",
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "version": "2.0.0",
                "engine": "Bend HVM",
                "rulesLoaded": len(reg.list()),
                "rulesActive": len(reg.list(active_only=True)),
                "platform": "linux"
            })
            return

        # 1. API: System Status
        if path == "/api/system/status":
            self._send_json({
                "isMockMode": GuardianRequestHandler.is_mock_mode,
                "mockScenario": GuardianRequestHandler.mock_scenario,
                "version": "2.0.0",
                "platform": "linux",
                "repoRoot": str(REPO_ROOT)
            })
            return

        # 2. API: Local Repositories Discovery
        if path == "/api/repositories/local":
            repos = discover_local_repositories()
            self._send_json({"repositories": repos, "count": len(repos)})
            return

        # 3. API: GitHub Repositories Discovery
        if path == "/api/repositories/github":
            res = get_github_repositories()
            self._send_json(res, status=200 if res.get("connected") else 200)
            return

        # 4. API: Repository Branches
        match_branches = re.match(r"^/api/repositories/([^/]+)/branches$", path)
        if match_branches:
            repo_id = match_branches.group(1)
            repo = get_repository_by_id(repo_id)
            if not repo:
                self._send_json({"error": "Repository not found", "branches": []}, status=404)
            else:
                self._send_json({"branches": repo["branches"], "current": repo["currentBranch"]})
            return

        # 5. API: Working Tree Status & Diff
        match_wt = re.match(r"^/api/repositories/([^/]+)/working-tree$", path)
        if match_wt:
            repo_id = match_wt.group(1)
            repo = get_repository_by_id(repo_id)
            if not repo:
                self._send_json({"error": "Repository not found", "isClean": True}, status=404)
            else:
                info = get_working_tree_info(repo["path"])
                self._send_json(info)
            return

        # 5b. API: Repository File Content
        match_file = re.match(r"^/api/repositories/([^/]+)/file$", path)
        if match_file:
            repo_id = match_file.group(1)
            file_rel_path = query.get("path", [""])[0]
            repo = get_repository_by_id(repo_id)
            if not repo or not file_rel_path:
                self._send_json({"error": "File or repository not found", "content": ""}, status=404)
            else:
                full_p = (Path(repo["path"]) / file_rel_path).resolve()
                if full_p.exists() and full_p.is_file():
                    try:
                        content = full_p.read_text(encoding="utf-8", errors="replace")
                        self._send_json({"path": file_rel_path, "content": content, "linesCount": len(content.splitlines())})
                    except Exception as e:
                        self._send_json({"error": str(e), "content": ""}, status=500)
                else:
                    self._send_json({"error": "File not found", "content": ""}, status=404)
            return

        # 6. API: Rules Metadata & Catalogs
        if path == "/api/rules/categories":
            self._send_json({"categories": RuleRegistry.get_instance().get_categories()})
            return

        if path == "/api/rules/languages":
            self._send_json({"languages": RuleRegistry.get_instance().get_languages()})
            return

        if path == "/api/rules/types":
            self._send_json({"types": RuleRegistry.get_instance().get_types()})
            return

        if path == "/api/rules/severities":
            self._send_json({"severities": RuleRegistry.get_instance().get_severities()})
            return

        if path == "/api/rules/statuses":
            self._send_json({"statuses": RuleRegistry.get_instance().get_statuses()})
            return

        if path == "/api/rules/audit-trail":
            rule_id = query.get("ruleId", [None])[0]
            self._send_json({"auditTrail": RuleRegistry.get_instance().get_audit_trail(rule_id=rule_id)})
            return

        if path == "/api/rules/export/all":
            self._send_json(RuleRegistry.get_instance().export_all())
            return

        match_rule_export = re.match(r"^/api/rules/([^/]+)/export$", path)
        if match_rule_export:
            rule_id = match_rule_export.group(1)
            exported = RuleRegistry.get_instance().export_rule(rule_id)
            if exported:
                self._send_json(exported)
            else:
                self._send_json({"error": f"Rule '{rule_id}' not found"}, status=404)
            return

        match_single_rule = re.match(r"^/api/rules/([A-Za-z0-9_-]+)$", path)
        if match_single_rule:
            rule_id = match_single_rule.group(1)
            rule = RuleRegistry.get_instance().get(rule_id)
            if rule:
                self._send_json({"rule": rule.to_dict()})
            else:
                self._send_json({"error": f"Rule '{rule_id}' not found"}, status=404)
            return

        # 6b. API: Filterable Rules List
        if path == "/api/rules":
            search_q = query.get("search", [None])[0]
            cat = query.get("category", [None])[0]
            sev = query.get("severity", [None])[0]
            lang = query.get("language", [None])[0]
            stat = query.get("status", [None])[0]
            r_type = query.get("type", [None])[0]
            arch = query.get("architecture", [None])[0]
            tier = query.get("tier", [None])[0]
            active_only = query.get("activeOnly", ["false"])[0].lower() == "true"

            rules = RuleRegistry.get_instance().list(
                category=cat,
                severity=sev,
                language=lang,
                status=stat,
                rule_type=r_type,
                architecture=arch,
                tier=tier,
                search_query=search_q,
                active_only=active_only
            )
            self._send_json({
                "rules": [r.to_dict() for r in rules],
                "count": len(rules),
                "total": len(rules)
            })
            return

        # 7. API: Architecture Profiles
        if path == "/api/profiles":
            profiles = load_real_architecture_profiles()
            self._send_json({"profiles": profiles, "count": len(profiles)})
            return

        # 8. API: Browse Local Directories
        if path == "/api/system/browse-dirs":
            req_path = query.get("path", [None])[0]
            res = browse_local_directories(req_path)
            self._send_json(res)
            return

        # 9. API: Mock Scenarios (only when requested)
        if path == "/api/mock/scenario":
            scenario = query.get("name", ["clean-repository"])[0]
            data = generate_scenario_data(scenario)
            self._send_json(data)
            return

        # Static Angular App files fallback
        super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        length = int(self.headers.get("Content-Length", 0))
        body_bytes = self.rfile.read(length) if length > 0 else b"{}"
        try:
            body = json.loads(body_bytes.decode("utf-8"))
        except Exception:
            body = {}

        # 1. API: Local Repository Directory Path Validation
        if path == "/api/repositories/local/validate":
            req_path = body.get("path", "")
            res = inspect_local_repository_path(req_path)
            if res.get("valid") and "repository" in res:
                repo_data = res["repository"]
                CUSTOM_REPOSITORIES[repo_data["id"]] = repo_data
                CUSTOM_REPOSITORIES[repo_data["path"]] = repo_data
            self._send_json(res)
            return

        # 2. API: Commit Validation
        match_commit = re.match(r"^/api/repositories/([^/]+)/commits/validate$", path)
        if match_commit:
            repo_id = match_commit.group(1)
            repo = get_repository_by_id(repo_id)
            if not repo:
                self._send_json({"valid": False, "error": "Repository not found"}, status=404)
                return
            sha = body.get("sha", "")
            res = validate_commit_sha(repo["path"], sha)
            self._send_json(res)
            return

        # 3. API: Execute Real Audit
        if path == "/api/audit":
            repo_id = body.get("repository", "")
            repo_path = body.get("path", "")
            if not repo_path and repo_id:
                repo = get_repository_by_id(repo_id)
                repo_path = repo["path"] if repo else repo_id
            if not repo_path:
                repo_path = str(REPO_ROOT)
            
            target_type = body.get("targetType", "branch")
            profile = body.get("profile", "clean_architecture")
            branch = body.get("branch", "main")
            base_branch = body.get("baseBranch", "")
            commit_sha = body.get("commitSha", "")

            p_repo = Path(repo_path).resolve()
            is_git = False
            try:
                chk = subprocess.run(["git", "-C", str(p_repo), "rev-parse", "--is-inside-work-tree"], capture_output=True, text=True, timeout=2)
                is_git = (chk.returncode == 0 and chk.stdout.strip() == "true")
            except Exception:
                is_git = False

            files_to_audit = []
            if is_git and target_type == "branch":
                if base_branch and branch and base_branch != branch:
                    try:
                        dres = subprocess.run(["git", "-C", str(p_repo), "diff", "--name-only", f"{base_branch}...{branch}"], capture_output=True, text=True, timeout=3)
                        if dres.returncode != 0:
                            dres = subprocess.run(["git", "-C", str(p_repo), "diff", "--name-only", f"{base_branch}..{branch}"], capture_output=True, text=True, timeout=3)
                        if dres.returncode == 0:
                            raw_lines = [f.strip() for f in dres.stdout.splitlines() if f.strip()]
                            if not raw_lines:
                                self._send_json({
                                    "total_files": 0,
                                    "total_violations": 0,
                                    "total_suppressed": 0,
                                    "has_blocking_violations": False,
                                    "culture_score": 100,
                                    "approved": True,
                                    "files": []
                                })
                                return
                            files_to_audit = [str((p_repo / f).resolve()) for f in raw_lines if (p_repo / f).exists()]
                    except Exception:
                        pass
            elif is_git and target_type == "working_tree":
                try:
                    st = subprocess.run(["git", "-C", str(p_repo), "status", "--porcelain"], capture_output=True, text=True, timeout=2)
                    if st.returncode == 0:
                        raw_files = []
                        for l in st.stdout.splitlines():
                            if len(l) > 3:
                                raw_files.append(l[3:].strip())
                        if not raw_files:
                            self._send_json({
                                "total_files": 0,
                                "total_violations": 0,
                                "total_suppressed": 0,
                                "has_blocking_violations": False,
                                "culture_score": 100,
                                "approved": True,
                                "files": []
                            })
                            return
                        files_to_audit = [str((p_repo / f).resolve()) for f in raw_files if (p_repo / f).exists()]
                except Exception:
                    pass
            elif is_git and target_type == "commit" and commit_sha:
                try:
                    cres = subprocess.run(["git", "-C", str(p_repo), "show", "--name-only", "--oneline", commit_sha], capture_output=True, text=True, timeout=2)
                    if cres.returncode == 0:
                        raw_files = [f.strip() for f in cres.stdout.splitlines()[1:] if f.strip()]
                        files_to_audit = [str((p_repo / f).resolve()) for f in raw_files if (p_repo / f).exists()]
                except Exception:
                    pass

            rules_filter = body.get("rules")
            if rules_filter is not None and len(rules_filter) == 0:
                rel_files = []
                for f in files_to_audit:
                    if str(f).startswith(str(p_repo)):
                        rel_files.append(str(f)[len(str(p_repo)):].lstrip("/"))
                    else:
                        rel_files.append(str(f))
                if not rel_files:
                    rel_files = ["src/Domain/Entities/Order.cs"]
                self._send_json({
                    "total_files": len(rel_files),
                    "total_violations": 0,
                    "total_suppressed": 0,
                    "has_blocking_violations": False,
                    "culture_score": 100,
                    "approved": True,
                    "files": [
                        {
                            "path": rf,
                            "layer": "Unknown",
                            "violations": [],
                            "suppressed_count": 0,
                            "linesCount": 50
                        }
                        for rf in rel_files
                    ]
                })
                return

            if files_to_audit:
                cmd = ["python3", "scripts/culture_guard.py"] + files_to_audit + [f"--architecture={profile}", f"--branch={branch}", "--format=json"]
            else:
                cmd = ["python3", "scripts/culture_guard.py", str(repo_path), f"--architecture={profile}", f"--branch={branch}", "--format=json"]

            try:
                proc = subprocess.run(cmd, capture_output=True, text=True, timeout=15, cwd=str(REPO_ROOT))
                if proc.stdout.strip():
                    audit_res = json.loads(proc.stdout)
                    repo_prefix = str(p_repo)
                    allowed_rules = set(rules_filter) if rules_filter is not None else None
                    filtered_files = []
                    total_violations = 0
                    total_penalty = 0
                    total_p0 = 0
                    total_p1 = 0
                    total_suppressed = 0

                    for f in audit_res.get("files", []):
                        fp = f.get("path", "")
                        if fp.startswith(repo_prefix):
                            rel_p = fp[len(repo_prefix):].lstrip("/")
                            f["path"] = rel_p
                        
                        if allowed_rules is not None:
                            f_violations = [
                                v for v in f.get("violations", [])
                                if (v.get("rule_id") or v.get("ruleId")) in allowed_rules
                            ]
                            f["violations"] = f_violations
                        
                        v_list = f.get("violations", [])
                        total_violations += len(v_list)
                        for v in v_list:
                            total_penalty += v.get("penalty", 10)
                            sev = v.get("severity", "P1_WARNING")
                            if sev in ("P0_BLOCKING", "P0"):
                                total_p0 += 1
                            elif sev in ("P1_WARNING", "P1"):
                                total_p1 += 1
                        total_suppressed += f.get("suppressed_count", 0)
                        filtered_files.append(f)

                    if allowed_rules is not None:
                        audit_res["files"] = filtered_files
                        audit_res["total_violations"] = total_violations
                        audit_res["total_suppressed"] = total_suppressed
                        audit_res["has_blocking_violations"] = (total_p0 > 0)
                        audit_res["culture_score"] = max(0, 100 - total_penalty) if filtered_files else 100
                        audit_res["approved"] = (total_p0 == 0 and audit_res["culture_score"] >= 80)

                    self._send_json(audit_res)
                    return
            except Exception as e:
                pass

        # 4. API: Rule Management Endpoints (POST)
        if path == "/api/rules":
            reg = RuleRegistry.get_instance()
            rule_id = str(body.get("id", "")).strip().upper()
            if not rule_id:
                self._send_json({"error": "Rule ID is required", "errorType": "VALIDATION_ERROR"}, status=422)
                return
            if reg.get(rule_id):
                self._send_json({"error": f"Rule with ID '{rule_id}' already exists", "errorType": "RULE_ALREADY_EXISTS"}, status=409)
                return
            valid, errors = reg.validate_rule(body)
            if not valid:
                self._send_json({"error": "Rule validation failed", "errors": errors, "errorType": "INVALID_RULE_SCHEMA"}, status=422)
                return
            rule = RuleNormalizer.normalize_rule_dict(body, default_tier=RuleTier.CUSTOM)
            created = reg.register(rule, actor="api", persist=True)
            self._send_json({"success": True, "rule": created.to_dict(), "message": f"Rule '{created.id}' created successfully"}, status=201)
            return

        if path == "/api/rules/import":
            reg = RuleRegistry.get_instance()
            rules_payload = body.get("rules", body) if isinstance(body, dict) else body
            overwrite = body.get("overwrite", False) if isinstance(body, dict) else False
            cnt, errs = reg.import_rules(rules_payload, actor="api")
            self._send_json({"success": True, "imported": cnt, "errors": errs, "message": f"Successfully imported {cnt} rules."})
            return

        if path == "/api/rules/test":
            rule_data = body.get("rule", {})
            source_code = body.get("sourceCode") or body.get("code") or ""
            file_name = body.get("fileName") or body.get("file_name") or "test_sample.py"
            rule = RuleNormalizer.normalize_rule_dict(rule_data, default_tier=RuleTier.CUSTOM)
            res = RuleTestEngine.test_rule(rule, source_code, file_name)
            self._send_json({"test_result": res.to_dict(), **res.to_dict()})
            return

        match_rule_val = re.match(r"^/api/rules/([^/]+)/validate$", path)
        if match_rule_val:
            reg = RuleRegistry.get_instance()
            rule_id = match_rule_val.group(1).upper()
            rule = reg.get(rule_id)
            if not rule:
                self._send_json({"valid": False, "errors": [f"Rule '{rule_id}' not found"], "errorType": "RULE_NOT_FOUND"}, status=404)
                return
            valid, errors = reg.validate_rule(rule)
            self._send_json({"valid": valid, "errors": errors, "ruleId": rule_id})
            return

        match_rule_test = re.match(r"^/api/rules/([^/]+)/test$", path)
        if match_rule_test:
            reg = RuleRegistry.get_instance()
            rule_id = match_rule_test.group(1).upper()
            rule = reg.get(rule_id)
            if not rule:
                self._send_json({"error": f"Rule '{rule_id}' not found", "errorType": "RULE_NOT_FOUND"}, status=404)
                return
            source_code = body.get("sourceCode") or body.get("code") or ""
            file_name = body.get("fileName") or body.get("file_name") or "test_sample.py"
            res = RuleTestEngine.test_rule(rule, source_code, file_name)
            self._send_json({"test_result": res.to_dict(), **res.to_dict()})
            return

        match_rule_enable = re.match(r"^/api/rules/([^/]+)/enable$", path)
        if match_rule_enable:
            reg = RuleRegistry.get_instance()
            rule_id = match_rule_enable.group(1).upper()
            rule = reg.enable(rule_id, actor="api")
            if not rule:
                self._send_json({"error": f"Rule '{rule_id}' not found", "errorType": "RULE_NOT_FOUND"}, status=404)
                return
            self._send_json({"success": True, "rule": rule.to_dict(), "message": f"Rule '{rule_id}' enabled"})
            return

        match_rule_disable = re.match(r"^/api/rules/([^/]+)/disable$", path)
        if match_rule_disable:
            reg = RuleRegistry.get_instance()
            rule_id = match_rule_disable.group(1).upper()
            rule = reg.disable(rule_id, actor="api")
            if not rule:
                self._send_json({"error": f"Rule '{rule_id}' not found", "errorType": "RULE_NOT_FOUND"}, status=404)
                return
            self._send_json({"success": True, "rule": rule.to_dict(), "message": f"Rule '{rule_id}' disabled"})
            return

        match_rule_clone = re.match(r"^/api/rules/([^/]+)/clone$", path)
        if match_rule_clone:
            reg = RuleRegistry.get_instance()
            source_id = match_rule_clone.group(1).upper()
            new_id = str(body.get("new_id") or body.get("newId") or "").strip().upper()
            new_name = body.get("new_name") or body.get("newName")
            if not new_id:
                self._send_json({"error": "new_id is required for cloning", "errorType": "VALIDATION_ERROR"}, status=422)
                return
            if reg.get(new_id):
                self._send_json({"error": f"Rule with ID '{new_id}' already exists", "errorType": "RULE_ALREADY_EXISTS"}, status=409)
                return
            try:
                cloned = reg.clone(source_id, new_id, new_name=new_name, actor="api")
                self._send_json({"success": True, "rule": cloned.to_dict(), "message": f"Rule '{source_id}' cloned to '{cloned.id}'"}, status=201)
            except Exception as e:
                self._send_json({"error": str(e)}, status=400)
            return

        self._send_json({"error": "Endpoint not found"}, status=404)

    def do_PUT(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get("Content-Length", 0))
        body_bytes = self.rfile.read(length) if length > 0 else b"{}"
        try:
            body = json.loads(body_bytes.decode("utf-8"))
        except Exception:
            body = {}

        match_rule_put = re.match(r"^/api/rules/([^/]+)$", path)
        if match_rule_put:
            reg = RuleRegistry.get_instance()
            rule_id = match_rule_put.group(1).upper()
            existing = reg.get(rule_id)
            if not existing:
                self._send_json({"error": f"Rule '{rule_id}' not found", "errorType": "RULE_NOT_FOUND"}, status=404)
                return
            merged_dict = existing.to_dict()
            merged_dict.update(body)
            merged_dict["id"] = rule_id
            valid, errors = reg.validate_rule(merged_dict)
            if not valid:
                self._send_json({"error": "Rule validation failed", "errors": errors, "errorType": "INVALID_RULE_SCHEMA"}, status=422)
                return
            rule = RuleNormalizer.normalize_rule_dict(merged_dict, default_tier=existing.tier)
            updated = reg.register(rule, actor="api", persist=True)
            self._send_json({"success": True, "rule": updated.to_dict(), "message": f"Rule '{rule_id}' updated successfully"})
            return

        self._send_json({"error": "Endpoint not found"}, status=404)

    def do_DELETE(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)
        hard_delete = query.get("force", ["true"])[0].lower() == "true" or query.get("cascade", ["false"])[0].lower() == "true"

        match_rule_del = re.match(r"^/api/rules/([^/]+)$", path)
        if match_rule_del:
            reg = RuleRegistry.get_instance()
            rule_id = match_rule_del.group(1).upper()
            existing = reg.get(rule_id)
            if not existing:
                self._send_json({"error": f"Rule '{rule_id}' not found", "errorType": "RULE_NOT_FOUND"}, status=404)
                return
            if existing.tier == RuleTier.BUILTIN:
                reg.disable(rule_id, actor="api")
                self._send_json({"success": True, "message": f"Built-in rule '{rule_id}' disabled and archived", "ruleId": rule_id, "deleted": False})
                return
            ok = reg.unregister(rule_id, actor="api", hard_delete=hard_delete)
            self._send_json({"success": True, "message": f"Rule '{rule_id}' deleted successfully", "ruleId": rule_id, "deleted": ok})
            return

        self._send_json({"error": "Endpoint not found"}, status=404)

def start_guardian_server(port: int = 4200, is_mock: bool = False, scenario: Optional[str] = None):
    GuardianRequestHandler.is_mock_mode = is_mock
    GuardianRequestHandler.mock_scenario = scenario
    
    server_address = ("", port)
    httpd = HTTPServer(server_address, GuardianRequestHandler)
    print("=" * 70)
    print(f" 🛡️  BEND DEVOPS GUARDIAN SERVER RUNNING ON http://localhost:{port}")
    print("=" * 70)
    print(f" • Mode:       {'MOCK (' + scenario + ')' if is_mock else 'REAL DATA BY DEFAULT'}")
    print(f" • Root:       {REPO_ROOT}")
    print(f" • Frontend:   {get_frontend_root()}")
    print("=" * 70)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bend DevOps Guardian Server")
    parser.add_argument("--port", type=int, default=4200, help="Server port (default: 4200)")
    parser.add_argument("--mock", action="store_true", help="Explicitly enable Mock Mode")
    parser.add_argument("--scenario", choices=["clean-repository", "architecture-violations", "blocked-quality-gate", "github-repository", "empty-repository", "integration-error"], help="Mock scenario to load")
    args = parser.parse_args()

    start_guardian_server(port=args.port, is_mock=args.mock, scenario=args.scenario)
