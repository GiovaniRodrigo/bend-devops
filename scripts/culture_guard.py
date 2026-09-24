#!/usr/bin/env python3
"""
# ==============================================================================
# Bend DevOps Guardian CLI (Bend Parallel HVM Quality Gate)
# ==============================================================================
# Reads source files across any tech stack (C#, Python, TypeScript, PHP, Go,
# Java, Rust), classifies architectural layers, loads the Layer Vocabulary &
# Token Taxonomy from `backend/rules/`, extracts compliance features, and submits
# the AST/file-tree to the massively parallel Bend (HVM) engine for verification.
# ==============================================================================
"""

import sys
import os
import re
import json
import subprocess
import argparse
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any, Set

# Ensure repository root is in sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.token_filter import (
    TokenFilter,
    parse_inline_pragmas,
    strip_comments,
    matches_exact_token,
    load_guardianignore,
    is_file_or_rule_exempt
)
from scripts.vcs_adapters import get_vcs_adapter, BranchPolicyEngine

# Base path for rules catalog
RULES_BASE_DIR = REPO_ROOT / "backend" / "rules"

# Regex Patterns for Cultural and Quality Rules
SECRET_PATTERNS = [
    r"(?i)(api[_-]?key|secret|password|token|bearer)\s*[:=]\s*['\"][A-Za-z0-9_\-\.]{12,}['\"]",
    r"ghp_[0-9a-zA-Z]{36,}",
    r"xox[baprs]-[0-9a-zA-Z]{10,}",
]

LAZY_PATTERNS = [
    r"(?i)#\s*TODO",
    r"(?i)//\s*TODO",
    r"(?i)#\s*FIXME",
    r"(?i)//\s*FIXME",
    r"(?i)to\s+be\s+implemented",
    r"(?i)implement\s+later",
    r"^\s*pass\s*$",
    r"raise\s+NotImplementedError",
]

SPEC_PATTERNS = [
    r"@spec\s+RF\d+",
    r"\[RF\d+\]",
    r"Requirement:\s*RF\d+",
    r"Spec-ID:\s*RF\d+",
]

# Supported source file extensions
SUPPORTED_EXTENSIONS = {
    ".py", ".ts", ".js", ".tsx", ".jsx", ".bend", 
    ".cs", ".cshtml", ".razor", ".php", ".go", ".java", ".rs"
}

# Fallback layer classification mappings
DEFAULT_LAYER_PATTERNS = [
    (r"(?i)(models|domain/entities|entities|domain)/.*\.(cs|py|ts|js|php|java|go|rs|rb)$", "Model"),
    (r"(?i)(controllers|endpoints|handlers|api|routes)/.*\.(cs|py|ts|js|php|java|go|rs|rb)$", "Controller"),
    (r"(?i)(views|templates|pages)/.*\.(cshtml|razor|blade\.php|jinja2|html|erb|tsx|vue)$", "View"),
    (r"(?i)(services|usecases|use_cases|domain/services)/.*\.(cs|py|ts|js|php|java|go|rs|rb)$", "Service"),
    (r"(?i)(validators|requests|dtos|schemas)/.*\.(cs|py|ts|js|php|java|go|rs|rb)$", "RequestValidator"),
    (r"(?i)(components/ui|atoms|molecules)/.*\.(tsx|vue|ts|html)$", "PresentationalUI"),
]

def load_layer_vocabulary() -> Dict[str, Any]:
    """Loads layer_vocabulary.json if available, or returns default mappings"""
    vocab_path = RULES_BASE_DIR / "layer_vocabulary.json"
    if vocab_path.exists():
        try:
            return json.loads(vocab_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}

def escape_for_regex(token: str) -> str:
    return re.escape(token)

def build_vocabulary_regexes(vocab: Dict[str, Any]) -> Dict[str, List[Tuple[str, str, str, int, str]]]:
    """Builds forbidden regexes per layer based on layer_vocabulary.json"""
    presentation_tokens = []
    transport_tokens = []
    infra_tokens = []

    if vocab and "layers" in vocab:
        layers_cfg = vocab["layers"]
        if "Presentation" in layers_cfg:
            for cat, tokens in layers_cfg["Presentation"].get("tokens", {}).items():
                presentation_tokens.extend(tokens)
        if "Interface_Transport" in layers_cfg:
            for cat, tokens in layers_cfg["Interface_Transport"].get("tokens", {}).items():
                transport_tokens.extend(tokens)
        if "Infrastructure_Persistence" in layers_cfg:
            for cat, tokens in layers_cfg["Infrastructure_Persistence"].get("tokens", {}).items():
                infra_tokens.extend(tokens)

    # Compile regex pattern groups
    pres_pattern = (
        r"(?i)(" + "|".join(escape_for_regex(t) for t in sorted(presentation_tokens, key=len, reverse=True)) + ")"
        if presentation_tokens else
        r"(?i)(<html|<div|<span|<p>|<img|<form|<button|<table|<script|<style|document\.getElement|window\.location|echo\s*\"<|print\(\"<|Response\.Write)"
    )

    trans_pattern = (
        r"(?i)(" + "|".join(escape_for_regex(t) for t in sorted(transport_tokens, key=len, reverse=True)) + ")"
        if transport_tokens else
        r"(?i)(HttpContext|HttpRequest|request\(\)|Request::|\$_POST|\$_GET|\$_REQUEST|express\.Request|fastapi\.Request)"
    )

    infra_pattern = (
        r"(?i)(" + "|".join(escape_for_regex(t) for t in sorted(infra_tokens, key=len, reverse=True)) + ")"
        if infra_tokens else
        r"(?i)(DB::|::where\(|::find\(|::all\(\)|::query\(|SELECT\s+\*\s+FROM|DbContext|objects\.filter|objects\.all)"
    )

    forbidden_rules = {
        "Model": [
            (pres_pattern, "ARCH-LAYER-01", "P0_BLOCKING", 40, "Forbidden presentation markup/script inside Domain or Model class"),
            (trans_pattern, "ARCH-LAYER-03", "P0_BLOCKING", 30, "Forbidden HTTP/transport protocol coupling inside Domain or Model class"),
        ],
        "Domain": [
            (pres_pattern, "ARCH-LAYER-01", "P0_BLOCKING", 40, "Forbidden presentation markup/script inside Domain Entity"),
            (trans_pattern, "ARCH-LAYER-03", "P0_BLOCKING", 30, "Forbidden HTTP/transport protocol coupling inside Domain Entity"),
        ],
        "Controller": [
            (pres_pattern, "ARCH-LAYER-01", "P0_BLOCKING", 40, "Forbidden raw presentation markup inside Controller class (use ViewModels/DTOs or Templates)"),
        ],
        "Service": [
            (pres_pattern, "ARCH-LAYER-01", "P0_BLOCKING", 40, "Forbidden raw presentation markup inside Service class"),
        ],
        "View": [
            (infra_pattern, "ARCH-LAYER-02", "P0_BLOCKING", 35, "Forbidden direct database or ORM query execution inside presentation template/view"),
        ],
        "PresentationalUI": [
            (r"(?i)(fetch\(|axios\.|http\.get\(|http\.post\()", "ARCH-FE-01", "P0_BLOCKING", 35, "Forbidden direct API/network call inside pure Presentational UI component"),
        ]
    }
    return forbidden_rules

FORBIDDEN_LAYER_PATTERNS = build_vocabulary_regexes(load_layer_vocabulary())

def classify_file_layer(path: Path) -> str:
    path_str = str(path).replace("\\", "/")
    for pattern, layer in DEFAULT_LAYER_PATTERNS:
        if re.search(pattern, path_str):
            return layer
    return "Generic"

class FileAuditResult:
    def __init__(self, path: Path, project_exemptions: Optional[List[Any]] = None):
        self.path = str(path)
        self.name = path.name
        self.layer = classify_file_layer(path)
        self.lines_count = 0
        self.has_spec_tag = 0
        self.has_lazy_code = 0
        self.has_secrets = 0
        self.has_test_coverage = 0
        self.has_type_annotations = 1
        self.suppressed_count = 0
        self.violations: List[Dict[str, Any]] = []
        self._analyze(path, project_exemptions or [])

    def _analyze(self, path: Path, project_exemptions: List[Any]):
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return

        lines = content.splitlines()
        self.lines_count = len(lines)

        # Check project-level exemptions (.guardianignore)
        if is_file_or_rule_exempt(self.path, "ALL", project_exemptions):
            self.has_spec_tag = 1
            self.has_test_coverage = 1
            self.suppressed_count += 1
            return

        # 1. Spec tag check (CULT02)
        if is_file_or_rule_exempt(self.path, "CULT02", project_exemptions):
            self.has_spec_tag = 1
            self.suppressed_count += 1
        else:
            for pattern in SPEC_PATTERNS:
                if re.search(pattern, content):
                    self.has_spec_tag = 1
                    break
            if not self.has_spec_tag:
                self.violations.append({
                    "rule_id": "CULT02",
                    "severity": "P1_WARNING",
                    "penalty": 15,
                    "message": "Missing requirement traceability tag (@spec RFxx)"
                })

        # 2. Lazy code check (CULT01)
        if is_file_or_rule_exempt(self.path, "CULT01", project_exemptions):
            self.suppressed_count += 1
        else:
            for idx, line in enumerate(lines, 1):
                for pattern in LAZY_PATTERNS:
                    if re.search(pattern, line):
                        self.has_lazy_code = 1
                        self.violations.append({
                            "rule_id": "CULT01",
                            "severity": "P0_BLOCKING",
                            "penalty": 35,
                            "line": idx,
                            "snippet": line.strip(),
                            "message": f"Incomplete or lazy code detected: '{line.strip()}'"
                        })
                        break

        # 3. Secret scan (CULT04)
        if is_file_or_rule_exempt(self.path, "CULT04", project_exemptions):
            self.suppressed_count += 1
        else:
            for idx, line in enumerate(lines, 1):
                for pattern in SECRET_PATTERNS:
                    if re.search(pattern, line):
                        self.has_secrets = 1
                        self.violations.append({
                            "rule_id": "CULT04",
                            "severity": "P0_BLOCKING",
                            "penalty": 40,
                            "line": idx,
                            "snippet": line.strip(),
                            "message": "Hardcoded API secret or sensitive token detected"
                        })
                        break

        # 4. Test coverage presence check (CULT03)
        if is_file_or_rule_exempt(self.path, "CULT03", project_exemptions):
            self.has_test_coverage = 1
            self.suppressed_count += 1
        else:
            test_candidates = [
                path.parent / f"test_{path.name}",
                path.parent / f"{path.stem}.test{path.suffix}",
                path.parent / f"{path.stem}.spec{path.suffix}",
                path.parent.parent / "tests" / f"test_{path.name}",
                Path("tests") / f"test_{path.name}"
            ]
            is_test_file = "test" in path.name.lower() or "spec" in path.name.lower()
            if is_test_file:
                self.has_test_coverage = 1
            else:
                self.has_test_coverage = 1 if any(c.exists() for c in test_candidates) else 0
                if not self.has_test_coverage:
                    self.violations.append({
                        "rule_id": "CULT03",
                        "severity": "P0_BLOCKING",
                        "penalty": 35,
                        "message": "Missing automated test file associated with this production artifact"
                    })

        # 5. Strict typing check (CULT05)
        if is_file_or_rule_exempt(self.path, "CULT05", project_exemptions):
            self.suppressed_count += 1
        else:
            if path.suffix == ".py":
                has_defs = bool(re.search(r"def\s+\w+\s*\(", content))
                has_hints = bool(re.search(r"->\s*[\w\[\], ]+:", content) or re.search(r":\s*(str|int|float|bool|list|dict|Any|Optional)", content))
                if has_defs and not has_hints:
                    self.has_type_annotations = 0
                    self.violations.append({
                        "rule_id": "CULT05",
                        "severity": "P1_WARNING",
                        "penalty": 10,
                        "message": "Functions detected without explicit parameter or return type annotations"
                    })

        # 6. Layer-Specific Architecture & Token Inspections (with False-Positive and Pragma Filtering)
        suppressed_map, pragma_warnings = parse_inline_pragmas(lines)
        self.violations.extend(pragma_warnings)

        if self.layer in FORBIDDEN_LAYER_PATTERNS:
            for pattern, rule_id, severity, penalty, msg in FORBIDDEN_LAYER_PATTERNS[self.layer]:
                if is_file_or_rule_exempt(self.path, rule_id, project_exemptions):
                    self.suppressed_count += 1
                    continue

                for idx, line in enumerate(lines, 1):
                    # Check if line is suppressed via inline pragma
                    is_suppressed = False
                    if idx in suppressed_map:
                        if rule_id in suppressed_map[idx] or "ALL" in suppressed_map[idx]:
                            is_suppressed = True
                            self.suppressed_count += 1

                    if is_suppressed:
                        continue

                    # Strip comments to prevent false positives from documentation/comments
                    code_only = strip_comments(line, path.suffix).strip()
                    if not code_only:
                        continue

                    if re.search(pattern, code_only):
                        self.violations.append({
                            "rule_id": rule_id,
                            "severity": severity,
                            "penalty": penalty,
                            "line": idx,
                            "snippet": code_only,
                            "layer": self.layer,
                            "message": msg
                        })

def generate_bend_harness(files: List[FileAuditResult]) -> str:
    """Generates dynamic Bend evaluation harness for parallel HVM reduction"""
    bend_code = [
        '# Auto-generated Bend evaluation harness for Bend DevOps Guardian',
        'type TargetFile:',
        '  TargetFile { name, lines_count, has_spec_tag, has_lazy_code, has_secrets, has_test_coverage, has_type_annotations }',
        '',
        'type Violation:',
        '  Violation { rule_id, file_name, severity, penalty, message }',
        '',
        'type FileTree:',
        '  Empty',
        '  Leaf { file }',
        '  Node { ~left, ~right }',
        '',
        'type ViolationStats:',
        '  ViolationStats { count, p0, p1, p2, penalties }',
        '',
        'type CultureReport:',
        '  CultureReport { total_files, total_violations, p0_count, p1_count, p2_count, penalty_total, score, is_approved }',
        '',
        'def check_cult01_lazy_code(file):',
        '  open TargetFile: file',
        '  if file.has_lazy_code == 1:',
        '    return [Violation/Violation("CULT01", file.name, 0, 35, "Incomplete code")]',
        '  else:',
        '    return []',
        '',
        'def check_cult02_spec_traceability(file):',
        '  open TargetFile: file',
        '  if file.has_spec_tag == 0:',
        '    return [Violation/Violation("CULT02", file.name, 1, 15, "Missing spec tag")]',
        '  else:',
        '    return []',
        '',
        'def check_cult03_test_coverage(file):',
        '  open TargetFile: file',
        '  if file.has_test_coverage == 0:',
        '    return [Violation/Violation("CULT03", file.name, 0, 35, "Missing tests")]',
        '  else:',
        '    return []',
        '',
        'def check_cult04_secrets(file):',
        '  open TargetFile: file',
        '  if file.has_secrets == 1:',
        '    return [Violation/Violation("CULT04", file.name, 0, 40, "Hardcoded secret")]',
        '  else:',
        '    return []',
        '',
        'def check_cult05_strict_typing(file):',
        '  open TargetFile: file',
        '  if file.has_type_annotations == 0:',
        '    return [Violation/Violation("CULT05", file.name, 1, 10, "Missing typing")]',
        '  else:',
        '    return []',
        '',
        'def list_concat(a, b):',
        '  match a:',
        '    case List/Nil:',
        '      return b',
        '    case List/Cons:',
        '      return List/Cons(a.head, list_concat(a.tail, b))',
        '',
        'def evaluate_file(file):',
        '  v1 = check_cult01_lazy_code(file)',
        '  v2 = check_cult02_spec_traceability(file)',
        '  v3 = check_cult03_test_coverage(file)',
        '  v4 = check_cult04_secrets(file)',
        '  v5 = check_cult05_strict_typing(file)',
        '  return list_concat(v1, list_concat(v2, list_concat(v3, list_concat(v4, v5))))',
        '',
        'def evaluate_tree_parallel(tree):',
        '  match tree:',
        '    case FileTree/Empty:',
        '      return []',
        '    case FileTree/Leaf:',
        '      return evaluate_file(tree.file)',
        '    case FileTree/Node:',
        '      left_v = evaluate_tree_parallel(tree.left)',
        '      right_v = evaluate_tree_parallel(tree.right)',
        '      return list_concat(left_v, right_v)',
        '',
        'def get_p0_inc(sev):',
        '  if sev == 0:',
        '    return 1',
        '  else:',
        '    return 0',
        '',
        'def get_p1_inc(sev):',
        '  if sev == 1:',
        '    return 1',
        '  else:',
        '    return 0',
        '',
        'def get_p2_inc(sev):',
        '  if sev == 2:',
        '    return 1',
        '  else:',
        '    return 0',
        '',
        'def aggregate_violations(violations):',
        '  match violations:',
        '    case List/Nil:',
        '      return ViolationStats/ViolationStats(0, 0, 0, 0, 0)',
        '    case List/Cons:',
        '      open Violation: violations.head',
        '      tail_stats = aggregate_violations(violations.tail)',
        '      open ViolationStats: tail_stats',
        '      p0_inc = get_p0_inc(violations.head.severity)',
        '      p1_inc = get_p1_inc(violations.head.severity)',
        '      p2_inc = get_p2_inc(violations.head.severity)',
        '      return ViolationStats/ViolationStats(tail_stats.count + 1, tail_stats.p0 + p0_inc, tail_stats.p1 + p1_inc, tail_stats.p2 + p2_inc, tail_stats.penalties + violations.head.penalty)',
        '',
        'def compute_score(total_penalties):',
        '  if total_penalties >= 100:',
        '    return 0',
        '  else:',
        '    return 100 - total_penalties',
        '',
        'def determine_approval(p0_count, score):',
        '  if p0_count > 0:',
        '    return 0',
        '  else:',
        '    if score < 80:',
        '      return 0',
        '    else:',
        '      return 1',
        '',
        'def generate_audit_report(files_count, violations):',
        '  stats = aggregate_violations(violations)',
        '  open ViolationStats: stats',
        '  score = compute_score(stats.penalties)',
        '  approved = determine_approval(stats.p0, score)',
        '  return CultureReport/CultureReport(files_count, stats.count, stats.p0, stats.p1, stats.p2, stats.penalties, score, approved)',
        '',
        'def main():'
    ]

    if not files:
        bend_code.append('  tree = FileTree/Empty')
        bend_code.append('  report = generate_audit_report(0, evaluate_tree_parallel(tree))')
    else:
        file_defs = []
        for i, f in enumerate(files):
            file_defs.append(f'  f{i} = TargetFile/TargetFile("{f.name}", {f.lines_count}, {f.has_spec_tag}, {f.has_lazy_code}, {f.has_secrets}, {f.has_test_coverage}, {f.has_type_annotations})')
        bend_code.extend(file_defs)

        leaves = [f"FileTree/Leaf(f{i})" for i in range(len(files))]
        while len(leaves) > 1:
            next_leaves = []
            for j in range(0, len(leaves), 2):
                if j + 1 < len(leaves):
                    next_leaves.append(f"FileTree/Node({leaves[j]}, {leaves[j+1]})")
                else:
                    next_leaves.append(leaves[j])
            leaves = next_leaves

        bend_code.append(f'  tree = {leaves[0]}')
        bend_code.append(f'  violations = evaluate_tree_parallel(tree)')
        bend_code.append(f'  report = generate_audit_report({len(files)}, violations)')

    bend_code.append('  open CultureReport: report')
    bend_code.append('  return (report.total_files, report.total_violations, report.p0_count, report.p1_count, report.penalty_total, report.score, report.is_approved)')
    
    return "\n".join(bend_code) + "\n"

def run_bend_engine(harness_code: str, files: Optional[List[FileAuditResult]] = None) -> tuple:
    """Executes Bend code via bend run-rs and extracts metrics"""
    file_list = files or []
    tot_files = len(file_list)
    p0 = sum(sum(1 for v in f.violations if v.get("severity") == "P0_BLOCKING") for f in file_list)
    p1 = sum(sum(1 for v in f.violations if v.get("severity") == "P1_WARNING") for f in file_list)
    pen = sum(sum(v.get("penalty", 0) for v in f.violations) for f in file_list)
    score = max(0, 100 - pen)
    approved = 1 if p0 == 0 and score >= 80 else 0
    tot_viol = sum(len(f.violations) for f in file_list)

    if file_list and len(file_list) <= 30:
        tmp_path = Path("/tmp/_culture_guard_run.bend")
        try:
            tmp_path.write_text(harness_code, encoding="utf-8")
            res = subprocess.run(["bend", "run-rs", str(tmp_path)], capture_output=True, text=True, timeout=3)
            if res.returncode == 0:
                numbers = [int(x) for x in re.findall(r"\d+", res.stdout.strip())]
                if len(numbers) >= 7:
                    return tuple(numbers[:7])
        except Exception:
            pass
        finally:
            if tmp_path.exists():
                tmp_path.unlink()

    return (tot_files, tot_viol, p0, p1, pen, score, approved)

def print_report(
    files: List[FileAuditResult],
    bend_stats: tuple,
    format_type: str = "text",
    branch_policy_verdict: Optional[Tuple[bool, str]] = None
) -> bool:
    tot_files, tot_viol, p0, p1, pen, score, approved = bend_stats
    
    extra_violations = sum(len(f.violations) for f in files)
    total_suppressed = sum(f.suppressed_count for f in files)
    has_blocking_violations = any(
        any(v.get("severity") == "P0_BLOCKING" for v in f.violations) 
        for f in files
    )
    
    is_ok = (not has_blocking_violations) and score >= 80 and approved == 1
    if branch_policy_verdict is not None:
        policy_ok, _ = branch_policy_verdict
        is_ok = is_ok and policy_ok

    if format_type == "json":
        data = {
            "total_files": tot_files,
            "total_violations": extra_violations,
            "total_suppressed": total_suppressed,
            "has_blocking_violations": has_blocking_violations,
            "culture_score": score,
            "approved": bool(is_ok),
            "files": [
                {
                    "path": str(f.path),
                    "layer": f.layer,
                    "suppressed_count": f.suppressed_count,
                    "violations": f.violations
                } for f in files
            ]
        }
        print(json.dumps(data, indent=2))
        return is_ok

    # Terminal Text Output
    status_badge = "✅ APPROVED IN DEVOPS QUALITY GATE" if is_ok else "❌ BLOCKED BY DEVOPS GUARDIAN"
    
    print("\n" + "="*70)
    print(" 🛡️  BEND DEVOPS GUARDIAN (BEND HVM ENGINE)")
    print("="*70)
    print(f" Status:              {status_badge}")
    print(f" Compliance Score:    {score}/100")
    print(f" Files Audited:       {tot_files}")
    print(f" Total Violations:    {extra_violations} (Blocking P0: {p0}, Warnings P1: {p1})")
    print(f" Active Suppressions: {total_suppressed} exemptions")
    print(f" Total Penalty:       {pen} pts")
    if branch_policy_verdict is not None:
        _, branch_reason = branch_policy_verdict
        print(f" Branch Policy:       {branch_reason}")
    print("="*70)

    if extra_violations > 0:
        print("\n📋 VIOLATIONS BREAKDOWN:")
        for f in files:
            if f.violations:
                print(f"\n📂 File: {f.path} [Layer: {f.layer}]")
                for v in f.violations:
                    sev = v["severity"]
                    line_info = f" [Line {v['line']}]" if "line" in v else ""
                    print(f"   - [{sev}] ({v['rule_id']}){line_info}: {v['message']}")
    else:
        print("\n✨ Zero infractions found! Code is 100% compliant with engineering standards.")

    print("\n" + "="*70 + "\n")
    return is_ok

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "mock":
        from scripts.guardian_mock import main as mock_main
        sys.argv.pop(1)
        mock_main()
        return

    parser = argparse.ArgumentParser(description="Bend DevOps Guardian (Bend Parallel HVM Quality Gate)")
    parser.add_argument("paths", nargs="*", default=["."], help="Files or directories to audit")
    parser.add_argument("--architecture", choices=["layered_mvc", "clean_architecture", "microservices", "cqrs", "rest_api", "frontend_clean"], default="layered_mvc", help="Target architecture profile")
    parser.add_argument("--branch", help="Target git branch to evaluate branch-specific gating policies (e.g. main, develop, feature/xyz)")
    parser.add_argument("--format", choices=["text", "json", "markdown"], default="text", help="Report output format")
    parser.add_argument("--min-score", type=int, default=80, help="Minimum score for approval (default: 80)")
    parser.add_argument("--vcs", choices=["github", "gitlab", "bitbucket"], help="Target VCS hosting platform for CI/CD status posting and reports")
    parser.add_argument("--mock-scenario", choices=["clean-repository", "architecture-violations", "blocked-quality-gate", "github-repository", "empty-repository", "integration-error"], help="Explicitly run a deterministic mock scenario")
    args = parser.parse_args()

    if args.mock_scenario:
        from scripts.guardian_mock import generate_scenario_data
        data = generate_scenario_data(args.mock_scenario)
        if args.format == "json":
            print(json.dumps(data, indent=2))
        else:
            print("="*70)
            print(f" ⚠️  BEND DEVOPS GUARDIAN — EXPLICIT MOCK SCENARIO: [{args.mock_scenario.upper()}]")
            print("="*70)
            print(f" Scenario:    {data.get('title')}")
            print(f" Environment: MOCK (Non-production deterministic fixture)")
            if "report" in data:
                rep = data["report"]
                print(f" Status:      {rep.get('status')} (Score: {rep.get('score')}%)")
                print(f" Violations:  {rep.get('totalViolations')} (P0: {rep.get('p0Count')}, P1: {rep.get('p1Count')})")
            print("="*70)
        sys.exit(0)

    project_exemptions = load_guardianignore()

    IGNORED_DIRS = {
        ".git", "node_modules", "dist", ".angular", "build", "bin", "obj", 
        "target", "venv", ".venv", "env", "__pycache__", ".pytest_cache", 
        ".mypy_cache", ".cache", "coverage", ".nyc_output", ".idea", ".vscode"
    }

    all_files = []
    for p_str in args.paths:
        p = Path(p_str).resolve()
        if p.is_file():
            if p.suffix in SUPPORTED_EXTENSIONS:
                all_files.append(p)
        elif p.is_dir():
            for root, dirs, files in os.walk(str(p)):
                dirs[:] = [d for d in dirs if d not in IGNORED_DIRS and not d.startswith(".")]
                for file_name in files:
                    file_path = Path(root) / file_name
                    if file_path.suffix in SUPPORTED_EXTENSIONS:
                        all_files.append(file_path)

    audit_results = [FileAuditResult(f, project_exemptions) for f in all_files]
    harness = generate_bend_harness(audit_results)
    bend_stats = run_bend_engine(harness, audit_results)
    score = bend_stats[5]
    p0_count = bend_stats[2]
    p1_count = bend_stats[3]

    branch_verdict = None
    if args.branch:
        policy_engine = BranchPolicyEngine()
        policy_ok, policy_reason, _ = policy_engine.evaluate_gate(args.branch, score=score, p0_count=p0_count, p1_count=p1_count)
        branch_verdict = (policy_ok, policy_reason)

    approved = print_report(audit_results, bend_stats, format_type=args.format, branch_policy_verdict=branch_verdict)

    # VCS Platform CI/CD Integration
    try:
        adapter = get_vcs_adapter(args.vcs)
        if adapter:
            all_violations = []
            for f in audit_results:
                all_violations.extend(f.violations)

            # 1. Generate platform-specific report artifact
            artifact_content = adapter.generate_report_artifact(all_violations, score=score, approved=approved)
            if args.vcs == "github" or getattr(adapter, "api_base", "").startswith("https://api.github.com"):
                Path("guardian-report.sarif").write_text(artifact_content, encoding="utf-8")
            elif args.vcs == "gitlab" or "gitlab" in getattr(adapter, "api_base", ""):
                Path("gl-code-quality-report.json").write_text(artifact_content, encoding="utf-8")
            elif args.vcs == "bitbucket" or "bitbucket" in getattr(adapter, "api_base", ""):
                Path("bitbucket-insights.json").write_text(artifact_content, encoding="utf-8")

            # 2. Publish Commit Status
            status_desc = f"Score: {score}/100 · {'Passed Gate' if approved else 'Violations Detected'}"
            adapter.publish_commit_status("success" if approved else "failure", status_desc, score)

            # 3. Post PR / MR Comment
            summary_md = adapter.build_markdown_summary(all_violations, score=score, approved=approved)
            adapter.post_pr_comment(summary_md)

            # 4. Publish Annotations
            adapter.publish_annotations(all_violations)
    except Exception as e:
        pass

    sys.exit(0 if approved else 1)

if __name__ == "__main__":
    main()
