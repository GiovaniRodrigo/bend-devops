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
import subprocess
import urllib.request
import urllib.parse
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from typing import Dict, Any, List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.token_filter import load_guardianignore
from scripts.guardian_mock import generate_scenario_data

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
                "remoteUrl": remote or f"https://github.com/GiovaniRodrigo/{top_path.name}.git",
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
        return {"valid": False, "error": "Directory path cannot be empty"}
    
    clean_str = os.path.expanduser(path_str.strip())
    p = Path(clean_str).resolve()
    
    if not p.exists():
        return {"valid": False, "error": f"Directory does not exist: {clean_str}"}
    if not p.is_dir():
        return {"valid": False, "error": f"Path is not a directory: {clean_str}"}
        
    try:
        is_git = subprocess.run(
            ["git", "-C", str(p), "rev-parse", "--is-inside-work-tree"],
            capture_output=True, text=True, timeout=2
        ).stdout.strip()
        if is_git != "true":
            return {"valid": False, "error": f"Directory is not a Git repository (no .git found): {clean_str}"}
            
        top_level = subprocess.run(
            ["git", "-C", str(p), "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=2
        ).stdout.strip()
        top_path = Path(top_level)
        
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

        repo_obj = {
            "id": top_path.name,
            "name": top_path.name,
            "path": str(top_path),
            "remoteUrl": remote or f"https://github.com/GiovaniRodrigo/{top_path.name}.git",
            "currentBranch": branch,
            "branches": branches,
            "headCommit": head,
            "headCommitMessage": head_msg,
            "isClean": len(status) == 0,
            "isCurrent": str(top_path) == str(REPO_ROOT)
        }
        return {"valid": True, "repository": repo_obj}
    except Exception as e:
        return {"valid": False, "error": f"Git inspection failed: {str(e)}"}

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
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

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

        # 6. API: Architecture Rules
        if path == "/api/rules":
            rules = load_real_rules_manifest()
            self._send_json({"rules": rules, "count": len(rules)})
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

        # 2. API: Execute Real Audit
        if path == "/api/audit":
            repo_id = body.get("repository", "ai-bend-devops")
            repo = get_repository_by_id(repo_id)
            repo_path = repo["path"] if repo else str(REPO_ROOT)
            
            target_type = body.get("targetType", "working_tree")
            profile = body.get("profile", "clean_architecture")
            
            # Execute python audit CLI
            cmd = ["python3", "scripts/culture_guard.py", repo_path, f"--architecture={profile}", "--format=json"]
            try:
                proc = subprocess.run(cmd, capture_output=True, text=True, timeout=10, cwd=str(REPO_ROOT))
                if proc.stdout.strip():
                    audit_res = json.loads(proc.stdout)
                    self._send_json(audit_res)
                    return
            except Exception as e:
                pass

            self._send_json({"error": "Audit execution failed", "isApproved": False, "score": 0}, status=500)
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
