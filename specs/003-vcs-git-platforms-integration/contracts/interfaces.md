# Interfaces: Multi-Platform VCS Adapters

---

## 1. Python Abstract Base Adapter Interface (`scripts/vcs_adapters/base_adapter.py`)

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class BaseVcsAdapter(ABC):
    """Abstract contract for VCS platform integrations."""

    @abstractmethod
    def get_changed_files(self) -> List[str]:
        """Returns list of modified or added file paths in the PR/MR."""
        pass

    @abstractmethod
    def publish_commit_status(self, state: str, description: str, score: int) -> bool:
        """Sets commit status check on the HEAD SHA (e.g. success, failure, pending)."""
        pass

    @abstractmethod
    def post_pr_comment(self, markdown_body: str) -> bool:
        """Posts or updates a markdown comment on the PR/MR discussion thread."""
        pass

    @abstractmethod
    def publish_annotations(self, violations: List[Dict[str, Any]]) -> bool:
        """Publishes line-level inline annotations (GitHub Check Runs, Bitbucket Insights)."""
        pass
```

---

## 2. SARIF v2.1.0 Exporter Contract

```json
{
  "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
  "version": "2.1.0",
  "runs": [
    {
      "tool": {
        "driver": {
          "name": "Bend DevOps Guardian",
          "version": "1.0.0",
          "rules": [
            {
              "id": "ARCH-LAYER-01",
              "shortDescription": {
                "text": "Zero Presentation Code in Domain & Models"
              }
            }
          ]
        }
      },
      "results": [
        {
          "ruleId": "ARCH-LAYER-01",
          "level": "error",
          "message": {
            "text": "Forbidden presentation markup inside Domain class"
          },
          "locations": [
            {
              "physicalLocation": {
                "artifactLocation": {
                  "uri": "src/Domain/Order.cs"
                },
                "region": {
                  "startLine": 12
                }
              }
            }
          ]
        }
      ]
    }
  ]
}
```
