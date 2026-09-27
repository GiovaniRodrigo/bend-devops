#!/usr/bin/env python3
"""
==============================================================================
Bend DevOps Guardian — Isolated Rule Test Engine & Safety Validator
==============================================================================
Provides isolated rule execution and verification against source code inputs,
test fixtures, and edge cases with ReDoS protection and pragma compliance checks.
==============================================================================
"""

import re
import time
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

from scripts.rule_model import (
    RuleDefinition,
    RuleType,
    RuleSeverity,
    RuleStatus,
    RuleTestFixture
)
from scripts.token_filter import strip_comments, parse_inline_pragmas

class RegexSafetyValidator:
    """Validates regex patterns against catastrophic backtracking (ReDoS)."""

    NESTED_QUANTIFIER_REGEX = re.compile(r"\([^)]*[\+\*][^)]*\)\s*[\+\*]")

    @classmethod
    def is_safe_pattern(cls, pattern: str) -> Tuple[bool, Optional[str]]:
        if not pattern or not str(pattern).strip():
            return False, "Pattern cannot be empty"
        
        # Check basic syntax
        try:
            compiled = re.compile(pattern)
        except re.error as e:
            return False, f"Invalid regex syntax: {e}"

        # Check for dangerous nested quantifiers (e.g. (a+)+, (\w+)+, (\.*)+, etc.)
        if cls.NESTED_QUANTIFIER_REGEX.search(pattern):
            return False, f"Potentially dangerous regex pattern with nested quantifiers (ReDoS risk): {pattern}"

        # Timeout benchmark test on adversarial synthetic input
        adversarial_inputs = [
            "a" * 100 + "!" + "a" * 100,
            "1234567890" * 10 + "!",
            " " * 100 + "X",
            "a=b;a=b;a=b;" * 10 + "!"
        ]
        for adv_in in adversarial_inputs:
            start_t = time.perf_counter()
            try:
                compiled.search(adv_in)
                duration = time.perf_counter() - start_t
                if duration > 0.1:  # 100ms threshold
                    return False, f"Pattern took {duration:.3f}s on synthetic input (exceeds 0.1s ReDoS threshold)"
            except Exception as e:
                return False, f"Regex evaluation error: {e}"

        return True, None

class RuleTestResult:
    def __init__(self, rule_id: str):
        self.rule_id = rule_id
        self.passed: bool = True
        self.has_violation: bool = False
        self.is_suppressed: bool = False
        self.suppression_reason: Optional[str] = None
        self.matched_lines: List[int] = []
        self.violations: List[Dict[str, Any]] = []
        self.pragma_warnings: List[Dict[str, Any]] = []
        self.error: Optional[str] = None
        self.duration_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ruleId": self.rule_id,
            "rule_id": self.rule_id,
            "passed": self.passed,
            "hasViolation": self.has_violation,
            "has_violation": self.has_violation,
            "isSuppressed": self.is_suppressed,
            "is_suppressed": self.is_suppressed,
            "suppressionReason": self.suppression_reason,
            "suppression_reason": self.suppression_reason,
            "matchedLines": self.matched_lines,
            "matched_lines": self.matched_lines,
            "violations": self.violations,
            "pragmaWarnings": self.pragma_warnings,
            "error": self.error,
            "durationMs": round(self.duration_ms, 2),
            "duration_ms": round(self.duration_ms, 2)
        }

class RuleTestEngine:
    """Evaluates rules against source code inputs and test fixtures."""

    @staticmethod
    def test_rule(
        rule: RuleDefinition,
        source_code: str,
        file_path: Optional[str] = None,
        expected_violation: Optional[bool] = None,
        file_name: Optional[str] = None,
        **kwargs
    ) -> RuleTestResult:
        if file_path is None:
            file_path = file_name or "test_sample.py"

        start_t = time.perf_counter()
        result = RuleTestResult(rule.id)

        if not source_code:
            result.duration_ms = (time.perf_counter() - start_t) * 1000
            result.passed = (expected_violation is False or expected_violation is None)
            return result

        lines = source_code.splitlines()
        ext = Path(file_path).suffix or ".py"

        # 1. Parse inline pragmas and check suppression
        suppressed_map, pragma_warnings = parse_inline_pragmas(lines)
        result.pragma_warnings.extend(pragma_warnings)

        # 2. Scope & Extension check
        if rule.languages:
            lang_map = {
                ".py": "python",
                ".ts": "typescript",
                ".tsx": "typescript",
                ".js": "typescript",
                ".jsx": "typescript",
                ".cs": "csharp",
                ".cshtml": "csharp",
                ".php": "php",
                ".go": "golang",
                ".java": "java",
                ".rs": "rust"
            }
            detected_lang = lang_map.get(ext, "")
            if detected_lang and detected_lang not in rule.languages:
                # File language not targeted by rule
                result.duration_ms = (time.perf_counter() - start_t) * 1000
                result.passed = (expected_violation is False or expected_violation is None)
                return result

        # 3. Evaluate by Rule Type
        if rule.type == RuleType.PATTERN or rule.type == RuleType.LANGUAGE_SPECIFIC or rule.type == RuleType.ARCHITECTURE:
            patterns = rule.condition.patterns or ([rule.condition.pattern] if rule.condition.pattern else [])
            if not patterns and rule.condition.forbidden_targets:
                patterns = [re.escape(t) for t in rule.condition.forbidden_targets]

            for pattern_str in patterns:
                if not pattern_str:
                    continue
                try:
                    compiled_re = re.compile(pattern_str)
                except re.error as e:
                    result.error = f"Invalid regex in rule {rule.id}: {e}"
                    result.passed = False
                    result.duration_ms = (time.perf_counter() - start_t) * 1000
                    return result

                for idx, line in enumerate(lines, 1):
                    code_only = strip_comments(line, ext).strip()
                    if not code_only:
                        continue

                    if compiled_re.search(code_only):
                        result.has_violation = True
                        # Check inline suppression
                        is_supp = False
                        if idx in suppressed_map:
                            if rule.id in suppressed_map[idx] or "ALL" in suppressed_map[idx]:
                                is_supp = True
                                result.is_suppressed = True
                                reason = suppressed_map[idx].get(rule.id) or suppressed_map[idx].get("ALL") or f"Suppressed via pragma on line {idx}"
                                result.suppression_reason = reason

                        if is_supp:
                            continue

                        result.matched_lines.append(idx)
                        result.violations.append({
                            "ruleId": rule.id,
                            "rule_id": rule.id,
                            "fileName": file_path,
                            "severity": rule.severity.value,
                            "penalty": rule.penalty_points,
                            "line": idx,
                            "snippet": code_only,
                            "message": rule.message or f"Violation of rule {rule.id}",
                            "suggestion": rule.suggestion or rule.remediation,
                            "remediation": rule.remediation or rule.suggestion
                        })

        elif rule.type == RuleType.NAMING:
            conv = rule.condition.naming_convention or "PascalCase"
            for idx, line in enumerate(lines, 1):
                code_only = strip_comments(line, ext).strip()
                # Find class/function definitions
                matches = re.findall(r"(?:class|interface|struct|enum|def|function)\s+([A-Za-z0-9_]+)", code_only)
                for ident in matches:
                    violates = False
                    if conv == "PascalCase" and not (ident[0].isupper() and "_" not in ident):
                        violates = True
                    elif conv == "camelCase" and not (ident[0].islower() and "_" not in ident):
                        violates = True
                    elif conv == "snake_case" and not (ident.islower() or "_" in ident):
                        violates = True
                    elif conv == "UPPER_CASE" and not ident.isupper():
                        violates = True

                    if violates:
                        result.has_violation = True
                        is_supp = (idx in suppressed_map and (rule.id in suppressed_map[idx] or "ALL" in suppressed_map[idx]))
                        if is_supp:
                            result.is_suppressed = True
                            result.suppression_reason = suppressed_map[idx].get(rule.id) or suppressed_map[idx].get("ALL") or f"Suppressed via pragma on line {idx}"
                        else:
                            result.matched_lines.append(idx)
                            result.violations.append({
                                "ruleId": rule.id,
                                "fileName": file_path,
                                "severity": rule.severity.value,
                                "penalty": rule.penalty_points,
                                "line": idx,
                                "snippet": code_only,
                                "message": f"Identifier '{ident}' violates {conv} naming convention ({rule.message})",
                                "suggestion": f"Rename '{ident}' to adhere to {conv}"
                            })

        elif rule.type == RuleType.DEPENDENCY:
            forbidden = rule.condition.forbidden_targets or []
            if rule.condition.forbidden_layer:
                forbidden.append(rule.condition.forbidden_layer)
            for f_target in forbidden:
                pattern_dep = r"(?i)\b" + re.escape(f_target) + r"\b"
                for idx, line in enumerate(lines, 1):
                    code_only = strip_comments(line, ext).strip()
                    if re.search(pattern_dep, code_only):
                        result.has_violation = True
                        is_supp = (idx in suppressed_map and (rule.id in suppressed_map[idx] or "ALL" in suppressed_map[idx]))
                        if is_supp:
                            result.is_suppressed = True
                            result.suppression_reason = suppressed_map[idx].get(rule.id) or suppressed_map[idx].get("ALL") or f"Suppressed via pragma on line {idx}"
                        else:
                            result.matched_lines.append(idx)
                            result.violations.append({
                                "ruleId": rule.id,
                                "fileName": file_path,
                                "severity": rule.severity.value,
                                "penalty": rule.penalty_points,
                                "line": idx,
                                "snippet": code_only,
                                "message": f"Forbidden dependency on '{f_target}' ({rule.message})",
                                "suggestion": rule.suggestion or f"Decouple from {f_target} using abstractions"
                            })

        elif rule.type == RuleType.FILE_FOLDER:
            req_prefix = rule.condition.required_path_prefix
            if req_prefix and not file_path.replace("\\", "/").startswith(req_prefix.replace("\\", "/")):
                result.has_violation = True
                result.matched_lines.append(1)
                result.violations.append({
                    "ruleId": rule.id,
                    "fileName": file_path,
                    "severity": rule.severity.value,
                    "penalty": rule.penalty_points,
                    "line": 1,
                    "snippet": file_path,
                    "message": f"File path '{file_path}' does not match required folder '{req_prefix}'",
                    "suggestion": f"Move file to '{req_prefix}'"
                })

        # Calculate pass/fail based on expected violation
        if expected_violation is not None:
            result.passed = (result.has_violation == expected_violation)
        else:
            result.passed = (len(result.violations) == 0)

        result.duration_ms = (time.perf_counter() - start_t) * 1000
        return result

    @classmethod
    def run_all_rule_fixtures(cls, rule: RuleDefinition) -> Tuple[bool, List[RuleTestResult]]:
        results = []
        all_passed = True
        for fixture in rule.tests:
            res = cls.test_rule(
                rule=rule,
                source_code=fixture.input,
                file_path=f"fixture_{fixture.name.replace(' ', '_')}.py",
                expected_violation=fixture.expected_violation
            )
            results.append(res)
            if not res.passed:
                all_passed = False
        return all_passed, results

    run_test = test_rule

    @classmethod
    def execute_fixtures(cls, rule: RuleDefinition) -> Dict[str, Any]:
        passed, results = cls.run_all_rule_fixtures(rule)
        passed_count = sum(1 for r in results if r.passed)
        return {
            "passed": passed,
            "total_fixtures": len(rule.tests),
            "passed_fixtures": passed_count,
            "failed_fixtures": len(rule.tests) - passed_count,
            "results": [r.to_dict() for r in results]
        }
