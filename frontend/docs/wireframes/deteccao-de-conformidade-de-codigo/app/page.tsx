'use client'

import { useState } from 'react'
import {
  FileText,
  AlertCircle,
  CheckCircle,
  Settings,
  BarChart3,
  Code2,
  GitBranch,
  GitPullRequest,
  ChevronDown,
  Play,
  Search,
  Filter,
  History,
  Download,
  MoreHorizontal,
  GitCompare,
  Users,
  Braces,
  UserRound,
} from 'lucide-react'

export default function Page() {
  const [activeTab, setActiveTab] = useState('dashboard')

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Header */}
      <header className="border-b border-border bg-card sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Code2 className="w-6 h-6 text-primary" />
            <h1 className="text-xl font-bold">CodeConform</h1>
          </div>
          <div className="flex items-center gap-4">
            <button className="flex items-center gap-2 px-3 py-2 rounded-md bg-muted hover:bg-muted/80 transition-colors">
              <GitBranch className="w-4 h-4" />
              <span className="text-sm">Repositório</span>
            </button>
            <button className="w-8 h-8 rounded-full bg-muted hover:bg-muted/80 flex items-center justify-center">
              <Settings className="w-4 h-4" />
            </button>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <div className="border-b border-border bg-card/50 sticky top-16 z-40">
        <div className="max-w-7xl mx-auto px-6">
          <nav className="flex gap-8">
            {[
              { id: 'dashboard', label: 'Dashboard', icon: BarChart3 },
              { id: 'analyze', label: 'Analisar MR/PR', icon: GitPullRequest },
              { id: 'results', label: 'Resultados', icon: AlertCircle },
              { id: 'history', label: 'Histórico', icon: History },
              { id: 'rules', label: 'Regras', icon: Settings },
            ].map((tab) => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-4 py-4 border-b-2 transition-colors ${
                    activeTab === tab.id
                      ? 'border-primary text-primary'
                      : 'border-transparent text-muted-foreground hover:text-foreground'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span className="text-sm font-medium">{tab.label}</span>
                </button>
              )
            })}
          </nav>
        </div>
      </div>

      {/* Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Dashboard Tab */}
        {activeTab === 'dashboard' && (
          <div className="space-y-8">
            {/* Stats Grid */}
            <div className="grid grid-cols-4 gap-4">
              {[
                { label: 'MRs/PRs Analisados', value: '24', color: 'bg-blue-50 dark:bg-blue-950' },
                { label: 'Não Conformidades', value: '142', color: 'bg-red-50 dark:bg-red-950' },
                { label: 'Taxa de Conformidade', value: '88%', color: 'bg-green-50 dark:bg-green-950' },
                { label: 'Padrões Monitorados', value: '12', color: 'bg-purple-50 dark:bg-purple-950' },
              ].map((stat, i) => (
                <div key={i} className={`${stat.color} rounded-lg p-6 border border-border`}>
                  <p className="text-sm text-muted-foreground mb-2">{stat.label}</p>
                  <p className="text-3xl font-bold">{stat.value}</p>
                </div>
              ))}
            </div>

            {/* Recent Analyses */}
            <div className="border border-border rounded-lg p-6 bg-card">
              <h2 className="text-lg font-semibold mb-4">Análises Recentes</h2>
              <div className="space-y-3">
                {[
                  { file: '!142 · Refatora parser', time: '2 horas atrás · Ana Souza', issues: 5, status: 'warning' },
                  { file: '#87 · Atualiza pagamentos', time: '4 horas atrás · Bruno Lima', issues: 2, status: 'success' },
                  { file: '!31 · Corrige lexer', time: '1 dia atrás · Carla Mendes', issues: 8, status: 'error' },
                ].map((item, i) => (
                  <div
                    key={i}
                    className="flex items-center justify-between p-3 rounded-md bg-muted/30 hover:bg-muted/50 cursor-pointer transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <FileText className="w-4 h-4 text-muted-foreground" />
                      <div>
                        <p className="text-sm font-medium">{item.file}</p>
                        <p className="text-xs text-muted-foreground">{item.time}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      {item.status === 'success' && <CheckCircle className="w-4 h-4 text-green-600" />}
                      {item.status === 'warning' && <AlertCircle className="w-4 h-4 text-yellow-600" />}
                      {item.status === 'error' && <AlertCircle className="w-4 h-4 text-red-600" />}
                      <span className="text-sm font-medium">{item.issues} problemas</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Analyze Tab */}
        {activeTab === 'analyze' && (
          <div className="space-y-6">
            {/* Merge Request / Pull Request */}
            <div className="border border-border rounded-lg p-6 bg-card">
              <div className="flex items-start gap-4">
                <div className="w-11 h-11 rounded-lg bg-primary/10 text-primary flex items-center justify-center shrink-0">
                  <GitPullRequest className="w-6 h-6" />
                </div>
                <div className="flex-1">
                  <h2 className="text-lg font-semibold">Nova análise de Merge Request / Pull Request</h2>
                  <p className="text-sm text-muted-foreground mt-1">A análise compara a branch de origem com a branch de destino e verifica apenas as alterações do MR/PR.</p>
                  <div className="grid grid-cols-3 gap-4 mt-5">
                    <label className="space-y-2">
                      <span className="text-sm font-medium">Repositório</span>
                      <select className="w-full border border-border rounded-lg bg-background px-3 py-2 text-sm" defaultValue="core-engine">
                        <option value="core-engine">acme/core-engine</option>
                        <option value="billing-service">acme/billing-service</option>
                      </select>
                    </label>
                    <label className="space-y-2">
                      <span className="text-sm font-medium">MR/PR</span>
                      <select className="w-full border border-border rounded-lg bg-background px-3 py-2 text-sm" defaultValue="142">
                        <option value="142">#142 — Refatora parser</option>
                        <option value="139">#139 — Atualiza validação</option>
                      </select>
                    </label>
                    <label className="space-y-2">
                      <span className="text-sm font-medium">Destino</span>
                      <select className="w-full border border-border rounded-lg bg-background px-3 py-2 text-sm" defaultValue="main">
                        <option value="main">main</option>
                        <option value="develop">develop</option>
                      </select>
                    </label>
                  </div>
                </div>
              </div>
            </div>

            <div className="border border-border rounded-lg bg-card overflow-hidden">
              <div className="px-5 py-4 border-b border-border flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <GitCompare className="w-5 h-5 text-primary" />
                    <h3 className="font-semibold">Trecho alterado no MR/PR</h3>
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">src/parser.cpp · linhas 118–126 · autoria identificada por trecho</p>
                </div>
                <span className="text-xs font-medium px-2.5 py-1 rounded-full bg-primary/10 text-primary">Diff + AST</span>
              </div>
              <div className="grid grid-cols-2 divide-x divide-border overflow-x-auto">
                <div className="min-w-0">
                  <div className="px-4 py-2 bg-muted/40 text-xs font-medium text-muted-foreground flex items-center justify-between">
                    <span>Versão base · main</span><span>AST anterior</span>
                  </div>
                  <pre className="p-4 text-xs leading-6 font-mono text-muted-foreground bg-background overflow-x-auto"><code>{`116  void Parser::parse(Token token) {
117    if (token.isValid()) {
118      process(token);
119    }
120  }`}</code></pre>
                </div>
                <div className="min-w-0">
                  <div className="px-4 py-2 bg-primary/5 text-xs font-medium text-primary flex items-center justify-between">
                    <span>Proposta · MR !142</span><span>AST atual</span>
                  </div>
                  <pre className="p-4 text-xs leading-6 font-mono bg-primary/5 overflow-x-auto"><code>{`116  void Parser::parse(Token token) {
117    if (token.isValid()) {
118 +    const auto owner = getOwner(token);
119 +    process(token, owner);
120    }
121  }`}</code></pre>
                </div>
              </div>
              <div className="px-5 py-3 border-t border-border flex flex-wrap items-center gap-5 text-xs text-muted-foreground">
                <span className="inline-flex items-center gap-1.5"><Users className="w-3.5 h-3.5 text-primary" /> Trecho alterado por <strong className="text-foreground">Ana Souza</strong></span>
                <span className="inline-flex items-center gap-1.5"><Braces className="w-3.5 h-3.5 text-primary" /> Nó AST: FunctionDecl → CallExpr</span>
                <span className="inline-flex items-center gap-1.5"><GitCompare className="w-3.5 h-3.5 text-primary" /> Comparação lado a lado</span>
              </div>
            </div>

            {/* Analysis Options */}
            <div className="grid grid-cols-2 gap-6">
              <div className="border border-border rounded-lg p-6 bg-card">
                <h3 className="font-semibold mb-4">Padrões a Verificar</h3>
                <div className="space-y-3">
                  {[
                    { name: 'Nomenclatura', enabled: true },
                    { name: 'Indentação', enabled: true },
                    { name: 'Paradigma OOP', enabled: true },
                    { name: 'Gestão de Memória', enabled: true },
                    { name: 'Tratamento de Erros', enabled: false },
                  ].map((pattern, i) => (
                    <label key={i} className="flex items-center gap-3 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={pattern.enabled}
                        className="w-4 h-4 rounded border-border"
                        readOnly
                      />
                      <span className="text-sm">{pattern.name}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div className="border border-border rounded-lg p-6 bg-card">
                <h3 className="font-semibold mb-4">Linguagens</h3>
                <div className="space-y-3">
                  {[
                    { name: 'C', enabled: true },
                    { name: 'C++', enabled: true },
                    { name: 'C#', enabled: true },
                  ].map((lang, i) => (
                    <label key={i} className="flex items-center gap-3 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={lang.enabled}
                        className="w-4 h-4 rounded border-border"
                        readOnly
                      />
                      <span className="text-sm">{lang.name}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>

            {/* Action Button */}
            <div className="flex gap-3">
              <button className="flex items-center gap-2 px-6 py-3 bg-primary text-primary-foreground rounded-lg hover:opacity-90 transition-opacity font-medium">
                <Play className="w-4 h-4" />
                Analisar MR/PR
              </button>
              <button className="px-6 py-3 border border-border rounded-lg hover:bg-muted transition-colors font-medium">
                Cancelar
              </button>
            </div>
          </div>
        )}

        {/* Results Tab */}
        {activeTab === 'results' && (
          <div className="space-y-6">
            {/* Filters */}
            <div className="flex gap-3">
              <div className="flex-1 relative">
                <Search className="w-4 h-4 absolute left-3 top-3 text-muted-foreground" />
                <input
                  type="text"
                  placeholder="Buscar problemas..."
                  className="w-full pl-10 pr-4 py-2 border border-border rounded-lg bg-card focus:outline-none focus:ring-2 focus:ring-primary/50"
                />
              </div>
              <button className="flex items-center gap-2 px-4 py-2 border border-border rounded-lg hover:bg-muted transition-colors">
                <Filter className="w-4 h-4" />
                Filtrar
              </button>
            </div>

            {/* Results List */}
            <div className="space-y-4">
              {[
                {
                  file: 'main.cpp',
                  line: 42,
                  type: 'Nomenclatura',
                  severity: 'warning',
                  message: 'Variável "x" não segue padrão camelCase',
                  author: 'Ana Souza',
                  ast: 'Nó Identifier alterado',
                },
                {
                  file: 'main.cpp',
                  line: 56,
                  type: 'Indentação',
                  severity: 'info',
                  message: 'Indentação inconsistente com o padrão do projeto',
                  author: 'Bruno Lima',
                  ast: 'Nó CompoundStmt preservado',
                },
                {
                  file: 'parser.c',
                  line: 103,
                  type: 'Gestão de Memória',
                  severity: 'error',
                  message: 'malloc() sem correspondente free()',
                  author: 'Carla Mendes',
                  ast: 'CallExpr adicionada sem par de liberação',
                },
              ].map((result, i) => {
                const severityColors = {
                  error: 'bg-red-50 dark:bg-red-950 border-red-200 dark:border-red-800',
                  warning: 'bg-yellow-50 dark:bg-yellow-950 border-yellow-200 dark:border-yellow-800',
                  info: 'bg-blue-50 dark:bg-blue-950 border-blue-200 dark:border-blue-800',
                }
                const severityIcons = {
                  error: 'text-red-600',
                  warning: 'text-yellow-600',
                  info: 'text-blue-600',
                }
                return (
                  <div
                    key={i}
                    className={`border rounded-lg p-4 ${severityColors[result.severity as keyof typeof severityColors]}`}
                  >
                    <div className="flex items-start gap-3">
                      <AlertCircle
                        className={`w-5 h-5 mt-0.5 flex-shrink-0 ${severityIcons[result.severity as keyof typeof severityIcons]}`}
                      />
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center gap-2">
                            <span className="font-mono text-sm font-medium">{result.file}</span>
                            <span className="text-xs text-muted-foreground">linha {result.line}</span>
                          </div>
                          <span className="text-xs font-medium px-2 py-1 rounded bg-background/50">{result.type}</span>
                        </div>
                        <p className="text-sm">{result.message}</p>
                        <div className="flex flex-wrap gap-x-5 gap-y-2 mt-3 pt-3 border-t border-current/10 text-xs text-muted-foreground">
                          <span className="inline-flex items-center gap-1.5"><UserRound className="w-3.5 h-3.5" /> Trecho por <strong className="text-foreground">{result.author}</strong></span>
                          <span className="inline-flex items-center gap-1.5"><Braces className="w-3.5 h-3.5" /> AST: {result.ast}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        )}

        {/* History Tab */}
        {activeTab === 'history' && (
          <div className="space-y-6">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-sm font-medium text-primary mb-1">Rastreabilidade</p>
                <h2 className="text-2xl font-bold tracking-tight">Histórico de análises</h2>
                <p className="text-sm text-muted-foreground mt-1">Consulte execuções anteriores, compare resultados e baixe relatórios.</p>
              </div>
              <button className="flex items-center gap-2 px-4 py-2 border border-border rounded-lg hover:bg-muted transition-colors">
                <Download className="w-4 h-4" />
                Exportar histórico
              </button>
            </div>

            <div className="grid grid-cols-3 gap-4">
              {[
                { label: 'MRs/PRs analisados', value: '24' },
                { label: 'Arquivos analisados', value: '186' },
                { label: 'Última execução', value: 'Hoje, 14:32' },
              ].map((item) => (
                <div key={item.label} className="border border-border rounded-lg bg-card p-5">
                  <p className="text-sm text-muted-foreground">{item.label}</p>
                  <p className="text-xl font-bold mt-2">{item.value}</p>
                </div>
              ))}
            </div>

            <div className="border border-border rounded-lg bg-card overflow-hidden">
              <div className="px-5 py-4 border-b border-border flex items-center justify-between">
                <h3 className="font-semibold">Execuções anteriores</h3>
                <div className="flex items-center gap-2">
                  <select className="text-sm border border-border rounded-md bg-background px-3 py-2" defaultValue="all" aria-label="Filtrar período">
                    <option value="all">Todos os períodos</option>
                    <option value="today">Hoje</option>
                    <option value="week">Últimos 7 dias</option>
                    <option value="month">Este mês</option>
                  </select>
                  <button className="p-2 rounded-md hover:bg-muted" aria-label="Mais opções">
                    <MoreHorizontal className="w-4 h-4" />
                  </button>
                </div>
              </div>
              <div className="divide-y divide-border">
                {[
                  { date: 'Hoje, 14:32', project: 'acme/core-engine · !142', files: 'Refatora parser → main', issues: '5 problemas', status: 'Concluída', duration: '32s' },
                  { date: 'Hoje, 09:18', project: 'acme/billing-service · #87', files: 'Atualiza pagamentos → main', issues: '2 problemas', status: 'Concluída', duration: '1m 08s' },
                  { date: 'Ontem, 17:45', project: 'acme/legacy-parser · !31', files: 'Corrige lexer → develop', issues: '8 problemas', status: 'Concluída', duration: '18s' },
                  { date: '12 jun, 11:06', project: 'acme/desktop-client · #64', files: 'Atualiza cliente → main', issues: '0 problemas', status: 'Conformidade total', duration: '2m 14s' },
                ].map((run) => (
                  <div key={`${run.date}-${run.project}`} className="px-5 py-4 flex items-center gap-4 hover:bg-muted/30 transition-colors">
                    <div className="w-10 h-10 rounded-lg bg-primary/10 text-primary flex items-center justify-center shrink-0">
                      <History className="w-5 h-5" />
                    </div>
                    <div className="min-w-0 flex-1 grid grid-cols-[1.1fr_1.4fr_1fr_0.8fr] gap-4 items-center">
                      <div>
                        <p className="text-sm font-medium">{run.date}</p>
                        <p className="text-xs text-muted-foreground mt-1">Duração: {run.duration}</p>
                      </div>
                      <div className="min-w-0">
                        <p className="text-sm font-mono font-medium truncate">{run.project}</p>
                        <p className="text-xs text-muted-foreground truncate mt-1">{run.files}</p>
                      </div>
                      <div>
                        <p className="text-sm font-medium">{run.issues}</p>
                        <span className="text-xs text-green-700 dark:text-green-300">{run.status}</span>
                      </div>
                      <div className="flex justify-end">
                        <button className="text-sm text-primary hover:underline">Ver detalhes</button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              <div className="px-5 py-4 border-t border-border flex items-center justify-between text-sm text-muted-foreground">
                <span>Mostrando 4 de 24 análises</span>
                <div className="flex gap-2">
                  <button className="px-3 py-1.5 border border-border rounded-md hover:bg-muted">Anterior</button>
                  <button className="px-3 py-1.5 border border-border rounded-md hover:bg-muted">Próxima</button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Rules Tab */}
        {activeTab === 'rules' && (
          <div className="space-y-6">
            {/* Add Rule Button */}
            <button className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:opacity-90 transition-opacity font-medium">
              <FileText className="w-4 h-4" />
              Nova Regra
            </button>

            {/* Rules List */}
            <div className="space-y-3">
              {[
                {
                  name: 'Nomenclatura em camelCase',
                  category: 'Padrão',
                  status: 'active',
                  languages: ['C', 'C++', 'C#'],
                },
                {
                  name: 'Indentação com espaços (2)',
                  category: 'Formatação',
                  status: 'active',
                  languages: ['C', 'C++', 'C#'],
                },
                {
                  name: 'Classes com PascalCase',
                  category: 'OOP',
                  status: 'active',
                  languages: ['C++', 'C#'],
                },
                {
                  name: 'Verificação de memória',
                  category: 'Segurança',
                  status: 'inactive',
                  languages: ['C', 'C++'],
                },
              ].map((rule, i) => (
                <div
                  key={i}
                  className="border border-border rounded-lg p-4 bg-card hover:bg-muted/30 transition-colors cursor-pointer"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <h3 className="font-medium mb-2">{rule.name}</h3>
                      <div className="flex items-center gap-3">
                        <span className="text-xs px-2 py-1 rounded-full bg-primary/10 text-primary">
                          {rule.category}
                        </span>
                        <span className="text-xs text-muted-foreground">
                          {rule.languages.join(', ')}
                        </span>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <span
                        className={`text-xs font-medium px-3 py-1 rounded-full ${
                          rule.status === 'active'
                            ? 'bg-green-100 dark:bg-green-950 text-green-700 dark:text-green-300'
                            : 'bg-muted text-muted-foreground'
                        }`}
                      >
                        {rule.status === 'active' ? 'Ativo' : 'Inativo'}
                      </span>
                      <ChevronDown className="w-4 h-4 text-muted-foreground" />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
