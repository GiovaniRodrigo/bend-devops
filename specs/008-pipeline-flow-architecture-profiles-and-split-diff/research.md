# Pesquisa Técnica: Pipeline Flow, Architecture Profiles, Split Diff & Coverage

Este documento registra os padrões arquiteturais, tecnologias avaliadas, decisões de design e referências técnicas utilizadas na implementação dos recursos de fluxo de pipeline, gerenciamento de perfis, split diff e medição de cobertura.

---

## 1. Padrões Existentes no Projeto

| Arquivo/Padrão | Localização | Relevância |
|---|---|---|
| **Angular Signals** | `frontend/src/app/app.ts` | Estado reativo síncrono para manipulação de listas, modais, ordenação de estágios e recalculo de diffs. |
| **CultureGuardianService** | `frontend/src/app/services/culture-guardian.service.ts` | Serviço principal para execução de auditoria, geração de diff e comunicação com backend. |
| **Tailwind CSS Utility Classes** | `frontend/src/styles.css` / `app.html` | Estilização uniforme com suporte a dark/light theme, classes de card (`card-guardian`), badges (`badge-tech`, `badge-pass`) e botões (`btn-guardian`). |
| **Coverage.py** | `requirements.txt`, `.coveragerc` | Padrão da comunidade Python para medição de cobertura de código e branches. |

---

## 2. Tecnologias e Bibliotecas

| Tecnologia | Versão | Uso | Já Instalada? |
|---|---|---|---|
| **HTML5 Drag and Drop API** | Nativa | Reordenação de elementos de lista no DOM sem pacotes extras | Sim |
| **Coverage.py** | 7.16.x | Medição de cobertura de código, branches e exportação HTML | Sim (`coverage>=7.16.1`) |
| **Angular** | 21.2.0 | Framework reativo para interface rica e componentização | Sim |
| **Playwright** | 1.40.0+ | Captura de screenshots automatizadas e testes E2E | Sim |
| **Bend / HVM** | Latest | Motor funcional de redução de grafos paralelo para regras | Sim |

---

## 3. Alternativas Consideradas

### 3.1. Reordenação de Lista: Drag & Drop Nativo vs Angular CDK
* **Opção A (Angular CDK DragDrop)**:
  * *Prós*: Animações embutidas, utilitários de reordenação prontos.
  * *Contras*: Introduz dependência pesada (`@angular/cdk`), aumento de bundle size.
* **Opção B (HTML5 Native Drag and Drop API)** — **ESCOLHIDA**:
  * *Prós*: Zero bytes extras no bundle, suporte nativo universal em navegadores, controle granular de eventos.
  * *Mitigação*: Adição de botões auxiliares táteis (Subir/Descer) para acessibilidade plena.

### 3.2. Medição de Cobertura: pytest-cov vs coverage.py CLI
* **Opção A (pytest-cov)**:
  * *Prós*: Integração com runner pytest.
  * *Contras*: Depende de pytest configurado; os testes do projeto usam `unittest` padrão do Python.
* **Opção B (coverage.py com python -m unittest)** — **ESCOLHIDA**:
  * *Prós*: Opera perfeitamente com a suíte existente de `unittest discover`, suporta `.coveragerc`, gera relatórios em terminal e HTML sem alterar os testes existentes.

---

## 4. Referências Externas

* [Coverage.py 7.16.1 Documentation](https://coverage.readthedocs.io/en/7.16.1/)
* [HTML Drag and Drop API - MDN Web Docs](https://developer.mozilla.org/en-US/docs/Web/API/HTML_Drag_and_Drop_API)
* [Angular Signals Guide](https://angular.dev/guide/signals)
