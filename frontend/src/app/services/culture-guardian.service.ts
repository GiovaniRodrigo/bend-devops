import { Injectable, signal } from '@angular/core';
import {
  AnalysisRun,
  ArchitectureProfile,
  ArchitectureProfileId,
  ArchitecturalLayer,
  AuditReport,
  BranchPolicy,
  CodeViolation,
  CultureRule,
  FileAuditInfo,
  LayerVocabularyItem,
  VcsPlatform,
  WebhookEventPayload
} from '../models/culture.model';

@Injectable({
  providedIn: 'root'
})
export class CultureGuardianService {
  // 1. Architecture Profiles (from backend/rules/1_architectures/)
  readonly architectureProfiles = signal<ArchitectureProfile[]>([
    {
      id: 'clean_architecture',
      name: 'Clean Architecture (Onion / Hexagonal / Concentric)',
      category: 'Enterprise Architectural Pattern',
      description: 'Concentric rings where dependencies flow strictly inwards towards pure domain entities.',
      tiers: [
        {
          name: 'Domain (Core Entities)',
          description: 'Pure enterprise rules, aggregates, and value objects. Zero external dependencies.',
          allowedDependencies: [],
          forbiddenDependencies: ['Application', 'Infrastructure', 'Presentation', 'Web', 'Database', 'Http']
        },
        {
          name: 'Application (Use Cases)',
          description: 'Use cases, commands, queries, orchestrators, and port interfaces.',
          allowedDependencies: ['Domain'],
          forbiddenDependencies: ['Infrastructure', 'Presentation', 'Web', 'Controllers']
        },
        {
          name: 'Interface Adapters',
          description: 'Controllers, presenters, gateways, repositories, and DTO serializers.',
          allowedDependencies: ['Application', 'Domain'],
          forbiddenDependencies: ['Frameworks']
        },
        {
          name: 'Frameworks & Drivers',
          description: 'Databases, HTTP servers, UI frameworks, and CLI runners.',
          allowedDependencies: ['Interface Adapters', 'Application', 'Domain'],
          forbiddenDependencies: []
        }
      ]
    },
    {
      id: 'domain_driven_design',
      name: 'Domain-Driven Design (DDD)',
      category: 'Strategic Domain Modeling',
      description: 'Isolates Domain Aggregates and Domain Services from Infrastructure persistence.',
      tiers: [
        {
          name: 'Domain Layer',
          description: 'Aggregates, entities, value objects, domain events, and repository interfaces.',
          allowedDependencies: [],
          forbiddenDependencies: ['Infrastructure', 'Application', 'UI', 'Persistence']
        },
        {
          name: 'Application Layer',
          description: 'Application services coordinating domain objects and transactions.',
          allowedDependencies: ['Domain'],
          forbiddenDependencies: ['UI', 'Controllers']
        },
        {
          name: 'Infrastructure Layer',
          description: 'Database implementations (EF Core, SQLAlchemy, Prisma), message brokers, external APIs.',
          allowedDependencies: ['Domain', 'Application'],
          forbiddenDependencies: ['UI']
        },
        {
          name: 'User Interface / API',
          description: 'REST controllers, GraphQL resolvers, Razor/React views.',
          allowedDependencies: ['Application', 'Domain'],
          forbiddenDependencies: ['Direct Database']
        }
      ]
    },
    {
      id: 'hexagonal',
      name: 'Hexagonal Architecture (Ports & Adapters)',
      category: 'Decoupled Boundary Architecture',
      description: 'Application core communicates with external world strictly through Ports (inbound/outbound interfaces).',
      tiers: [
        {
          name: 'Domain & Application Core',
          description: 'Core logic + Driving/Driven Port interfaces.',
          allowedDependencies: [],
          forbiddenDependencies: ['Adapters', 'HTTP', 'Database', 'Drivers']
        },
        {
          name: 'Inbound Adapters (Primary / Driving)',
          description: 'REST controllers, CLI commands, Event consumers.',
          allowedDependencies: ['Domain & Application Core'],
          forbiddenDependencies: ['Outbound Adapters']
        },
        {
          name: 'Outbound Adapters (Secondary / Driven)',
          description: 'SQL repositories, mail clients, payment gateways.',
          allowedDependencies: ['Domain & Application Core'],
          forbiddenDependencies: ['Inbound Adapters']
        }
      ]
    },
    {
      id: 'layered_mvc',
      name: 'Layered MVC (4-Tier Traditional)',
      category: 'Classical Web Tier Architecture',
      description: 'Traditional separation of Model, View, Controller, and Infrastructure layers.',
      tiers: [
        {
          name: 'Model (Domain / Entities)',
          description: 'Data structures and business logic.',
          allowedDependencies: [],
          forbiddenDependencies: ['View', 'Controller', 'Presentation']
        },
        {
          name: 'Controller',
          description: 'Handles HTTP requests and delegates to services or models.',
          allowedDependencies: ['Model', 'Service'],
          forbiddenDependencies: ['View Direct Rendering']
        },
        {
          name: 'View / Presentation',
          description: 'Templates and UI markup.',
          allowedDependencies: ['Model (DTOs)'],
          forbiddenDependencies: ['Database', 'Controller']
        }
      ]
    },
    {
      id: 'microservices',
      name: 'Microservices & Event-Driven Architecture',
      category: 'Distributed Systems',
      description: 'Decoupled bounded contexts communicating via asynchronous events and REST contracts.',
      tiers: [
        {
          name: 'Domain Core',
          description: 'Internal service domain logic.',
          allowedDependencies: [],
          forbiddenDependencies: ['External Service Internals']
        },
        {
          name: 'Events & Messaging',
          description: 'Event publishers and consumers.',
          allowedDependencies: ['Domain Core'],
          forbiddenDependencies: ['UI']
        }
      ]
    },
    {
      id: 'cqrs_event_sourcing',
      name: 'CQRS & Event Sourcing',
      category: 'High-Throughput State Pattern',
      description: 'Segregates Read Models (Queries) from Write Models (Commands & Events).',
      tiers: [
        {
          name: 'Command Model (Write)',
          description: 'Aggregates enforcing invariants; emits events.',
          allowedDependencies: [],
          forbiddenDependencies: ['Read Model', 'UI']
        },
        {
          name: 'Query Model (Read)',
          description: 'Denormalized projections optimized for queries.',
          allowedDependencies: [],
          forbiddenDependencies: ['Command Model Aggregates']
        }
      ]
    },
    {
      id: 'rest_api',
      name: 'REST API & Resource Oriented',
      category: 'Web API Services',
      description: 'Resource endpoints with DTO validation and separation from domain entities.',
      tiers: [
        {
          name: 'Domain Entities',
          description: 'Internal persistence models.',
          allowedDependencies: [],
          forbiddenDependencies: ['HTTP Requests', 'ViewModels']
        },
        {
          name: 'Resource Controllers',
          description: 'Translates HTTP verbs into service actions.',
          allowedDependencies: ['Domain Entities', 'Services'],
          forbiddenDependencies: ['Raw SQL in handlers']
        }
      ]
    },
    {
      id: 'frontend_clean',
      name: 'Frontend Clean Architecture (Components / Hooks / Services)',
      category: 'Client-Side Architecture',
      description: 'Strict separation between Presentational Components, State Containers, and API Clients.',
      tiers: [
        {
          name: 'Presentational UI Components',
          description: 'Pure dumb components with props and event emitters.',
          allowedDependencies: ['Types', 'Design System'],
          forbiddenDependencies: ['Direct fetch', 'Direct axios', 'Global Storage Mutation']
        },
        {
          name: 'State / Hooks / Containers',
          description: 'Signals, state stores, and lifecycle hooks.',
          allowedDependencies: ['API Services', 'Domain Types'],
          forbiddenDependencies: ['DOM Manipulation']
        },
        {
          name: 'API Clients & Adapters',
          description: 'HTTP communication and DTO serialization.',
          allowedDependencies: ['Domain Types'],
          forbiddenDependencies: ['UI Templates']
        }
      ]
    }
  ]);

  // 2. Complete Canonical Rules Catalog (26 Real Manifest Rules)
  readonly rules = signal<CultureRule[]>([
    {
      id: 'CULT01',
      name: 'Zero Lazy Code & Complete Implementation',
      category: 'Culture & Quality',
      severity: 'P0_BLOCKING',
      penaltyPoints: 35,
      description: 'Prohibits placeholder or incomplete code in pull requests, including TODO, FIXME, empty pass statements, or unimplemented stubs.',
      rationale: 'Engineering discipline demands fully implemented features without hidden operational gaps.',
      remediation: 'Implement the full business logic or split the scope with documented specs before merging.',
      languages: ['Bend', 'Python', 'TypeScript', 'C#', 'PHP', 'Go', 'Java', 'Rust'],
      status: 'active'
    },
    {
      id: 'CULT02',
      name: 'Spec Traceability Obligation (@spec RFxx)',
      category: 'Culture & Quality',
      severity: 'P1_WARNING',
      penaltyPoints: 15,
      description: 'Requires an explicit annotation or comment linking the source unit to its specification requirement (e.g. @spec RF01).',
      rationale: 'Guarantees bidirectional traceability between formal requirements and source code.',
      remediation: 'Add an annotation @spec RF<number> referencing the requirement ID in the header comment.',
      languages: ['Bend', 'Python', 'TypeScript', 'C#', 'PHP', 'Go', 'Java', 'Rust'],
      status: 'active'
    },
    {
      id: 'CULT03',
      name: 'Mandatory Automated Test Coverage (TDD)',
      category: 'Culture & Quality',
      severity: 'P0_BLOCKING',
      penaltyPoints: 35,
      description: 'Requires every production code module to have a corresponding unit/integration test file with behavioral assertions.',
      rationale: 'No code may be merged into production without automated validation.',
      remediation: 'Create the corresponding test file covering happy paths, edge cases, and error branches.',
      languages: ['Bend', 'Python', 'TypeScript', 'C#', 'PHP', 'Go', 'Java', 'Rust'],
      status: 'active'
    },
    {
      id: 'CULT04',
      name: 'Zero Hardcoded Secrets and Tokens',
      category: 'Security',
      severity: 'P0_BLOCKING',
      penaltyPoints: 40,
      description: 'Detects credentials, API keys, passwords, bearer tokens, or private keys hardcoded in source code.',
      rationale: 'Protects infrastructure and data against credential leaks in public or internal repositories.',
      remediation: 'Use environment variables, vault injection, or key vault managers.',
      languages: ['Bend', 'Python', 'TypeScript', 'C#', 'PHP', 'Go', 'Java', 'Rust'],
      status: 'active'
    },
    {
      id: 'CULT05',
      name: 'Strict Typing & Contract Clarity',
      category: 'Culture & Quality',
      severity: 'P1_WARNING',
      penaltyPoints: 10,
      description: 'Requires explicit type annotations for function parameters and return types.',
      rationale: 'Prevents ambiguity and runtime type errors in dynamic and statically typed code.',
      remediation: 'Declare explicit parameter and return types for all public functions and methods.',
      languages: ['Python', 'TypeScript', 'C#', 'PHP', 'Go', 'Java', 'Rust'],
      status: 'active'
    },
    {
      id: 'ARCH-LAYER-01',
      name: 'Zero Presentation Code in Domain, Models & Services',
      category: 'Architecture - Layer Boundaries',
      layer: 'Domain, Model, Controller, Service',
      severity: 'P0_BLOCKING',
      penaltyPoints: 40,
      description: 'Strictly prohibits raw UI markup (HTML, JSX, client scripts, styles) inside Domain, Model, Service, or Controller classes.',
      rationale: 'Universal Separation of Concerns across multi-tier software systems.',
      remediation: 'Move presentation markup into dedicated View templates/components or return structured DTOs.',
      languages: ['C#', 'Python', 'TypeScript', 'PHP', 'Java', 'Go', 'Rust'],
      status: 'active'
    },
    {
      id: 'ARCH-LAYER-02',
      name: 'Zero Direct Database Queries in Presentation & Views',
      category: 'Architecture - Layer Boundaries',
      layer: 'View, Template, Presentation',
      severity: 'P0_BLOCKING',
      penaltyPoints: 35,
      description: 'Prohibits executing raw database queries or ORM calls inside presentation templates and views.',
      rationale: 'Prevents N+1 query leaks, data coupling, and template bloat.',
      remediation: 'Fetch data in controllers or application services and pass prepared collections/ViewModels.',
      languages: ['C#', 'Python', 'TypeScript', 'PHP', 'Java', 'Go', 'Rust'],
      status: 'active'
    },
    {
      id: 'ARCH-LAYER-03',
      name: 'Zero Transport Protocol Coupling in Domain Models',
      category: 'Architecture - Layer Boundaries',
      layer: 'Domain, Model, Entity',
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
      name: 'Thin Controllers (Delegation to Application Services)',
      category: 'Architecture - Layer Boundaries',
      layer: 'Controller, Endpoint',
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
      category: 'Architecture - Layer Boundaries',
      layer: 'Presentational UI Component',
      severity: 'P0_BLOCKING',
      penaltyPoints: 35,
      description: 'Prohibits direct API network calls (fetch, axios, http.get) inside dumb Presentational UI components.',
      rationale: 'Ensures UI components remain pure, decoupled, and reusable across containers.',
      remediation: 'Delegate API calls to container components, custom hooks, or state managers.',
      languages: ['TypeScript', 'JavaScript'],
      status: 'active'
    }
  ]);

  // 3. Layer Vocabulary Taxonomy (from backend/rules/layer_vocabulary.json)
  readonly layerVocabulary = signal<LayerVocabularyItem[]>([
    {
      layer: 'Domain',
      description: 'Pure enterprise core business rules and entities.',
      keywords: ['Entity', 'AggregateRoot', 'ValueObject', 'DomainEvent', 'DomainService', 'Specification'],
      forbiddenInOtherLayers: ['UI markup', 'HTTP request handling', 'Direct Database context'],
      languages: {
        'C#': ['namespace Core.Domain', 'public class Order : IAggregateRoot', 'ValueObject'],
        'Python': ['class Order(DomainEntity):', '@dataclass(frozen=True)'],
        'TypeScript': ['export class UserEntity implements AggregateRoot', 'ValueObject<Props>'],
        'Go': ['package domain', 'type Order struct'],
        'Java': ['package com.company.domain', 'public class Invoice implements Aggregate'],
        'Rust': ['pub struct OrderId(Uuid);', 'impl Aggregate for Order']
      }
    },
    {
      layer: 'Application',
      description: 'Use cases, commands, queries, orchestrators, and port interfaces.',
      keywords: ['UseCase', 'CommandHandler', 'QueryHandler', 'Port', 'Dto', 'Service'],
      forbiddenInOtherLayers: ['Direct UI View templates', 'Raw HTTP response stream mutation'],
      languages: {
        'C#': ['IRequestHandler<CreateOrderCommand, Result>', 'public async Task<OrderDto> Handle'],
        'Python': ['class CreateOrderUseCase:', 'def execute(self, cmd: CreateOrderCommand)'],
        'TypeScript': ['export class CreateOrderHandler implements ICommandHandler'],
        'Go': ['type OrderService struct', 'func (s *OrderService) CreateOrder'],
        'Java': ['@Service', 'public class CreateOrderUseCase']
      }
    },
    {
      layer: 'Infrastructure',
      description: 'External tools, databases, network adapters, and third-party integrations.',
      keywords: ['Repository', 'DbContext', 'HttpClient', 'KafkaProducer', 'RedisCache', 'S3Storage'],
      forbiddenInOtherLayers: ['Direct domain aggregate modification without business methods'],
      languages: {
        'C#': ['public class SqlOrderRepository : IOrderRepository', 'AppDbContext'],
        'Python': ['class PostgresUserRepository(UserRepository):', 'engine = create_engine()'],
        'TypeScript': ['export class TypeOrmUserRepository implements UserRepository'],
        'Go': ['type PostgresRepo struct', 'db.QueryRow()'],
        'Java': ['@Repository', 'public class JpaOrderRepository implements OrderRepository']
      }
    },
    {
      layer: 'Presentation',
      description: 'UI components, HTTP controllers, REST endpoints, and views.',
      keywords: ['Controller', 'Endpoint', 'View', 'Page', 'Component', 'Router', 'ViewModel'],
      forbiddenInOtherLayers: ['Direct SQL execution', 'Raw ORM schema mutation'],
      languages: {
        'C#': ['[ApiController]', '[HttpGet("{id}")]', 'public IActionResult GetOrder'],
        'Python': ['@router.get("/orders/{id}")', 'def get_order(id: int):'],
        'TypeScript': ['@Controller("orders")', '@Get(":id")', '@Component({ selector: "app-order" })'],
        'Go': ['r.GET("/orders/:id", GetOrderHandler)'],
        'Java': ['@RestController', '@GetMapping("/orders/{id}")']
      }
    }
  ]);

  // 4. Branch Policies (from backend/rules/4_scanner/ & scripts/vcs_adapters/policy_engine.py)
  readonly branchPolicies = signal<BranchPolicy[]>([
    {
      branchPattern: 'main | master | release/*',
      minScore: 80,
      allowP0: false,
      allowP1: true,
      description: 'Production branches require 0 blocking (P0) violations and a minimum quality score of 80%.'
    },
    {
      branchPattern: 'feature/* | fix/* | chore/*',
      minScore: 50,
      allowP0: true,
      allowP1: true,
      description: 'Feature development branches emit warning annotations without blocking CI pipeline progression.'
    }
  ]);

  // 5. Real Audit History State (strictly populated by real session runs)
  readonly history = signal<AnalysisRun[]>([]);

  // 6. Real Code & Diff Presets for Interactive Audits
  readonly codePresets = [
    {
      name: 'Clean Architecture Domain Entity (100% Compliant)',
      language: 'C#',
      layer: 'Domain' as ArchitecturalLayer,
      fileName: 'src/Domain/Entities/Order.cs',
      targetBranch: 'main',
      author: 'Senior Software Engineer',
      hasTestFile: true,
      code: `// @spec RF14 - Clean Architecture Domain Entity
using System;
using System.Collections.Generic;

namespace Enterprise.Domain.Entities
{
    public class Order
    {
        public Guid Id { get; private set; }
        public DateTime CreatedAtUtc { get; private set; }
        private readonly List<OrderItem> _items = new();

        public IReadOnlyCollection<OrderItem> Items => _items.AsReadOnly();

        public Order(Guid id)
        {
            Id = id;
            CreatedAtUtc = DateTime.UtcNow;
        }

        public void AddItem(string productSku, decimal unitPrice, int quantity)
        {
            if (string.IsNullOrWhiteSpace(productSku))
                throw new ArgumentException("SKU is required", nameof(productSku));
            if (unitPrice <= 0)
                throw new ArgumentException("Unit price must be positive", nameof(unitPrice));
            if (quantity <= 0)
                throw new ArgumentException("Quantity must be greater than zero", nameof(quantity));

            _items.Add(new OrderItem(productSku, unitPrice, quantity));
        }
    }
}`
    },
    {
      name: 'Non-Compliant Layer Leakage (Presentation in Domain & Lazy Code)',
      language: 'C#',
      layer: 'Domain' as ArchitecturalLayer,
      fileName: 'src/Domain/Models/OrderInvoice.cs',
      targetBranch: 'main',
      author: 'Junior Developer',
      hasTestFile: false,
      code: `using System;

namespace Enterprise.Domain.Models
{
    public class OrderInvoice
    {
        public string InvoiceId { get; set; }
        public string ApiSecretKey = "ghp_99887766554433221100aabbccddeeff1122";

        public string RenderInvoiceHtml()
        {
            // TODO: Implement complete PDF/HTML rendering logic later
            return "<div class='invoice'><h1>Invoice #" + InvoiceId + "</h1></div>";
        }
    }
}`
    },
    {
      name: 'Database Query in Presentation View (ARCH-LAYER-02 Violation)',
      language: 'C#',
      layer: 'Presentation' as ArchitecturalLayer,
      fileName: 'src/Presentation/Views/Orders/Index.cshtml.cs',
      targetBranch: 'main',
      author: 'Fullstack Dev',
      hasTestFile: true,
      code: `// @spec RF20 - Orders View Component
using Microsoft.AspNetCore.Mvc.RazorPages;
using System.Linq;

namespace Enterprise.Presentation.Pages
{
    public class OrdersIndexModel : PageModel
    {
        public void OnGet()
        {
            // Direct ORM context access in presentation page
            var db = new AppDbContext();
            var orders = db.Orders.Where(o => o.IsActive).ToList();
        }
    }
}`
    },
    {
      name: 'Pragma Suppression with Justification (@guardian-ignore)',
      language: 'Python',
      layer: 'Infrastructure' as ArchitecturalLayer,
      fileName: 'src/infrastructure/legacy_connector.py',
      targetBranch: 'main',
      author: 'DevOps Architect',
      hasTestFile: true,
      code: `"""
@spec RF45 - Legacy Integration Adapter
"""
import os
from typing import Dict, Any

class LegacyConnector:
    def __init__(self, endpoint: str) -> None:
        self.endpoint: str = endpoint

    def dispatch(self, payload: Dict[str, Any]) -> bool:
        # @guardian-ignore ARCH-LAYER-03: Approved temporary legacy coupling pending microservice migration
        raw_transport_socket = "tcp://10.0.0.1:8080"
        return True
`
    }
  ];

  // 7. Multi-Language Lexer & Lexical Scoper
  stripComments(code: string, language: string): string {
    let stripped = code;
    // Strip multi-line comments
    stripped = stripped.replace(/\/\*[\s\S]*?\*\//g, '');
    stripped = stripped.replace(/"""[\s\S]*?"""/g, '');
    stripped = stripped.replace(/'''[\s\S]*?'''/g, '');
    // Strip single-line comments
    stripped = stripped.replace(/\/\/.*$/gm, '');
    stripped = stripped.replace(/#.*$/gm, '');
    stripped = stripped.replace(/--.*$/gm, '');
    return stripped;
  }

  // 8. Word Boundary Token Matching Engine
  matchesToken(line: string, token: string): boolean {
    const regex = new RegExp(`\\b${token}\\b`, 'i');
    return regex.test(line);
  }

  // 9. Inline & Block Pragma Parser
  parseSuppression(line: string): { ruleId: string; reason: string } | null {
    const match = line.match(/@guardian-ignore\s+([A-Za-z0-9_\-\*]+)\s*:\s*(.+)$/i);
    if (match) {
      return {
        ruleId: match[1].trim(),
        reason: match[2].trim()
      };
    }
    return null;
  }

  // 10. Audit Code Engine (Direct in-browser execution matching guardian.bend and token_filter.py)
  auditCode(
    fileName: string,
    code: string,
    hasTestFile: boolean,
    author: string = 'DevOps Pipeline',
    targetBranch: string = 'main',
    profileId: ArchitectureProfileId = 'clean_architecture'
  ): FileAuditInfo {
    const lines = code.split('\n');
    const violations: CodeViolation[] = [];
    let activeSuppressionsCount = 0;

    const activeRulesMap = new Map<string, CultureRule>();
    this.rules().forEach(r => {
      if (r.status === 'active') activeRulesMap.set(r.id, r);
    });

    // Detect file language
    let language = 'Unknown';
    if (fileName.endsWith('.cs')) language = 'C#';
    else if (fileName.endsWith('.py')) language = 'Python';
    else if (fileName.endsWith('.ts') || fileName.endsWith('.tsx')) language = 'TypeScript';
    else if (fileName.endsWith('.js') || fileName.endsWith('.jsx')) language = 'JavaScript';
    else if (fileName.endsWith('.go')) language = 'Go';
    else if (fileName.endsWith('.java')) language = 'Java';
    else if (fileName.endsWith('.rs')) language = 'Rust';
    else if (fileName.endsWith('.php')) language = 'PHP';
    else if (fileName.endsWith('.bend')) language = 'Bend';

    // Layer classification
    let layer: ArchitecturalLayer = 'Unknown';
    const lowerName = fileName.toLowerCase();
    if (lowerName.includes('domain') || lowerName.includes('entity') || lowerName.includes('entities') || lowerName.includes('model')) {
      layer = 'Domain';
    } else if (lowerName.includes('service') || lowerName.includes('usecase') || lowerName.includes('application') || lowerName.includes('handler')) {
      layer = 'Application';
    } else if (lowerName.includes('controller') || lowerName.includes('view') || lowerName.includes('page') || lowerName.includes('component')) {
      layer = 'Presentation';
    } else if (lowerName.includes('repo') || lowerName.includes('infra') || lowerName.includes('database') || lowerName.includes('gateway')) {
      layer = 'Infrastructure';
    }

    // Check 1: Spec tag (CULT02)
    const specRegex = /@spec\s+RF\d+|\[RF\d+\]|Requirement:\s*RF\d+|Spec-ID:\s*RF\d+/i;
    const hasSpecTag = specRegex.test(code);
    if (!hasSpecTag && activeRulesMap.has('CULT02')) {
      const r = activeRulesMap.get('CULT02')!;
      violations.push({
        ruleId: 'CULT02',
        fileName,
        severity: r.severity,
        penalty: r.penaltyPoints,
        author,
        astNode: 'Module Header Annotation',
        message: 'Missing requirement traceability tag (@spec RFxx)',
        remediation: r.remediation
      });
    }

    // Check 2: Lazy code (CULT01)
    let hasLazyCode = false;
    const lazyPatterns = [
      /#\s*TODO/i,
      /\/\/\s*TODO/i,
      /#\s*FIXME/i,
      /\/\/\s*FIXME/i,
      /to\s+be\s+implemented/i,
      /implement\s+later/i,
      /^\s*pass\s*$/,
      /raise\s+NotImplementedError/,
      /throw\s+new\s+NotImplementedException/
    ];

    // Check 3: Secrets (CULT04)
    let hasSecrets = false;
    const secretPatterns = [
      /(api[_-]?key|secret|password|token|bearer)\s*[:=]\s*['"][A-Za-z0-9_\-\.]{12,}['"]/i,
      /ghp_[0-9a-zA-Z]{36,}/,
      /xox[baprs]-[0-9a-zA-Z]{10,}/
    ];

    // Inspect line-by-line with inline pragma checking
    lines.forEach((line, index) => {
      const lineNum = index + 1;
      const suppression = this.parseSuppression(line);

      // Evaluate CULT01 (Lazy code)
      if (activeRulesMap.has('CULT01')) {
        for (const pattern of lazyPatterns) {
          if (pattern.test(line)) {
            hasLazyCode = true;
            if (suppression && (suppression.ruleId === 'CULT01' || suppression.ruleId === '*')) {
              activeSuppressionsCount++;
            } else {
              const r = activeRulesMap.get('CULT01')!;
              violations.push({
                ruleId: 'CULT01',
                fileName,
                severity: r.severity,
                penalty: r.penaltyPoints,
                line: lineNum,
                author,
                astNode: 'StmtList (Lazy Code / Stub)',
                snippet: line.trim(),
                message: `Incomplete code placeholder detected: "${line.trim()}"`,
                remediation: r.remediation
              });
            }
            break;
          }
        }
      }

      // Evaluate CULT04 (Secrets)
      if (activeRulesMap.has('CULT04')) {
        for (const pattern of secretPatterns) {
          if (pattern.test(line)) {
            hasSecrets = true;
            if (suppression && (suppression.ruleId === 'CULT04' || suppression.ruleId === '*')) {
              activeSuppressionsCount++;
            } else {
              const r = activeRulesMap.get('CULT04')!;
              violations.push({
                ruleId: 'CULT04',
                fileName,
                severity: r.severity,
                penalty: r.penaltyPoints,
                line: lineNum,
                author,
                astNode: 'VarDecl (Secret Token Exposure)',
                snippet: line.trim().replace(/(['"])[A-Za-z0-9_\-\.]{8,}(['"])/, '$1[REDACTED_SECRET]$2'),
                message: 'Hardcoded API secret token or credential detected',
                remediation: r.remediation
              });
            }
            break;
          }
        }
      }

      // Evaluate ARCH-LAYER-01 (Zero presentation in domain/model)
      if (activeRulesMap.has('ARCH-LAYER-01') && (layer === 'Domain' || lowerName.includes('domain') || lowerName.includes('model') || lowerName.includes('service'))) {
        const hasHtml = /<html|<div|<span|<p>|<script>|<style>|document\.getElement|window\.location|echo\s*\"<|print\(\"<|Response\.Write\(\"/i.test(line);
        if (hasHtml) {
          if (suppression && (suppression.ruleId === 'ARCH-LAYER-01' || suppression.ruleId === '*')) {
            activeSuppressionsCount++;
          } else {
            const r = activeRulesMap.get('ARCH-LAYER-01')!;
            violations.push({
              ruleId: 'ARCH-LAYER-01',
              fileName,
              severity: r.severity,
              penalty: r.penaltyPoints,
              line: lineNum,
              author,
              astNode: 'PresentationInDomainLayer',
              snippet: line.trim(),
              message: 'Forbidden presentation markup / HTML inside Domain model or Service class',
              remediation: r.remediation
            });
          }
        }
      }

      // Evaluate ARCH-LAYER-02 (Zero direct DB queries in Presentation)
      if (activeRulesMap.has('ARCH-LAYER-02') && (layer === 'Presentation' || lowerName.includes('view') || lowerName.includes('page') || lowerName.includes('component'))) {
        const hasDirectDb = /DbContext|AppDbContext|DB::table|objects\.filter|SELECT\s+.*FROM/i.test(line);
        if (hasDirectDb) {
          if (suppression && (suppression.ruleId === 'ARCH-LAYER-02' || suppression.ruleId === '*')) {
            activeSuppressionsCount++;
          } else {
            const r = activeRulesMap.get('ARCH-LAYER-02')!;
            violations.push({
              ruleId: 'ARCH-LAYER-02',
              fileName,
              severity: r.severity,
              penalty: r.penaltyPoints,
              line: lineNum,
              author,
              astNode: 'DatabaseInPresentationLayer',
              snippet: line.trim(),
              message: 'Forbidden direct database or DbContext access in presentation view component',
              remediation: r.remediation
            });
          }
        }
      }

      // Evaluate ARCH-LAYER-03 (Zero transport coupling in Domain)
      if (activeRulesMap.has('ARCH-LAYER-03') && (layer === 'Domain' || lowerName.includes('domain'))) {
        const hasTransport = /HttpContext|express\.Request|\$_POST|\$_GET|HttpRequest|socket\.connect|raw_transport_socket/i.test(line);
        if (hasTransport) {
          if (suppression && (suppression.ruleId === 'ARCH-LAYER-03' || suppression.ruleId === '*')) {
            activeSuppressionsCount++;
          } else {
            const r = activeRulesMap.get('ARCH-LAYER-03')!;
            violations.push({
              ruleId: 'ARCH-LAYER-03',
              fileName,
              severity: r.severity,
              penalty: r.penaltyPoints,
              line: lineNum,
              author,
              astNode: 'TransportInDomainLayer',
              snippet: line.trim(),
              message: 'Forbidden transport protocol or HTTP request binding inside domain entities',
              remediation: r.remediation
            });
          }
        }
      }
    });

    // Check 4: Test presence (CULT03)
    const isTestFile = lowerName.includes('test') || lowerName.includes('spec');
    const hasTestCoverage = isTestFile || hasTestFile;
    if (!hasTestCoverage && activeRulesMap.has('CULT03')) {
      const r = activeRulesMap.get('CULT03')!;
      violations.push({
        ruleId: 'CULT03',
        fileName,
        severity: r.severity,
        penalty: r.penaltyPoints,
        author,
        astNode: 'Project Structure / Test Suite',
        message: 'Missing automated test file associated with this production module',
        remediation: r.remediation
      });
    }

    // Check 5: Strict typing (CULT05)
    let hasTypeAnnotations = true;
    if (activeRulesMap.has('CULT05')) {
      if (language === 'Python' || language === 'TypeScript' || language === 'PHP') {
        const hasDefs = /def\s+\w+\s*\(|function\s+\w+\s*\(/.test(code);
        const hasHints = /->\s*[\w\[\], ]+:/.test(code) || /:\s*(string|number|boolean|str|int|float|bool|void)/.test(code);
        if (hasDefs && !hasHints) {
          hasTypeAnnotations = false;
          const r = activeRulesMap.get('CULT05')!;
          violations.push({
            ruleId: 'CULT05',
            fileName,
            severity: r.severity,
            penalty: r.penaltyPoints,
            author,
            astNode: 'FunctionSignature (Type Annotations)',
            message: 'Functions detected without explicit parameter or return type annotations',
            remediation: r.remediation
          });
        }
      }
    }

    return {
      name: fileName,
      linesCount: lines.length,
      language,
      identifiedLayer: layer,
      hasSpecTag,
      hasLazyCode,
      hasSecrets,
      hasTestCoverage,
      hasTypeAnnotations,
      violations,
      activeSuppressions: activeSuppressionsCount
    };
  }

  // 11. Generate Consolidated Audit Report
  generateReport(files: FileAuditInfo[]): AuditReport {
    let totalViolations = 0;
    let p0Count = 0;
    let p1Count = 0;
    let p2Count = 0;
    let totalPenalty = 0;
    let activeSuppressionsCount = 0;

    files.forEach(f => {
      activeSuppressionsCount += f.activeSuppressions;
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
      activeSuppressionsCount,
      score,
      isApproved,
      files,
      timestamp: new Date().toISOString()
    };
  }

  // 12. Multi-Platform VCS Exporters
  generateSarifJson(report: AuditReport): string {
    const sarif = {
      $schema: 'https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json',
      version: '2.1.0',
      runs: [
        {
          tool: {
            driver: {
              name: 'Bend DevOps Guardian (HVM)',
              version: '1.0.0',
              informationUri: 'https://github.com/GiovaniRodrigo/bend-devops',
              rules: this.rules().map(r => ({
                id: r.id,
                name: r.name,
                shortDescription: { text: r.description },
                help: { text: `${r.rationale}\nRemediation: ${r.remediation}` },
                defaultConfiguration: {
                  level: r.severity === 'P0_BLOCKING' ? 'error' : r.severity === 'P1_WARNING' ? 'warning' : 'note'
                }
              }))
            }
          },
          results: report.files.flatMap(f =>
            f.violations.map(v => ({
              ruleId: v.ruleId,
              message: { text: v.message },
              locations: [
                {
                  physicalLocation: {
                    artifactLocation: { uri: v.fileName },
                    region: { startLine: v.line || 1 }
                  }
                }
              ],
              level: v.severity === 'P0_BLOCKING' ? 'error' : 'warning'
            }))
          )
        }
      ]
    };
    return JSON.stringify(sarif, null, 2);
  }

  generateGitLabCodeQualityJson(report: AuditReport): string {
    const codeQuality = report.files.flatMap(f =>
      f.violations.map(v => ({
        description: `[${v.ruleId}] ${v.message}`,
        check_name: v.ruleId,
        fingerprint: `${v.fileName}:${v.line || 1}:${v.ruleId}`,
        severity: v.severity === 'P0_BLOCKING' ? 'blocker' : v.severity === 'P1_WARNING' ? 'major' : 'minor',
        location: {
          path: v.fileName,
          lines: {
            begin: v.line || 1
          }
        }
      }))
    );
    return JSON.stringify(codeQuality, null, 2);
  }

  generateBitbucketCodeInsightsJson(report: AuditReport): string {
    const insights = {
      title: 'Bend DevOps Guardian Audit Report',
      details: `Compliance Score: ${report.score}/100. Violations: ${report.totalViolations} (P0: ${report.p0Count}, P1: ${report.p1Count}).`,
      report_type: 'SECURITY',
      reporter: 'Bend DevOps Quality Gate',
      result: report.isApproved ? 'PASSED' : 'FAILED',
      data: [
        { title: 'Score', type: 'NUMBER', value: report.score },
        { title: 'Status', type: 'TEXT', value: report.isApproved ? 'APPROVED' : 'BLOCKED' },
        { title: 'Total Violations', type: 'NUMBER', value: report.totalViolations },
        { title: 'Active Suppressions', type: 'NUMBER', value: report.activeSuppressionsCount }
      ]
    };
    return JSON.stringify(insights, null, 2);
  }

  generateGitHubMarkdownSummary(report: AuditReport, repo: string, prNumber: string): string {
    const statusIcon = report.isApproved ? '✅' : '❌';
    const statusText = report.isApproved ? 'APPROVED' : 'BLOCKED';

    let md = `## ${statusIcon} Bend DevOps Guardian Quality Gate: ${statusText}\n\n`;
    md += `**Repository**: \`${repo}\` | **Pull Request**: \`#${prNumber}\`\n\n`;
    md += `| Compliance Score | Decision | Total Violations | Blocking (P0) | Warnings (P1) | Suppressions |\n`;
    md += `| :---: | :---: | :---: | :---: | :---: | :---: |\n`;
    md += `| **${report.score}/100** | **${statusText}** | **${report.totalViolations}** | **${report.p0Count}** | **${report.p1Count}** | **${report.activeSuppressionsCount}** |\n\n`;

    if (report.totalViolations === 0) {
      md += `✨ **Zero infractions detected!** Code adheres 100% to architecture and engineering standards.\n`;
    } else {
      md += `### ⚠️ Detected Violations\n\n`;
      md += `| Severity | Rule ID | File & Line | Violation Message |\n`;
      md += `| :---: | :---: | :--- | :--- |\n`;
      report.files.forEach(f => {
        f.violations.forEach(v => {
          const sevBadge = v.severity === 'P0_BLOCKING' ? '🔴 **P0 BLOCKING**' : '🟡 **P1 WARNING**';
          const lineStr = v.line ? `:${v.line}` : '';
          md += `| ${sevBadge} | \`${v.ruleId}\` | \`${v.fileName}${lineStr}\` | ${v.message} |\n`;
        });
      });
    }

    return md;
  }
}
