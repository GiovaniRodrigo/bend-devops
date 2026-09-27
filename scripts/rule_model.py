#!/usr/bin/env python3
"""
==============================================================================
Bend DevOps Guardian — Rule Domain Models & Data Structures
==============================================================================
Defines the canonical dataclasses, enums, and types for the Extensible Rule
Management engine, supporting multi-tier governance, lifecycle transitions,
and deterministic precedence resolution.
==============================================================================
"""

import re
import datetime
from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional, Set

class RuleType(str, Enum):
    PATTERN = "pattern"
    NAMING = "naming"
    DEPENDENCY = "dependency"
    ARCHITECTURE = "architecture"
    FILE_FOLDER = "file_folder"
    AST = "ast"
    LANGUAGE_SPECIFIC = "language_specific"

class RuleSeverity(str, Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    INFO = "INFO"
    # Legacy Aliases
    P0_BLOCKING = "P0_BLOCKING"
    P1_WARNING = "P1_WARNING"
    P2_INFO = "P2_INFO"

    @classmethod
    def normalize(cls, val: Any) -> "RuleSeverity":
        if isinstance(val, RuleSeverity):
            return val
        s = str(val).strip().upper()
        if s in ("P0", "P0_BLOCKING", "BLOCKING", "CRITICAL"):
            return cls.P0
        if s in ("P1", "P1_WARNING", "WARNING", "HIGH", "MAJOR"):
            return cls.P1
        if s in ("P2", "P2_INFO", "MEDIUM", "MINOR"):
            return cls.P2
        if s in ("P3", "LOW", "NITPICK"):
            return cls.P3
        return cls.INFO

    @property
    def penalty_points(self) -> int:
        norm = RuleSeverity.normalize(self.value)
        if norm == RuleSeverity.P0:
            return 35
        elif norm == RuleSeverity.P1:
            return 15
        elif norm == RuleSeverity.P2:
            return 10
        elif norm == RuleSeverity.P3:
            return 5
        return 0

    @property
    def is_blocking(self) -> bool:
        return RuleSeverity.normalize(self.value) == RuleSeverity.P0

class RuleStatus(str, Enum):
    DRAFT = "DRAFT"
    TESTING = "TESTING"
    VALIDATED = "VALIDATED"
    ACTIVE = "ACTIVE"
    DEPRECATED = "DEPRECATED"
    ARCHIVED = "ARCHIVED"

    @classmethod
    def normalize(cls, val: Any) -> "RuleStatus":
        if isinstance(val, RuleStatus):
            return val
        s = str(val).strip().upper()
        if s in ("ACTIVE", "ENABLED", "TRUE"):
            return cls.ACTIVE
        if s in ("INACTIVE", "DISABLED", "FALSE", "ARCHIVED"):
            return cls.ARCHIVED
        if s in ("DRAFT", "NEW"):
            return cls.DRAFT
        if s in ("TESTING", "TEST"):
            return cls.TESTING
        if s in ("VALIDATED", "READY"):
            return cls.VALIDATED
        if s in ("DEPRECATED", "OBSOLETE"):
            return cls.DEPRECATED
        return cls.ACTIVE

class RuleTier(str, Enum):
    BUILTIN = "builtin"
    ORGANIZATION = "organization"
    PROJECT = "project"
    CUSTOM = "custom"

    @property
    def precedence_rank(self) -> int:
        ranks = {
            RuleTier.BUILTIN: 1,
            RuleTier.ORGANIZATION: 2,
            RuleTier.PROJECT: 3,
            RuleTier.CUSTOM: 4
        }
        return ranks.get(self, 1)

class UserRole(str, Enum):
    VIEWER = "Viewer"
    RULE_AUTHOR = "Rule Author"
    RULE_MAINTAINER = "Rule Maintainer"
    RULE_ADMIN = "Rule Admin"
    ADMINISTRATOR = "Administrator"
    ADMIN = "Administrator"

@dataclass
class RuleScope:
    include: List[str] = field(default_factory=lambda: ["**/*"])
    exclude: List[str] = field(default_factory=lambda: ["tests/**", "test/**", "node_modules/**"])
    target_layer: Optional[str] = None

@dataclass
class RuleCondition:
    pattern: Optional[str] = None
    patterns: List[str] = field(default_factory=list)
    naming_convention: Optional[str] = None
    source_layer: Optional[str] = None
    forbidden_layer: Optional[str] = None
    forbidden_targets: List[str] = field(default_factory=list)
    required_path_prefix: Optional[str] = None
    ast_selector: Optional[str] = None

@dataclass
class RuleSuppressionConfig:
    allowed: bool = True
    pragma: str = "@guardian-ignore"
    requires_reason: bool = True
    minimum_reason_length: int = 8

@dataclass
class RuleTestFixture:
    name: str
    input: str
    expected_violation: bool = True
    expected_line: Optional[int] = None
    expected_message: Optional[str] = None

@dataclass
class RuleAuditEntry:
    timestamp: str
    action: str
    actor: str = "system"
    rule_id: str = ""
    version: str = "1.0.0"
    details: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RuleDefinition:
    id: str
    name: str
    version: str = "1.0.0"
    description: str = ""
    type: RuleType = RuleType.PATTERN
    category: str = "custom"
    severity: RuleSeverity = RuleSeverity.P0
    penalty_points: int = 35
    status: RuleStatus = RuleStatus.ACTIVE
    enabled: bool = True
    tier: RuleTier = RuleTier.CUSTOM
    layer: Optional[str] = None
    architectures: List[str] = field(default_factory=lambda: ["clean_architecture", "layered_mvc"])
    languages: List[str] = field(default_factory=lambda: ["csharp", "python", "typescript"])
    scope: RuleScope = field(default_factory=RuleScope)
    condition: RuleCondition = field(default_factory=RuleCondition)
    message: str = "Rule violation detected"
    suggestion: str = "Review and refactor code according to engineering guidelines"
    rationale: str = ""
    remediation: str = ""
    suppression: RuleSuppressionConfig = field(default_factory=RuleSuppressionConfig)
    tests: List[RuleTestFixture] = field(default_factory=list)
    author: str = "system"
    created_at: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    executions_count: int = 0
    violations_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "version": self.version,
            "name": self.name,
            "description": self.description,
            "type": self.type.value if isinstance(self.type, RuleType) else str(self.type),
            "category": self.category,
            "severity": self.severity.value if isinstance(self.severity, RuleSeverity) else str(self.severity),
            "penaltyPoints": self.penalty_points,
            "penalty_points": self.penalty_points,
            "status": self.status.value if isinstance(self.status, RuleStatus) else str(self.status),
            "enabled": self.enabled,
            "tier": self.tier.value if isinstance(self.tier, RuleTier) else str(self.tier),
            "layer": self.layer,
            "architectures": self.architectures,
            "languages": self.languages,
            "scope": asdict(self.scope) if isinstance(self.scope, RuleScope) else self.scope,
            "condition": asdict(self.condition) if isinstance(self.condition, RuleCondition) else self.condition,
            "message": self.message,
            "suggestion": self.suggestion,
            "rationale": self.rationale,
            "remediation": self.remediation,
            "suppression": asdict(self.suppression) if isinstance(self.suppression, RuleSuppressionConfig) else self.suppression,
            "tests": [asdict(t) if isinstance(t, RuleTestFixture) else t for t in self.tests],
            "metadata": {
                "author": self.author,
                "created_at": self.created_at,
                "updated_at": self.updated_at,
                "executions_count": self.executions_count,
                "violations_count": self.violations_count
            }
        }
