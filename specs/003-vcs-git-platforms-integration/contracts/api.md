# API Contracts: Multi-Platform VCS Webhooks & REST Endpoints

---

## 1. Webhook Payloads

### 1.1. GitHub Pull Request Event (`POST /webhooks/github`)

```json
{
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
    }
  },
  "repository": {
    "full_name": "acme-corp/core-service"
  }
}
```

---

### 1.2. GitLab Merge Request Event (`POST /webhooks/gitlab`)

```json
{
  "object_kind": "merge_request",
  "project": {
    "id": 98765,
    "path_with_namespace": "acme-corp/core-service"
  },
  "object_attributes": {
    "iid": 14,
    "last_commit": {
      "id": "7d9b1c8f4e2a1b3c5d6e7f8a9b0c1d2e3f4a5b6c"
    },
    "target_branch": "main",
    "source_branch": "feature/billing-update"
  }
}
```

---

### 1.3. Bitbucket Pull Request Event (`POST /webhooks/bitbucket`)

```json
{
  "event_key": "pullrequest:created",
  "pullrequest": {
    "id": 8,
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
  "repository": {
    "full_name": "acmeworkspace/core-repo"
  }
}
```
