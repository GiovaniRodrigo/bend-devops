#!/usr/bin/env python3
"""
==============================================================================
Bend DevOps Guardian — Rule Normalizer
==============================================================================
Transforms raw rule JSON payloads, legacy rules, and manifest dictionaries
into canonical, strongly-typed RuleDefinition instances.
==============================================================================
"""

import re
import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

from scripts.rule_model import (
    RuleDefinition,
    RuleType,
    RuleSeverity,
    RuleStatus,
    RuleTier,
    RuleScope,
    RuleCondition,
    RuleSuppressionConfig,
    RuleTestFixture
)

class RuleNormalizer:
    """Canonical normalizer for rule definitions across all tiers."""

    @classmethod
    def normalize_rule_dict(
        cls,
        raw: Dict[str, Any],
        default_tier: RuleTier = RuleTier.CUSTOM,
        fallback_tier: Optional[RuleTier] = None,
        **kwargs
    ) -> RuleDefinition:
        """Normalizes a raw dictionary into a canonical RuleDefinition."""
        effective_default_tier = fallback_tier or default_tier
        rule_id = str(raw.get("id", "")).strip().upper()
        name = str(raw.get("name", rule_id or "Unnamed Rule")).strip()
        version = str(raw.get("version", "1.0.0")).strip()
        description = str(raw.get("description", raw.get("rationale", ""))).strip()
        
        # Category
        raw_cat = str(raw.get("category", "custom")).strip()

        # Rule Type
        raw_cond = raw.get("condition") if isinstance(raw.get("condition"), dict) else {}
        raw_type = str(raw.get("type", "")).strip().lower()
        if raw_type in [t.value for t in RuleType]:
            rule_type = RuleType(raw_type)
        elif raw.get("forbidden_targets") or raw_cond.get("forbidden_targets"):
            rule_type = RuleType.DEPENDENCY
        elif "architecture" in raw_cat.lower() or rule_id.startswith("ARCH"):
            rule_type = RuleType.ARCHITECTURE
        elif raw.get("detection_patterns") or raw.get("pattern") or raw_cond.get("pattern"):
            rule_type = RuleType.PATTERN
        else:
            rule_type = RuleType.PATTERN

        # Canonical category assignment
        if "security" in raw_cat.lower() or "sec" in rule_id.lower():
            category = "security"
        elif "culture" in raw_cat.lower() or "cult" in rule_id.lower():
            category = "culture"
        elif "performance" in raw_cat.lower() or "perf" in rule_id.lower():
            category = "performance"
        elif "quality" in raw_cat.lower():
            category = "quality"
        elif "architecture" in raw_cat.lower() or "boundary" in raw_cat.lower() or "arch" in rule_id.lower():
            category = "architecture"
        else:
            category = raw_cat.lower()

        # Severity & Penalty
        sev_val = raw.get("severity", "P0")
        severity = RuleSeverity.normalize(sev_val)
        
        penalty = raw.get("penalty_points", raw.get("penaltyPoints", raw.get("penalty", None)))
        if penalty is None:
            penalty = severity.penalty_points
        else:
            try:
                penalty = int(penalty)
            except Exception:
                penalty = severity.penalty_points

        # Status & Enabled
        status_val = raw.get("status", "ACTIVE")
        status = RuleStatus.normalize(status_val)
        
        enabled = raw.get("enabled", True)
        if isinstance(enabled, str):
            enabled = enabled.lower() in ("true", "1", "yes")
        if status == RuleStatus.ARCHIVED or status == RuleStatus.DEPRECATED:
            if "enabled" not in raw:
                enabled = False

        # Tier
        tier_val = str(raw.get("tier", effective_default_tier.value)).strip().lower()
        try:
            tier = RuleTier(tier_val)
        except Exception:
            tier = effective_default_tier

        layer = raw.get("layer", None)

        # Architectures & Languages
        archs = raw.get("architectures", [])
        if isinstance(archs, str):
            archs = [archs]
        if not archs:
            archs = ["clean_architecture", "layered_mvc", "microservices", "cqrs_event_sourcing", "rest_api", "frontend_clean"]

        languages = raw.get("languages", [])
        if isinstance(languages, str):
            languages = [languages]
        if not languages:
            languages = ["csharp", "python", "typescript", "php", "golang", "java", "rust"]

        # Scope
        raw_scope = raw.get("scope", {})
        if isinstance(raw_scope, dict):
            include_patterns = raw_scope.get("include", ["**/*"])
            exclude_patterns = raw_scope.get("exclude", ["tests/**", "test/**", "node_modules/**"])
            target_layer = raw_scope.get("target_layer", layer)
        else:
            include_patterns = ["**/*"]
            exclude_patterns = ["tests/**", "test/**"]
            target_layer = layer
        scope = RuleScope(include=include_patterns, exclude=exclude_patterns, target_layer=target_layer)

        # Condition
        raw_cond = raw.get("condition", {})
        if not isinstance(raw_cond, dict):
            raw_cond = {}
            
        pattern = raw_cond.get("pattern", raw.get("pattern", None))
        patterns = raw_cond.get("patterns", raw.get("detection_patterns", []))
        
        # Built-in canonical fallback patterns
        if not patterns and not pattern:
            if rule_id == "CULT01":
                patterns = [
                    r"(?i)#\s*TODO",
                    r"(?i)//\s*TODO",
                    r"(?i)#\s*FIXME",
                    r"(?i)//\s*FIXME",
                    r"(?i)to\s+be\s+implemented",
                    r"(?i)implement\s+later",
                    r"^\s*pass\s*$",
                    r"raise\s+NotImplementedError",
                ]
            elif rule_id == "CULT04":
                patterns = [
                    r"(?i)(api[_-]?key|secret|password|token|bearer)\s*[:=]\s*['\"][A-Za-z0-9_\-\.]{12,}['\"]",
                    r"ghp_[0-9a-zA-Z]{36,}",
                    r"xox[baprs]-[0-9a-zA-Z]{10,}",
                ]
            elif rule_id == "CULT02":
                patterns = [
                    r"@spec\s+RF\d+",
                    r"\[RF\d+\]",
                    r"Requirement:\s*RF\d+",
                    r"Spec-ID:\s*RF\d+",
                ]

        if pattern and not patterns:
            patterns = [pattern]
        elif patterns and not pattern:
            pattern = patterns[0]

        naming_convention = raw_cond.get("naming_convention", raw.get("naming_convention", None))
        source_layer = raw_cond.get("source_layer", raw.get("source_layer", layer))
        forbidden_layer = raw_cond.get("forbidden_layer", raw.get("forbidden_layer", None))
        forbidden_targets = raw_cond.get("forbidden_targets", raw.get("forbidden_targets", []))
        required_path_prefix = raw_cond.get("required_path_prefix", raw.get("required_path_prefix", None))
        ast_selector = raw_cond.get("ast_selector", raw.get("ast_selector", None))

        condition = RuleCondition(
            pattern=pattern,
            patterns=patterns,
            naming_convention=naming_convention,
            source_layer=source_layer,
            forbidden_layer=forbidden_layer,
            forbidden_targets=forbidden_targets,
            required_path_prefix=required_path_prefix,
            ast_selector=ast_selector
        )

        message = str(raw.get("message", raw.get("description", "Rule violation detected"))).strip()
        suggestion = str(raw.get("suggestion", raw.get("remediation", "Refactor code to satisfy engineering rule"))).strip()
        rationale = str(raw.get("rationale", description)).strip()
        remediation = str(raw.get("remediation", suggestion)).strip()

        # Suppression
        raw_supp = raw.get("suppression", {})
        if isinstance(raw_supp, dict):
            supp_allowed = raw_supp.get("allowed", True)
            supp_pragma = raw_supp.get("pragma", "@guardian-ignore")
            supp_req_reason = raw_supp.get("requires_reason", True)
            supp_min_len = int(raw_supp.get("minimum_reason_length", 8))
        else:
            supp_allowed = True
            supp_pragma = "@guardian-ignore"
            supp_req_reason = True
            supp_min_len = 8

        suppression = RuleSuppressionConfig(
            allowed=supp_allowed,
            pragma=supp_pragma,
            requires_reason=supp_req_reason,
            minimum_reason_length=supp_min_len
        )

        # Tests / Fixtures
        tests = []
        for t in raw.get("tests", []):
            if isinstance(t, dict) and "input" in t:
                tests.append(RuleTestFixture(
                    name=t.get("name", "Test case"),
                    input=t.get("input", ""),
                    expected_violation=t.get("expected_violation", True),
                    expected_line=t.get("expected_line"),
                    expected_message=t.get("expected_message")
                ))

        # Metadata
        meta = raw.get("metadata", {})
        author = meta.get("author", raw.get("author", "system"))
        created_at = meta.get("created_at", raw.get("created_at", datetime.datetime.now(datetime.timezone.utc).isoformat()))
        updated_at = meta.get("updated_at", raw.get("updated_at", datetime.datetime.now(datetime.timezone.utc).isoformat()))
        exec_count = int(meta.get("executions_count", 0))
        viol_count = int(meta.get("violations_count", 0))

        return RuleDefinition(
            id=rule_id,
            name=name,
            version=version,
            description=description,
            type=rule_type,
            category=category,
            severity=severity,
            penalty_points=penalty,
            status=status,
            enabled=enabled,
            tier=tier,
            layer=layer,
            architectures=archs,
            languages=languages,
            scope=scope,
            condition=condition,
            message=message,
            suggestion=suggestion,
            rationale=rationale,
            remediation=remediation,
            suppression=suppression,
            tests=tests,
            author=author,
            created_at=created_at,
            updated_at=updated_at,
            executions_count=exec_count,
            violations_count=viol_count
        )

    normalize = normalize_rule_dict
