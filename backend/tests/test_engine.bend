# ==============================================================================
# Integration Test Suite for the Audit Engine in Bend
# ==============================================================================

type TargetFile:
  TargetFile { 
    name, 
    lines_count, 
    has_spec_tag, 
    has_lazy_code, 
    has_secrets, 
    has_test_coverage, 
    has_type_annotations 
  }

type Violation:
  Violation { rule_id, file_name, severity, penalty, message }

type FileTree:
  Empty
  Leaf { file }
  Node { ~left, ~right }

type ViolationStats:
  ViolationStats { count, p0, p1, p2, penalties }

type CultureReport:
  CultureReport { 
    total_files, 
    total_violations, 
    p0_count, 
    p1_count, 
    p2_count, 
    penalty_total, 
    score, 
    is_approved 
  }

def check_cult01_lazy_code(file):
  open TargetFile: file
  if file.has_lazy_code == 1:
    return [Violation/Violation("CULT01", file.name, 0, 35, "Incomplete code")]
  else:
    return []

def check_cult02_spec_traceability(file):
  open TargetFile: file
  if file.has_spec_tag == 0:
    return [Violation/Violation("CULT02", file.name, 1, 15, "Missing spec tag")]
  else:
    return []

def check_cult03_test_coverage(file):
  open TargetFile: file
  if file.has_test_coverage == 0:
    return [Violation/Violation("CULT03", file.name, 0, 35, "Missing tests")]
  else:
    return []

def check_cult04_secrets(file):
  open TargetFile: file
  if file.has_secrets == 1:
    return [Violation/Violation("CULT04", file.name, 0, 40, "Hardcoded secret")]
  else:
    return []

def check_cult05_strict_typing(file):
  open TargetFile: file
  if file.has_type_annotations == 0:
    return [Violation/Violation("CULT05", file.name, 1, 10, "Missing typing")]
  else:
    return []

def list_concat(a, b):
  match a:
    case List/Nil:
      return b
    case List/Cons:
      return List/Cons(a.head, list_concat(a.tail, b))

def evaluate_file(file):
  v1 = check_cult01_lazy_code(file)
  v2 = check_cult02_spec_traceability(file)
  v3 = check_cult03_test_coverage(file)
  v4 = check_cult04_secrets(file)
  v5 = check_cult05_strict_typing(file)
  return list_concat(v1, list_concat(v2, list_concat(v3, list_concat(v4, v5))))

def evaluate_tree_parallel(tree):
  match tree:
    case FileTree/Empty:
      return []
    case FileTree/Leaf:
      return evaluate_file(tree.file)
    case FileTree/Node:
      left_v = evaluate_tree_parallel(tree.left)
      right_v = evaluate_tree_parallel(tree.right)
      return list_concat(left_v, right_v)

def get_p0_inc(sev):
  if sev == 0:
    return 1
  else:
    return 0

def get_p1_inc(sev):
  if sev == 1:
    return 1
  else:
    return 0

def get_p2_inc(sev):
  if sev == 2:
    return 1
  else:
    return 0

def aggregate_violations(violations):
  match violations:
    case List/Nil:
      return ViolationStats/ViolationStats(0, 0, 0, 0, 0)
    case List/Cons:
      open Violation: violations.head
      tail_stats = aggregate_violations(violations.tail)
      open ViolationStats: tail_stats
      
      p0_inc = get_p0_inc(violations.head.severity)
      p1_inc = get_p1_inc(violations.head.severity)
      p2_inc = get_p2_inc(violations.head.severity)

      return ViolationStats/ViolationStats(
        tail_stats.count + 1,
        tail_stats.p0 + p0_inc,
        tail_stats.p1 + p1_inc,
        tail_stats.p2 + p2_inc,
        tail_stats.penalties + violations.head.penalty
      )

def compute_score(total_penalties):
  if total_penalties >= 100:
    return 0
  else:
    return 100 - total_penalties

def determine_approval(p0_count, score):
  if p0_count > 0:
    return 0
  else:
    if score < 80:
      return 0
    else:
      return 1

def generate_audit_report(files_count, violations):
  stats = aggregate_violations(violations)
  open ViolationStats: stats
  score = compute_score(stats.penalties)
  approved = determine_approval(stats.p0, score)
  return CultureReport/CultureReport(files_count, stats.count, stats.p0, stats.p1, stats.p2, stats.penalties, score, approved)

# Test 1: Fully compliant codebase
def test_fully_compliant_codebase():
  f1 = TargetFile/TargetFile("auth.py", 100, 1, 0, 0, 1, 1)
  f2 = TargetFile/TargetFile("user.py", 50, 1, 0, 0, 1, 1)
  tree = FileTree/Node(FileTree/Leaf(f1), FileTree/Leaf(f2))
  v = evaluate_tree_parallel(tree)
  r = generate_audit_report(2, v)
  open CultureReport: r
  if r.score == 100:
    if r.is_approved == 1:
      return 1
    else:
      return 0
  else:
    return 0

# Test 2: Codebase with blocking violation (P0) must reject
def test_blocking_violation_rejection():
  f1 = TargetFile/TargetFile("auth.py", 100, 1, 0, 0, 1, 1)
  f2 = TargetFile/TargetFile("leak.py", 30, 1, 0, 1, 1, 1)
  tree = FileTree/Node(FileTree/Leaf(f1), FileTree/Leaf(f2))
  v = evaluate_tree_parallel(tree)
  r = generate_audit_report(2, v)
  open CultureReport: r
  if r.is_approved == 0:
    if r.p0_count == 1:
      return 1
    else:
      return 0
  else:
    return 0

# Test 3: Empty tree
def test_empty_tree():
  tree = FileTree/Empty
  v = evaluate_tree_parallel(tree)
  r = generate_audit_report(0, v)
  open CultureReport: r
  if r.score == 100:
    if r.total_violations == 0:
      return 1
    else:
      return 0
  else:
    return 0

def main():
  t1 = test_fully_compliant_codebase()
  t2 = test_blocking_violation_rejection()
  t3 = test_empty_tree()

  if t1 == 1:
    if t2 == 1:
      if t3 == 1:
        return "ALL_INTEGRATION_TESTS_PASSED"
      else:
        return "FAIL_EMPTY_TREE"
    else:
      return "FAIL_BLOCKING_TEST"
  else:
    return "FAIL_COMPLIANT_TEST"
