#!/usr/bin/env python3
"""
Playwright Screen Capture & E2E Visual Suite
Project: Bend DevOps Guardian (CodeConform Dashboard)

This script launches a headless Chromium instance via Playwright, navigates through
all interactive views, executes audit actions across multiple presets (clean, non-compliant,
suppressed), triggers modals and filters, and captures high-resolution screenshots of each
system state, saving them into `tests/screenshots/`.
"""

import os
import sys
import time
import socket
import threading
import http.server
import socketserver
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from scripts.guardian_server import GuardianRequestHandler

DIST_DIR = BASE_DIR / "frontend" / "dist" / "frontend" / "browser"
SCREENSHOTS_DIR = BASE_DIR / "tests" / "screenshots"

def get_free_port():
    """Finds an available TCP port on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

class StaticHttpServer:
    def __init__(self, directory, port):
        self.directory = directory
        self.port = port
        self.server = None
        self.thread = None

    def start(self):
        GuardianRequestHandler.is_mock_mode = False
        GuardianRequestHandler.mock_scenario = None
        self.server = socketserver.TCPServer(('127.0.0.1', self.port), GuardianRequestHandler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        time.sleep(0.5)

    def stop(self):
        if self.server:
            self.server.shutdown()
            self.server.server_close()

def capture_all_screens():
    if not DIST_DIR.exists():
        print(f"Error: Dist directory does not exist at {DIST_DIR}. Please run 'npm run build' first.")
        sys.exit(1)

    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    port = get_free_port()
    base_url = f"http://127.0.0.1:{port}"

    print(f"🌐 Starting local server at {base_url} serving {DIST_DIR}...")
    server = StaticHttpServer(DIST_DIR, port)
    server.start()

    captured_screens = []

    try:
        with sync_playwright() as p:
            print("🚀 Launching Chromium with Playwright...")
            browser = p.chromium.launch(headless=True)
            
            # --- 1. DESKTOP VIEWPORT (1440x900, High DPI) ---
            context = browser.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=2)
            page = context.new_page()

            print("📍 Navigating to application root...")
            page.goto(base_url, wait_until="networkidle")
            page.wait_for_selector("header")
            time.sleep(0.5)

            # 1. Initial Dashboard
            print("📸 [1/20] Capturing Dashboard (Initial State)...")
            page.locator("nav button:has-text('Dashboard')").click()
            time.sleep(0.3)
            p1 = SCREENSHOTS_DIR / "01_dashboard_initial.png"
            page.screenshot(path=str(p1), full_page=True)
            captured_screens.append({
                "file": "01_dashboard_initial.png",
                "title": "Dashboard Executivo (Inicial)",
                "desc": "Visão geral de métricas KPI, perfis de arquitetura suportados e card de veredito do último arquivo avaliado."
            })

            # 2. Live Auditor - Branch Analysis (Primary Workflow)
            print("📸 [2/20] Capturing Live Code Auditor (Branch Analysis Workflow)...")
            page.locator("nav button:has-text('Live Code & Diff Auditor')").click()
            time.sleep(0.3)
            page.locator("button:has-text('Branch Analysis')").first.click()
            time.sleep(0.3)
            p2 = SCREENSHOTS_DIR / "02_live_auditor_clean_preset.png"
            page.screenshot(path=str(p2), full_page=True)
            captured_screens.append({
                "file": "02_live_auditor_clean_preset.png",
                "title": "Live Code Auditor (Branch Analysis Workflow)",
                "desc": "Fluxo primário de auditoria por branch comparando todas as alterações com as regras de arquitetura."
            })

            # 3. Execute Audit on Branch -> Audit Results Approved
            print("📸 [3/20] Executing Audit on Branch -> Audit Results...")
            page.locator("button:has-text('Analyze Branch')").first.click()
            time.sleep(0.3)
            page.locator("nav button:has-text('Audit Results')").click()
            time.sleep(0.4)
            p3 = SCREENSHOTS_DIR / "03_audit_results_approved_100.png"
            page.screenshot(path=str(p3), full_page=True)
            captured_screens.append({
                "file": "03_audit_results_approved_100.png",
                "title": "Audit Results (Relatório Consolidado da Auditoria)",
                "desc": "Tela de resultados com veredito consolidado da branch e detalhamento de conformidade arquitetural."
            })

            # 4. Live Auditor - Review Specific File (Before / After Diff)
            print("📸 [4/20] Capturing Live Code Auditor (File Review Before/After Diff)...")
            page.locator("nav button:has-text('Live Code & Diff Auditor')").click()
            time.sleep(0.3)
            page.locator("button:has-text('OrderInvoice.cs')").first.click()
            time.sleep(0.3)
            p4 = SCREENSHOTS_DIR / "04_live_auditor_violation_preset.png"
            page.screenshot(path=str(p4), full_page=True)
            captured_screens.append({
                "file": "04_live_auditor_violation_preset.png",
                "title": "Live Code Auditor (Revisão de Arquivo com Diff Before & After)",
                "desc": "Inspeção detalhada de arquivo alterado na branch com comparativo Before (Original) e After (Guardian-Corrected)."
            })

            # 5. Execute Audit on Violation Code -> Audit Results Blocked
            print("📸 [5/20] Executing Audit on Violation Code -> Audit Results Blocked...")
            page.locator("button:has-text('Analyze Branch')").first.click()
            time.sleep(0.3)
            page.locator("nav button:has-text('Audit Results')").click()
            time.sleep(0.4)
            p5 = SCREENSHOTS_DIR / "05_audit_results_blocked_violations.png"
            page.screenshot(path=str(p5), full_page=True)
            captured_screens.append({
                "file": "05_audit_results_blocked_violations.png",
                "title": "Audit Results (Quality Gate BLOCKED - Detalhamento de Violações)",
                "desc": "Diagnóstico detalhado com infrações P0/P1, linha de código, snippets destacados e instruções de remediação."
            })

            # 6. Audit Results Filtered P0
            print("📸 [6/20] Capturing Audit Results Filtered by P0 Severity...")
            page.locator("select").last.select_option("P0_BLOCKING")
            time.sleep(0.3)
            p6 = SCREENSHOTS_DIR / "06_audit_results_filtered_p0.png"
            page.screenshot(path=str(p6), full_page=True)
            captured_screens.append({
                "file": "06_audit_results_filtered_p0.png",
                "title": "Audit Results (Filtro Severidade P0 Blocking)",
                "desc": "Filtro dinâmico isolando apenas os itens impeditivos de build/merge na branch protegida."
            })
            # Reset filter back to all
            page.locator("select").last.select_option("all")
            time.sleep(0.2)

            # 7. Live Auditor - Single File Review (Pragma Suppression Preset)
            print("📸 [7/20] Capturing Live Code Auditor (Single File Review Mode)...")
            page.locator("nav button:has-text('Live Code & Diff Auditor')").click()
            time.sleep(0.3)
            page.locator("button:has-text('Single File Review')").first.click()
            time.sleep(0.3)
            page.locator("[data-testid='file-preset-select']").select_option(index=3)
            time.sleep(0.3)
            p7 = SCREENSHOTS_DIR / "07_live_auditor_suppression_preset.png"
            page.screenshot(path=str(p7), full_page=True)
            captured_screens.append({
                "file": "07_live_auditor_suppression_preset.png",
                "title": "Live Code Auditor (Single File Review - Supressão @guardian-ignore)",
                "desc": "Modo de revisão de arquivo avulso com código Python e pragma inline devidamente justificado."
            })
            page.locator("button:has-text('Analyze')").first.click()
            time.sleep(0.3)

            # 8. Rules Manifests Catalog
            print("📸 [8/20] Capturing Rules Manifests Catalog...")
            page.locator("nav button:has-text('Rules Manifests')").click()
            time.sleep(0.3)
            p8 = SCREENSHOTS_DIR / "08_rules_manifests_catalog.png"
            page.screenshot(path=str(p8), full_page=True)
            captured_screens.append({
                "file": "08_rules_manifests_catalog.png",
                "title": "Rules Manifests Catalog",
                "desc": "Catálogo de 26 regras declarativas com IDs canônicos, penalidades, linguagens suportadas e switches Enforced/Disabled."
            })

            # 9. Rules Search & Filter
            print("📸 [9/20] Capturing Rules Manifests (Search Filter)...")
            search_rules = page.locator("input[placeholder*='Search rules']")
            search_rules.fill("layer")
            time.sleep(0.3)
            p9 = SCREENSHOTS_DIR / "09_rules_manifests_search_filter.png"
            page.screenshot(path=str(p9), full_page=True)
            captured_screens.append({
                "file": "09_rules_manifests_search_filter.png",
                "title": "Rules Manifests (Busca e Filtragem por Termo)",
                "desc": "Busca instantânea de regras arquiteturais filtradas pela palavra-chave 'layer'."
            })
            search_rules.fill("")
            time.sleep(0.2)

            # 10. Layer Taxonomy Explorer
            print("📸 [10/20] Capturing Layer Taxonomy Explorer...")
            page.locator("nav button:has-text('Layer Taxonomy')").click()
            time.sleep(0.3)
            p10 = SCREENSHOTS_DIR / "10_layer_taxonomy_explorer.png"
            page.screenshot(path=str(p10), full_page=True)
            captured_screens.append({
                "file": "10_layer_taxonomy_explorer.png",
                "title": "Layer Vocabulary & Taxonomy Explorer",
                "desc": "Dicionário de camadas (Domain, Application, Infrastructure, Presentation) com keywords canônicas e fronteiras proibidas."
            })

            # 11. Layer Taxonomy Search Filter
            print("📸 [11/20] Capturing Layer Taxonomy (Search Filter)...")
            vocab_search = page.locator("input[placeholder*='Search keywords']")
            vocab_search.fill("database")
            time.sleep(0.3)
            p11 = SCREENSHOTS_DIR / "11_layer_taxonomy_search.png"
            page.screenshot(path=str(p11), full_page=True)
            captured_screens.append({
                "file": "11_layer_taxonomy_search.png",
                "title": "Layer Taxonomy (Busca de Vocabulário)",
                "desc": "Busca refinada por termos como 'database' para validação de regras de persistência."
            })
            vocab_search.fill("")
            time.sleep(0.2)

            # 12. VCS & Webhook Simulator (Initial)
            print("📸 [12/20] Capturing VCS & Webhook Simulator...")
            page.locator("nav button:has-text('VCS & Webhook Simulator')").click()
            time.sleep(0.3)
            p12 = SCREENSHOTS_DIR / "12_vcs_webhook_simulator.png"
            page.screenshot(path=str(p12), full_page=True)
            captured_screens.append({
                "file": "12_vcs_webhook_simulator.png",
                "title": "VCS & Webhook Simulator (Configuração Inicial)",
                "desc": "Configuração de eventos de webhook para GitHub, GitLab e Bitbucket, com matriz de políticas de branch ativas."
            })

            # 13. VCS Simulator (Dispatched Event)
            print("📸 [13/20] Capturing VCS Simulator (Dispatched Webhook)...")
            page.locator("button:has-text('Dispatch Webhook Event')").click()
            time.sleep(0.3)
            p13 = SCREENSHOTS_DIR / "13_vcs_webhook_dispatched.png"
            page.screenshot(path=str(p13), full_page=True)
            captured_screens.append({
                "file": "13_vcs_webhook_dispatched.png",
                "title": "VCS Simulator (Evento Disparado & Processado)",
                "desc": "Saída da ingestão canônica do webhook com validação de gating policy para branch main."
            })

            # 14. Session History & Telemetry (Populated)
            print("📸 [14/20] Capturing Session History & Telemetry...")
            page.locator("nav button:has-text('Session History')").click()
            time.sleep(0.3)
            p14 = SCREENSHOTS_DIR / "14_session_history_telemetry.png"
            page.screenshot(path=str(p14), full_page=True)
            captured_screens.append({
                "file": "14_session_history_telemetry.png",
                "title": "Session History & Telemetria em Tempo Real",
                "desc": "Registro histórico determinístico de todas as auditorias executadas na sessão com pontuações e status."
            })

            # 15. Dashboard after Audits (Populated KPIs)
            print("📸 [15/20] Capturing Dashboard (Populated KPIs & Telemetry)...")
            page.locator("nav button:has-text('Dashboard')").click()
            time.sleep(0.3)
            p15 = SCREENSHOTS_DIR / "15_dashboard_with_telemetry.png"
            page.screenshot(path=str(p15), full_page=True)
            captured_screens.append({
                "file": "15_dashboard_with_telemetry.png",
                "title": "Dashboard Atualizado com Telemetria",
                "desc": "KPIs consolidados da sessão: total de auditorias, violações bloqueadas, média de conformidade e status do último arquivo."
            })

            # 16. Export Modal - SARIF v2.1.0
            print("📸 [16/20] Capturing SARIF Export Modal...")
            page.locator("header button:has-text('SARIF Export')").click()
            time.sleep(0.4)
            p16 = SCREENSHOTS_DIR / "16_modal_export_sarif.png"
            page.screenshot(path=str(p16), full_page=True)
            captured_screens.append({
                "file": "16_modal_export_sarif.png",
                "title": "Modal de Exportação SARIF v2.1.0 (OASIS Standard)",
                "desc": "Relatório estruturado em formato SARIF para integração com GitHub Security Code Scanning e SonarQube."
            })
            page.locator("button:has-text('Close')").click()
            time.sleep(0.3)

            # 17. Export Modal - Markdown PR Summary
            print("📸 [17/20] Capturing Markdown PR Summary Modal...")
            page.locator("nav button:has-text('Audit Results')").click()
            time.sleep(0.3)
            page.locator("button:has-text('Markdown PR Summary')").click()
            time.sleep(0.4)
            p17 = SCREENSHOTS_DIR / "17_modal_export_markdown_pr.png"
            page.screenshot(path=str(p17), full_page=True)
            captured_screens.append({
                "file": "17_modal_export_markdown_pr.png",
                "title": "Modal de Exportação Markdown PR Summary",
                "desc": "Resumo formatado em Markdown para publicação automática de comentários em Pull Requests e Merge Requests."
            })
            page.locator("button:has-text('Close')").click()
            time.sleep(0.3)

            context.close()

            # --- 2. MOBILE VIEWPORT (390x844 - iPhone / Mobile Responsiveness) ---
            print("📸 [18/20] Capturing Mobile Responsive Dashboard...")
            mobile_context = browser.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, device_scale_factor=2)
            mobile_page = mobile_context.new_page()
            mobile_page.goto(base_url, wait_until="networkidle")
            time.sleep(0.5)
            p18 = SCREENSHOTS_DIR / "18_mobile_dashboard.png"
            mobile_page.screenshot(path=str(p18), full_page=True)
            captured_screens.append({
                "file": "18_mobile_dashboard.png",
                "title": "Responsividade Mobile (Dashboard)",
                "desc": "Layout responsivo adaptado para dispositivos móveis com cartões empilhados e navegação touch fluida."
            })

            print("📸 [19/20] Capturing Mobile Responsive Live Auditor...")
            mobile_page.locator("nav button:has-text('Live Code & Diff Auditor')").click(force=True)
            time.sleep(0.3)
            p19 = SCREENSHOTS_DIR / "19_mobile_live_auditor.png"
            mobile_page.screenshot(path=str(p19), full_page=True)
            captured_screens.append({
                "file": "19_mobile_live_auditor.png",
                "title": "Responsividade Mobile (Live Code Auditor)",
                "desc": "Editor de código e controles de auditoria ajustados para telas compactas."
            })

            print("📸 [20/20] Capturing Mobile Responsive Audit Results...")
            mobile_page.locator("nav button:has-text('Audit Results')").click(force=True)
            time.sleep(0.3)
            p20 = SCREENSHOTS_DIR / "20_mobile_audit_results.png"
            mobile_page.screenshot(path=str(p20), full_page=True)
            captured_screens.append({
                "file": "20_mobile_audit_results.png",
                "title": "Responsividade Mobile (Audit Results)",
                "desc": "Cartões de violação e remediação exibidos de forma clara em viewport vertical móvel."
            })

            mobile_context.close()
            browser.close()
            print("✅ All 20 screenshots captured successfully!")

    finally:
        server.stop()
        print("🛑 Local server stopped.")

    # Generate README catalog in tests/screenshots/
    readme_content = "# Catálogo de Telas e Evidências Visuais do Sistema (Playwright E2E)\n\n"
    readme_content += "**Projeto**: Bend DevOps Guardian (CodeConform Dashboard)\n"
    readme_content += f"**Data de Captura**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
    readme_content += f"**Total de Telas Capturadas**: {len(captured_screens)}\n"
    readme_content += "**Ferramenta de Automação**: Playwright Chromium (Desktop 1440x900 @2x + Mobile 390x844 @2x)\n\n"
    readme_content += "---\n\n"
    readme_content += "## Índice de Telas Capturadas\n\n"

    for idx, screen in enumerate(captured_screens, 1):
        slug = f"{idx}-{screen['title'].lower().replace(' ', '-').replace('(', '').replace(')', '').replace('/', '').replace('%', '').replace('@', '').replace(':', '')}"
        readme_content += f"- [{idx}. {screen['title']}](#{slug})\n"

    readme_content += "\n---\n\n"

    for idx, screen in enumerate(captured_screens, 1):
        slug = f"{idx}-{screen['title'].lower().replace(' ', '-').replace('(', '').replace(')', '').replace('/', '').replace('%', '').replace('@', '').replace(':', '')}"
        readme_content += f"## {idx}. {screen['title']}\n\n"
        readme_content += f"- **Arquivo**: [`{screen['file']}`]({screen['file']})\n"
        readme_content += f"- **Descrição**: {screen['desc']}\n\n"
        readme_content += f"![{screen['title']}]({screen['file']})\n\n"
        readme_content += "---\n\n"

    readme_path = SCREENSHOTS_DIR / "README.md"
    readme_path.write_text(readme_content, encoding="utf-8")
    print(f"📝 Screenshot documentation catalog saved to {readme_path}")
    return captured_screens

if __name__ == "__main__":
    capture_all_screens()
