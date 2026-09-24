#!/usr/bin/env python3
"""
# ==============================================================================
# Bend DevOps Guardian — Explicit Scenario Mocking & Fixture CLI
# ==============================================================================
# Provides explicit, deterministic mock scenarios for development, visual
# testing, Playwright verification, and demonstration environments.
#
# RULE: Mock mode is NEVER the default. It must be explicitly requested.
# ==============================================================================
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, List

REPO_ROOT = Path(__file__).resolve().parent.parent

AVAILABLE_SCENARIOS = [
    "clean-repository",
    "architecture-violations",
    "blocked-quality-gate",
    "github-repository",
    "empty-repository",
    "integration-error"
]

def generate_scenario_data(scenario: str) -> Dict[str, Any]:
    """Generates deterministic mock scenario data for CLI testing and frontend simulation."""
    if scenario == "clean-repository":
        return {
            "scenario": "clean-repository",
            "isMock": True,
            "environment": "MOCK",
            "title": "Clean Architecture Domain Entity (100% Compliant)",
            "repository": {
                "name": "bend-devops",
                "path": "~/projects/bend-devops",
                "source": "local",
                "branch": "feature/order-refactor",
                "targetBranch": "main"
            },
            "report": {
                "score": 100,
                "isApproved": True,
                "p0Count": 0,
                "p1Count": 0,
                "p2Count": 0,
                "totalViolations": 0,
                "totalFiles": 1,
                "status": "APPROVED",
                "violations": []
            },
            "files": [
                {
                    "name": "src/Domain/Entities/Order.cs",
                    "status": "passed",
                    "additions": 42,
                    "deletions": 0,
                    "violationsCount": 0,
                    "code": "// @spec RF14 - Clean Architecture Domain Entity\nnamespace Core.Domain.Entities;\n\npublic class Order {\n    public Guid Id { get; private set; }\n    public decimal TotalAmount { get; private set; }\n\n    public Order(Guid id, decimal totalAmount) {\n        Id = id;\n        TotalAmount = totalAmount;\n    }\n}"
                }
            ]
        }
    elif scenario == "architecture-violations":
        return {
            "scenario": "architecture-violations",
            "isMock": True,
            "environment": "MOCK",
            "title": "Severe Architecture & Security Violations",
            "repository": {
                "name": "bend-devops",
                "path": "~/projects/bend-devops",
                "source": "local",
                "branch": "feature/billing-refactor",
                "targetBranch": "main"
            },
            "report": {
                "score": 25,
                "isApproved": False,
                "p0Count": 3,
                "p1Count": 1,
                "p2Count": 0,
                "totalViolations": 4,
                "totalFiles": 2,
                "status": "BLOCKED",
                "violations": [
                    {
                        "ruleId": "CULT04",
                        "severity": "P0_BLOCKING",
                        "fileName": "src/Domain/Models/OrderInvoice.cs",
                        "line": 8,
                        "message": "Hardcoded API secret token or credential detected",
                        "remediation": "Use environment variables or Azure Key Vault."
                    },
                    {
                        "ruleId": "ARCH-LAYER-01",
                        "severity": "P0_BLOCKING",
                        "fileName": "src/Domain/Models/OrderInvoice.cs",
                        "line": 14,
                        "message": "Forbidden presentation markup / HTML inside Domain model or Service class",
                        "remediation": "Move presentation markup into dedicated View templates."
                    },
                    {
                        "ruleId": "CULT01",
                        "severity": "P0_BLOCKING",
                        "fileName": "src/Domain/Models/OrderInvoice.cs",
                        "line": 20,
                        "message": "Incomplete code placeholder detected: '// TODO: Implement later'",
                        "remediation": "Implement the full business logic before merging."
                    }
                ]
            },
            "files": [
                {
                    "name": "src/Domain/Models/OrderInvoice.cs",
                    "status": "blocked",
                    "additions": 65,
                    "deletions": 12,
                    "violationsCount": 3
                },
                {
                    "name": "src/Presentation/Controllers/CheckoutController.cs",
                    "status": "blocked",
                    "additions": 84,
                    "deletions": 36,
                    "violationsCount": 1
                }
            ]
        }
    elif scenario == "blocked-quality-gate":
        return {
            "scenario": "blocked-quality-gate",
            "isMock": True,
            "environment": "MOCK",
            "title": "Strict Branch Policy Quality Gate BLOCKED",
            "repository": {
                "name": "bend-devops",
                "path": "~/projects/bend-devops",
                "source": "local",
                "branch": "feature/payment-v2",
                "targetBranch": "main"
            },
            "policy": {
                "targetBranch": "main",
                "policyType": "Strict Gate",
                "requiredP0": 0,
                "minScore": 80,
                "actualScore": 45,
                "actualP0": 2,
                "decision": "BLOCKED"
            }
        }
    elif scenario == "github-repository":
        return {
            "scenario": "github-repository",
            "isMock": True,
            "environment": "MOCK",
            "title": "GitHub Integration & PR Webhook Ingestion",
            "github": {
                "account": "GiovaniRodrigo",
                "repository": "bend-devops",
                "prNumber": 42,
                "prTitle": "feat: enforce clean architecture domain isolation",
                "commitSha": "45aa45489f02c613e71d3d68bc8610eb6750011b",
                "status": "connected"
            }
        }
    elif scenario == "empty-repository":
        return {
            "scenario": "empty-repository",
            "isMock": True,
            "environment": "MOCK",
            "title": "Empty Repository (No Files / Initial State)",
            "repository": {
                "name": "",
                "path": "",
                "source": "local",
                "branch": "",
                "targetBranch": ""
            },
            "report": {
                "score": 0,
                "isApproved": False,
                "p0Count": 0,
                "p1Count": 0,
                "p2Count": 0,
                "totalViolations": 0,
                "totalFiles": 0,
                "status": "EMPTY",
                "violations": []
            },
            "files": []
        }
    elif scenario == "integration-error":
        return {
            "scenario": "integration-error",
            "isMock": True,
            "environment": "MOCK",
            "title": "GitHub Integration Failure (Simulated OAuth Expiry)",
            "error": {
                "code": "AUTH_EXPIRED",
                "platform": "GitHub",
                "message": "GitHub API returned 401 Unauthorized. Personal access token or OAuth token expired.",
                "action": "Reconnect Account"
            }
        }
    else:
        raise ValueError(f"Unknown scenario: {scenario}. Available scenarios: {AVAILABLE_SCENARIOS}")

def main():
    parser = argparse.ArgumentParser(description="Bend DevOps Guardian — Explicit Scenario Mocking CLI")
    parser.add_argument("--scenario", choices=AVAILABLE_SCENARIOS, default="clean-repository", help="Mock scenario to execute/output")
    parser.add_argument("--format", choices=["json", "text"], default="text", help="Output format")
    parser.add_argument("--export", type=str, help="Optional file path to export mock scenario JSON to")
    args = parser.parse_args()

    data = generate_scenario_data(args.scenario)

    if args.export:
        out_path = Path(args.export)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        print(f"✅ Mock scenario '{args.scenario}' exported to {out_path}")
        return

    if args.format == "json":
        print(json.dumps(data, indent=2))
    else:
        print("="*70)
        print(f" ⚠️  BEND DEVOPS GUARDIAN — EXPLICIT MOCK SCENARIO: [{args.scenario.upper()}]")
        print("="*70)
        print(f" Scenario:    {data.get('title')}")
        print(f" Environment: MOCK (Non-production deterministic fixture)")
        if "report" in data:
            rep = data["report"]
            print(f" Status:      {rep.get('status')} (Score: {rep.get('score')}%)")
            print(f" Violations:  {rep.get('totalViolations')} (P0: {rep.get('p0Count')}, P1: {rep.get('p1Count')})")
        if "error" in data:
            err = data["error"]
            print(f" Error:       [{err.get('code')}] {err.get('message')}")
            print(f" Action:      {err.get('action')}")
        print("="*70)
        print("NOTE: Mock data is only active when explicitly requested with --scenario.")

if __name__ == "__main__":
    main()
