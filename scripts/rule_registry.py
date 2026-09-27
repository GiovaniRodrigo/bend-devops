#!/usr/bin/env python3
"""
==============================================================================
Bend DevOps Guardian — Central Rule Registry & Governance Engine
==============================================================================
Manages the multi-tier rules catalog (Built-in, Organization, Project, Custom),
handles deterministic precedence resolution, persistence, lifecycle transitions,
audit trails, and RBAC authorization.
==============================================================================
"""

import os
import sys
import json
import re
import datetime
import threading
from pathlib import Path
from typing import Dict, Any, List, Optional, Set, Tuple

# Ensure repository root is in sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.rule_model import (
    RuleDefinition,
    RuleType,
    RuleSeverity,
    RuleStatus,
    RuleTier,
    UserRole,
    RuleAuditEntry
)
from scripts.rule_normalizer import RuleNormalizer
from scripts.rule_test_engine import RegexSafetyValidator, RuleTestEngine

RULES_ROOT = REPO_ROOT / "backend" / "rules"
BUILTIN_DIR = RULES_ROOT / "builtin"
ORG_DIR = RULES_ROOT / "organization"
PROJECT_DIR = RULES_ROOT / "projects"
CUSTOM_DIR = RULES_ROOT / "custom"
LEGACY_RULES_DIR = RULES_ROOT / "2_rules"

class AuditTrailRecord(dict):
    def __init__(self, entry: RuleAuditEntry):
        d = {
            "timestamp": entry.timestamp,
            "action": entry.action,
            "actor": entry.actor,
            "ruleId": entry.rule_id,
            "rule_id": entry.rule_id,
            "version": entry.version,
            "details": entry.details
        }
        super().__init__(d)
        self.timestamp = entry.timestamp
        self.action = entry.action
        self.actor = entry.actor
        self.rule_id = entry.rule_id
        self.ruleId = entry.rule_id
        self.version = entry.version
        self.details = entry.details

class RuleRegistry:
    """Central singleton managing all rules across lifecycle, tiers, and interfaces."""

    _instance: Optional["RuleRegistry"] = None
    _lock = threading.RLock()

    def __init__(self, base_dir: Optional[Path] = None, custom_rules_dir: Optional[Path] = None):
        self.base_dir = base_dir or RULES_ROOT
        self.builtin_dir = self.base_dir / "builtin"
        self.org_dir = self.base_dir / "organization"
        self.project_dir = self.base_dir / "projects"
        self.custom_dir = custom_rules_dir or (self.base_dir / "custom")
        self.legacy_2rules_dir = self.base_dir / "2_rules"

        self._rules_by_tier: Dict[RuleTier, Dict[str, RuleDefinition]] = {
            RuleTier.BUILTIN: {},
            RuleTier.ORGANIZATION: {},
            RuleTier.PROJECT: {},
            RuleTier.CUSTOM: {}
        }
        self._effective_rules_cache: Optional[Dict[str, RuleDefinition]] = None
        self._audit_trail: List[RuleAuditEntry] = []
        self._ensure_directories()
        self.load_all()

    @classmethod
    def get_instance(cls, base_dir: Optional[Path] = None) -> "RuleRegistry":
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls(base_dir)
            return cls._instance

    def _ensure_directories(self):
        for d in [self.builtin_dir, self.org_dir, self.project_dir, self.custom_dir, self.legacy_2rules_dir]:
            d.mkdir(parents=True, exist_ok=True)
            for sub in ["culture", "architecture", "security", "quality", "performance", "custom"]:
                (self.legacy_2rules_dir / sub).mkdir(parents=True, exist_ok=True)

    def _invalidate_cache(self):
        self._effective_rules_cache = None

    def record_audit(self, action: str, rule_id: str, actor: str = "system", version: str = "1.0.0", details: Optional[Dict[str, Any]] = None):
        entry = RuleAuditEntry(
            timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            action=action,
            actor=actor,
            rule_id=rule_id,
            version=version,
            details=details or {}
        )
        self._audit_trail.append(entry)

    def get_audit_trail(self, rule_id: Optional[str] = None, limit: int = 100) -> List[AuditTrailRecord]:
        entries = self._audit_trail if not rule_id else [e for e in self._audit_trail if e.rule_id == rule_id]
        return [AuditTrailRecord(e) for e in reversed(entries[-limit:])]

    def check_permission(self, role: UserRole, action: str) -> bool:
        """Role-Based Access Control matrix for governance operations."""
        if role in (UserRole.ADMINISTRATOR, UserRole.ADMIN, UserRole.RULE_ADMIN):
            return True
        if role == UserRole.RULE_MAINTAINER:
            return action in ("create", "edit", "enable", "disable", "test", "clone", "validate", "import", "export", "deprecate", "delete")
        if role == UserRole.RULE_AUTHOR:
            return action in ("create", "edit", "test", "clone", "validate", "export")
        # VIEWER
        return action in ("view", "list", "search", "test", "export")

    def load_all(self):
        """Loads all rules from built-in, organization, project, and custom folders."""
        with self._lock:
            self._rules_by_tier = {
                RuleTier.BUILTIN: {},
                RuleTier.ORGANIZATION: {},
                RuleTier.PROJECT: {},
                RuleTier.CUSTOM: {}
            }

            # 1. Built-in Rules
            self._load_from_dir(self.builtin_dir, RuleTier.BUILTIN)
            self._load_from_legacy_rules()

            # 2. Organization Rules
            self._load_from_dir(self.org_dir, RuleTier.ORGANIZATION)

            # 3. Project Rules
            self._load_from_dir(self.project_dir, RuleTier.PROJECT)

            # 4. Custom Rules
            self._load_from_dir(self.custom_dir, RuleTier.CUSTOM)
            self._load_from_dir(self.legacy_2rules_dir / "custom", RuleTier.CUSTOM)

            self._invalidate_cache()

    def _load_from_dir(self, directory: Path, tier: RuleTier):
        if not directory.exists():
            return
        for file_path in directory.rglob("*.json"):
            try:
                data = json.loads(file_path.read_text(encoding="utf-8"))
                if "rules" in data and isinstance(data["rules"], list):
                    for r_dict in data["rules"]:
                        rule = RuleNormalizer.normalize_rule_dict(r_dict, default_tier=tier)
                        rule.tier = tier
                        self._rules_by_tier[tier][rule.id] = rule
                elif "id" in data:
                    rule = RuleNormalizer.normalize_rule_dict(data, default_tier=tier)
                    rule.tier = tier
                    self._rules_by_tier[tier][rule.id] = rule
            except Exception:
                pass

    def _load_from_legacy_rules(self):
        """Loads legacy architecture and culture manifests for backward compatibility."""
        # 1. 2_rules/*.json
        if self.legacy_2rules_dir.exists():
            for p in self.legacy_2rules_dir.glob("*.json"):
                try:
                    data = json.loads(p.read_text(encoding="utf-8"))
                    for r in data.get("rules", []):
                        rule = RuleNormalizer.normalize_rule_dict(r, default_tier=RuleTier.BUILTIN)
                        rule.tier = RuleTier.BUILTIN
                        self._rules_by_tier[RuleTier.BUILTIN][rule.id] = rule
                except Exception:
                    pass

        # 2. backend/rules/architecture_*.json
        for p in self.base_dir.glob("architecture_*.json"):
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                for r in data.get("rules", []):
                    rule = RuleNormalizer.normalize_rule_dict(r, default_tier=RuleTier.BUILTIN)
                    rule.tier = RuleTier.BUILTIN
                    self._rules_by_tier[RuleTier.BUILTIN][rule.id] = rule
            except Exception:
                pass

        # 3. culture_manifesto.json
        culture_path = self.base_dir / "culture_manifesto.json"
        if culture_path.exists():
            try:
                data = json.loads(culture_path.read_text(encoding="utf-8"))
                for r in data.get("rules", []):
                    rule = RuleNormalizer.normalize_rule_dict(r, default_tier=RuleTier.BUILTIN)
                    rule.tier = RuleTier.BUILTIN
                    self._rules_by_tier[RuleTier.BUILTIN][rule.id] = rule
            except Exception:
                pass

    def resolve(self) -> Dict[str, RuleDefinition]:
        """Resolves the Effective Rule Set applying deterministic precedence:
           Built-in (rank 1) < Organization (rank 2) < Project (rank 3) < Custom (rank 4)."""
        if self._effective_rules_cache is not None:
            return self._effective_rules_cache

        effective: Dict[str, RuleDefinition] = {}

        # 1. Base: Builtin
        for rule_id, rule in self._rules_by_tier[RuleTier.BUILTIN].items():
            effective[rule_id] = rule

        # 2. Organization overrides
        for rule_id, rule in self._rules_by_tier[RuleTier.ORGANIZATION].items():
            effective[rule_id] = rule

        # 3. Project overrides
        for rule_id, rule in self._rules_by_tier[RuleTier.PROJECT].items():
            effective[rule_id] = rule

        # 4. Custom overrides (Highest Precedence)
        for rule_id, rule in self._rules_by_tier[RuleTier.CUSTOM].items():
            effective[rule_id] = rule

        self._effective_rules_cache = effective
        return effective

    def get(self, rule_id: str) -> Optional[RuleDefinition]:
        rule_id = rule_id.strip().upper()
        effective = self.resolve()
        return effective.get(rule_id)

    def list(
        self,
        category: Optional[str] = None,
        severity: Optional[str] = None,
        language: Optional[str] = None,
        status: Optional[str] = None,
        rule_type: Optional[str] = None,
        architecture: Optional[str] = None,
        search_query: Optional[str] = None,
        tier: Optional[str] = None,
        active_only: bool = False
    ) -> List[RuleDefinition]:
        """Lists resolved rules matching multi-dimensional filter criteria."""
        rules = list(self.resolve().values())

        if active_only:
            rules = [r for r in rules if r.enabled and r.status == RuleStatus.ACTIVE]

        if category and category.lower() != "all":
            c_low = category.lower()
            rules = [r for r in rules if c_low in r.category.lower()]

        if severity and severity.upper() != "ALL":
            s_norm = RuleSeverity.normalize(severity)
            rules = [r for r in rules if RuleSeverity.normalize(r.severity) == s_norm]

        if language and language.lower() != "all":
            l_low = language.lower()
            rules = [r for r in rules if any(l_low in lang.lower() for lang in r.languages)]

        if status and status.upper() != "ALL":
            st_norm = RuleStatus.normalize(status)
            rules = [r for r in rules if RuleStatus.normalize(r.status) == st_norm]

        if rule_type and rule_type.lower() != "all":
            t_low = rule_type.lower()
            rules = [r for r in rules if r.type.value == t_low or str(r.type) == t_low]

        if architecture and architecture.lower() != "all":
            a_low = architecture.lower()
            rules = [r for r in rules if any(a_low in arch.lower() for arch in r.architectures)]

        if tier and tier.lower() != "all":
            t_low = tier.lower()
            rules = [r for r in rules if r.tier.value == t_low]

        if search_query and search_query.strip():
            q = search_query.strip().lower()
            rules = [
                r for r in rules if
                q in r.id.lower() or
                q in r.name.lower() or
                q in r.description.lower() or
                q in r.category.lower() or
                q in r.message.lower()
            ]

        return sorted(rules, key=lambda r: (r.tier.precedence_rank, r.id))

    def search(self, query: str) -> List[RuleDefinition]:
        return self.list(search_query=query)

    def validate_rule(self, rule_dict_or_def: Any) -> Tuple[bool, List[str]]:
        """Validates a rule dictionary or instance against schema, types, and ReDoS safety."""
        errors = []
        if isinstance(rule_dict_or_def, dict):
            rule_id = str(rule_dict_or_def.get("id", "")).strip().upper()
            name = str(rule_dict_or_def.get("name", "")).strip()
            pattern = rule_dict_or_def.get("condition", {}).get("pattern", rule_dict_or_def.get("pattern", ""))
            patterns = rule_dict_or_def.get("condition", {}).get("patterns", rule_dict_or_def.get("detection_patterns", []))
            rule_type = str(rule_dict_or_def.get("type", "pattern")).strip().lower()
        elif isinstance(rule_dict_or_def, RuleDefinition):
            rule_id = rule_dict_or_def.id
            name = rule_dict_or_def.name
            pattern = rule_dict_or_def.condition.pattern
            patterns = rule_dict_or_def.condition.patterns
            rule_type = rule_dict_or_def.type.value
        else:
            return False, ["Invalid rule data format"]

        if not rule_id or not re.match(r"^[A-Z0-9_-]+$", rule_id):
            errors.append(f"Invalid rule ID '{rule_id}'. Must contain only uppercase letters, numbers, hyphens, and underscores.")

        if not name or len(name) < 2:
            errors.append("Rule name must have at least 2 characters.")

        valid_types = {t.value for t in RuleType}
        if rule_type not in valid_types:
            errors.append(f"Invalid rule type '{rule_type}'. Allowed types: {', '.join(sorted(valid_types))}")

        # ReDoS Safety check for pattern rules
        all_patterns = patterns or ([pattern] if pattern else [])
        if rule_type == "pattern" and all_patterns:
            for pat in all_patterns:
                is_safe, err_msg = RegexSafetyValidator.is_safe_pattern(pat)
                if not is_safe:
                    errors.append(f"Unsafe pattern '{pat}': {err_msg}")

        return len(errors) == 0, errors

    def register(self, rule: RuleDefinition, actor: str = "system", persist: bool = True, user_role: Optional[UserRole] = None) -> RuleDefinition:
        """Registers and persists a new or updated rule in the registry."""
        tier = rule.tier or RuleTier.CUSTOM
        is_new = rule.id not in self._rules_by_tier.get(tier, {})
        action_name = "create" if is_new else "edit"
        if user_role is not None and not self.check_permission(user_role, action_name):
            raise PermissionError(f"User role '{user_role}' lacks permission to {action_name} rules")

        is_valid, errors = self.validate_rule(rule)
        if not is_valid:
            raise ValueError(f"Rule validation failed: {'; '.join(errors)}")

        rule.updated_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
        self._rules_by_tier[tier][rule.id] = rule
        self._invalidate_cache()

        if persist and tier == RuleTier.CUSTOM:
            self._persist_custom_rule(rule)

        action = "CREATE" if is_new else "UPDATE"
        self.record_audit(action=action, rule_id=rule.id, actor=actor, version=rule.version, details={"name": rule.name, "tier": tier.value})
        return rule

    def _persist_custom_rule(self, rule: RuleDefinition):
        """Saves a custom rule as a JSON file in backend/rules/custom/."""
        self.custom_dir.mkdir(parents=True, exist_ok=True)
        file_path = self.custom_dir / f"{rule.id.lower()}.json"
        data = rule.to_dict()
        file_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def unregister(self, rule_id: str, actor: str = "system", hard_delete: bool = True, user_role: Optional[UserRole] = None) -> bool:
        """Deletes or archives a custom rule."""
        if user_role is not None and not self.check_permission(user_role, "delete"):
            raise PermissionError(f"User role '{user_role}' lacks permission to delete rules")

        rule_id = rule_id.strip().upper()
        found = False

        for tier in [RuleTier.CUSTOM, RuleTier.PROJECT, RuleTier.ORGANIZATION]:
            if rule_id in self._rules_by_tier[tier]:
                rule = self._rules_by_tier[tier][rule_id]
                if hard_delete:
                    del self._rules_by_tier[tier][rule_id]
                    # Remove persisted file if present
                    custom_file = self.custom_dir / f"{rule_id.lower()}.json"
                    if custom_file.exists():
                        custom_file.unlink()
                    self.record_audit(action="DELETE", rule_id=rule_id, actor=actor, version=rule.version)
                else:
                    rule.status = RuleStatus.ARCHIVED
                    rule.enabled = False
                    self._persist_custom_rule(rule)
                    self.record_audit(action="ARCHIVE", rule_id=rule_id, actor=actor, version=rule.version)
                found = True

        if found:
            self._invalidate_cache()
        return found

    def enable(self, rule_id: str, actor: str = "system", user_role: Optional[UserRole] = None) -> Optional[RuleDefinition]:
        if user_role is not None and not self.check_permission(user_role, "enable"):
            raise PermissionError(f"User role '{user_role}' lacks permission to enable rules")

        rule = self.get(rule_id)
        if not rule:
            return None
        rule.enabled = True
        rule.status = RuleStatus.ACTIVE
        rule.updated_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
        if rule.tier == RuleTier.CUSTOM:
            self._persist_custom_rule(rule)
        self._invalidate_cache()
        self.record_audit(action="ENABLE", rule_id=rule.id, actor=actor, version=rule.version)
        return rule

    def disable(self, rule_id: str, actor: str = "system", user_role: Optional[UserRole] = None) -> Optional[RuleDefinition]:
        if user_role is not None and not self.check_permission(user_role, "disable"):
            raise PermissionError(f"User role '{user_role}' lacks permission to disable rules")

        rule = self.get(rule_id)
        if not rule:
            return None
        rule.enabled = False
        rule.status = RuleStatus.ARCHIVED
        rule.updated_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
        if rule.tier == RuleTier.CUSTOM:
            self._persist_custom_rule(rule)
        self._invalidate_cache()
        self.record_audit(action="DISABLE", rule_id=rule.id, actor=actor, version=rule.version)
        return rule

    def clone(self, source_id: str, new_id: str, new_name: Optional[str] = None, actor: str = "system", user_role: Optional[UserRole] = None) -> RuleDefinition:
        if user_role is not None and not self.check_permission(user_role, "clone"):
            raise PermissionError(f"User role '{user_role}' lacks permission to clone rules")

        source_id = source_id.strip().upper()
        new_id = new_id.strip().upper()

        source_rule = self.get(source_id)
        if not source_rule:
            raise ValueError(f"Source rule '{source_id}' not found")

        if self.get(new_id):
            raise ValueError(f"Rule with ID '{new_id}' already exists")

        # Create cloned copy
        cloned_dict = source_rule.to_dict()
        cloned_dict["id"] = new_id
        cloned_dict["name"] = new_name or f"{source_rule.name} (Clone)"
        cloned_dict["tier"] = RuleTier.CUSTOM.value
        cloned_dict["status"] = RuleStatus.DRAFT.value
        cloned_dict["metadata"]["author"] = actor
        cloned_dict["metadata"]["created_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        cloned_dict["metadata"]["updated_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()

        cloned_rule = RuleNormalizer.normalize_rule_dict(cloned_dict, default_tier=RuleTier.CUSTOM)
        cloned_rule.tier = RuleTier.CUSTOM
        cloned_rule.status = RuleStatus.DRAFT
        self.register(cloned_rule, actor=actor, persist=True, user_role=user_role)
        return cloned_rule

    def import_rules(self, data_or_path: Any, actor: str = "system") -> Tuple[int, List[str]]:
        """Imports rules from JSON string, dictionary, array, or directory path."""
        imported_count = 0
        errors = []

        if isinstance(data_or_path, str) and Path(data_or_path).exists():
            p = Path(data_or_path)
            if p.is_file():
                try:
                    data = json.loads(p.read_text(encoding="utf-8"))
                    return self.import_rules(data, actor=actor)
                except Exception as e:
                    return 0, [f"Failed to read file {data_or_path}: {e}"]
            elif p.is_dir():
                for f in p.rglob("*.json"):
                    cnt, errs = self.import_rules(str(f), actor=actor)
                    imported_count += cnt
                    errors.extend(errs)
                return imported_count, errors

        # Process payload
        items = []
        if isinstance(data_or_path, dict):
            if "rules" in data_or_path:
                items = data_or_path["rules"]
            else:
                items = [data_or_path]
        elif isinstance(data_or_path, list):
            items = data_or_path

        for item in items:
            if not isinstance(item, dict):
                continue
            try:
                rule = RuleNormalizer.normalize_rule_dict(item, default_tier=RuleTier.CUSTOM)
                rule.tier = RuleTier.CUSTOM
                self.register(rule, actor=actor, persist=True)
                imported_count += 1
            except Exception as e:
                errors.append(f"Failed to import rule {item.get('id', 'unknown')}: {e}")

        return imported_count, errors

    def export_manifest(self, tier: Optional[RuleTier] = None) -> str:
        tier_str = tier.value if isinstance(tier, RuleTier) else tier
        rules = self.list(tier=tier_str)
        manifest = {
            "$schema": "./rules_schema.json",
            "version": "2.0.0",
            "manifesto_name": "Bend DevOps Guardian Exported Ruleset",
            "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "total_rules": len(rules),
            "rules": [r.to_dict() for r in rules]
        }
        return json.dumps(manifest, indent=2)

    def import_manifest(
        self,
        rules_data: Any,
        overwrite: bool = True,
        actor: str = "system",
        user_role: Optional[UserRole] = None
    ) -> Dict[str, Any]:
        if user_role is not None and not self.check_permission(user_role, "import"):
            raise PermissionError(f"User role '{user_role}' lacks permission to import rules")

        items = []
        if isinstance(rules_data, dict):
            items = rules_data.get("rules", [rules_data])
        elif isinstance(rules_data, list):
            items = rules_data
        elif isinstance(rules_data, str):
            try:
                parsed = json.loads(rules_data)
                return self.import_manifest(parsed, overwrite=overwrite, actor=actor, user_role=user_role)
            except Exception as e:
                return {"imported": 0, "failed": 1, "errors": [str(e)]}

        imported = 0
        failed = 0
        errors = []

        for item in items:
            if not isinstance(item, dict):
                continue
            rule_id = item.get("id")
            if not overwrite and self.get(rule_id):
                failed += 1
                errors.append(f"Rule '{rule_id}' already exists and overwrite=False")
                continue
            try:
                rule = RuleNormalizer.normalize_rule_dict(item, default_tier=RuleTier.CUSTOM)
                rule.tier = RuleTier.CUSTOM
                self.register(rule, actor=actor, persist=True, user_role=user_role)
                imported += 1
            except Exception as e:
                failed += 1
                errors.append(f"Failed to import rule {rule_id}: {e}")

        return {
            "imported": imported,
            "failed": failed,
            "errors": errors
        }

    delete = unregister

    def export_rule(self, rule_id: str) -> Optional[Dict[str, Any]]:
        rule = self.get(rule_id)
        return rule.to_dict() if rule else None

    def export_all(self) -> Dict[str, Any]:
        rules = [r.to_dict() for r in self.list()]
        return {
            "$schema": "./rules_schema.json",
            "version": "2.0.0",
            "manifesto_name": "Bend DevOps Guardian Exported Ruleset",
            "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "total_rules": len(rules),
            "rules": rules
        }

    def get_categories(self) -> List[str]:
        cats = set()
        for r in self.resolve().values():
            if r.category:
                cats.add(r.category)
        return sorted(list(cats)) or ["culture", "architecture", "security", "quality", "performance", "custom"]

    def get_languages(self) -> List[str]:
        return ["csharp", "python", "typescript", "php", "golang", "java", "rust"]

    def get_types(self) -> List[str]:
        return [t.value for t in RuleType]

    def get_severities(self) -> List[str]:
        return ["P0", "P1", "P2", "P3", "INFO"]

    def get_statuses(self) -> List[str]:
        return [s.value for s in RuleStatus]
