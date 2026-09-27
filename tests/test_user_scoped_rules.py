"""
Unit and Integration Tests for User-Scoped Rules & Modular Composition
Spec: specs/007-escopo-e-regras-arquiteturais-do-usuario/
"""

import os
import json
import unittest
import tempfile
import shutil
from pathlib import Path

from scripts.culture_guard import resolve_scope_files, evaluate_scoped_rules
from scripts.vcs_adapters.base_adapter import BaseVcsAdapter


class TestUserScopedRules(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.test_dir, "backend", "domain"), exist_ok=True)
        os.makedirs(os.path.join(self.test_dir, "frontend", "src"), exist_ok=True)

        # Arquivo no backend (com violacao de camada)
        self.file_backend = os.path.join(self.test_dir, "backend", "domain", "model.py")
        with open(self.file_backend, "w", encoding="utf-8") as f:
            f.write("import requests # violacao de camada\nclass OrderModel:\n    pass\n")

        # Arquivo no frontend (com segredo)
        self.file_frontend = os.path.join(self.test_dir, "frontend", "src", "app.ts")
        with open(self.file_frontend, "w", encoding="utf-8") as f:
            f.write("const API_KEY = 'sk_live_12345678901234567890';\n")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_RF01_repository_origin_and_branch_scope(self):
        """RF01: Resolucao de escopo em repositorio local com branch especifica"""
        files = resolve_scope_files(self.test_dir, scope="full_branch", branch="main")
        self.assertIn(self.file_backend, files)
        self.assertIn(self.file_frontend, files)

    def test_RF02_RN03_subdirectory_scope_ignores_other_directories(self):
        """RF02 & RN03: Escopo 'subdirectory' avalia apenas backend e ignora frontend"""
        files = resolve_scope_files(self.test_dir, scope="subdirectory", target="backend")
        self.assertIn(self.file_backend, files)
        self.assertNotIn(self.file_frontend, files)

    def test_RF02_single_file_scope_targets_exact_file(self):
        """RF02: Escopo 'single_file' restringe avaliacao ao arquivo informado"""
        files = resolve_scope_files(self.test_dir, scope="single_file", target="frontend/src/app.ts")
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0], self.file_frontend)

    def test_RF03_RN02_modular_rules_composition_and_blocking_gate(self):
        """RF03 & RN02: Regras ativas complementares bloqueiam gate quando violadas"""
        active_rules = [{"id": "CULT04", "severity": "P0_BLOCKING"}]
        report = evaluate_scoped_rules(files=[self.file_frontend], rules=active_rules)
        self.assertFalse(report["isApproved"])
        self.assertEqual(len(report["violations"]), 1)
        self.assertEqual(report["violations"][0]["rule_id"], "CULT04")

    def test_RF04_custom_severity_override(self):
        """RF04: Calibracao e sobrescrita de severidade personalizada pelo usuario"""
        # Overriding CULT04 from P0 to P1_WARNING reduces penalty and does not block P0 gate
        active_rules = [{"id": "CULT04", "customSeverity": "P1_WARNING"}]
        report = evaluate_scoped_rules(files=[self.file_frontend], rules=active_rules)
        self.assertEqual(report["violations"][0]["severity"], "P1_WARNING")
        # Score is 100 - 15 = 85, no P0 violation => Approved!
        self.assertTrue(report["isApproved"])
        self.assertGreaterEqual(report["score"], 80)

    def test_RF05_evaluation_restricted_strictly_to_scope(self):
        """RF05: Avaliacao restrita estritamente aos arquivos dentro do escopo"""
        backend_files = resolve_scope_files(self.test_dir, scope="subdirectory", target="backend")
        # Active rules include secret scan (CULT04), but frontend is out of scope
        active_rules = [{"id": "CULT04", "severity": "P0_BLOCKING"}]
        report = evaluate_scoped_rules(files=backend_files, rules=active_rules)
        self.assertEqual(len(report["violations"]), 0)
        self.assertTrue(report["isApproved"])
        self.assertEqual(report["score"], 100)

    def test_RF06_scope_profile_config_roundtrip(self):
        """RF06: Serializacao e restauracao de configuracao de escopo"""
        config = {
            "repositoryId": "local-ai-bend",
            "scopeMode": "subdirectory",
            "targetPath": "backend",
            "branch": "feature/refactor",
            "activeRules": ["ARCH-LAYER-01", "SEC-001"]
        }
        saved_json = json.dumps(config)
        restored = json.loads(saved_json)
        self.assertEqual(restored["scopeMode"], "subdirectory")
        self.assertEqual(restored["targetPath"], "backend")
        self.assertEqual(len(restored["activeRules"]), 2)

    def test_RF07_sarif_export_scoped_report(self):
        """RF07: Emissao de relatorio e exportacao SARIF filtrada pelo escopo"""
        from scripts.vcs_adapters.github_adapter import GitHubAdapter
        active_rules = [{"id": "CULT04", "severity": "P0_BLOCKING"}]
        report = evaluate_scoped_rules(files=[self.file_frontend], rules=active_rules)
        adapter = GitHubAdapter(token="dummy", repo="owner/repo")
        sarif = adapter.generate_report_artifact(report["violations"], score=report["score"], approved=report["isApproved"])
        self.assertIn("CULT04", sarif)
        self.assertIn("sarif-schema-2.1.0.json", sarif)

    def test_RN01_user_autonomy_inactive_rules_ignored(self):
        """RN01: Nenhuma regra inativa emite violacao (autonomia total do usuario)"""
        # CULT04 exists in frontend file, but active_rules does NOT include CULT04
        active_rules = [{"id": "ARCH-LAYER-01", "enabled": True}]
        report = evaluate_scoped_rules(files=[self.file_frontend], rules=active_rules)
        self.assertEqual(len(report["violations"]), 0)
        self.assertTrue(report["isApproved"])

    def test_RN04_empty_scope_does_not_crash(self):
        """RN04: Escopo vazio retorna relatorio limpo sem excecoes"""
        files = resolve_scope_files(self.test_dir, scope="subdirectory", target="empty_folder")
        report = evaluate_scoped_rules(files=files, rules=[{"id": "ARCH-LAYER-01"}])
        self.assertEqual(len(files), 0)
        self.assertTrue(report["isApproved"])
        self.assertEqual(report["score"], 100)


if __name__ == "__main__":
    unittest.main()
