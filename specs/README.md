# 📋 Índice de Especificações Técnicas (Spec-Driven Development)

Todas as funcionalidades do **Bend DevOps Guardian** são concebidas e documentadas seguindo o padrão **Spec-Driven Development (SDD)**. Cada diretório contém especificação funcional, modelo de dados, pesquisa técnica, contratos de API/interfaces, matriz de testes e checklist de tarefas no fluxo TDD.

---

## 🗂️ Especificações Registradas

| Spec | Slug | Título / Escopo | Status |
| :--- | :--- | :--- | :--- |
| **001** | [`001-devops-standards-validator/`](./001-devops-standards-validator/) | **Core Parallel HVM Engine**: Motor funcional paralelo de redução de árvores AST em Bend/HVM e regras de higiene DevOps. | ✅ Implementado |
| **002** | [`002-layered-architecture-auditor/`](./002-layered-architecture-auditor/) | **Layered Architecture & Vocabulary**: Validador de fronteiras concêntricas de Clean Architecture e taxonomia de camadas. | ✅ Implementado |
| **003** | [`003-vcs-git-platforms-integration/`](./003-vcs-git-platforms-integration/) | **VCS Git Platforms Integration**: Adaptadores multiplataforma para GitHub Actions, GitLab CI/CD e Bitbucket Pipelines. | ✅ Implementado |
| **004** | [`004-false-positive-suppression-engine/`](./004-false-positive-suppression-engine/) | **False-Positive Suppression Engine**: Motor de supressão por pragmas (`@guardian-ignore`) e delimitação léxica de tokens. | ✅ Implementado |
| **005** | [`005-live-code-diff-auditor/`](./005-live-code-diff-auditor/) | **Live Code & Diff Auditor**: Auditoria interativa em tempo real com visualizador de diff unificado e split para PRs/commits. | ✅ Implementado |
| **006** | [`006-extensible-rule-management/`](./006-extensible-rule-management/) | **Extensible Rule Management**: Catálogo de regras de 4 camadas, wizard de criação de regras customizadas e console de teste. | ✅ Implementado |
| **007** | [`007-escopo-e-regras-arquiteturais-do-usuario/`](./007-escopo-e-regras-arquiteturais-do-usuario/) | **Escopo e Regras Arquiteturais do Usuário**: Parametrização de escopo (Full, Diff, Subdir, File) e composição modular de regras complementares pelo usuário. | 🚀 Pronto para Implementação |

---

## 📐 Estrutura Padrão de uma Spec

Cada especificação em `specs/<demanda>/` é composta por:

```
specs/<demanda>/
├── spec.md          # Requisitos funcionais (RF), não-funcionais (RNF), regras de negócio (RN) e diagramas UML
├── plan.md          # Plano técnico de arquitetura, arquivos afetados e mitigação de riscos
├── data-model.md    # Modelagem das entidades, tabelas/estruturas e diagramas ER
├── research.md      # Pesquisa de padrões existentes, dependências e alternativas
├── tasks.md         # Checklist de tarefas atômicas sequenciadas no fluxo TDD
├── tests.md         # Matriz de cobertura e esqueletos de teste automatizados
├── quickstart.md    # Guia prático de execução e validação local
└── contracts/       # Contratos formais de endpoints REST e interfaces de código
    ├── api.md
    └── interfaces.md
```
