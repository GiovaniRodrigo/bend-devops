"""
Unit tests for scripts/guardian_server.py (Backend Server, Repositories, Rules API, and Audit Endpoints).
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


class TestGuardianServerHelpers(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_get_frontend_root(self):
        root = get_frontend_root()
        self.assertIsInstance(root, Path)

    def test_discover_local_repositories(self):
        repos = discover_local_repositories()
        self.assertIsInstance(repos, list)
        if repos:
            self.assertIn("name", repos[0])
            self.assertIn("path", repos[0])

    def test_inspect_local_repository_path(self):
        res = inspect_local_repository_path(str(REPO_ROOT))
        self.assertTrue(res.get("valid", False))
        self.assertIn("repository", res)

        invalid_res = inspect_local_repository_path("/non/existent/repo/path")
        self.assertFalse(invalid_res.get("valid", True))

    def test_browse_local_directories(self):
        res = browse_local_directories(str(REPO_ROOT))
        self.assertIn("directories", res)
        self.assertIn("currentPath", res)

    def test_detect_repository_framework(self):
        # Python / Angular / Bend workspace
        framework = detect_repository_framework(REPO_ROOT)
        self.assertIn("detectedFrameworks", framework)

    def test_get_repository_by_id(self):
        repo = get_repository_by_id("ai-bend-devops")
        # Should return repo dict or None if not found
        self.assertTrue(repo is None or isinstance(repo, dict))

    def test_get_working_tree_info(self):
        info = get_working_tree_info(str(REPO_ROOT))
        self.assertIn("changedFiles", info)
        self.assertIn("isClean", info)

    def test_validate_commit_sha(self):
        # Valid HEAD short sha
        res = validate_commit_sha(str(REPO_ROOT), "HEAD")
        self.assertTrue(res.get("valid", False))

        # Invalid sha
        res_invalid = validate_commit_sha(str(REPO_ROOT), "invalid_sha_12345")
        self.assertFalse(res_invalid.get("valid", True))

    def test_get_github_repositories(self):
        res = get_github_repositories()
        self.assertIn("repositories", res)

    def test_load_real_rules_manifest(self):
        rules = load_real_rules_manifest()
        self.assertIsInstance(rules, list)
        self.assertGreater(len(rules), 0)

    def test_load_real_architecture_profiles(self):
        profiles = load_real_architecture_profiles()
        self.assertIsInstance(profiles, list)
        self.assertGreater(len(profiles), 0)


class TestGuardianServerEndpoints(unittest.TestCase):
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

    def _get(self, path: str):
        req = urllib.request.Request(f"{self.base_url}{path}")
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))

    def _post(self, path: str, payload: dict):
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}{path}",
            data=data,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))

    def _put(self, path: str, payload: dict):
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}{path}",
            data=data,
            headers={"Content-Type": "application/json"},
            method="PUT"
        )
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))

    def _delete(self, path: str):
        req = urllib.request.Request(f"{self.base_url}{path}", method="DELETE")
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))

    def test_healthz(self):
        status, data = self._get("/api/healthz")
        self.assertEqual(status, 200)
        self.assertEqual(data["status"], "UP")

    def test_options(self):
        req = urllib.request.Request(f"{self.base_url}/api/rules", method="OPTIONS")
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 204)
            self.assertIn("Access-Control-Allow-Origin", resp.headers)

    def test_repositories_endpoints(self):
        status, data = self._get("/api/repositories/local")
        self.assertEqual(status, 200)
        self.assertIn("repositories", data)

        status, data = self._get("/api/system/browse-dirs")
        self.assertEqual(status, 200)
        self.assertIn("directories", data)

        status, data = self._post("/api/repositories/local/validate", {"path": str(REPO_ROOT)})
        self.assertEqual(status, 200)
        self.assertTrue(data.get("valid"))

        status, data = self._get("/api/repositories/github")
        self.assertEqual(status, 200)

        status, data = self._get("/api/repositories/ai-bend-devops/working-tree")
        self.assertEqual(status, 200)

    def test_rules_metadata_endpoints(self):
        for ep in ["categories", "languages", "types", "severities", "statuses"]:
            status, data = self._get(f"/api/rules/{ep}")
            self.assertEqual(status, 200)

    def test_rules_crud_lifecycle(self):
        # 1. Get all rules with filters
        status, data = self._get("/api/rules?severity=P0&status=active&tier=builtin")
        self.assertEqual(status, 200)
        self.assertIn("rules", data)
        self.assertIsInstance(data["rules"], list)

        # 2. Get specific rule
        status, rule_resp = self._get("/api/rules/CULT01")
        self.assertEqual(status, 200)
        self.assertEqual(rule_resp["rule"]["id"], "CULT01")

        # 3. Export rule
        status, exp = self._get("/api/rules/CULT01/export")
        self.assertEqual(status, 200)
        self.assertEqual(exp["id"], "CULT01")

        # 4. Create new rule via POST
        new_rule_data = {
            "id": "API-TEST-999",
            "name": "Integration Test Rule",
            "category": "Architecture",
            "severity": "P1",
            "status": "ACTIVE",
            "languages": ["python"],
            "tier": "custom",
            "type": "pattern",
            "pattern": "def bad_pattern\\(\\):",
            "message": "Bad pattern detected",
            "suggestion": "Fix bad pattern"
        }
        status, created = self._post("/api/rules", new_rule_data)
        self.assertEqual(status, 201)

        # 5. Validate rule
        status, val = self._post("/api/rules/API-TEST-999/validate", {})
        self.assertEqual(status, 200)
        self.assertTrue(val["valid"])

        # 6. Test rule execution
        status, test_res = self._post(
            "/api/rules/API-TEST-999/test",
            {"code": "def bad_pattern():\n    pass\n", "fileName": "test.py"}
        )
        self.assertEqual(status, 200)
        self.assertTrue(test_res.get("hasViolation", False))

        # Test standalone rule test
        status, test_res2 = self._post(
            "/api/rules/test",
            {"rule": new_rule_data, "code": "def bad_pattern():\n    pass\n", "fileName": "test.py"}
        )
        self.assertEqual(status, 200)

        # 7. Clone rule
        status, cloned = self._post("/api/rules/API-TEST-999/clone", {"new_id": "API-TEST-CLONE-999"})
        self.assertEqual(status, 201)
        cloned_id = cloned["rule"]["id"]

        # 8. Disable & Enable
        status, dis = self._post("/api/rules/API-TEST-999/disable", {})
        self.assertEqual(status, 200)
        status, en = self._post("/api/rules/API-TEST-999/enable", {})
        self.assertEqual(status, 200)

        # 9. Edit via PUT
        new_rule_data["name"] = "Updated Integration Test Rule"
        status, updated = self._put("/api/rules/API-TEST-999", new_rule_data)
        self.assertEqual(status, 200)

        # 10. Delete rules
        status, del_res = self._delete("/api/rules/API-TEST-999?cascade=true")
        self.assertEqual(status, 200)
        status, del_cloned = self._delete(f"/api/rules/{cloned_id}?cascade=true")
        self.assertEqual(status, 200)

    def test_profiles_endpoints(self):
        status, data = self._get("/api/profiles")
        self.assertEqual(status, 200)
        self.assertIn("profiles", data)

    def test_audit_endpoints(self):
        # POST /api/audit
        audit_payload = {
            "path": str(REPO_ROOT),
            "branch": "main",
            "profile": "clean_architecture",
            "targetType": "full_repo"
        }
        status, audit_res = self._post("/api/audit", audit_payload)
        self.assertEqual(status, 200)
        self.assertIn("files", audit_res)


if __name__ == "__main__":
    unittest.main()
