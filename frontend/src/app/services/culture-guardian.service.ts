import { Injectable, signal } from '@angular/core';
import { AnalysisRun, AuditReport, CodeViolation, CultureRule, FileAuditInfo } from '../models/culture.model';

@Injectable({
  providedIn: 'root'
})
export class CultureGuardianService {
  readonly rules = signal<CultureRule[]>([
    {
      id: 'CULT01',
      name: 'Zero Lazy Code (TODO/FIXME/pass)',
      category: 'Integrity',
      severity: 'P0_BLOCKING',
      penaltyPoints: 35,
      description: 'Prohibits incomplete code in pull requests, including TODOs, FIXMEs, empty pass statements, or stubs without a functional body.',
      rationale: 'Engineering standards require complete implementations without hidden operational gaps.',
      remediation: 'Implement the logic completely or formally document the pending item in spec.md before submitting code.',
      languages: ['Python', 'Bend', 'TypeScript', 'C++', 'C#', 'PHP'],
      status: 'active'
    },
    {
      id: 'CULT02',
      name: 'Spec Traceability (@spec RFxx)',
      category: 'Standard',
      severity: 'P1_WARNING',
      penaltyPoints: 15,
      description: 'Requires an annotation or tag linking the artifact to the specification requirement (e.g. @spec RF01).',
      rationale: 'Ensures strict alignment between business/architectural requirements and the implementation.',
      remediation: 'Add a header comment or annotation @spec RF<number> referencing the corresponding requirement.',
      languages: ['Python', 'Bend', 'TypeScript', 'C++', 'C#', 'PHP'],
      status: 'active'
    },
    {
      id: 'CULT03',
      name: 'Mandatory Automated Tests (TDD)',
      category: 'Quality',
      severity: 'P0_BLOCKING',
      penaltyPoints: 35,
      description: 'Requires every component or module to have a corresponding test file with behavioral assertions.',
      rationale: 'No code may be merged into the codebase without automated tests validating its correctness.',
      remediation: 'Create the corresponding unit/integration test file covering happy and error paths.',
      languages: ['Python', 'TypeScript', 'C++', 'C#', 'PHP'],
      status: 'active'
    },
    {
      id: 'CULT04',
      name: 'Zero Hardcoded Secrets and Tokens',
      category: 'Security',
      severity: 'P0_BLOCKING',
      penaltyPoints: 40,
      description: 'Detection of credentials, API keys, passwords, or sensitive tokens hardcoded in source code.',
      rationale: 'Security and compliance are non-negotiable.',
      remediation: 'Use environment variables or secrets management vaults (e.g., os.environ or secrets manager).',
      languages: ['Python', 'Bend', 'TypeScript', 'C++', 'C#', 'PHP'],
      status: 'active'
    },
    {
      id: 'CULT05',
      name: 'Strict Typing and Clear Signatures',
      category: 'Contracts',
      severity: 'P1_WARNING',
      penaltyPoints: 10,
      description: 'Requires strict typing on parameters and return types of functions.',
      rationale: 'Prevents ambiguity and runtime type errors.',
      remediation: 'Explicitly declare parameter and return types for all public functions.',
      languages: ['Python', 'TypeScript', 'C++', 'C#', 'PHP'],
      status: 'active'
    },
    {
      id: 'ARCH-LAYER-01',
      name: 'Zero Presentation Code in Domain, Models & Controllers',
      category: 'Architecture',
      severity: 'P0_BLOCKING',
      penaltyPoints: 40,
      description: 'Strictly prohibits embedding raw HTML, JSX, CSS styles, or client scripts inside Domain, Model, Service, or Controller classes.',
      rationale: 'Universal Separation of Concerns across layered architectures.',
      remediation: 'Move presentation markup into dedicated View templates/components or return structured DTOs.',
      languages: ['C#', 'Python', 'TypeScript', 'PHP', 'Java', 'Go', 'Rust'],
      status: 'active'
    },
    {
      id: 'ARCH-LAYER-02',
      name: 'Zero Direct Database Queries in Presentation & Views',
      category: 'Architecture',
      severity: 'P0_BLOCKING',
      penaltyPoints: 35,
      description: 'Prohibits executing raw database queries (SELECT, DbContext, DB::table, objects.filter) inside presentation templates.',
      rationale: 'Prevents N+1 query leaks, data coupling, and template bloat.',
      remediation: 'Fetch data in controllers or application services and pass prepared collections/ViewModels.',
      languages: ['C#', 'Python', 'TypeScript', 'PHP', 'Java', 'Go', 'Rust'],
      status: 'active'
    },
    {
      id: 'ARCH-LAYER-03',
      name: 'Zero Transport Protocol Coupling in Domain Models',
      category: 'Architecture',
      severity: 'P0_BLOCKING',
      penaltyPoints: 30,
      description: 'Prohibits binding HTTP request objects or transport superglobals (HttpContext, express.Request, $_POST) inside domain entities.',
      rationale: 'Enables domain reuse in background workers, CLI tools, and isolated unit tests.',
      remediation: 'Pass primitive arguments or domain DTOs to entity methods.',
      languages: ['C#', 'Python', 'TypeScript', 'PHP', 'Java', 'Go', 'Rust'],
      status: 'active'
    },
    {
      id: 'ARCH-LAYER-04',
      name: 'Thin Controllers (Delegation to Application / Domain Services)',
      category: 'Architecture',
      severity: 'P1_WARNING',
      penaltyPoints: 20,
      description: 'Controllers must act as lightweight coordinators without containing heavy business algorithms.',
      rationale: 'Avoids fat controllers and improves unit testability.',
      remediation: 'Extract business logic into Use Cases or Application Services.',
      languages: ['C#', 'Python', 'TypeScript', 'PHP', 'Java', 'Go', 'Rust'],
      status: 'active'
    },
    {
      id: 'ARCH-FE-01',
      name: 'Zero Direct Network Calls in Presentational UI Components',
      category: 'Architecture',
      severity: 'P0_BLOCKING',
      penaltyPoints: 35,
      description: 'Prohibits direct API network calls (fetch, axios, http.get) inside dumb Presentational UI components.',
      rationale: 'Ensures UI components remain pure and reusable across containers.',
      remediation: 'Delegate API calls to container components, custom hooks, or state managers.',
      languages: ['TypeScript', 'JavaScript'],
      status: 'active'
    }
  ]);

  readonly history = signal<AnalysisRun[]>([
    {
      id: '142',
      date: 'Today, 14:32',
      project: 'acme/core-engine · !142',
      mrTitle: 'Refactor parser and lexer in Bend',
      author: 'Alice Walker',
      targetBranch: 'main',
      issues: 0,
      status: 'Full compliance',
      duration: '32s',
      score: 100,
      violations: []
    },
    {
      id: '87',
      date: 'Today, 09:18',
      project: 'acme/billing-service · #87',
      mrTitle: 'Update payment gateway with Rate Limiter',
      author: 'Bob Miller',
      targetBranch: 'main',
      issues: 2,
      status: 'Completed',
      duration: '1m 08s',
      score: 85,
      violations: [
        {
          ruleId: 'CULT02',
          fileName: 'src/billing.py',
          severity: 'P1_WARNING',
          penalty: 15,
          line: 12,
          author: 'Bob Miller',
          astNode: 'FunctionDecl (charge)',
          message: 'Missing requirement traceability tag @spec RFxx in main function'
        }
      ]
    },
    {
      id: '31',
      date: 'Yesterday, 17:45',
      project: 'acme/legacy-parser · !31',
      mrTitle: 'Fix lexer and add validation stub',
      author: 'Charlie Green',
      targetBranch: 'develop',
      issues: 5,
      status: 'Blocked',
      duration: '18s',
      score: 45,
      violations: [
        {
          ruleId: 'CULT01',
          fileName: 'src/lexer.py',
          severity: 'P0_BLOCKING',
          penalty: 35,
          line: 42,
          author: 'Charlie Green',
          astNode: 'StmtList (TODO)',
          message: 'Incomplete or lazy code detected: # TODO: Handle nested expressions'
        },
        {
          ruleId: 'CULT04',
          fileName: 'src/lexer.py',
          severity: 'P0_BLOCKING',
          penalty: 40,
          line: 8,
          author: 'Charlie Green',
          astNode: 'VarDecl (API_SECRET)',
          message: 'Hardcoded API secret token secret_key_mock... detected'
        }
      ]
    },
    {
      id: '64',
      date: 'Jun 12, 11:06',
      project: 'acme/desktop-client · #64',
      mrTitle: 'Update desktop client and type contracts',
      author: 'David Vance',
      targetBranch: 'main',
      issues: 0,
      status: 'Full compliance',
      duration: '2m 14s',
      score: 100,
      violations: []
    }
  ]);

  readonly mrPresets = [
    {
      repo: 'acme/core-engine',
      mrId: '142',
      mrTitle: '#142 — Implement Token Bucket Rate Limiter',
      targetBranch: 'main',
      fileName: 'src/rate_limiter.py',
      author: 'Alice Walker',
      astNode: 'ClassDecl → FunctionDecl(allow_request)',
      baseCode: `110  class RateLimiter:
111      def __init__(self, capacity):
112          self.capacity = capacity
113          self.current = capacity
114
115      def allow_request(self):
116          return True`,
      proposalCode: `110  class RateLimiter:
111 +    """Traceability: @spec RF01"""
112 +    def __init__(self, capacity: int, refill_rate: float) -> None:
113 +        self.capacity: int = capacity
114 +        self.refill_rate: float = refill_rate
115 +        self.buckets: dict = {}
116
117 +    def allow_request(self, client_id: str, tokens: int = 1) -> bool:
118 +        return self._evaluate(client_id, tokens)`,
      fullCode: `"""
@spec RF01 - Token Bucket Rate Limiter
"""
import time
from typing import Dict, Tuple

class RateLimiter:
    def __init__(self, capacity: int, refill_rate_per_sec: float) -> None:
        self.capacity: int = capacity
        self.refill_rate: float = refill_rate_per_sec
        self.buckets: Dict[str, Tuple[float, float]] = {}

    def allow_request(self, client_id: str, tokens: int = 1) -> bool:
        now: float = time.time()
        if client_id not in self.buckets:
            self.buckets[client_id] = (float(self.capacity) - float(tokens), now)
            return True
        current, last = self.buckets[client_id]
        refilled = min(float(self.capacity), current + ((now - last) * self.refill_rate))
        if refilled >= float(tokens):
            self.buckets[client_id] = (refilled - float(tokens), now)
            return True
        return False
`,
      hasTestFile: true
    },
    {
      repo: 'acme/billing-service',
      mrId: '87',
      mrTitle: '#87 — Update payment gateway integration',
      targetBranch: 'main',
      fileName: 'src/payment_gateway.py',
      author: 'Bob Miller',
      astNode: 'CallExpr → VarDecl(API_SECRET)',
      baseCode: `40  def charge(user_id, amount):
41      return gateway.process(user_id, amount)
42  `,
      proposalCode: `40  API_SECRET = "secret_key_mock_token_99887766554433221100"
41
42  def process_charge(user_id, amount):
43 +    # TODO: Implement complete gateway communication
44 +    if amount <= 0:
45 +        return False
46 +    pass`,
      fullCode: `API_SECRET = "secret_key_mock_token_99887766554433221100"

def process_charge(user_id, amount):
    # TODO: Implement complete gateway communication
    if amount <= 0:
        return False
    pass
`,
      hasTestFile: false
    }
  ];

  auditCode(fileName: string, code: string, hasTestFile: boolean, author: string = 'DevOps Pipeline'): FileAuditInfo {
    const lines = code.split('\n');
    const violations: CodeViolation[] = [];

    // 1. Spec tag check (CULT02)
    const specRegex = /@spec\s+RF\d+|\[RF\d+\]|Requirement:\s*RF\d+|Spec-ID:\s*RF\d+/i;
    const hasSpecTag = specRegex.test(code);
    if (!hasSpecTag) {
      violations.push({
        ruleId: 'CULT02',
        fileName,
        severity: 'P1_WARNING',
        penalty: 15,
        author,
        astNode: 'Module / Header Annotation',
        message: 'Missing requirement traceability tag (@spec RFxx)'
      });
    }

    // 2. Lazy code check (CULT01)
    let hasLazyCode = false;
    const lazyPatterns = [
      /#\s*TODO/i,
      /\/\/\s*TODO/i,
      /#\s*FIXME/i,
      /\/\/\s*FIXME/i,
      /to\s+be\s+implemented/i,
      /implement\s+later/i,
      /^\s*pass\s*$/,
      /raise\s+NotImplementedError/
    ];

    lines.forEach((line, index) => {
      for (const pattern of lazyPatterns) {
        if (pattern.test(line)) {
          hasLazyCode = true;
          violations.push({
            ruleId: 'CULT01',
            fileName,
            severity: 'P0_BLOCKING',
            penalty: 35,
            line: index + 1,
            author,
            astNode: 'StmtList (Lazy Code / Stub)',
            snippet: line.trim(),
            message: `Incomplete or lazy code detected: "${line.trim()}"`
          });
          break;
        }
      }
    });

    // 3. Secret scan (CULT04)
    let hasSecrets = false;
    const secretPatterns = [
      /(api[_-]?key|secret|password|token|bearer)\s*[:=]\s*['"][A-Za-z0-9_\-\.]{12,}['"]/i,
      /ghp_[0-9a-zA-Z]{36,}/,
      /xox[baprs]-[0-9a-zA-Z]{10,}/
    ];

    lines.forEach((line, index) => {
      for (const pattern of secretPatterns) {
        if (pattern.test(line)) {
          hasSecrets = true;
          violations.push({
            ruleId: 'CULT04',
            fileName,
            severity: 'P0_BLOCKING',
            penalty: 40,
            line: index + 1,
            author,
            astNode: 'VarDecl (Secret Token Exposure)',
            snippet: line.trim(),
            message: 'Hardcoded API credential or secret token detected'
          });
          break;
        }
      }
    });

    // 4. Test presence check (CULT03)
    const isTestFile = fileName.toLowerCase().includes('test') || fileName.toLowerCase().includes('spec');
    const hasTestCoverage = isTestFile || hasTestFile;
    if (!hasTestCoverage) {
      violations.push({
        ruleId: 'CULT03',
        fileName,
        severity: 'P0_BLOCKING',
        penalty: 35,
        author,
        astNode: 'Project Structure / Test Suite',
        message: 'Missing automated test file associated with this artifact'
      });
    }

    // 5. Strict typing check (CULT05)
    let hasTypeAnnotations = true;
    if (fileName.endsWith('.py') || fileName.endsWith('.ts') || fileName.endsWith('.js') || fileName.endsWith('.cpp')) {
      const hasDefs = /def\s+\w+\s*\(/.test(code);
      const hasHints = /->\s*[\w\[\], ]+:/.test(code) || /:\s*(str|int|float|bool|list|dict|Any|Optional)/.test(code);
      if (hasDefs && !hasHints) {
        hasTypeAnnotations = false;
        violations.push({
          ruleId: 'CULT05',
          fileName,
          severity: 'P1_WARNING',
          penalty: 10,
          author,
          astNode: 'FunctionSignature (Type Annotations)',
          message: 'Functions detected without explicit parameter or return type annotations'
        });
      }
    }

    // 6. Universal Layer-Specific Architecture Inspections (ARCH-LAYER-01)
    if (fileName.includes('Controller') || fileName.includes('Model') || fileName.includes('Service')) {
      const hasHtml = /<html|<div|<span|<p>|<script>|<style>|document\.getElement|window\.location|echo\s*\"<|print\(\"<|Response\.Write\(\"</i.test(code);
      if (hasHtml) {
        violations.push({
          ruleId: 'ARCH-LAYER-01',
          fileName,
          severity: 'P0_BLOCKING',
          penalty: 40,
          author,
          astNode: 'PresentationInBackendLayer',
          message: 'Forbidden presentation markup/script inside Domain, Model, Service, or Controller class'
        });
      }
    }

    return {
      name: fileName,
      linesCount: lines.length,
      hasSpecTag,
      hasLazyCode,
      hasSecrets,
      hasTestCoverage,
      hasTypeAnnotations,
      violations
    };
  }

  generateReport(files: FileAuditInfo[]): AuditReport {
    let totalViolations = 0;
    let p0Count = 0;
    let p1Count = 0;
    let p2Count = 0;
    let totalPenalty = 0;

    files.forEach(f => {
      f.violations.forEach(v => {
        totalViolations++;
        totalPenalty += v.penalty;
        if (v.severity === 'P0_BLOCKING') p0Count++;
        else if (v.severity === 'P1_WARNING') p1Count++;
        else p2Count++;
      });
    });

    const score = Math.max(0, 100 - totalPenalty);
    const isApproved = p0Count === 0 && score >= 80;

    return {
      totalFiles: files.length,
      totalViolations,
      p0Count,
      p1Count,
      p2Count,
      totalPenalty,
      score,
      isApproved,
      files
    };
  }
}
