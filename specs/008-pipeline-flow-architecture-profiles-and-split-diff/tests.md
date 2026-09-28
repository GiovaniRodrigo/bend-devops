# Especificação de Testes: Pipeline Flow, Architecture Profiles, Split Diff & Coverage

Este documento define a matriz de cobertura de testes e os esqueletos de testes automatizados para os requisitos e regras de negócio da spec 008, cobrindo o frontend Angular (Vitest) e o backend/scripts Python (Coverage.py).

---

## 1. Matriz de Cobertura de Testes

| RF/RN | Descrição | Status | Criticidade | Suíte / Arquivo |
|---|---|---|---|---|
| **RF01** | Diagrama de Fluxo Visual de Pipeline | ✅ Coberto | 🟠 P1 | `frontend/src/app/app.spec.ts` |
| **RF02** | Reordenação Drag & Drop de Estágios do Pipeline | ✅ Coberto | 🔴 P0 | `frontend/src/app/app.spec.ts` |
| **RF03** | Alternador de Execução Local / Nuvem | ✅ Coberto | 🟡 P2 | `frontend/src/app/app.spec.ts` |
| **RF04** | Editor de Architecture Profiles | ✅ Coberto | 🔴 P0 | `frontend/src/app/app.spec.ts` |
| **RF05** | Turnover de Status Ativo / Inativo de Perfis | ✅ Coberto | 🔴 P0 | `frontend/src/app/app.spec.ts` |
| **RF06** | Modal de Detalhes de Regras | ✅ Coberto | 🟠 P1 | `frontend/src/app/app.spec.ts` |
| **RF07** | Layout Split View no Branch Analysis Result | ✅ Coberto | 🔴 P0 | `frontend/src/app/app.spec.ts` |
| **RF08** | Live Split Diff Inspector (Before/After) | ✅ Coberto | 🔴 P0 | `frontend/src/app/app.spec.ts` |
| **RF09** | Rolagem Central Independente | ✅ Coberto | 🟡 P2 | `frontend/src/app/app.spec.ts` |
| **RF10** | Medição de Cobertura com Coverage.py | ✅ Coberto | 🔴 P0 | `tests/test_*.py`, `tests/vcs/test_*.py` |
| **RN01** | Reordenação atualiza fluxo instantaneamente | ✅ Coberto | 🔴 P0 | `frontend/src/app/app.spec.ts` |
| **RN02** | Perfil inativo não selecionável sem ativação | ✅ Coberto | 🟠 P1 | `frontend/src/app/app.spec.ts` |
| **RN03** | Seleção de arquivo atualiza Split Diff sem fechar resumo | ✅ Coberto | 🔴 P0 | `frontend/src/app/app.spec.ts` |
| **RN04** | Sincronismo de linhas e realce no Split Diff | ✅ Coberto | 🔴 P0 | `frontend/src/app/app.spec.ts` |
| **RN05** | Relatório unificado de cobertura | ✅ Coberto | 🔴 P0 | `scripts/validate.sh` |

---

## 2. Esqueletos e Exemplos de Teste

### 2.1. Teste de Reordenação Drag & Drop de Pipeline (Angular / Vitest)

```typescript
it('should reorder pipeline stages via drag and drop and precision buttons', () => {
  const fixture = TestBed.createComponent(App);
  const app = fixture.componentInstance;
  app.activeTab.set('pipelines');
  fixture.detectChanges();

  const stagesInitial = app.pipelineStages();
  expect(stagesInitial.length).toBeGreaterThan(1);
  const initialFirst = stagesInitial[0].id;
  const initialSecond = stagesInitial[1].id;

  // Simulate drag and drop
  app.onPipelineDragStart(0);
  expect(app.draggedPipelineStageIndex()).toBe(0);

  const mockEvent = { preventDefault: () => {}, dataTransfer: { dropEffect: 'move' } } as unknown as DragEvent;
  app.onPipelineDragOver(mockEvent, 1);
  app.onPipelineDrop(mockEvent, 1);

  const updatedStages = app.pipelineStages();
  expect(updatedStages[0].id).toBe(initialSecond);
  expect(updatedStages[1].id).toBe(initialFirst);
});
```

### 2.2. Teste de Turnover Ativo/Inativo em Architecture Profiles (Angular / Vitest)

```typescript
it('should toggle architecture profile status between Ativo and Inativo in 1 click', () => {
  const fixture = TestBed.createComponent(App);
  const app = fixture.componentInstance;
  app.activeTab.set('profiles');
  fixture.detectChanges();

  const profile = app.architectureProfiles()[0];
  const initialStatus = profile.enabled;

  // Direct toggle turnover
  app.toggleArchitectureProfile(profile.id);
  expect(app.architectureProfiles().find(p => p.id === profile.id)?.enabled).toBe(!initialStatus);

  // Flip back
  app.toggleArchitectureProfile(profile.id);
  expect(app.architectureProfiles().find(p => p.id === profile.id)?.enabled).toBe(initialStatus);
});
```

### 2.3. Teste de Split View no Branch Analysis (Angular / Vitest)

```typescript
it('should render side-by-side split code diff on the right side in Branch Analysis Result view', async () => {
  const fixture = TestBed.createComponent(App);
  const app = fixture.componentInstance;
  app.activeTab.set('analyze');
  app.setAuditScope('branch_analysis');
  fixture.detectChanges();

  await app.analyzeBranch();
  fixture.detectChanges();

  expect(app.displayBranchFiles().length).toBeGreaterThan(0);
  expect(app.selectedBranchFileIndex()).toBe(0);

  const diff = app.currentCodeDiff();
  expect(diff).toBeDefined();
  expect(diff.splitBefore.length).toBeGreaterThan(0);
  expect(diff.splitAfter.length).toBeGreaterThan(0);

  const compiled = fixture.nativeElement as HTMLElement;
  expect(compiled.textContent).toContain('Branch Analysis Result');
  expect(compiled.textContent).toContain('Diff Inspector');
  expect(compiled.textContent).toContain('BEFORE');
  expect(compiled.textContent).toContain('AFTER');
});
```

### 2.4. Teste de Cobertura via Coverage.py (Python)

```bash
# Execução e verificação de cobertura
coverage run --source=scripts -m unittest discover -s tests -p "test_*.py"
coverage run -a --source=scripts -m unittest discover -s tests/vcs -p "test_*.py"
coverage report --fail-under=50
```
