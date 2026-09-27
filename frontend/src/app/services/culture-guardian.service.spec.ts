import { describe, it, expect, beforeEach } from 'vitest';
import { TestBed } from '@angular/core/testing';
import { CultureGuardianService } from './culture-guardian.service';

describe('CultureGuardianService (Specs 006 & 007)', () => {
  let service: CultureGuardianService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [CultureGuardianService]
    });
    service = TestBed.inject(CultureGuardianService);
  });

  it('should be initialized with architecture profiles and layer vocabulary', () => {
    expect(service).toBeTruthy();
    expect(service.architectureProfiles().length).toBeGreaterThan(0);
    expect(service.layerVocabulary().length).toBeGreaterThan(0);
  });

  it('should list rule categories and supported languages', () => {
    expect(service.ruleCategories()).toContain('Architecture');
    expect(service.ruleCategories()).toContain('Security');
    expect(service.ruleLanguages()).toContain('TypeScript');
    expect(service.ruleLanguages()).toContain('Python');
    expect(service.ruleLanguages()).toContain('C#');
  });

  it('should audit code and generate clean compliance report', () => {
    const cleanCode = `
      // @spec RF01
      export class CleanDomainEntity {
        constructor(public id: string, public name: string) {}
      }
    `;
    const auditInfo = service.auditCode('src/domain/entity.ts', cleanCode, true);
    const report = service.generateReport([auditInfo]);
    expect(report.score).toBe(100);
    expect(report.isApproved).toBe(true);
    expect(report.p0Count).toBe(0);
  });

  it('should detect blocking violations (P0) in dirty code with secrets and TODOs', () => {
    const dirtyCode = `
      const API_KEY = "sk_live_12345678901234567890";
      // TODO: implement later
      class BadModel {}
    `;
    const auditInfo = service.auditCode('src/models/bad.ts', dirtyCode, false);
    const report = service.generateReport([auditInfo]);
    expect(report.isApproved).toBe(false);
    expect(report.p0Count).toBeGreaterThan(0);
    expect(report.score).toBeLessThan(100);
  });

  it('should generate valid SARIF v2.1.0 export format', () => {
    const auditInfo = service.auditCode('src/test.ts', 'class Test {}', true);
    const report = service.generateReport([auditInfo]);
    const sarif = service.generateSarifJson(report);
    expect(sarif).toContain('2.1.0');
    expect(sarif).toContain('Bend DevOps Guardian');
  });

  it('should strip comments correctly according to language', () => {
    const codeWithComments = 'let x = 10; // inline comment';
    const stripped = service.stripComments(codeWithComments, 'TypeScript');
    expect(stripped.trim()).toBe('let x = 10;');
  });
});
