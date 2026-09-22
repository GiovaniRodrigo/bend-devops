"""
==============================================================================
TDD Unit Tests: Unified Webhook Gateway
==============================================================================
@spec RF05 - Unified Webhook Gateway Request Routing
==============================================================================
"""

import unittest
from scripts.vcs_adapters.webhook_gateway import WebhookGateway, VcsPullRequestEvent

class TestWebhookGateway(unittest.TestCase):
    def test_parse_github_pull_request_webhook(self):
        payload = {
            "action": "opened",
            "number": 42,
            "pull_request": {
                "head": {
                    "sha": "7d9b1c8f4e2a1b3c5d6e7f8a9b0c1d2e3f4a5b6c",
                    "ref": "feature/order-rate-limiter"
                },
                "base": {
                    "sha": "1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b",
                    "ref": "main"
                },
                "user": {
                    "login": "devops-engineer"
                },
                "title": "feat: order rate limiter"
            },
            "repository": {
                "full_name": "acme-corp/core-service"
            }
        }
        event = WebhookGateway.handle_webhook(payload)
        self.assertIsNotNone(event)
        self.assertEqual(event.platform, "github")
        self.assertEqual(event.repo_id, "acme-corp/core-service")
        self.assertEqual(event.pr_number, 42)
        self.assertEqual(event.commit_sha, "7d9b1c8f4e2a1b3c5d6e7f8a9b0c1d2e3f4a5b6c")
        self.assertEqual(event.author, "devops-engineer")

    def test_parse_gitlab_merge_request_webhook(self):
        payload = {
            "object_kind": "merge_request",
            "project": {
                "id": 98765,
                "path_with_namespace": "acme-corp/core-service"
            },
            "user": {
                "username": "gitlab-dev"
            },
            "object_attributes": {
                "iid": 14,
                "title": "feat: billing update",
                "last_commit": {
                    "id": "7d9b1c8f4e2a1b3c5d6e7f8a9b0c1d2e3f4a5b6c"
                },
                "target_branch": "main",
                "source_branch": "feature/billing-update"
            }
        }
        event = WebhookGateway.handle_webhook(payload)
        self.assertIsNotNone(event)
        self.assertEqual(event.platform, "gitlab")
        self.assertEqual(event.repo_id, "acme-corp/core-service")
        self.assertEqual(event.pr_number, 14)
        self.assertEqual(event.commit_sha, "7d9b1c8f4e2a1b3c5d6e7f8a9b0c1d2e3f4a5b6c")
        self.assertEqual(event.author, "gitlab-dev")

    def test_parse_bitbucket_pullrequest_webhook(self):
        payload = {
            "event_key": "pullrequest:created",
            "pullrequest": {
                "id": 8,
                "title": "feat: new gateway",
                "source": {
                    "commit": {
                        "hash": "7d9b1c8f4e2a1b3c5d6e7f8a9b0c1d2e3f4a5b6c"
                    },
                    "branch": {
                        "name": "feature/new-gateway"
                    }
                },
                "destination": {
                    "branch": {
                        "name": "main"
                    }
                }
            },
            "actor": {
                "username": "bb-user"
            },
            "repository": {
                "full_name": "acmeworkspace/core-repo"
            }
        }
        event = WebhookGateway.handle_webhook(payload)
        self.assertIsNotNone(event)
        self.assertEqual(event.platform, "bitbucket")
        self.assertEqual(event.repo_id, "acmeworkspace/core-repo")
        self.assertEqual(event.pr_number, 8)
        self.assertEqual(event.commit_sha, "7d9b1c8f4e2a1b3c5d6e7f8a9b0c1d2e3f4a5b6c")
        self.assertEqual(event.author, "bb-user")

    def test_handle_unknown_webhook_returns_none(self):
        payload = {"random_key": "random_val"}
        event = WebhookGateway.handle_webhook(payload)
        self.assertIsNone(event)

if __name__ == "__main__":
    unittest.main()
