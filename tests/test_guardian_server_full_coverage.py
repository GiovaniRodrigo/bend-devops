"""
Full branch and line coverage test suite for scripts/guardian_server.py
"""

import sys
import os
import json
import socket
import tempfile
import threading
import unittest
import urllib.request
import urllib.error
import urllib.parse
from http.server import HTTPServer
from pathlib import Path
from unittest.mock import patch, MagicMock

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.guardian_server import (
    get_frontend_root,
    discover_local_repositories,
    inspect_local_repository_path,
    browse_local_directories,
    detect_repository_framework,
    get_repository_by_id,
    get_working_tree_info,
    validate_commit_sha,
    get_github_repositories,
    load_real_rules_manifest,
    load_real_architecture_profiles,
    GuardianRequestHandler
)


def get_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        return s.getsockname()[1]


class TestGuardianServerFullCoverage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.port = get_free_port()
        cls.server = HTTPServer(('127.0.0.1', cls.port), GuardianRequestHandler)
        cls.server_thread = threading.Thread(target=cls.server.serve_forever)
        cls.server_thread.daemon = True
        cls.server_thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def _get(self, path: str):
        req = urllib.request.Request(f"{self.base_url}{path}")
        try:
            with urllib.request.urlopen(req) as resp:
                return resp.status, json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read().decode("utf-8"))

    def _post(self, path: str, payload: dict, headers: dict = None):
        data = json.dumps(payload).encode("utf-8")
        h = {"Content-Type": "application/json"}
        if headers:
            h.update(headers)
        req = urllib.request.Request(
            f"{self.base_url}{path}",
            data=data,
            headers=h
        )
        try:
            with urllib.request.urlopen(req) as resp:
                return resp.status, json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read().decode("utf-8"))

    def _put(self, path: str, payload: dict):
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}{path}",
            data=data,
            headers={"Content-Type": "application/json"},
            method="PUT"
        )
        try:
            with urllib.request.urlopen(req) as resp:
                return resp.status, json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read().decode("utf-8"))

    def _delete(self, path: str):
        req = urllib.request.Request(f"{self.base_url}{path}", method="DELETE")
        try:
            with urllib.request.urlopen(req) as resp:
                return resp.status, json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read().decode("utf-8"))

    def test_framework_detection_all_languages(self):
        # 1. Nonexistent
        self.assertFalse(detect_repository_framework(Path("/nonexistent"))["valid"])

        # 2. Go repo
        go_dir = self.temp_path / "go_repo"
        go_dir.mkdir()
        (go_dir / "go.mod").write_text("module myapp\ngo 1.21", encoding="utf-8")
        res_go = detect_repository_framework(go_dir)
        self.assertTrue(any("Go" in f["name"] for f in res_go["detectedFrameworks"]))

        # 3. Rust repo
        rust_dir = self.temp_path / "rust_repo"
        rust_dir.mkdir()
        (rust_dir / "Cargo.toml").write_text("[package]\nname = 'rust_app'\nversion = '0.1.0'", encoding="utf-8")
        res_rust = detect_repository_framework(rust_dir)
        self.assertTrue(any("Rust" in f["name"] for f in res_rust["detectedFrameworks"]))

        # 4. Java repo
        java_dir = self.temp_path / "java_repo"
        java_dir.mkdir()
        (java_dir / "pom.xml").write_text("<project></project>", encoding="utf-8")
        res_java = detect_repository_framework(java_dir)
        self.assertTrue(any("Java" in f["name"] for f in res_java["detectedFrameworks"]))

        # 5. Python repo
        py_dir = self.temp_path / "py_repo"
        py_dir.mkdir()
        (py_dir / "requirements.txt").write_text("fastapi\n", encoding="utf-8")
        (py_dir / "main.py").write_text("print('hello')", encoding="utf-8")
        res_py = detect_repository_framework(py_dir)
        self.assertTrue(any("Python" in f["name"] for f in res_py["detectedFrameworks"]))

    def test_inspect_and_browse_edge_cases(self):
        # Empty path
        self.assertFalse(inspect_local_repository_path("")["valid"])
        # Non-directory path
        file_path = self.temp_path / "file.txt"
        file_path.write_text("hello", encoding="utf-8")
        self.assertFalse(inspect_local_repository_path(str(file_path))["valid"])
        # Non-git directory
        non_git_dir = self.temp_path / "nongit"
        non_git_dir.mkdir()
        self.assertFalse(inspect_local_repository_path(str(non_git_dir))["valid"])

        # Browse directory
        browse_res = browse_local_directories(str(self.temp_path))
        self.assertIn("directories", browse_res)

        # Working tree nonexistent
        wt = get_working_tree_info("/nonexistent/repo")
        self.assertTrue(wt["isClean"])

    def test_all_get_endpoints_and_branches(self):
        # /api/system/status
        status, data = self._get("/api/system/status")
        self.assertEqual(status, 200)

        # /api/repositories/{id}/branches
        status, data = self._get("/api/repositories/ai-bend-devops/branches")
        self.assertEqual(status, 200)

        status, data = self._get("/api/repositories/NONEXISTENT_REPO/branches")
        self.assertEqual(status, 404)

        # /api/repositories/{id}/framework-detect
        status, data = self._get("/api/repositories/ai-bend-devops/framework-detect")
        self.assertEqual(status, 200)

        status, data = self._get("/api/repositories/NONEXISTENT_REPO/framework-detect")
        self.assertEqual(status, 404)

        # /api/repositories/{id}/file
        status, data = self._get("/api/repositories/ai-bend-devops/file?path=README.md")
        self.assertEqual(status, 200)

        status, data = self._get("/api/repositories/ai-bend-devops/file?path=nonexistent.txt")
        self.assertEqual(status, 404)

        status, data = self._get("/api/repositories/NONEXISTENT/file?path=README.md")
        self.assertEqual(status, 404)

        # /api/rules/audit-trail
        status, data = self._get("/api/rules/audit-trail?ruleId=CULT01")
        self.assertEqual(status, 200)

        # /api/rules/export/all
        status, data = self._get("/api/rules/export/all")
        self.assertEqual(status, 200)

        # /api/mock/scenario
        status, data = self._get("/api/mock/scenario?name=clean-repository")
        self.assertEqual(status, 200)

    def test_all_post_put_delete_endpoints_and_errors(self):
        # POST /api/repositories/local/framework-detect
        status, data = self._post("/api/repositories/local/framework-detect", {"path": str(REPO_ROOT)})
        self.assertEqual(status, 200)

        # POST /api/repositories/{id}/commits/validate
        status, data = self._post("/api/repositories/ai-bend-devops/commits/validate", {"sha": "HEAD"})
        self.assertEqual(status, 200)

        status, data = self._post("/api/repositories/NONEXISTENT/commits/validate", {"sha": "HEAD"})
        self.assertEqual(status, 404)

        # POST /api/rules/import
        status, data = self._post("/api/rules/import", {"rules": [{"id": "POST-IMP-01", "name": "Imported", "pattern": "x"}]})
        self.assertEqual(status, 200)
        self._delete("/api/rules/POST-IMP-01?cascade=true")

        # POST /api/rules/test with invalid regex
        status, data = self._post("/api/rules/test", {"rule": {"id": "INV", "pattern": "[unclosed"}, "code": "foo"})
        self.assertEqual(status, 200)

        # POST /api/rules (missing ID -> 422, duplicate -> 409)
        status, data = self._post("/api/rules", {"name": "No ID"})
        self.assertEqual(status, 422)

        status, data = self._post("/api/rules", {"id": "CULT01", "name": "Duplicate"})
        self.assertEqual(status, 409)

        # POST /api/rules/{id}/clone errors
        status, data = self._post("/api/rules/CULT01/clone", {})
        self.assertEqual(status, 422)

        status, data = self._post("/api/rules/CULT01/clone", {"new_id": "CULT02"})
        self.assertEqual(status, 409)

        # POST /api/rules/{id}/validate, test, enable, disable 404s
        status, data = self._post("/api/rules/NONEXISTENT/validate", {})
        self.assertEqual(status, 404)

        status, data = self._post("/api/rules/NONEXISTENT/test", {})
        self.assertEqual(status, 404)

        status, data = self._post("/api/rules/NONEXISTENT/enable", {})
        self.assertEqual(status, 404)

        status, data = self._post("/api/rules/NONEXISTENT/disable", {})
        self.assertEqual(status, 404)

        # PUT /api/rules/{id} 404
        status, data = self._put("/api/rules/NONEXISTENT", {"name": "test"})
        self.assertEqual(status, 404)

        # DELETE /api/rules/{id} 404
        status, data = self._delete("/api/rules/NONEXISTENT")
        self.assertEqual(status, 404)

        # Builtin rule delete archives/disables instead of removing
        status, data = self._delete("/api/rules/CULT02")
        self.assertEqual(status, 200)
        self.assertIn("deleted", data)

        # VCS Ping & Webhooks
        status, data = self._post("/api/v1/vcs/ping", {})
        self.assertEqual(status, 200)

        status, data = self._post("/api/v1/webhook", {"platform": "gitlab", "branch": "feature/test"})
        self.assertEqual(status, 200)

        status, data = self._post("/api/v1/webhook", {}, headers={"X-GitHub-Event": "pull_request"})
        self.assertEqual(status, 200)


if __name__ == "__main__":
    unittest.main()
