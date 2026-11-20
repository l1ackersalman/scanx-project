"""
Initialize default documentation content for scanX.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime
import pytz

from docs_app.models import DocSection, DocAccessControl, TeamMember, DocSettings


class Command(BaseCommand):
    help = 'Initialize default documentation content'

    def handle(self, *args, **options):
        self.stdout.write('Initializing documentation...')
        
        # Create default settings
        settings, created = DocSettings.objects.get_or_create(
            id='00000000-0000-0000-0000-000000000002',
            defaults={
                'site_title': 'scanX Documentation',
                'site_tagline': 'AI-Powered Security Reconnaissance Platform',
                'primary_color': '#76B900',
                'accent_color': '#35B779',
                'enable_search': True,
                'enable_export_pdf': True,
                'enable_export_md': True,
                'enable_anchor_links': True,
                'enable_toc': True,
                'meta_description': 'Complete documentation for scanX - AI-powered security reconnaissance platform with automated asset discovery, technology fingerprinting, and AI-generated analysis reports.',
                'meta_keywords': 'security, reconnaissance, vulnerability assessment, attack surface, ASM, bug bounty, penetration testing',
            }
        )
        if created:
            self.stdout.write('  Created default settings')
        
        # Create access control with June 10-14 default window
        tz = pytz.timezone('Asia/Dhaka')
        access_control, created = DocAccessControl.objects.get_or_create(
            id='00000000-0000-0000-0000-000000000001',
            defaults={
                'is_enabled': True,
                'schedule_start': tz.localize(datetime(2026, 6, 10, 0, 0, 0)),
                'schedule_end': tz.localize(datetime(2026, 6, 14, 23, 59, 59)),
                'use_duration': False,
                'disabled_message': 'Documentation is currently not available. Please check back during the scheduled viewing window.',
                'scheduled_message': 'Documentation will be available from {start} to {end}.',
                'default_start': tz.localize(datetime(2026, 6, 10, 0, 0, 0)),
                'default_end': tz.localize(datetime(2026, 6, 14, 23, 59, 59)),
            }
        )
        if created:
            self.stdout.write('  Created access control (Jun 10-14 window)')
        
        # Create default sections for Pitch Deck
        pitch_sections = [
            {
                'section_type': 'problem',
                'title': 'The Problem',
                'subtitle': 'Organizations are blind to their external attack surface',
                'order': 1,
                'is_pitch_deck': True,
                'is_technical': False,
                'content': '''## Expanding Attack Surface

Modern organizations have a vast and growing external attack surface:

- **Shadow IT**: Unauthorized cloud services, forgotten subdomains, deprecated applications
- **M&A Activity**: Acquired companies bring unknown assets and vulnerabilities
- **Rapid Development**: CI/CD pipelines deploy new services faster than security can track
- **Supply Chain**: Third-party vendors, contractors, and partners extend the perimeter

## Visibility Gap

> **70% of breaches originate from unknown, unmanaged, or poorly managed internet-facing assets.** (Gartner)

Traditional tools fail because:
- Periodic scans miss changes between scans
- Asset inventories are manually maintained and outdated
- Vulnerability scanners require known targets
- Security teams lack context for prioritization

## Current Solutions Fall Short

| Approach | Limitation |
|----------|------------|
| Manual spreadsheets | Not scalable, quickly outdated |
| Annual pentests | Point-in-time, expensive, slow |
| Traditional VA scanners | Need target lists, noisy, no context |
| Bug bounty programs | Reactive, unpredictable coverage |
''',
            },
            {
                'section_type': 'solution',
                'title': 'The Solution',
                'subtitle': 'Continuous, AI-augmented attack surface management',
                'order': 2,
                'is_pitch_deck': True,
                'is_technical': False,
                'content': '''## scanX: Continuous Reconnaissance Platform

scanX automates the entire reconnaissance lifecycle — from asset discovery to AI-powered analysis — giving security teams real-time visibility into their external attack surface.

### Core Capabilities

1. **Automated Asset Discovery**
   - Subdomain enumeration via multiple sources (subfinder, assetfinder, Chaos, crt.sh)
   - DNS resolution and HTTP probing (httpx)
   - Technology fingerprinting and CNAME tracking

2. **Organization-Centric Management**
   - Authorized target programs with 17 industry categories
   - Per-organization scan history and aggregate statistics
   - New subdomain detection across scan iterations

3. **AI-Generated Analysis Reports**
   - Attack Surface Analysis
   - Vulnerability Assessment
   - Technology Exposure Mapping
   - Attack Vector Analysis
   - Custom prompt-driven reports

4. **MCP Integration for AI Agents**
   - Model Context Protocol server exposes scan data to LLMs
   - Tools: search_subdomains, analyze_attack_surface, create_report
   - Enables autonomous security workflows

### Key Differentiators

- **Authorized-only scanning** — Every scan linked to approved program
- **Live log streaming** — Real-time visibility during scans
- **Historical comparison** — Automatic new asset detection
- **Extensible architecture** — Bash script core, Django web layer, MCP for AI
''',
            },
            {
                'section_type': 'why_now',
                'title': 'Why Now',
                'subtitle': 'Convergence of trends makes this the right time',
                'order': 3,
                'is_pitch_deck': True,
                'is_technical': False,
                'content': '''## Market Timing

### 1. Attack Surface Explosion
- Average enterprise has **300+ unknown internet-facing assets** (Censys)
- Cloud adoption accelerated 7 years during pandemic
- Remote work permanently expanded corporate perimeter

### 2. Regulatory Pressure
- SEC cyber disclosure rules (2023)
- NIS2 Directive in EU (2024)
- CMMC 2.0 for defense contractors
- All require continuous asset visibility

### 3. AI Agent Maturity
- LLMs now capable of complex security reasoning
- Model Context Protocol (MCP) standardizes tool access
- Autonomous security workflows becoming feasible

### 4. Tool Consolidation
- Security teams reducing vendor count
- Platform approach preferred over point tools
- Budget pressure favors integrated solutions

## Competitive Window

The ASM market is transitioning from **"scan and report"** to **"continuous intelligence"**. Early movers who combine:
- Reliable data collection (our Bash script heritage)
- Modern web platform (Django + real-time UX)
- AI-native architecture (MCP integration)

...will define the category.
''',
            },
            {
                'section_type': 'product_demo',
                'title': 'Product Demo',
                'subtitle': 'See scanX in action',
                'order': 4,
                'is_pitch_deck': True,
                'is_technical': False,
                'content': '''## Dashboard Overview

The scanX dashboard provides a single pane of glass for all reconnaissance activities.

### Starting a Scan

1. Select target domain (validated RFC 1035)
2. Choose authorized organization program
3. Click "Start Scan" — executes in background thread
4. Watch live logs stream in real-time

### Live Scan Logs

```
[✔] Identifying Subdomains of example.com...
[✔] Checking Live domains...
[✔] Analyzing Technologies...
[✔] Collecting Informations...
[✔] Deep Scanning...
[✔] Checking IP & CNAME records...
[✔] Final Evaluation...
[✔] Scan completed for example.com.

⏱️  Total Execution Time: 0h 4m
```

### Scan Results

Results include:
- **Total subdomains** discovered
- **Live hosts** with DNS resolution
- **HTTP services** with status codes, titles, technologies
- **IP addresses** and **CNAME records**
- **New subdomain detection** vs previous scans

### Filtering & Exploration

Filter HTTP results by:
- Status code (2xx, 3xx, 403, 404, 5xx)
- Technology (nginx, WordPress, React, etc.)
- IP address or CIDR
- CNAME target

### Organization View

Aggregate statistics across all scans for an organization:
- Per-domain metrics (deduplicated)
- Technology breakdown
- Scan history timeline

### AI Reports

Generate analysis reports via MCP:
```
> analyze_attack_surface("example.com")
> create_report(scan_id, "attack_surface", "Q3 Review", "Focus on exposed admin panels")
```

Reports include structured findings + markdown narrative.
''',
            },
            {
                'section_type': 'market_opportunity',
                'title': 'Market Opportunity',
                'subtitle': 'Large and growing TAM with clear entry points',
                'order': 5,
                'is_pitch_deck': True,
                'is_technical': False,
                'content': '''## Total Addressable Market

### ASM Market
- **$1.2B** in 2024 → **$3.8B** by 2029 (26% CAGR)
- Driven by cloud migration, regulatory compliance, breach costs

### Adjacent Markets
- Vulnerability Management: $14B
- Penetration Testing: $3.2B
- Bug Bounty Platforms: $800M
- **Combined TAM: ~$20B**

## Target Segments

| Segment | Pain Point | scanX Fit |
|---------|------------|-----------|
| **Mid-market (500-5000 emp)** | No dedicated red team, limited budget | Automated continuous recon |
| **Security Consultancies** | Manual recon for each engagement | Reusable scan data, AI reports |
| **Bug Bounty Hunters** | Need efficient recon workflows | Live logs, organized results, MCP tools |
| **Enterprise Security** | Shadow IT, M&A integration | Org-centric, historical tracking |

## Go-to-Market Strategy

1. **Bottom-up**: Individual hunters/consultants → team adoption
2. **Content-led**: Technical blog, open-source components, MCP tools
3. **Integration-first**: Works with existing tools (Burp, Nuclei, etc.)
4. **Community-driven**: Discord, GitHub, security conferences
''',
            },
            {
                'section_type': 'business_model',
                'title': 'Business Model',
                'subtitle': 'SaaS with usage-based pricing',
                'order': 6,
                'is_pitch_deck': True,
                'is_technical': False,
                'content': '''## Pricing Tiers

| Plan | Price | Scans/Month | Organizations | AI Reports | MCP Access |
|------|-------|-------------|---------------|------------|------------|
| **Free** | $0 | 10 | 1 | 5 | Read-only |
| **Pro** | $199/mo | 100 | 5 | 50 | Full |
| **Team** | $599/mo | 500 | 20 | 200 | Full + API |
| **Enterprise** | Custom | Unlimited | Unlimited | Unlimited | Full + SSO + SLA |

## Revenue Drivers

1. **Subscription SaaS** — Recurring monthly/annual
2. **Usage overages** — Additional scans, reports, API calls
3. **Professional services** — Custom integrations, training
4. **Marketplace** — Revenue share on community templates/plugins

## Unit Economics (Projected)

- **LTV/CAC**: 5:1 (Year 2)
- **Gross Margin**: 85% (software + compute)
- **Payback Period**: 8 months
- **Net Revenue Retention**: 120%+ (expansion revenue)
''',
            },
            {
                'section_type': 'traction',
                'title': 'Traction',
                'subtitle': 'Early validation from security community',
                'order': 7,
                'is_pitch_deck': True,
                'is_technical': False,
                'content': '''## Technical Milestones

✅ **Phase 1 Complete** — Core scanner web interface
- Django + Bash integration
- Background scan execution
- Live log streaming
- Scan history & detail views

✅ **Phase 2 Complete** — Organization & Asset management
- Program CRUD with 17 industry types
- Per-domain deduplicated statistics
- Technology breakdown across orgs
- New subdomain detection

✅ **Phase 3 Complete** — AI Integration (MCP)
- Model Context Protocol server (stdio + HTTP)
- 6 MCP tools for AI agents
- 5 report types with structured findings
- Markdown export

## Community Signals

- **GitHub**: Growing star count, external contributors
- **Discord**: Active security practitioner community
- **Conference Talks**: Accepted at BSides, DEF CON villages
- **Blog Posts**: Technical deep-dives on recon methodology

## Pilot Customers

3 design partners using scanX for:
- Continuous monitoring of 50+ domains
- Pre-engagement recon for pentests
- Bug bounty target preparation
''',
            },
            {
                'section_type': 'competition',
                'title': 'Competition',
                'subtitle': 'Differentiated by architecture and AI-native approach',
                'order': 8,
                'is_pitch_deck': True,
                'is_technical': False,
                'content': '''## Competitive Landscape

### Traditional ASM Vendors
| Vendor | Strength | Weakness |
|--------|----------|----------|
| **Censys/Shodan** | Massive internet dataset | Expensive, no org context, API-only |
| **Assetnote** | Continuous, good UI | Closed source, enterprise-only |
| **JupiterOne** | Graph-based, integrations | Complex, expensive, not recon-focused |

### Vulnerability Management
| Vendor | Strength | Weakness |
|--------|----------|----------|
| **Tenable/Qualys** | Enterprise standard | Agent-based, slow, compliance-focused |
| **Nuclei/Templates** | Fast, community-driven | No asset management, no AI |

### Bug Bounty Platforms
| Vendor | Strength | Weakness |
|--------|----------|----------|
| **HackerOne/Bugcrowd** | Researcher network | Reactive, no continuous monitoring |

## scanX Differentiation

```
                    ┌─────────────────────────────────────┐
                    │         scanX Positioning           │
                    └─────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
    ┌─────────┐         ┌─────────┐         ┌─────────┐
    │  Open   │         │  AI-    │         │ Org-    │
    │  Core   │         │  Native │         │  Centric│
    │ (Bash)  │         │  (MCP)  │         │  Model  │
    └─────────┘         └─────────┘         └─────────┘
```

**No competitor combines all three:**
1. **Transparent core** — Bash script auditable, extensible
2. **AI-first** — MCP built-in, not bolted on
3. **Org-centric** — Programs, not just domains
''',
            },
            {
                'section_type': 'unique_advantage',
                'title': 'Unique Advantage',
                'subtitle': 'Technical moats that compound over time',
                'order': 9,
                'is_pitch_deck': True,
                'is_technical': False,
                'content': '''## Defensible Moats

### 1. Reconnaissance Script Heritage
- **scanx.sh** battle-tested in real bug bounty engagements
- Community-contributed tool chain (ProjectDiscovery ecosystem)
- Not a black box — every step auditable and customizable
- **Switching cost**: Replacing validated recon logic is hard

### 2. MCP as Platform Primitive
- First ASM with native Model Context Protocol support
- AI agents can *directly* query live scan data
- Enables autonomous workflows: triage → analyze → report
- **Network effect**: More MCP tools = more valuable platform

### 3. Organizational Knowledge Graph
- Programs → Domains → Scans → Subdomains → Technologies
- Historical comparisons build proprietary intelligence
- "This subdomain is new" → immediate signal
- **Data moat**: Compounds with every scan

### 4. Extensible Architecture
```
┌─────────────────────────────────────────────────────┐
│                    scanX Platform                   │
├─────────────┬─────────────┬─────────────┬───────────┤
│  Bash Core  │  Django API │  MCP Server │  Plugins  │
│  (Recon)    │  (Web/UI)   │  (AI)       │  (Custom) │
└─────────────┴─────────────┴─────────────┴───────────┘
```
- Swap Bash tools without touching web layer
- Add MCP tools without changing scanner
- Plugin system for custom integrations

### 5. Security-First Design
- Authorized scanning enforced at data model level
- No shell injection (validated domains, list args)
- Isolated per-scan directories
- Cancellation with graceful cleanup
''',
            },
            {
                'section_type': 'go_to_market',
                'title': 'Go-To-Market',
                'subtitle': 'Developer-first, community-led growth',
                'order': 10,
                'is_pitch_deck': True,
                'is_technical': False,
                'content': '''## GTM Motion: Bottom-Up Developer Adoption

### Phase 1: Individual Practitioners (Months 1-6)
- **Free tier** for bug bounty hunters, pentesters
- **Open source** core scanner (scanx.sh) on GitHub
- **Technical content**: "How I found X using scanX"
- **Discord community** for support and feedback

### Phase 2: Team Adoption (Months 6-18)
- **Pro tier** for small security teams
- **MCP integrations** with Cursor, Claude, custom agents
- **Templates**: "SOC2 evidence collection", "M&A due diligence"
- **Integrations**: Slack, Jira, GitHub Actions, SIEM

### Phase 3: Enterprise (Months 18+)
- **Team/Enterprise tiers** with SSO, RBAC, SLA
- **Professional services**: Custom recon modules, training
- **Marketplace**: Community-contributed MCP tools, report templates
- **Partner program**: MSSPs, consultancies, VARs

## Channel Strategy

| Channel | Tactics | Metrics |
|---------|---------|---------|
| **Content** | Technical blog, YouTube, conference talks | Organic traffic, signups |
| **Community** | Discord, GitHub, security Discords | Active users, contributions |
| **SEO** | "attack surface management", "recon automation" | Keyword rankings |
| **Partnerships** | Tool integrations (Nuclei, Burp, Amass) | Referral signups |
| **Events** | BSides, DEF CON, local meetups | Pipeline from events |

## Key Metrics

- **North Star**: Weekly Active Organizations (WAO)
- **Leading**: Scans initiated, MCP tool calls, reports generated
- **Lagging**: ARR, NRR, CAC payback
''',
            },
            {
                'section_type': 'team',
                'title': 'The Team',
                'subtitle': 'Security practitioners building for security practitioners',
                'order': 11,
                'is_pitch_deck': True,
                'is_technical': False,
                'content': '''## Core Team

*Team members are managed in the admin panel and displayed here automatically.*

### Advisors

*Advisors are managed in the admin panel with role="advisor".*

### Hiring Plan (Next 12 Months)

| Role | Priority | Rationale |
|------|----------|-----------|
| **Senior Backend Engineer** | High | Scale Django, PostgreSQL, Celery |
| **Security Researcher** | High | Recon methodology, Nuclei templates |
| **AI/ML Engineer** | Medium | RAG, GraphRAG, agent workflows |
| **DevOps/Platform Engineer** | Medium | Kubernetes, multi-tenant, observability |
| **Developer Advocate** | Medium | Community, content, integrations |
| **Product Designer** | Low | UX for complex security workflows |
''',
            },
            {
                'section_type': 'vision',
                'title': 'Vision',
                'subtitle': 'The autonomous security reconnaissance platform',
                'order': 12,
                'is_pitch_deck': True,
                'is_technical': False,
                'content': '''## 10-Year Vision

### Year 1-2: Continuous Intelligence
- Real-time asset monitoring with change detection
- AI triage of new exposures (CVEs, config changes)
- Natural language queries: "Show me all new admin panels this week"

### Year 3-4: Autonomous Investigation
- AI agents that plan and execute reconnaissance
- GraphRAG connecting assets, vulnerabilities, threat intel
- Simulated attack paths from internet to crown jewels

### Year 5-7: Predictive Defense
- Predict where attackers will strike next
- Automated remediation guidance with code fixes
- Continuous compliance evidence generation

### Year 10: Self-Securing Infrastructure
- Infrastructure that discovers, assesses, and hardens itself
- AI red team vs AI blue team continuous simulation
- Security as an emergent property, not a bolt-on

## Mission

> **Make continuous security reconnaissance accessible to every organization, enabling proactive defense at scale.**

## Values

1. **Transparency** — Open core, auditable logic, no black boxes
2. **Practitioner-first** — Built by hackers, for hackers
3. **AI-native** — Not AI-washed; MCP is a primitive, not a feature
4. **Authorization always** — Ethical by design, not by policy
5. **Community over competition** — Open protocols, shared intelligence
''',
            },
        ]
        
        # Create default sections for Technical Documentation
        tech_sections = [
            {
                'section_type': 'product_overview',
                'title': 'Product Overview',
                'subtitle': 'What scanX does and who it\'s for',
                'order': 1,
                'is_pitch_deck': False,
                'is_technical': True,
                'live_data_source': 'docs_app.live_data.get_feature_matrix',
                'content': '''## What is scanX?

scanX is a **continuous security reconnaissance platform** that automates the discovery, enumeration, and analysis of an organization's external attack surface.

### Core Value Proposition

| Problem | scanX Solution |
|---------|----------------|
| Unknown internet-facing assets | Automated multi-source subdomain enumeration |
| Point-in-time assessments | Continuous scanning with historical comparison |
| Manual triage of findings | AI-generated analysis reports via MCP |
| Disconnected tools | Unified platform: recon → analysis → reporting |

### Target Users

- **Security Teams** — Continuous ASM, compliance evidence
- **Penetration Testers** — Pre-engagement reconnaissance automation
- **Bug Bounty Hunters** — Efficient target enumeration and tracking
- **Consultancies** — Standardized recon methodology across engagements
- **AI Agents** — MCP server for autonomous security workflows

### Key Workflows

1. **Continuous Monitoring**: Schedule recurring scans → Detect changes → Alert on new exposures
2. **Pre-Engagement Recon**: Scan target → Generate attack surface report → Plan testing approach
3. **Vulnerability Triage**: New CVE released → Query technology exposure → Prioritize patching
4. **M&A Due Diligence**: Scan acquired company → Compare attack surfaces → Risk assessment
''',
            },
            {
                'section_type': 'feature_matrix',
                'title': 'Feature Matrix',
                'subtitle': 'Current capabilities with live status',
                'order': 2,
                'is_pitch_deck': False,
                'is_technical': True,
                'live_data_source': 'docs_app.live_data.get_feature_matrix',
                'content': '''## Feature Status

*This section is automatically populated with live data from the scanX platform.*
''',
            },
            {
                'section_type': 'architecture',
                'title': 'Architecture',
                'subtitle': 'System components and interactions',
                'order': 3,
                'is_pitch_deck': False,
                'is_technical': True,
                'live_data_source': 'docs_app.live_data.get_architecture_data',
                'content': '''## System Architecture

*Live architecture diagram generated from current system state.*

```mermaid
graph TB
    subgraph "Frontend"
        UI[Django Templates + Vanilla JS]
    end
    
    subgraph "Backend"
        API[Django Views + REST-like Endpoints]
        SCAN[Scanner Service + Threading]
        MCP[MCP Server - stdio/HTTP]
    end
    
    subgraph "Data Layer"
        DB[(PostgreSQL/SQLite)]
        FS[File System - SCANX_DATA_DIR]
    end
    
    subgraph "External Tools"
        BASH[scanx.sh]
        SUB[subfinder]
        ASSET[assetfinder]
        CHAOS[chaos]
        CRT[crt.sh]
        DNSX[dnsx]
        HTTPX[httpx]
    end
    
    UI --> API
    API --> SCAN
    SCAN --> BASH
    BASH --> SUB & ASSET & CHAOS & CRT & DNSX & HTTPX
    BASH --> FS
    SCAN --> DB
    API --> DB
    MCP --> DB
    API --> MCP
```
''',
            },
            {
                'section_type': 'data_flow',
                'title': 'Data Flow',
                'subtitle': 'How data moves through the system',
                'order': 4,
                'is_pitch_deck': False,
                'is_technical': True,
                'content': '''## Data Flow Pipeline

```mermaid
flowchart LR
    A[User Input: Domain + Program] --> B[Scan Record Created]
    B --> C[Background Thread Spawned]
    C --> D[scanx.sh Executed]
    D --> E[Subdomain Enumeration]
    E --> F[DNS Resolution]
    F --> G[HTTP Probing]
    G --> H[Artifacts Written to FS]
    H --> I[Results Parsed]
    I --> J[Scan Model Updated]
    J --> K[Live Log Stream]
    K --> L[Dashboard Updates]
    J --> M[MCP Resources Available]
    M --> N[AI Agent Queries]
    N --> O[Report Generation]
    O --> P[Report Model Stored]
```

### Detailed Stages

1. **Input Validation**: Domain RFC 1035 + program existence
2. **Scan Initialization**: UUID directory, status=RUNNING
3. **Reconnaissance**: 6-tool pipeline (subfinder → assetfinder → chaos → crt.sh → dnsx → httpx)
4. **Artifact Storage**: Isolated per-scan directories
5. **Parsing**: Statistics + structured JSON results
6. **Persistence**: Django ORM updates Scan model
7. **Real-time UI**: Polling-based log streaming
8. **MCP Exposure**: Resources + Tools for AI agents
9. **Report Generation**: On-demand via MCP create_report tool
''',
            },
            {
                'section_type': 'tech_stack',
                'title': 'Technology Stack',
                'subtitle': 'Languages, frameworks, and tools',
                'order': 5,
                'is_pitch_deck': False,
                'is_technical': True,
                'live_data_source': 'docs_app.live_data.get_tech_stack_data',
                'content': '''*Live technology stack generated from current environment.*''',
            },
            {
                'section_type': 'api_docs',
                'title': 'API Documentation',
                'subtitle': 'Endpoints exposed by scanX',
                'order': 6,
                'is_pitch_deck': False,
                'is_technical': True,
                'live_data_source': 'docs_app.live_data.get_api_docs_data',
                'content': '''*Live API documentation generated from URL patterns.*''',
            },
            {
                'section_type': 'data_layer',
                'title': 'Data Layer',
                'subtitle': 'Storage, privacy, and data handling',
                'order': 7,
                'is_pitch_deck': False,
                'is_technical': True,
                'live_data_source': 'docs_app.live_data.get_data_layer_info',
                'content': '''*Live data layer information from current system.*''',
            },
            {
                'section_type': 'ai_layer',
                'title': 'AI Layer',
                'subtitle': 'MCP integration and report generation',
                'order': 8,
                'is_pitch_deck': False,
                'is_technical': True,
                'live_data_source': 'docs_app.live_data.get_ai_layer_info',
                'content': '''*Live AI layer architecture and capabilities.*''',
            },
            {
                'section_type': 'roadmap',
                'title': 'Product Roadmap',
                'subtitle': 'Short, mid, and long-term plans',
                'order': 9,
                'is_pitch_deck': False,
                'is_technical': True,
                'live_data_source': 'docs_app.live_data.get_roadmap_data',
                'content': '''*Live roadmap data.*''',
            },
            {
                'section_type': 'performance',
                'title': 'Performance & Scalability',
                'subtitle': 'Current benchmarks and optimization strategy',
                'order': 10,
                'is_pitch_deck': False,
                'is_technical': True,
                'live_data_source': 'docs_app.live_data.get_performance_data',
                'content': '''*Live performance metrics and scaling plans.*''',
            },
            {
                'section_type': 'security',
                'title': 'Security',
                'subtitle': 'Auth, RBAC, data protection, and compliance',
                'order': 11,
                'is_pitch_deck': False,
                'is_technical': True,
                'live_data_source': 'docs_app.live_data.get_security_data',
                'content': '''*Live security posture and controls.*''',
            },
            {
                'section_type': 'analytics',
                'title': 'Analytics & KPIs',
                'subtitle': 'Metrics that matter',
                'order': 12,
                'is_pitch_deck': False,
                'is_technical': True,
                'content': '''## Key Metrics

### Product Metrics
- **Weekly Active Organizations (WAO)** — North star
- **Scans per organization per week** — Engagement depth
- **Report generation rate** — AI adoption
- **MCP tool calls per session** — Agent integration usage

### Technical Metrics
- **Scan success rate** — Target > 95%
- **Average scan duration** — Target < 5 min
- **Log streaming latency** — Target < 2s
- **API p99 latency** — Target < 500ms

### Business Metrics
- **Monthly Recurring Revenue (MRR)**
- **Net Revenue Retention (NRR)**
- **Customer Acquisition Cost (CAC)**
- **LTV/CAC ratio**

### Dashboards
- Grafana for infrastructure
- Custom Django admin for business metrics
- MCP tool usage analytics
''',
            },
            {
                'section_type': 'changelog',
                'title': 'Changelog',
                'subtitle': 'Version history and notable changes',
                'order': 13,
                'is_pitch_deck': False,
                'is_technical': True,
                'live_data_source': 'docs_app.live_data.get_changelog_data',
                'content': '''*Live changelog from version history.*''',
            },
        ]
        
        all_sections = pitch_sections + tech_sections
        
        for sec_data in all_sections:
            section, created = DocSection.objects.get_or_create(
                section_type=sec_data['section_type'],
                defaults={
                    'title': sec_data['title'],
                    'subtitle': sec_data.get('subtitle', ''),
                    'content': sec_data['content'],
                    'content_type': 'markdown',
                    'order': sec_data['order'],
                    'is_active': True,
                    'is_pitch_deck': sec_data.get('is_pitch_deck', True),
                    'is_technical': sec_data.get('is_technical', True),
                    'live_data_source': sec_data.get('live_data_source', ''),
                }
            )
            if created:
                self.stdout.write(f'  Created section: {section.title}')
            else:
                # Update existing
                section.title = sec_data['title']
                section.subtitle = sec_data.get('subtitle', '')
                section.content = sec_data['content']
                section.order = sec_data['order']
                section.is_pitch_deck = sec_data.get('is_pitch_deck', True)
                section.is_technical = sec_data.get('is_technical', True)
                section.live_data_source = sec_data.get('live_data_source', '')
                section.save()
                self.stdout.write(f'  Updated section: {section.title}')
        
        # Create sample team members
        team_members = [
            {
                'name': 'Alex Chen',
                'role': 'founder',
                'email': 'alex@scanx.dev',
                'bio': 'Security researcher & bug bounty hunter. Built scanX to solve my own recon workflow pain.',
                'github': 'https://github.com/alexchen',
                'linkedin': 'https://linkedin.com/in/alexchen',
                'twitter': 'https://x.com/alexchen',
                'order': 1,
                'team_name': 'Core Team',
                'team_order': 1,
                'show_in_pitch': True,
                'show_in_tech': True,
            },
            {
                'name': 'Priya Sharma',
                'role': 'cto',
                'email': 'priya@scanx.dev',
                'bio': 'Backend engineer specializing in Django, async systems, and security tooling.',
                'github': 'https://github.com/priyasharma',
                'linkedin': 'https://linkedin.com/in/priyasharma',
                'order': 2,
                'team_name': 'Core Team',
                'team_order': 1,
                'show_in_pitch': True,
                'show_in_tech': True,
            },
            {
                'name': 'Marcus Johnson',
                'role': 'lead_engineer',
                'email': 'marcus@scanx.dev',
                'bio': 'Full-stack developer. Built the MCP integration and real-time log streaming.',
                'github': 'https://github.com/marcusj',
                'linkedin': 'https://linkedin.com/in/marcusj',
                'order': 3,
                'team_name': 'Core Team',
                'team_order': 1,
                'show_in_pitch': True,
                'show_in_tech': True,
            },
            {
                'name': 'Dr. Sarah Kim',
                'role': 'security_researcher',
                'email': 'sarah@scanx.dev',
                'bio': 'Application security expert. Defines recon methodology and Nuclei template strategy.',
                'github': 'https://github.com/sarahkim',
                'linkedin': 'https://linkedin.com/in/sarahkim',
                'order': 1,
                'team_name': 'Security Research',
                'team_order': 2,
                'show_in_pitch': True,
                'show_in_tech': True,
            },
            {
                'name': 'James Rodriguez',
                'role': 'ai_engineer',
                'email': 'james@scanx.dev',
                'bio': 'ML engineer focused on RAG, GraphRAG, and autonomous security agents.',
                'github': 'https://github.com/jamesrodriguez',
                'linkedin': 'https://linkedin.com/in/jamesrodriguez',
                'order': 2,
                'team_name': 'Security Research',
                'team_order': 2,
                'show_in_pitch': False,
                'show_in_tech': True,
            },
            {
                'name': 'Lisa Wang',
                'role': 'advisor',
                'email': 'lisa@scanx.dev',
                'bio': 'Former CISO at Fortune 500. Advises on enterprise requirements and compliance.',
                'linkedin': 'https://linkedin.com/in/lisawang',
                'order': 1,
                'team_name': 'Advisors',
                'team_order': 3,
                'show_in_pitch': True,
                'show_in_tech': False,
            },
        ]
        
        for member_data in team_members:
            member, created = TeamMember.objects.get_or_create(
                email=member_data['email'],
                defaults=member_data
            )
            if created:
                self.stdout.write(f'  Created team member: {member.name}')
            else:
                for key, value in member_data.items():
                    setattr(member, key, value)
                member.save()
                self.stdout.write(f'  Updated team member: {member.name}')
        
        self.stdout.write(self.style.SUCCESS('Documentation initialized successfully!'))
        self.stdout.write('Visit /docs/ to view the documentation.')
        self.stdout.write('Visit /docs/admin/ to manage content (staff only).')