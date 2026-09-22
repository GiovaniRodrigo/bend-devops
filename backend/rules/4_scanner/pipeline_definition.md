# Scanner Pipeline Definition: Architecture ➔ Rules ➔ Language ➔ Scan

This document defines the formal 4-step execution flow of the **AI Culture & Architecture Guardian**.

---

## 4-Step Execution Pipeline

```mermaid
flowchart TD
    subgraph Step1["Step 1: Identify Architecture (1_architectures/)"]
        ArchProfile["Architecture Profile (Layered MVC / Clean / Microservices)"]
        LayerClass["Layer Directory Classification (Domain, App, Interface, View)"]
        ArchProfile --> LayerClass
    end

    subgraph Step2["Step 2: Load Rules (2_rules/)"]
        Constraints["Abstract Constraints & Severities"]
        R_P0["P0_BLOCKING (Zero Tolerance)"]
        R_P1["P1_WARNING (Penalty Points)"]
        Constraints --> R_P0 & R_P1
    end

    subgraph Step3["Step 3: Apply Language Adapter (3_languages/)"]
        LangAdapter["Language Pack (.NET, Python, TypeScript, PHP, Go, Java)"]
        Tokens["Concrete Syntax Tokens & Regex Patterns"]
        LangAdapter --> Tokens
    end

    subgraph Step4["Step 4: Execute Scan & Reduction (4_scanner/)"]
        BendTree["Parallel Binary FileTree (Bend / HVM Runtime)"]
        ReportGen["Consolidated Report & CI/CD Gate Decision"]
        BendTree --> ReportGen
    end

    LayerClass --> Constraints
    R_P0 & R_P1 --> Tokens
    Tokens --> BendTree
```

---

## Step Breakdown

1. **`1_architectures/`**: Establishes the expected structural topology, layer boundaries, and allowed dependency directions.
2. **`2_rules/`**: Specifies what is forbidden or required (e.g. no UI in Domain, zero lazy code) along with penalty weights.
3. **`3_languages/`**: Translates abstract rules into concrete language-specific AST and token detection patterns for C#, Python, TS, PHP, Go, Java, and Bend.
4. **`4_scanner/`**: Dispatches the parallel tree evaluation to the Bend HVM engine, aggregates violations, and enforces the CI/CD quality gate.
