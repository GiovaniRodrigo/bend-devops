# Especificação de Testes: Escopo e Regras Arquiteturais do Usuário

Este documento estabelece a matriz de cobertura e os esqueletos de testes automatizados (unitários, integração e E2E) para validar os Requisitos Funcionais e Regras de Negócio definidos em `spec.md`.

---

## 1. Matriz de Cobertura

| RF/RN | Descrição | Status | Criticidade | Camada |
| :--- | :--- | :--- | :--- | :--- |
| **RF01** | Seleção de origem (local/GitHub) e branch | ❌ Ausente | 🔴 P0 | Integração / UI |
| **RF02** | Resolução correta dos 4 níveis de escopo (Full, Diff, Subdir, File) | ❌ Ausente | 🔴 P0 | Unitário / Backend |
| **RF03** | Composição modular e aditiva de regras complementares | ❌ Ausente | 🔴 P0 | Unitário / Backend |
| **RF04** | Sobrescrita de severidade personalizada pelo usuário | ❌ Ausente | 🟠 P1 | Unitário |
| **RF05** | Avaliação restrita estritamente aos arquivos dentro do escopo | ❌ Ausente | 🔴 P0 | Integração |
| **RF06** | Persistência e restauração de perfil de escopo/regras | ❌ Ausente | 🟡 P2 | Unitário / Frontend |
| **RF07** | Emissão de relatório e exportação SARIF filtrada pelo escopo | ❌ Ausente | 🟠 P1 | Integração |
| **RN01** | Autonomia total do usuário sobre o conjunto de regras ativas | ❌ Ausente | 🔴 P0 | Unitário |
| **RN02** | Bloqueio do Quality Gate caso qualquer regra P0 ativa falhe | ❌ Ausente | 🔴 P0 | Unitário |
| **RN03** | Arquivos fora do escopo são ignorados (sem penalidades) | ❌ Ausente | 🔴 P0 | Unitário |
| **RN04** | Tratamento gracioso para escopo vazio sem quebra | ❌ Ausente | 🟡 P2 | Unitário |

---

## 2. Esqueletos de Testes Automatizados

### 2.1. Testes de Escopo e Resolução de Arquivos (`tests/test_user_scoped_rules.py`)

```python
import unittest
import os
import tempfile
import shutil
from scripts.culture_guard import resolve_scope_files, evaluate_scoped_rules

class TestUserScopedRules(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.test_dir, "backend", "domain"))
        os.makedirs(os.path.join(self.test_dir, "frontend", "src"))
        
        # Arquivo no backend (com violação)
        self.file_backend = os.path.join(self.test_dir, "backend", "domain", "model.py")
        with open(self.file_backend, "w") as f:
            f.write("import requests # violacao de camada\n")
            
        # Arquivo no frontend (com segredo)
        self.file_frontend = os.path.join(self.test_dir, "frontend", "src", "app.ts")
        with open(self.file_frontend, "w") as f:
            f.write("const API_KEY = 'sk_live_12345678901234567890';\n")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_RF02_RN03_subdirectory_scope_ignores_other_directories(self):
        """RF02 & RN03: Escopo 'subdirectory' avalia apenas backend e ignora frontend"""
        files = resolve_scope_files(self.test_dir, scope='subdirectory', target='backend')
        self.assertIn(self.file_backend, files)
        self.assertNotIn(self.file_frontend, files)

    def test_RF03_RN02_modular_rules_composition_and_blocking_gate(self):
        """RF03 & RN02: Regras ativas complementares bloqueiam gate quando violadas"""
        active_rules = [{'id': 'ARCH-LAYER-01', 'severity': 'P0_BLOCKING'}]
        report = evaluate_scoped_rules(files=[self.file_backend], rules=active_rules)
        self.assertFalse(report['isApproved'])
        self.assertEqual(len(report['violations']), 1)

    def test_RN04_empty_scope_does_not_crash(self):
        """RN04: Escopo vazio retorna relatório limpo sem exceções"""
        files = resolve_scope_files(self.test_dir, scope='subdirectory', target='empty_folder')
        report = evaluate_scoped_rules(files=files, rules=[{'id': 'ARCH-LAYER-01'}])
        self.assertEqual(len(files), 0)
        self.assertTrue(report['isApproved'])
        self.assertEqual(report['score'], 100)
```

---

### 2.2. Testes de Frontend Angular (`frontend/src/app/app.spec.ts`)

```typescript
import { describe, it, expect, beforeEach } from 'vitest';
import { App } from './app';

describe('App Component - User Scoped Architectural Rules', () => {
  let app: App;

  beforeEach(() => {
    // Configuração do componente
  });

  it('deve permitir ao usuário alternar o modo de escopo (RF02)', () => {
    // Validação da seleção de escopo via Signal
  });

  it('deve filtrar as regras ativas de acordo com a seleção do usuário (RF03, RN01)', () => {
    // Validação da composição modular de regras
  });

  it('deve recalcular a aprovação do Quality Gate com base nas regras selecionadas (RN02)', () => {
    // Validação do score e isApproved
  });
});
```
