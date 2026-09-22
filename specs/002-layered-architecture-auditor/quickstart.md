# Quickstart: Universal 4-Tier Architecture Guardian

Guide to running the Architecture & Engineering Culture Guardian locally and in CI/CD pipelines.

---

## 1. Prerequisites

- [Bend](https://github.com/HigherOrderCO/Bend) (`bend` compiler installed in PATH)
- [Python 3.10+](https://www.python.org/)
- [Node.js 20+](https://nodejs.org/) & [Angular CLI](https://angular.dev/)

---

## 2. Quick Execution

```bash
# Run complete end-to-end quality gate (Bend + Angular + CLI Audit)
./scripts/validate.sh
```

---

## 3. CLI Audit Usage

```bash
# Audit specific files or directories
python3 scripts/culture_guard.py src/

# Export JSON audit report for CI/CD integration
python3 scripts/culture_guard.py src/ --format json

# Require strict passing score (default: 80)
python3 scripts/culture_guard.py src/ --min-score 90
```

---

## 4. Run Angular Dashboard

```bash
cd frontend
npm install
npm start
# Open http://localhost:4200
```
