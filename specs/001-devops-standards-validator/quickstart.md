# Quickstart: DevOps Standards & Architecture Quality Gate

---

## Prerequisites

- Bend (`~/.cargo/bin/bend`) and HVM (`~/.cargo/bin/hvm`).
- Python 3.10+.
- Node.js 20+ (for Angular Dashboard).

---

## Execution Steps

### 1. Run Complete 8-Stage Validation Suite
```bash
./scripts/validate.sh
```

### 2. Audit Codebase via CLI
```bash
python3 scripts/culture_guard.py src/
```

### 3. Run in CI/CD Mode with VCS PR/MR Commenting
```bash
python3 scripts/culture_guard.py --vcs github
```
