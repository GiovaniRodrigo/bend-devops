"""
Integration Tests for Guardian Server Rule REST API Endpoints
"""

import json
import socket
import unittest
import threading
import urllib.request
import urllib.error
from http.server import ThreadingHTTPServer

from scripts.guardian_server import GuardianRequestHandler
from scripts.rule_registry import RuleRegistry
from scripts.rule_model import UserRole, RuleTier, RuleDefinition, RuleType, RuleSeverity, RuleStatus, RuleCondition


class TestGuardianRuleApi(unittest.TestCase):
    server: ThreadingHTTPServer
    server_thread: threading.Thread
    port: int

    @classmethod
    def setUpClass(cls):
        # Bind to port 0 for dynamic ephemeral port allocation
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), GuardianRequestHandler)
        cls.port = cls.server.server_address[1]
        cls.server_thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.server_thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def setUp(self):
        # Clean up any leftover test rules
        RuleRegistry.get_instance().unregister("API-TEST-001", hard_delete=True)
        RuleRegistry.get_instance().unregister("API-TEST-001-CLONED", hard_delete=True)

    def _url(self, path: str) -> str:
        return f"http://127.0.0.1:{self.port}{path}"

    def _json_request(self, method: str, path: str, body: dict = None):
        url = self._url(path)
        data = json.dumps(body).encode("utf-8") if body is not None else None
        headers = {"Content-Type": "application/json"} if body is not None else {}
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req) as response:
                status = response.status
                content = response.read().decode("utf-8")
                return status, json.loads(content) if content else {}
        except urllib.error.HTTPError as e:
            content = e.read().decode("utf-8")
            return e.code, json.loads(content) if content else {}

    def test_healthz(self):
        status, data = self._json_request("GET", "/api/healthz")
        self.assertEqual(status, 200)
        self.assertIn(data.get("status"), ["healthy", "UP", "OK"])

    def test_get_rules_list(self):
        status, data = self._json_request("GET", "/api/rules")
        self.assertEqual(status, 200)
        self.assertIn("rules", data)
        self.assertIsInstance(data["rules"], list)
        self.assertGreater(len(data["rules"]), 0)

    def test_get_metadata_endpoints(self):
        # Categories
        status, data = self._json_request("GET", "/api/rules/categories")
        self.assertEqual(status, 200)
        self.assertIn("categories", data)

        # Languages
        status, data = self._json_request("GET", "/api/rules/languages")
        self.assertEqual(status, 200)
        self.assertIn("languages", data)

        # Types
        status, data = self._json_request("GET", "/api/rules/types")
        self.assertEqual(status, 200)
        self.assertIn("types", data)

        # Severities
        status, data = self._json_request("GET", "/api/rules/severities")
        self.assertEqual(status, 200)
        self.assertIn("severities", data)

        # Statuses
        status, data = self._json_request("GET", "/api/rules/statuses")
        self.assertEqual(status, 200)
        self.assertIn("statuses", data)

    def test_crud_rule_lifecycle(self):
        rule_id = "API-TEST-001"
        payload = {
            "id": rule_id,
            "version": "1.0.0",
            "name": "API Test Rule",
            "description": "Rule created via REST API test",
            "type": "pattern",
            "category": "Security",
            "severity": "P0",
            "penalty_points": 35,
            "tier": "custom",
            "condition": {
                "pattern": r"API_KEY\s*=\s*['\"][^'\"]+['\"]"
            },
            "message": "Hardcoded API key detected in source code.",
            "suggestion": "Store API key in secure environment variables.",
            "suppression": {
                "allowed": True,
                "pragma": "@guardian-ignore",
                "requires_reason": True,
                "minimum_reason_length": 8
            }
        }

        # 1. CREATE
        status, create_res = self._json_request("POST", "/api/rules", payload)
        self.assertIn(status, [200, 201])
        self.assertTrue(create_res.get("success"))

        # 2. GET BY ID
        status, get_res = self._json_request("GET", f"/api/rules/{rule_id}")
        self.assertEqual(status, 200)
        self.assertEqual(get_res["rule"]["id"], rule_id)
        self.assertEqual(get_res["rule"]["name"], "API Test Rule")

        # 3. VALIDATE RULE
        status, val_res = self._json_request("POST", f"/api/rules/{rule_id}/validate")
        self.assertEqual(status, 200)
        self.assertTrue(val_res.get("valid"))

        # 4. TEST RULE
        test_payload = {
            "code": 'API_KEY = "sk_live_1234567890abcdef"\n',
            "file_name": "src/api_client.py"
        }
        status, test_res = self._json_request("POST", f"/api/rules/{rule_id}/test", test_payload)
        self.assertEqual(status, 200)
        self.assertTrue(test_res["test_result"]["has_violation"])

        # 5. CLONE RULE
        clone_payload = {
            "new_id": f"{rule_id}-CLONED",
            "new_name": "Cloned API Rule"
        }
        status, clone_res = self._json_request("POST", f"/api/rules/{rule_id}/clone", clone_payload)
        self.assertEqual(status, 201)
        self.assertEqual(clone_res["rule"]["id"], f"{rule_id}-CLONED")

        # 6. DISABLE & ENABLE
        status, dis_res = self._json_request("POST", f"/api/rules/{rule_id}/disable")
        self.assertEqual(status, 200)
        self.assertFalse(dis_res["rule"]["enabled"])

        status, en_res = self._json_request("POST", f"/api/rules/{rule_id}/enable")
        self.assertEqual(status, 200)
        self.assertTrue(en_res["rule"]["enabled"])

        # 7. EXPORT RULE
        status, exp_res = self._json_request("GET", f"/api/rules/{rule_id}/export")
        self.assertEqual(status, 200)
        self.assertEqual(exp_res["id"], rule_id)

        # 8. UPDATE RULE
        update_payload = {
            "name": "Updated API Test Rule",
            "penalty_points": 40
        }
        status, upd_res = self._json_request("PUT", f"/api/rules/{rule_id}", update_payload)
        self.assertEqual(status, 200)
        self.assertEqual(upd_res["rule"]["name"], "Updated API Test Rule")

        # 9. DELETE RULE
        status, del_res = self._json_request("DELETE", f"/api/rules/{rule_id}?cascade=true")
        self.assertEqual(status, 200)
        self.assertTrue(del_res.get("success"))

        # Clean up clone
        self._json_request("DELETE", f"/api/rules/{rule_id}-CLONED?cascade=true")

    def test_ad_hoc_test_endpoint(self):
        payload = {
            "rule": {
                "id": "ADHOC-01",
                "type": "pattern",
                "condition": {
                    "pattern": r"console\.log\("
                },
                "message": "console.log prohibited in production"
            },
            "code": 'console.log("debug message");\n',
            "file_name": "src/app.ts"
        }
        status, data = self._json_request("POST", "/api/rules/test", payload)
        self.assertEqual(status, 200)
        self.assertTrue(data["test_result"]["has_violation"])


if __name__ == "__main__":
    unittest.main()
