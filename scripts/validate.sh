#!/usr/bin/env bash
# ==============================================================================
# CI/CD Validation and Quality Gate Script for Bend DevOps Guardian
# (Bend HVM Engine + Angular Frontend Dashboard)
# ==============================================================================
set -e

echo "🚀 [1/8] Checking Bend syntax and types (backend/src/guardian.bend)..."
bend check backend/src/guardian.bend
bend check backend/tests/test_rules.bend
bend check backend/tests/test_engine.bend
echo "✅ Bend syntax and integrity validated."

echo ""
echo "🧪 [2/8] Running Bend unit tests for culture and architecture rules..."
BEND_OUT=$(bend run-rs backend/tests/test_rules.bend)
echo "$BEND_OUT"
if [[ "$BEND_OUT" != *"ALL_UNIT_TESTS_PASSED"* ]]; then
  echo "❌ Unit tests failed in Bend!"
  exit 1
fi
echo "✅ Bend unit tests passed."

echo ""
echo "🧪 [3/8] Running Bend parallel engine integration tests..."
ENGINE_OUT=$(bend run-rs backend/tests/test_engine.bend)
echo "$ENGINE_OUT"
if [[ "$ENGINE_OUT" != *"ALL_INTEGRATION_TESTS_PASSED"* ]]; then
  echo "❌ Integration tests failed in Bend!"
  exit 1
fi
echo "✅ Bend integration tests passed."

echo ""
echo "🅰️  [4/8] Running Angular tests and production build (frontend/)..."
cd frontend
npm run test -- --watch=false
npm run build
cd ..
echo "✅ Angular frontend tested and compiled successfully."

echo ""
echo "⚡ [5/8] Executing main Bend engine (backend/src/guardian.bend)..."
bend run-rs backend/src/guardian.bend
echo "✅ Bend engine executed successfully."

echo ""
echo "🛡️  [6/8] Running False-Positive & Token Filter Tests..."
python3 -m unittest discover -s tests -p "test_*.py"
echo "✅ Token filter and false-positive prevention tests passed."

echo ""
echo "🛡️  [7/8] Running Multi-Platform VCS Adapter Tests (GitHub, GitLab, Bitbucket)..."
python3 -m unittest discover -s tests/vcs -p "test_*.py"
echo "✅ VCS platform integration tests passed."

echo ""
echo "🛡️  [8/8] Executing DevOps Architecture Guard audit on test examples..."
python3 scripts/culture_guard.py examples/compliant_agent_output.py examples/test_compliant_agent_output.py

echo ""
echo "🎉 ALL VALIDATIONS (BEND + ANGULAR + VCS + FILTERS + CLI) PASSED SUCCESSFULLY! 100% OPERATIONAL."
