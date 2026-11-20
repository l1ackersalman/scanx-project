# scanX — Full Architecture & Development Guide

> **Version:** 2.0 (post-rewrite) · **Date:** 2026-11-20
> This document describes the *actual implemented* architecture of scanX after the
> full rewrite (`10f7040`), and the development roadmap going forward.

---

## 1. System Overview

scanX is a **Django-based web application for authorized security reconnaissance**
that wraps a battle-tested Bash scanner (`scanner/scanx.sh`) in a modern web UI,
and exposes scan data + actions to AI agents via a built-in **MCP (Model Context
Protocol) server** over STDIO and HTTP/SSE.

```
┌────────────────────────────────────────────────────────────────────────┐
│                            USER BROWSER                                │
│              http://localhost:8000  (dark-first UI)                    │
└───────────────┬────────────────────────────────────────────────────────┘
                │ HTTP
┌───────────────▼───────────────────────────┐
│         DJANGO WEB PROCESS (8000)         │
│  scanx/urls.py → scanner/views.py         │
│  - Dashboard / Scan form                  │
│  - Live logs (1.5s offset polling)        │
│  - Organizations CRUD, Assets, Reports    │
│  - MCP HTTP start/status widget           │
└───────┬───────────────────────────────────┘
        │ Scan row (status=pending)
        ▼
┌───────────────────────────────────────────┐     ┌──────────────────────────┐
│              SQLite DATABASE              │◄────│   BACKGROUND WORKER      │
│  Scan · Program · Report                  │     │  manage.py worker        │
│  (httpx_results JSONField per scan)       │     │  - SELECT FOR UPDATE     │
└───────────────────────────────────────────┘     │    SKIP LOCKED claim     │
        ▲                                         │  - Runs scanx.sh         │
        │ mark_completed(stats)                   │  - Streams live.log      │
        │                                         └──────────┬───────────────┘
        │                                                    │ subprocess (list args,
        │                                                    │  no shell=True)
        │                                         ┌──────────▼───────────────┐
        │                                         │   scanx.sh (Bash)        │
        │                                         │   scan_data/<uuid>/      │
        │                                         │    └── <domain>/         │
        │                                         │        alldomains.txt    │
        │                                         │        live.txt          │
        │                                         │        httpx.json        │
        │                                         │        report.txt        │
        │                                         └──────────┬───────────────┘
        │                                                    │ exec
        │                              ┌─────────────────────┼────────────────┐
        │                              ▼          ▼          ▼                ▼
        │                          subfinder  assetfinder  chaos+crt   dnsx→httpx
        │
┌───────┴────────────────────────────────────────────────────────────────┐
│                        MCP SERVER (AI agents)                          │
│  scanner/mcp_server.py — MCP SDK "Server('scanx-mcp')"                 │
│  ├─ STDIO transport:  manage.py mcp_server        (local agents)       │
│  └─ HTTP/SSE:         manage.py mcp_server_http   (port 8001, /mcp)     │
│      6 tools · 3 resources · report generation                         │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Technology Stack

| Layer | Technology | Notes |
|---|---|---|
| Web framework | Django 5.x | `scanx/settings.py`, all config via env vars |
| Database | SQLite (dev) / PostgreSQL (prod via `DATABASE_URL`) | `dj_database_url` |
| Language | Python 3.10+ | |
| Scanner | Bash (`scanner/scanx.sh`) | Source of truth for recon pipeline |
| Recon tools | subfinder, assetfinder, chaos, crt, dnsx, httpx (Go binaries) | Installed by `scripts/install.sh` |
| MCP SDK | `mcp` Python SDK | `Server` + `streamable_http_app()` |
| MCP HTTP host | uvicorn (Starlette ASGI) | Port 8001, path `/mcp` |
| Process model | 1 web process + 1 worker process (+ optional MCP process) | `scripts/start.sh` |
| Frontend | Django templates (11), vanilla JS, CSS | No build step |
| Logging | Console + `scanx.log` file | `scanner` logger at DEBUG |

---

## 3. Project Structure (as implemented)

```
scanX/
├── manage.py
├── scanx/                        # Django project
│   ├── settings.py               # Env-driven config (SECRET_KEY, SCANX_DATA_DIR, …)
│   ├── urls.py                   # Root URLconf → scanner app
│   └── wsgi.py
├── scanner/                      # The single main app
│   ├── models.py                 # Scan, Program, Report
│   ├── views.py                  # All pages + JSON APIs (651 lines)
│   ├── services.py               # ScanExecutor, log streaming, aggregation (658 lines)
│   ├── urls.py                   # 20 URL patterns
│   ├── admin.py                  # Admin registration
│   ├── scanx.sh                  # Bash recon pipeline (source of truth)
│   ├── mcp_server.py             # MCP server: resources + tools + reports (507 lines)
│   ├── migrations/0001…0009      # Schema evolution
│   ├── tests/                    # test_services.py, test_views.py
│   └── management/commands/
│       ├── worker.py             # Background scan worker (claim + execute)
│       ├── check_tools.py        # Tool dependency verification
│       ├── mcp_server.py         # MCP over STDIO
│       └── mcp_server_http.py    # MCP over HTTP/SSE (uvicorn, :8001)
├── core/                         # Shared utilities
│   ├── validators.py             # RFC 1035/1123 domain validation + injection guard
│   └── middleware.py             # NoCacheMiddleware
├── templates/                    # 11 templates (overview, scan_detail, reports, mcp_guide…)
├── static/                       # CSS / JS / images
├── scripts/
│   ├── install.sh                # venv + deps + Go tools + migrations + collectstatic
│   └── start.sh                  # Dev launcher (web + worker)
├── scan_data/                    # Runtime scan outputs (gitignored)
│   └── <scan-uuid>/<domain>/     # alldomains.txt · live.txt · httpx.json · report.txt
├── .env                          # Secrets (never committed)
├── requirements.txt
├── README.md
└── ARCHITECTURE.md               # ← this document
```

---

## 4. Data Model

### 4.1 `Program` — authorized organization
| Field | Type | Notes |
|---|---|---|
| `id` | BigAutoField | |
| `name` | CharField(255) | Organization / target name |
| `description` | TextField | Optional |
| `organization_type` | CharField | 17 choices (fintech, healthcare, government, …) |
| `created_at` | DateTimeField | Indexed by type |

### 4.2 `Scan` — one recon run of one domain
| Field | Type | Notes |
|---|---|---|
| `id` | **UUID** (PK) | Also the `scan_data/` directory name |
| `domain` | CharField(253) | Validated by `core.validators.validate_domain` |
| `status` | pending → running → completed / failed / cancelled | Indexed (status, -created_at) |
| `output_dir` | CharField(512) | Relative to `SCANX_DATA_DIR` (= scan UUID) |
| `program` | FK → Program, `SET_NULL` | Authorization link |
| `authorized`, `authorized_by` | Bool / Char | Authorization tracking |
| `total_subdomains`, `live_subdomains`, `http_success`, `http_failed` | IntegerField | Parsed post-scan |
| `httpx_results` | **JSONField** | Full httpx JSON-lines array (url, status-code, title, tech, ip, cname) |
| `error_message`, `started_at`, `completed_at` | | Lifecycle |

Model helpers: `mark_running()`, `mark_completed(**stats)`, `mark_failed()`,
`mark_cancelled()`, `is_terminal`, `duration_display`, `get_artifact_path()`.

### 4.3 `Report` — AI/MCP analysis of a scan
| Field | Type | Notes |
|---|---|---|
| `id` | UUID (PK) | |
| `scan` | FK → Scan, `CASCADE` | `related_name='reports'` |
| `report_type` | attack_surface / vulnerability / technology_exposure / attack_vector / custom | |
| `title`, `summary`, `content` (Markdown), `findings` (JSON) | | |
| `status` | generating → completed / failed | |
| `generated_by` | Char(100) | "MCP Agent" |

> **Design note:** per-scan results live in a denormalized `httpx_results`
> JSONField. This keeps the schema simple but forces Python-side aggregation
> (see §7.3). A normalized asset model is a roadmap item (§12, Phase D).

---

## 5. Scan Lifecycle (end-to-end flow)

```
Browser        Django           Worker            scanx.sh         Tools
   │ POST /start/  │                │                  │               │
   │──────────────►│ validate domain│                  │               │
   │               │ create Scan(pending)              │               │
   │◄──────────────│ redirect to /scan/<uuid>/         │               │
   │               │                │                  │               │
   │               │   poll loop    │                  │               │
   │               │                │ claim (SKIP LOCKED)              │
   │               │                │ mark_running()   │               │
   │               │                │ Popen([scanx.sh, domain], cwd=scan_data/<uuid>/)
   │               │                │─────────────────►│ subfinder    │
   │               │                │   stream stdout  │ assetfinder  │
   │               │                │   → live.log     │ chaos / crt  │
   │ GET /scan/<id>/logs/?offset=N  │   (line-buffered)│ sort -u      │
   │──────────────►│ read live.log from offset        │ dnsx         │
   │◄──────────────│ {lines, offset, status}          │ httpx -json  │
   │    (1.5s)     │                │                  │               │
   │               │                │ refresh_from_db() per line:        │
   │ POST /scan/<id>/cancel/        │   status==CANCELLED → terminate() │
   │──────────────►│ mark_cancelled │                  │               │
   │               │                │ exit 0 → parse stats + httpx.json │
   │               │                │ mark_completed(total, live, http, httpx_results)
   │               │                │ exit≠0/timeout → mark_failed()    │
   │               │                │                  │               │
   │ GET /scan/<uuid>/              │                  │               │
   │──────────────►│ stats cards + results table + "NEW" badge        │
   │               │ (vs previous scans of same domain)                │
```

Key mechanics:
- **Atomic claim** — worker uses `select_for_update(skip_locked=True)` so multiple
  workers never run the same scan.
- **Cancellation** — cooperative: the executor re-reads the Scan row every output
  line; web cancel sets status → executor terminates the subprocess.
- **Timeout** — `SCAN_TIMEOUT` (default 3600s) enforced via `Popen.wait(timeout)`.
- **Artifact contract** — executor locates the script's output dir by scanning
  `scan_data/<uuid>/` for a dir named `<domain>` or `<domain>-NN`, then parses
  `alldomains.txt`, `live.txt`, `httpx.json` (JSON-lines) into model stats.

---

## 6. Reconnaissance Pipeline (`scanner/scanx.sh`)

| Stage | Tool | Output |
|---|---|---|
| 1. Subdomain enumeration | `subfinder -d <domain>` | `subfinder.txt` |
| 2. Subdomain enumeration | `assetfinder --subs-only <domain>` | `assetfinder.txt` |
| 3. Subdomain enumeration | `chaos -d <domain> -key $CHAOS_API_KEY` | `chaos.txt` |
| 4. Certificate transparency | `crt -s <domain>` | `crt.txt` |
| 5. Dedup/normalize | `sort -u` of all four | `alldomains.txt` |
| 6. DNS resolution | `dnsx -l alldomains.txt` | `live.txt` |
| 7. HTTP probing | `httpx -sc -title -tech-detect -ip -cname -probe -json` | `httpx.json` |

All console output is `tee`-ed into `report.txt` (full run transcript).
Environment: `CHAOS_API_KEY` injected by `ScanExecutor._prepare_environment()`;
`TOOLS_PATH` prepended to `PATH`.

---

## 7. Web Application Layer

### 7.1 URL surface (`scanner/urls.py`)
| Method | Path | View |
|---|---|---|
| GET | `/` | redirect → `/overview/` |
| GET | `/overview/` | Dashboard: scan form + recent scans |
| POST | `/start/` | Validate domain + program → create Scan |
| GET | `/history/` | Paginated scan history |
| GET | `/scan/<uuid>/` | Live logs (running) or results (completed) |
| GET | `/scan/<uuid>/logs/` | JSON: `{lines, offset, status}` since offset |
| POST | `/scan/<uuid>/cancel/` | Mark cancelled |
| GET/POST | `/organizations/(add\|edit/<id>\|delete/<id>/)` | Program CRUD |
| GET | `/organizations/<id>/` | Per-domain aggregate stats |
| GET | `/assets/` | Global stats + technology breakdown |
| GET | `/assets/tech/?tech=` | Subdomains using a technology |
| GET | `/reports/`, `/reports/<uuid>/`, `/reports/<uuid>/download/` | MCP reports |
| GET | `/mcp/` | MCP integration guide page |
| GET/POST | `/mcp/status/`, `/mcp/start/` | MCP HTTP server control |

### 7.2 `services.py` responsibilities
- `ScanExecutor` — subprocess lifecycle, env prep, log streaming, stat parsing.
- `get_log_lines(scan_id, offset)` — offset-based incremental log reads.
- `get_scan_artifacts(scan)` — resolve artifact paths for download.
- Aggregation: `get_program_statistics()`, `get_assets_overview()`,
  `get_technology_breakdown()`, `get_technology_subdomains()`,
  `get_programs_with_stats()`.
- Deltas: `get_previous_scan_urls()`, `mark_new_subdomains()` → "NEW" badge.

### 7.3 Aggregation strategy
Because results are stored as JSON arrays per scan, aggregation iterates scans
in Python (`httpx_results`) with in-memory dicts/sets + Django `Paginator`.
Fine for hundreds of scans; will need the normalized model (§12 Phase D) or
caching for thousands.

---

## 8. MCP Server (`scanner/mcp_server.py`)

A single `Server("scanx-mcp")` instance with two transports:

| Transport | Command | Endpoint |
|---|---|---|
| STDIO | `python manage.py mcp_server` | stdin/stdout (local clients, e.g. Claude Desktop) |
| Streamable HTTP/SSE | `python manage.py mcp_server_http [--host --port]` | `http://<host>:8001/mcp` via uvicorn |

The web UI can start the HTTP server as a background subprocess
(`POST /mcp/start/` → `Popen([sys.executable, "manage.py", "mcp_server_http", ...])`)
and poll `GET /mcp/status/` (socket probe of port 8001).

### 8.1 Resources (read-only)
| URI | Content |
|---|---|
| `scanx://organizations` | All programs with type/description |
| `scanx://scans/recent` | 20 most recent scans incl. stats |
| `scanx://technologies` | Technology breakdown (by count) |

### 8.2 Tools (actions)
| Tool | Purpose |
|---|---|
| `get_scan_details(scan_id)` | Full scan record + `httpx_results` |
| `get_organization_scans(organization_id)` | All scans of a program |
| `search_subdomains(pattern[, organization_type])` | Wildcard search (`*` → `.*`), max 100 |
| `analyze_attack_surface(domain)` | Aggregated subdomains/techs/IPs for a domain |
| `get_technology_exposure(technology)` | All hosts using a technology |
| `create_report(scan_id, report_type, title, prompt)` | Creates `Report`, generates Markdown + JSON findings, returns report URL + download URL |

### 8.3 Report generation
`create_report` is currently **deterministic template generation** (not an LLM
call): it builds context + findings dicts from the scan, then renders
type-specific Markdown (`_generate_report_content`). The *actual* AI analysis
is expected from the MCP client agent, which can read resources/tools and write
reports through `create_report` with a custom prompt.

---

## 9. Security Architecture

| Control | Implementation |
|---|---|
| Domain validation | `core/validators.py`: RFC 1035/1123 regex, shell-metachar block, path-traversal block |
| No shell injection | `subprocess.Popen([...])` list args, `shell=False` everywhere (web + worker) |
| Isolation | Each scan in `scan_data/<uuid>/<domain>/`; cwd confined |
| Secrets | `.env` only (`SECRET_KEY`, `CHAOS_API_KEY`, `DATABASE_URL`) — gitignored |
| Tool PATH | `TOOLS_PATH` env, appended at subprocess level |
| Timeout | `SCAN_TIMEOUT` hard kill on runaway scans |
| Auth | ⚠️ **None** — no Django login, no MCP auth (see §11 gaps) |
| MCP binding | ⚠️ defaults `0.0.0.0:8001` (see §11 gaps) |

---

## 10. Configuration Reference (`.env`)

| Var | Default | Purpose |
|---|---|---|
| `DEBUG` | True | Django debug |
| `SECRET_KEY` | dev fallback | Django secret |
| `ALLOWED_HOSTS` | localhost,127.0.0.1 | Host header allowlist |
| `SCANX_DATA_DIR` | `./scan_data` | Scan artifact root |
| `CHAOS_API_KEY` | — | chaos tool API key (injected to subprocess env) |
| `TOOLS_PATH` | — | Extra PATH for Go binaries |
| `SCAN_TIMEOUT` | 3600 | Max scan seconds |
| `DATABASE_URL` | sqlite:///db.sqlite3 | DB (PostgreSQL in prod) |

---

## 11. Known Gaps & Issues (found in this review)

| # | Severity | Issue |
|---|---|---|
| G1 | **High** | MCP HTTP server binds `0.0.0.0` by default and has **no authentication** — anyone who can reach port 8001 can read all scan data and create reports. Should default to `127.0.0.1` + optional bearer token. |
| G2 | High | No Django authentication — the whole app (including cancel/delete) is unauthenticated. |
| G3 | Medium | `scanx.sh` hardcodes `/home/insomniax/go/bin/httpx` — breaks portability; should use `httpx` from `TOOLS_PATH`. |
| G4 | Medium | Attack-surface report section prints `findings.get('subdomains_found', 0)` but that key is never set → always shows 0. |
| G5 | Medium | `views.mcp_http_status` references `settings.MCP_VPS_IP` which is not defined in `settings.py` (silently `None` via getattr). |
| G6 | Low | `run_scan_in_background()` in `services.py` is dead code — the worker is now the only execution path. |
| G7 | Low | No tests for the MCP server (tools/resources/report generation). |
| G8 | Low | Python-side aggregation over JSONField will not scale past ~1k scans (Phase D fixes). |
| G9 | Info | Report generation is template-based; true LLM synthesis happens client-side (MCP agent) or is a future server-side integration. |

---

## 12. Development Roadmap (next phases)

### Phase A — Security Hardening *(do first)*
- [ ] MCP HTTP default bind `127.0.0.1`; `MCP_ALLOWED_HOSTS` env override
- [ ] Optional `MCP_AUTH_TOKEN` bearer check on `/mcp`
- [ ] Optional Django login (`LOGIN_REQUIRED` toggle) for destructive endpoints
- [ ] Fix G3 (httpx path) and G4 (subdomains_found key)
- **Deliverable:** localhost-safe defaults, portable installer

### Phase B — MCP Enhancement (tools ↔ app parity)
- [ ] New tools: `start_scan(domain, organization_id)`, `cancel_scan(scan_id)`,
      `get_scan_progress(scan_id)` (live tail), `list_organizations()`,
      `get_scan_artifacts(scan_id)` (inline text artifacts)
- [ ] Resource templates: `scanx://scans/{id}`, `scanx://organizations/{id}/scans`
- [ ] MCP prompts: `attack_surface_review`, `scope_check`, `report_from_scan`
- [ ] MCP server tests (tools list/call, resource read, report flow)
- **Deliverable:** an agent can run a full recon workflow without the web UI

### Phase C — Normalized Asset Store (scalability)
- [ ] Models: `Subdomain`, `Asset`(http), `Technology` (M2M), `DNSRecord`
- [ ] Ingest `httpx.json` into relational rows at `mark_completed()`
- [ ] SQL aggregation replaces Python loops (G8); keep JSONField as raw archive
- **Deliverable:** instant cross-scan queries, historical diffing per host

### Phase D — Scheduling & Automation
- [ ] Recurring scans (`interval` on Program), scheduler in worker loop
- [ ] Change detection: new/removed subdomains + tech drift between runs
- [ ] Optional webhook/notification on completion

### Phase E — Real AI Analysis (optional)
- [ ] Server-side LLM synthesis for reports (env-configured provider) **or**
      documented agent-in-the-loop workflow (client LLM via MCP)
- [ ] Finding severity model + prioritization

### Phase F — Packaging & Deployment
- [ ] Multi-container: `docker-compose` (web / worker / mcp-http / postgres)
- [ ] Pinned tool versions at build time (reproducible installs)
- [ ] CI: run `manage.py test` + `check_tools --dry-run` on push

> **Order agreed with user:** one by one, starting with **Phase A → B**.

---

## 13. Operations Cheat-Sheet

```bash
./scripts/install.sh                       # one-time setup (venv, Go tools, migrations)
nano .env                                  # set CHAOS_API_KEY
./scripts/start.sh                         # web (8000) + worker

python manage.py check_tools --install-hints   # verify binaries
python manage.py worker --interval 2           # standalone worker
python manage.py mcp_server                    # MCP over STDIO
python manage.py mcp_server_http --host 127.0.0.1 --port 8001   # MCP over HTTP/SSE

python manage.py test                      # test suite
./scanner/scanx.sh example.com             # run scanner manually
```

**MCP client config (Claude Desktop / any MCP client, STDIO):**
```json
{
  "mcpServers": {
    "scanx": {
      "command": "/path/to/scanX/venv/bin/python",
      "args": ["/path/to/scanX/manage.py", "mcp_server"]
    }
  }
}
```

**MCP over HTTP (remote agent):** endpoint `http://<host>:8001/mcp`
(keep it on localhost or behind a reverse proxy with auth until Phase A lands).
