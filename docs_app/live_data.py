"""
Live Data Providers for Documentation

These functions inject real-time system data into documentation sections.
Each function takes a config dict and returns a context dict for template rendering.
"""
from django.conf import settings
from django.utils import timezone
from django.db.models import Count, Sum, Max, Min, Q
from scanner.models import Scan, Program, Report
from scanner.services import get_assets_overview, get_technology_breakdown


def get_feature_matrix(config=None):
    """Get live feature matrix data from the scanner app."""
    config = config or {}
    
    # Get current system stats
    total_scans = Scan.objects.count()
    completed_scans = Scan.objects.filter(status=Scan.Status.COMPLETED).count()
    running_scans = Scan.objects.filter(status=Scan.Status.RUNNING).count()
    total_programs = Program.objects.count()
    total_reports = Report.objects.count()
    
    # Feature categories with live status
    features = [
        {
            "category": "Reconnaissance",
            "features": [
                {"name": "Subdomain Enumeration", "status": "live", "tools": "subfinder, assetfinder, chaos, crt.sh"},
                {"name": "DNS Resolution", "status": "live", "tools": "dnsx"},
                {"name": "HTTP Probing", "status": "live", "tools": "httpx (status, title, tech-detect, IP, CNAME)"},
                {"name": "Certificate Transparency", "status": "live", "tools": "crt.sh"},
                {"name": "Chaos Dataset Integration", "status": "live" if settings.CHAOS_API_KEY else "config_required", "tools": "chaos"},
            ]
        },
        {
            "category": "Management & Organization",
            "features": [
                {"name": "Organization Management", "status": "live", "detail": f"{total_programs} organizations configured"},
                {"name": "Scan Scheduling & History", "status": "live", "detail": f"{total_scans} scans tracked"},
                {"name": "Asset Inventory", "status": "live", "detail": "Cross-organization technology tracking"},
                {"name": "Team Collaboration", "status": "planned"},
                {"name": "Role-Based Access Control", "status": "planned"},
            ]
        },
        {
            "category": "Analysis & Reporting",
            "features": [
                {"name": "AI-Generated Reports", "status": "live", "detail": f"{total_reports} reports generated", "types": "Attack Surface, Vulnerability, Tech Exposure, Attack Vector, Custom"},
                {"name": "MCP Integration", "status": "live", "detail": "Model Context Protocol server for AI agents"},
                {"name": "Attack Surface Analysis", "status": "live", "tools": "MCP tools: analyze_attack_surface, search_subdomains"},
                {"name": "Technology Exposure Mapping", "status": "live", "tools": "MCP tool: get_technology_exposure"},
                {"name": "Custom Report Generation", "status": "live", "detail": "Prompt-driven AI analysis"},
            ]
        },
        {
            "category": "Platform & Infrastructure",
            "features": [
                {"name": "Background Job Processing", "status": "live", "detail": "Thread-based async scan execution"},
                {"name": "Live Log Streaming", "status": "live", "detail": "Real-time scan output via polling"},
                {"name": "Data Export", "status": "live", "formats": "JSON, Markdown, CSV"},
                {"name": "Documentation System", "status": "live", "detail": "This /docs module with access control"},
                {"name": "Multi-tenant Support", "status": "planned"},
            ]
        },
        {
            "category": "Security & Compliance",
            "features": [
                {"name": "Authorized Scanning Only", "status": "live", "detail": "Program-based authorization required"},
                {"name": "Scan Cancellation", "status": "live", "detail": "Graceful stop with cleanup"},
                {"name": "Input Validation", "status": "live", "detail": "RFC 1035 domain validation + shell safety"},
                {"name": "Isolated Scan Directories", "status": "live", "detail": "Per-scan UUID directories"},
                {"name": "Audit Logging", "status": "partial", "detail": "Django admin + scan logs"},
            ]
        },
    ]
    
    return {
        "feature_categories": features,
        "stats": {
            "total_scans": total_scans,
            "completed_scans": completed_scans,
            "running_scans": running_scans,
            "total_programs": total_programs,
            "total_reports": total_reports,
        }
    }


def get_architecture_data(config=None):
    """Get live architecture data."""
    config = config or {}
    
    return {
        "components": [
            {
                "name": "Django Web Application",
                "type": "backend",
                "tech": "Django 5.0, Python 3.11+",
                "description": "Main web framework handling HTTP, auth, admin, ORM",
                "connections": ["PostgreSQL/SQLite", "Redis (optional)", "File System"],
            },
            {
                "name": "Scanner Service",
                "type": "service",
                "tech": "Python threading, subprocess",
                "description": "Background scan execution with live log streaming",
                "connections": ["Django ORM", "scanx.sh", "Go tools"],
            },
            {
                "name": "scanx.sh (Bash Recon Script)",
                "type": "external",
                "tech": "Bash, Go binaries",
                "description": "Original reconnaissance engine - source of truth",
                "tools": ["subfinder", "assetfinder", "chaos", "crt.sh", "dnsx", "httpx"],
                "connections": ["File System", "External APIs"],
            },
            {
                "name": "MCP Server",
                "type": "service",
                "tech": "Python MCP SDK, asyncio",
                "description": "Model Context Protocol server for AI agent integration",
                "connections": ["Django ORM", "stdio/HTTP transport"],
            },
            {
                "name": "Database",
                "type": "data",
                "tech": "SQLite (dev) / PostgreSQL (prod)",
                "description": "Scan metadata, programs, reports, documentation",
                "connections": ["Django ORM"],
            },
            {
                "name": "File Storage",
                "type": "data",
                "tech": "Local filesystem (SCANX_DATA_DIR)",
                "description": "Scan artifacts: alldomains.txt, live.txt, httpx.json, report.txt",
                "connections": ["Scanner Service"],
            },
            {
                "name": "Frontend",
                "type": "frontend",
                "tech": "Vanilla JS, CSS Variables, Bootstrap-like components",
                "description": "Dashboard, scan detail, organizations, assets, reports, docs",
                "connections": ["Django Templates", "REST-like endpoints"],
            },
        ],
        "data_flows": [
            {"from": "Frontend", "to": "Django", "protocol": "HTTP/HTTPS", "description": "User interactions, form submissions"},
            {"from": "Django", "to": "Scanner Service", "protocol": "In-process", "description": "Background thread spawn"},
            {"from": "Scanner Service", "to": "scanx.sh", "protocol": "subprocess", "description": "Execute recon with domain arg"},
            {"from": "scanx.sh", "to": "External APIs", "protocol": "HTTPS", "description": "Chaos, crt.sh, DNS queries"},
            {"from": "scanx.sh", "to": "File Storage", "protocol": "Local FS", "description": "Write artifacts"},
            {"from": "Scanner Service", "to": "Database", "protocol": "Django ORM", "description": "Update scan status, parse results"},
            {"from": "Django", "to": "MCP Server", "protocol": "In-process/HTTP", "description": "Expose data to AI agents"},
            {"from": "MCP Server", "to": "AI Agents", "protocol": "MCP (stdio/HTTP)", "description": "Tool calls, resource reads"},
        ],
    }


def get_tech_stack_data(config=None):
    """Get live technology stack information."""
    config = config or {}
    
    # Detect actual versions from environment
    import django
    import sys
    
    stack = {
        "frontend": [
            {"name": "HTML5 / Django Templates", "version": "", "category": "Template Engine"},
            {"name": "CSS3 with Custom Properties", "version": "", "category": "Styling (Dark-first, Lime accent)"},
            {"name": "Vanilla JavaScript (ES6+)", "version": "", "category": "Interactivity"},
            {"name": "Mermaid.js", "version": "10.x", "category": "Diagrams"},
            {"name": "Marked.js", "version": "12.x", "category": "Markdown Rendering"},
        ],
        "backend": [
            {"name": "Django", "version": django.get_version(), "category": "Web Framework"},
            {"name": "Python", "version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}", "category": "Runtime"},
            {"name": "dj-database-url", "version": "", "category": "DB Config"},
            {"name": "python-dotenv", "version": "", "category": "Environment"},
        ],
        "database": [
            {"name": "SQLite", "version": "3.x", "category": "Development"},
            {"name": "PostgreSQL", "version": "15+", "category": "Production (via dj-database-url)"},
        ],
        "infrastructure": [
            {"name": "Gunicorn", "version": "", "category": "WSGI Server"},
            {"name": "Nginx", "version": "", "category": "Reverse Proxy (prod)"},
            {"name": "Systemd", "version": "", "category": "Process Management"},
            {"name": "Docker", "version": "", "category": "Containerization (optional)"},
        ],
        "recon_tools": [
            {"name": "subfinder", "version": "projectdiscovery.io", "category": "Subdomain Enum"},
            {"name": "assetfinder", "version": "tomnomnom.github.io", "category": "Subdomain Enum"},
            {"name": "chaos", "version": "projectdiscovery.io", "category": "Dataset (API key required)"},
            {"name": "crt.sh", "version": "crt.sh", "category": "Certificate Transparency"},
            {"name": "dnsx", "version": "projectdiscovery.io", "category": "DNS Resolution"},
            {"name": "httpx", "version": "projectdiscovery.io", "category": "HTTP Probing"},
        ],
        "ai_integration": [
            {"name": "MCP (Model Context Protocol)", "version": "2024 spec", "category": "AI Agent Protocol"},
            {"name": "MCP Python SDK", "version": "latest", "category": "Server Implementation"},
        ],
        "development": [
            {"name": "Git", "version": "", "category": "Version Control"},
            {"name": "GitHub", "version": "", "category": "Hosting/CI"},
            {"name": "pytest", "version": "", "category": "Testing"},
            {"name": "ruff/black", "version": "", "category": "Linting/Formatting"},
        ],
    }
    
    return {"tech_stack": stack}


def get_api_docs_data(config=None):
    """Get live API documentation from scanner URLs."""
    config = config or {}
    
    from scanner.urls import urlpatterns
    from scanner import views
    
    endpoints = [
        {
            "category": "Scan Management",
            "endpoints": [
                {"method": "GET", "path": "/overview/", "name": "Dashboard", "description": "Main dashboard with scan form and history"},
                {"method": "POST", "path": "/overview/", "name": "Start Scan", "description": "Initiate new reconnaissance scan"},
                {"method": "GET", "path": "/scan/<uuid:scan_id>/", "name": "Scan Detail", "description": "Live logs (running) or results (completed)"},
                {"method": "GET", "path": "/scan/<uuid:scan_id>/logs/", "name": "Scan Logs", "description": "JSON log streaming (poll every 1.5s)"},
                {"method": "POST", "path": "/scan/<uuid:scan_id>/cancel/", "name": "Stop Scan", "description": "Cancel running/pending scan"},
                {"method": "GET", "path": "/history/", "name": "Scan History", "description": "Paginated list of all scans"},
            ]
        },
        {
            "category": "Organization Management",
            "endpoints": [
                {"method": "GET", "path": "/organizations/", "name": "List Organizations", "description": "All organizations with aggregate stats"},
                {"method": "GET", "path": "/organizations/add/", "name": "Add Organization", "description": "Form to create new organization"},
                {"method": "POST", "path": "/organizations/add/", "name": "Create Organization", "description": "Submit new organization"},
                {"method": "GET", "path": "/organizations/edit/<int:id>/", "name": "Edit Organization", "description": "Form to edit organization"},
                {"method": "POST", "path": "/organizations/edit/<int:id>/", "name": "Update Organization", "description": "Submit organization updates"},
                {"method": "POST", "path": "/organizations/delete/<int:id>/", "name": "Delete Organization", "description": "Remove organization"},
                {"method": "GET", "path": "/organizations/<int:id>/", "name": "Organization Detail", "description": "Per-domain stats for organization"},
            ]
        },
        {
            "category": "Asset Intelligence",
            "endpoints": [
                {"method": "GET", "path": "/assets/", "name": "Assets Overview", "description": "Aggregate stats + technology breakdown"},
                {"method": "GET", "path": "/assets/tech/", "name": "Technology Detail", "description": "Subdomains using specific technology"},
            ]
        },
        {
            "category": "Reports (MCP Analysis)",
            "endpoints": [
                {"method": "GET", "path": "/reports/", "name": "List Reports", "description": "All AI-generated analysis reports"},
                {"method": "GET", "path": "/reports/<uuid:report_id>/", "name": "Report Detail", "description": "View single report with markdown"},
                {"method": "GET", "path": "/reports/<uuid:report_id>/download/", "name": "Download Report", "description": "Download as Markdown file"},
            ]
        },
        {
            "category": "MCP Integration",
            "endpoints": [
                {"method": "GET", "path": "/mcp/", "name": "MCP Guide", "description": "Documentation for MCP usage"},
                {"method": "GET", "path": "/mcp/status/", "name": "MCP HTTP Status", "description": "Check if MCP HTTP server running (port 8001)"},
                {"method": "POST", "path": "/mcp/start/", "name": "Start MCP HTTP", "description": "Start MCP HTTP server in background"},
            ]
        },
        {
            "category": "Documentation",
            "endpoints": [
                {"method": "GET", "path": "/docs/", "name": "Documentation Home", "description": "Pitch deck + technical docs (access controlled)"},
                {"method": "GET", "path": "/docs/export/", "name": "Export Documentation", "description": "Download as PDF/Markdown/HTML"},
            ]
        },
    ]
    
    return {
        "api_endpoints": endpoints,
        "auth_model": "Session-based (Django auth) + MCP stdio/HTTP transport",
        "rate_limits": "None implemented (add for production)",
        "content_type": "application/json for API endpoints, text/html for views",
    }


def get_data_layer_info(config=None):
    """Get live data layer information."""
    config = config or {}
    
    total_scans = Scan.objects.count()
    completed_scans = Scan.objects.filter(status=Scan.Status.COMPLETED).count()
    total_subdomains = Scan.objects.aggregate(Sum('total_subdomains'))['total_subdomains__sum'] or 0
    total_live = Scan.objects.aggregate(Sum('live_subdomains'))['live_subdomains__sum'] or 0
    
    return {
        "data_sources": [
            {
                "name": "Subdomain Enumeration",
                "tools": ["subfinder", "assetfinder", "chaos", "crt.sh"],
                "output": "alldomains.txt (deduplicated)",
                "storage": "File system + Scan.total_subdomains",
                "frequency": "Per scan execution",
            },
            {
                "name": "DNS Resolution",
                "tool": "dnsx",
                "output": "live.txt (resolved subdomains)",
                "storage": "File system + Scan.live_subdomains",
                "frequency": "Per scan execution",
            },
            {
                "name": "HTTP Probing",
                "tool": "httpx",
                "output": "httpx.json (JSON Lines)",
                "fields": ["url", "status_code", "title", "tech", "ip", "cname"],
                "storage": "File system + Scan.httpx_results (JSONField) + Scan.http_success/failed",
                "frequency": "Per scan execution",
            },
            {
                "name": "Organization Metadata",
                "source": "Admin input",
                "fields": ["name", "description", "organization_type (17 types)"],
                "storage": "Program model (PostgreSQL/SQLite)",
                "frequency": "Manual CRUD",
            },
            {
                "name": "AI Reports",
                "source": "MCP Agent (LLM)",
                "types": ["attack_surface", "vulnerability", "technology_exposure", "attack_vector", "custom"],
                "storage": "Report model (content: markdown, findings: JSON)",
                "frequency": "On-demand via MCP tools",
            },
        ],
        "storage_architecture": {
            "database": "SQLite (dev) / PostgreSQL (prod) via Django ORM",
            "scan_artifacts": f"File system at {getattr(settings, 'SCANX_DATA_DIR', 'scan_data/')}/<scan_uuid>/",
            "artifact_structure": "Each scan creates isolated directory with domain-named subdirectory",
            "cleanup": "Manual (no auto-retention implemented)",
        },
        "privacy_handling": {
            "authorization_required": "Every scan must link to a Program (authorized organization)",
            "data_scope": "Only authorized target domains are scanned",
            "data_retention": "Indefinite until manual deletion",
            "access_control": "Django admin + session auth (no public API)",
            "pii_handling": "No PII collected beyond org contact info",
        },
        "stats": {
            "total_scans": total_scans,
            "completed_scans": completed_scans,
            "total_subdomains_collected": total_subdomains,
            "total_live_hosts": total_live,
        }
    }


def get_ai_layer_info(config=None):
    """Get live AI layer information."""
    config = config or {}
    
    total_reports = Report.objects.count()
    report_types = Report.objects.values('report_type').annotate(count=Count('id'))
    type_counts = {r['report_type']: r['count'] for r in report_types}
    
    return {
        "models_used": [
            {
                "name": "NVIDIA Nemotron 3 Ultra",
                "provider": "NVIDIA via OpenCode",
                "purpose": "Report generation, analysis, code assistance",
                "access": "OpenCode integration",
            },
            {
                "name": "Local/Configurable LLMs",
                "provider": "Configurable via MCP",
                "purpose": "Extensible for other models",
                "access": "MCP tool calls",
            },
        ],
        "rag_architecture": {
            "approach": "Context injection via MCP tools",
            "data_sources": [
                "Scan.httpx_results (structured JSON)",
                "Scan statistics (aggregated)",
                "Program metadata",
                "Historical scan comparisons",
            ],
            "retrieval": "MCP tools query Django ORM directly",
            "context_window": "Full scan data passed to LLM",
            "vector_store": "Not currently used (direct context injection)",
        },
        "personalization": {
            "report_types": list(Report.ReportType.values),
            "custom_prompts": "Supported via create_report MCP tool",
            "organization_context": "Included in report generation",
            "historical_context": "Previous scans of same domain compared",
        },
        "explainability": {
            "structured_findings": "JSON findings field in Report model",
            "source_attribution": "Each finding references scan data",
            "confidence_scoring": "Not yet implemented",
            "audit_trail": "Report model tracks generated_by, timestamps",
        },
        "mcp_tools": [
            "get_scan_details",
            "get_organization_scans",
            "search_subdomains",
            "analyze_attack_surface",
            "get_technology_exposure",
            "create_report",
        ],
        "stats": {
            "total_reports": total_reports,
            "by_type": type_counts,
        }
    }


def get_performance_data(config=None):
    """Get live performance and scalability data."""
    config = config or {}
    
    from django.db import connection
    
    # Get some DB stats
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM scanner_scan")
        scan_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM scanner_program")
        program_count = cursor.fetchone()[0]
    
    return {
        "current_scale": {
            "scans": scan_count,
            "organizations": program_count,
            "avg_subdomains_per_scan": "~500-5000 (depends on target)",
            "avg_scan_duration": "2-10 minutes",
        },
        "bottlenecks": [
            "scanx.sh sequential execution (subfinder → assetfinder → chaos → crt → dnsx → httpx)",
            "httpx probing is slowest step (network I/O bound)",
            "Single-threaded scanner (one scan at a time per worker)",
            "SQLite write contention under load",
        ],
        "optimizations_implemented": [
            "Background thread execution (non-blocking web requests)",
            "Line-buffered log streaming (real-time UX)",
            "Database indexes on Scan.status, Scan.domain, Scan.created_at",
            "JSONField for httpx_results (avoids N+1 queries)",
            "select_related/prefetch_related in views",
        ],
        "planned_optimizations": [
            "Celery/Redis for distributed task queue",
            "PostgreSQL for production concurrency",
            "Parallel subdomain enumeration",
            "Incremental scanning (only new subdomains)",
            "Caching for asset/technology views",
            "CDN for static assets",
        ],
        "load_expectations": {
            "concurrent_scans": "1-5 (current threading model)",
            "scans_per_hour": "6-30",
            "data_per_scan": "1-10 MB artifacts",
            "database_growth": "~100 KB per scan",
        },
    }


def get_security_data(config=None):
    """Get live security information."""
    config = config or {}
    
    return {
        "authentication": {
            "method": "Django Session Authentication",
            "admin": "Django Admin (staff/superuser)",
            "public_views": "No auth required (but /docs has access control)",
            "api": "Session-based CSRF + MCP stdio transport",
        },
        "authorization": {
            "scan_authorization": "Program-based (org must exist, scan linked to program)",
            "admin_actions": "Django permission system (is_staff, is_superuser)",
            "mcp_access": "stdio (local) or HTTP with custom auth (to be implemented)",
        },
        "input_validation": {
            "domain": "RFC 1035/1123 regex + shell metacharacter blocking + path traversal prevention",
            "program_selection": "Must exist in database",
            "file_upload": "Image validation (team avatars) - extension + size",
        },
        "execution_safety": {
            "subprocess": "shell=False, args as list, env sanitized",
            "timeout": f"{getattr(settings, 'SCAN_TIMEOUT', 3600)} seconds",
            "isolation": "Per-scan UUID directory, no shared state",
            "cancellation": "SIGTERM → SIGKILL with DB status check",
        },
        "data_protection": {
            "secrets": "Environment variables (.env), not in code",
            "api_keys": "CHAOS_API_KEY injected at runtime only",
            "scan_data": "File system permissions + DB access control",
            "logs": "No secrets in scan logs (validated)",
        },
        "network": {
            "outbound": "Only to authorized target domains + Chaos API + crt.sh",
            "inbound": "Django on configured ALLOWED_HOSTS",
            "mcp_http": "Optional, port 80001, localhost by default",
        },
        "compliance": {
            "authorized_only": "Enforced at scan creation (Program required)",
            "scope_enforcement": "Domain validation + program linkage",
            "audit_trail": "Scan model tracks created_by, authorized_by, timestamps",
            "data_retention": "Configurable (manual cleanup currently)",
        },
    }


def get_roadmap_data(config=None):
    """Get live product roadmap."""
    config = config or {}
    
    return {
        "short_term": [
            {"title": "Celery Task Queue", "description": "Replace threading with distributed task queue for reliability", "status": "planned"},
            {"title": "PostgreSQL Migration", "description": "Production-ready database with connection pooling", "status": "planned"},
            {"title": "Incremental Scanning", "description": "Only scan new subdomains since last run", "status": "planned"},
            {"title": "Real-time WebSocket Logs", "description": "Replace polling with WebSocket for live logs", "status": "planned"},
            {"title": "Scan Scheduling (Cron)", "description": "Recurring scans per organization", "status": "planned"},
        ],
        "mid_term": [
            {"title": "Multi-tenant SaaS", "description": "Organizations as isolated tenants with billing", "status": "concept"},
            {"title": "Vulnerability Scanner Integration", "description": "Nuclei integration for active vuln scanning", "status": "concept"},
            {"title": "Screenshot Capture", "description": "Headless browser screenshots of live hosts", "status": "concept"},
            {"title": "API Gateway + Rate Limiting", "description": "Public API with auth tokens and quotas", "status": "concept"},
            {"title": "Advanced RBAC", "description": "Roles: Admin, Analyst, Viewer per organization", "status": "concept"},
        ],
        "long_term": [
            {"title": "GraphRAG Knowledge Base", "description": "Build attack graph from recon data for AI reasoning", "status": "research"},
            {"title": "Autonomous Red Team Agent", "description": "AI agent that plans and executes attack paths", "status": "research"},
            {"title": "Threat Intelligence Fusion", "description": "Real-time CVE/KEV/Exploit feed correlation", "status": "research"},
            {"title": "Compliance Reporting", "description": "SOC2, ISO27001, NIST automated evidence", "status": "research"},
            {"title": "Marketplace/Extensions", "description": "Plugin system for custom tools and integrations", "status": "vision"},
        ],
    }


def get_changelog_data(config=None):
    """Get live changelog from git or manual entries."""
    config = config or {}
    
    # In production, this could parse git tags or use a dedicated changelog model
    return {
        "versions": [
            {
                "version": "2.0.0",
                "date": "2026-01-15",
                "type": "major",
                "title": "MCP Integration & AI Reports",
                "changes": [
                    "Added Model Context Protocol (MCP) server for AI agent integration",
                    "AI-generated analysis reports (5 types)",
                    "MCP HTTP transport on port 8001",
                    "MCP tools: get_scan_details, search_subdomains, analyze_attack_surface, create_report",
                    "Report download as Markdown",
                ]
            },
            {
                "version": "1.5.0",
                "date": "2025-11-20",
                "type": "minor",
                "title": "Asset Intelligence & Technology Mapping",
                "changes": [
                    "Assets page with technology breakdown",
                    "Technology detail page (subdomains per tech)",
                    "Organization detail with per-domain stats",
                    "New subdomain detection (comparison with previous scans)",
                    "Advanced filtering on scan detail (status, tech, IP, CNAME)",
                ]
            },
            {
                "version": "1.0.0",
                "date": "2025-08-01",
                "type": "major",
                "title": "Initial Release - Phase 1 Complete",
                "changes": [
                    "Django web interface for scanx.sh",
                    "Dashboard with scan form and live logs",
                    "Background scan execution with threading",
                    "Scan history and detail views",
                    "Organization/Program management",
                    "Real-time log streaming via polling",
                    "Export scan artifacts",
                ]
            },
        ]
    }


# Registry of all live data providers
LIVE_DATA_PROVIDERS = {
    "feature_matrix": get_feature_matrix,
    "architecture": get_architecture_data,
    "tech_stack": get_tech_stack_data,
    "api_docs": get_api_docs_data,
    "data_layer": get_data_layer_info,
    "ai_layer": get_ai_layer_info,
    "performance": get_performance_data,
    "security": get_security_data,
    "roadmap": get_roadmap_data,
    "changelog": get_changelog_data,
}


def get_provider(name):
    """Get a live data provider by name."""
    return LIVE_DATA_PROVIDERS.get(name)


def get_all_providers():
    """Get all registered provider names."""
    return list(LIVE_DATA_PROVIDERS.keys())