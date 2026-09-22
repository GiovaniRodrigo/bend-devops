# Research and References: AI Agent Culture Validator in Bend

---

## 1. Existing Patterns & Architecture

Modern AI agent workflows face a critical challenge: **silent degradation of code quality and engineering standards**.
AI agents often:
1. Leave stubs like `# TODO` or `// to be implemented`.
2. Omit test coverage in favor of speed.
3. Code hardcoded API secrets and tokens into source files.
4. Disconnect generated code from specification requirements (`spec.md`).

The **AI Culture Guardian** acts as an uncompromising compliance oracle to preserve codebase integrity.

---

## 2. Technologies and Tools

| Technology | Version | Purpose | Status |
| :--- | :--- | :--- | :--- |
| **Bend** | 0.2.38 | Rule evaluation engine with massive parallelism on HVM | Installed (`~/.cargo/bin/bend`) |
| **HVM** | 2.x | High-performance interaction combinators virtual machine | Installed (`~/.cargo/bin/hvm`) |
| **Python** | 3.12+ | I/O orchestrator, CLI, and rich report formatting | Installed (`/usr/bin/python3`) |
| **Git & GitHub Actions** | Latest | CI/CD automation pipeline and quality gate hooks | Installed |

---

## 3. Parallelism Paradigm in Bend

Bend utilizes interaction trees based on *Interaction Combinators*. Pure functions and evaluation trees suffer no GIL or thread contention. Multi-file audits execute natively concurrently across CPU and GPU hardware.
