# Pesquisa e Referências: Escopo e Composição de Regras

---

## 1. Padrões Existentes no Projeto

O projeto `bend-devops` já possui uma base sólida de auditoria funcional e relatórios de conformidade. A tabela abaixo lista os componentes existentes reutilizados nesta implementação:

| Arquivo/Padrão | Localização | Relevância |
| :--- | :--- | :--- |
| **Esquema de Regras JSON** | `backend/rules/rules_schema.json` | Estrutura de validação de regras com condições, severidade e supressões. |
| **CLI & Orquestrador** | `scripts/culture_guard.py` | Motor de auditoria que invoca o analisador léxico e calcula o score de conformidade. |
| **Serviço de Descoberta Git** | `frontend/src/app/services/culture-guardian.service.ts` | Descoberta de repositórios locais, listagem de branches e inspeção de working tree. |
| **Interface Reativa de Auditoria** | `frontend/src/app/app.ts` & `app.html` | Interface em Angular 19 com Signals para feedback visual imediato. |

---

## 2. Tecnologias e Bibliotecas

| Tecnologia | Versão | Uso | Já instalada? |
| :--- | :--- | :--- | :--- |
| **Angular** | `^21.2.0` | UI Web, Gerenciamento de Estado com Signals | Sim |
| **Tailwind CSS** | `^3.4.19` | Estilização responsiva e tema Dark/Light | Sim |
| **Python** | `3.10+` | Resolvedor de escopo, CLI e servidor HTTP local | Sim |
| **Bend / HVM** | `latest` | Redução paralela em massa de regras estruturais | Sim |

---

## 3. Alternativas Consideradas

### Opção A: Escopo Fixo por Arquivo de Configuração Estático (`.guardrc`)
* **Prós**: Configuração persistida no repositório versionado via git.
* **Contras**: Pouca flexibilidade para o desenvolvedor testar um arquivo ou subdiretório avulso interativamente sem modificar e comitar arquivos no git.
* **Decisão**: **Descartada** como única opção. O sistema prioriza a flexibilidade interativa na UI/CLI, mantendo a opção de salvar perfis.

### Opção B: Orquestração Dinâmica em Tempo Real pelo Usuário (Escolhida)
* **Prós**: O usuário decide exatamente o escopo (full, diff, pasta ou arquivo) e quais regras quer testar no momento, visualizando o impacto imediatamente.
* **Contras**: Requer parametrização clara na interface e no CLI.
* **Decisão**: **Escolhida**. Atende perfeitamente ao requisito de que o usuário é quem decide as regras e o escopo da validação.
