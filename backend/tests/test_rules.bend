# ==============================================================================
# Unit Test Suite for Culture & Architecture Rules in Bend
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

def check_cult01_lazy_code(file):
  open TargetFile: file
  if file.has_lazy_code == 1:
    return [Violation/Violation("CULT01", file.name, 0, 35, "Incomplete code detected")]
  else:
    return []

def check_cult02_spec_traceability(file):
  open TargetFile: file
  if file.has_spec_tag == 0:
    return [Violation/Violation("CULT02", file.name, 1, 15, "Missing @spec RFxx tag")]
  else:
    return []

def check_cult03_test_coverage(file):
  open TargetFile: file
  if file.has_test_coverage == 0:
    return [Violation/Violation("CULT03", file.name, 0, 35, "Missing automated test coverage")]
  else:
    return []

def check_cult04_secrets(file):
  open TargetFile: file
  if file.has_secrets == 1:
    return [Violation/Violation("CULT04", file.name, 0, 40, "Hardcoded secret detected")]
  else:
    return []

def check_cult05_strict_typing(file):
  open TargetFile: file
  if file.has_type_annotations == 0:
    return [Violation/Violation("CULT05", file.name, 1, 10, "Missing strict typing")]
  else:
    return []

def list_len(lst):
  match lst:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + list_len(lst.tail)

# Scenario 1: Compliant file (must pass all rule checks)
def test_all_rules_pass_on_compliant_file():
  f = TargetFile/TargetFile("compliant.py", 100, 1, 0, 0, 1, 1)
  v1 = list_len(check_cult01_lazy_code(f))
  v2 = list_len(check_cult02_spec_traceability(f))
  v3 = list_len(check_cult03_test_coverage(f))
  v4 = list_len(check_cult04_secrets(f))
  v5 = list_len(check_cult05_strict_typing(f))
  return v1 + v2 + v3 + v4 + v5 # Expected: 0

# Scenario 2: Individual rule violation tests
def test_cult01_lazy_code_violation():
  f = TargetFile/TargetFile("lazy.py", 50, 1, 1, 0, 1, 1)
  v = check_cult01_lazy_code(f)
  return list_len(v) # Expected: 1

def test_cult02_missing_spec_tag():
  f = TargetFile/TargetFile("no_spec.py", 50, 0, 0, 0, 1, 1)
  v = check_cult02_spec_traceability(f)
  return list_len(v) # Expected: 1

def test_cult03_missing_tests():
  f = TargetFile/TargetFile("no_tests.py", 50, 1, 0, 0, 0, 1)
  v = check_cult03_test_coverage(f)
  return list_len(v) # Expected: 1

def test_cult04_secret_leak():
  f = TargetFile/TargetFile("leak.py", 50, 1, 0, 1, 1, 1)
  v = check_cult04_secrets(f)
  return list_len(v) # Expected: 1

def test_cult05_missing_types():
  f = TargetFile/TargetFile("untyped.py", 50, 1, 0, 0, 1, 0)
  v = check_cult05_strict_typing(f)
  return list_len(v) # Expected: 1

def main():
  t_pass = test_all_rules_pass_on_compliant_file()
  t_c1 = test_cult01_lazy_code_violation()
  t_c2 = test_cult02_missing_spec_tag()
  t_c3 = test_cult03_missing_tests()
  t_c4 = test_cult04_secret_leak()
  t_c5 = test_cult05_missing_types()

  if t_pass == 0:
    if t_c1 == 1:
      if t_c2 == 1:
        if t_c3 == 1:
          if t_c4 == 1:
            if t_c5 == 1:
              return "ALL_UNIT_TESTS_PASSED"
            else:
              return "FAIL_CULT05"
          else:
            return "FAIL_CULT04"
        else:
          return "FAIL_CULT03"
      else:
        return "FAIL_CULT02"
    else:
      return "FAIL_CULT01"
  else:
    return "FAIL_COMPLIANT_TEST"
