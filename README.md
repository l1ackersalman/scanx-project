# scanX

[![Django](https://img.shields.io/badge/Django-5.x-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://python.org/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Security](https://img.shields.io/badge/Purpose-Authorized%20Security%20Testing-red.svg)](#security--scope)

> **Portable, Django-based web application for authorized security reconnaissance.**  
> Wraps a battle-tested Bash reconnaissance script in a modern web interface with live log streaming, scan history, artifact downloads, and AI-powered analysis reports.

---

## 🎯 Features

### Core Scanning
- **Dashboard** — Start new scans with domain validation and organization selection
- **Live Logs** — Real-time streaming of scanner output via background worker (1.5s polling)
- **Scan History** — Paginated list of all scans with status, timestamps, and statistics
- **Artifact Downloads** — Download `alldomains.txt`, `live.txt`, `httpx.json`, `report.txt`

### Organization & Asset Management
- **Organizations (Programs)** — CRUD for authorized target organizations with 17 industry types
- **Program Detail** — Aggregate statistics per domain within an organization
- **Assets View** — Cross-program technology breakdown with search & pagination
- **Technology Detail** — All subdomains using a specific technology across programs

### AI-Powered Analysis (MCP Integration)
- **Report Generation** — 5 report types: Attack Surface, Vulnerability Assessment, Technology Exposure, Attack Vector, Custom
- **MCP HTTP Server** — Built-in management (start/status on port 8001)
- **Structured Findings** — Markdown content + JSON findings with download support

### Security & Operations
- **Dark-first UI** — Lime-green accent, responsive design, theme toggle (dark/light)
- **Portable** — Works on any Linux device with configurable paths via `.env`
- **Secure** — No shell injection, isolated scan directories, strict input validation
- **No-cache Middleware** — Prevents stale UI during long-running scans

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    scanX Django App                          │
├─────────────────────────────────────────────────────────────┤
│  Dashboard (scan form + history)                            │
│  Scan Detail (live logs + stats + downloads)                │
│  API: /scan/<id>/logs/ (polling for live output)            │
└──────────────────────────┬──────────────────────────────────┘
                           │
          ┌─────────────────┴─────────────────┐
          ▼                                   ▼
┌─────────────────────┐             ┌─────────────────────┐
│  Django Web Process │             │  Worker Process     │
│  (gunicorn/runserver)            │  (manage.py worker) │
│  - Handles HTTP     │             │  - Polls DB for     │
│  - Creates Scan     │             │    pending scans    │
│  - Serves UI        │             │  - Runs scanx.sh    │
└─────────────────────┘             └─────────────────────┘
                           │
                           ▼
              ┌─────────────────────────────┐
              │     Scan Data Directory     │
              │  (SCANX_DATA_DIR)           │
              │  scan_data/<scan_id>/       │
              │    ├── <domain>/            │
              │    │   ├── alldomains.txt   │
              │    │   ├── live.txt         │
              │    │   ├── httpx.json       │
              │    │   └── report.txt       │
              │    └── live.log (streaming) │
              └─────────────────────────────┘
```

---

## 🚀 Quick Start

```bash
# Clone and enter
git clone <repo-url> scanX
cd scanX

# Run installer (installs deps, sets up venv, Go tools, database)
./scripts/install.sh

# Edit .env with your Chaos API key
nano .env

# Start development server + background worker
./scripts/start.sh

# Open http://localhost:8000
```

### What the installer does:
1. ✅ Checks Python 3.10+, Git, Go
2. ✅ Creates virtual environment (`venv/`)
3. ✅ Installs Python dependencies (`requirements.txt`)
4. ✅ Installs Go reconnaissance tools (subfinder, assetfinder, chaos, dnsx, httpx, crt)
5. ✅ Installs `figlet` (ASCII banners)
6. ✅ Creates `.env` from `.env.example`
7. ✅ Runs Django migrations
8. ✅ Collects static files
9. ✅ Verifies all tools with `python manage.py check_tools`

---

## ⚙️ Configuration

All settings via `.env` file (copy from `.env.example`):

```bash
# Django
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Data directory (absolute path recommended for production)
SCANX_DATA_DIR=/var/lib/scanx

# Chaos API key (required for chaos tool - get from chaos.projectdiscovery.io)
CHAOS_API_KEY=your-chaos-api-key

# Additional PATH for Go tools (colon-separated)
TOOLS_PATH=/usr/local/go/bin:$HOME/go/bin

# Maximum scan execution time in seconds
SCAN_TIMEOUT=3600

# Database (SQLite default, use PostgreSQL for production)
DATABASE_URL=sqlite:///db.sqlite3
```

---

## 🔧 External Tools Required

The Bash scanner (`scanner/scanx.sh`) depends on these tools:

| Tool | Purpose | Install Command |
|------|---------|-----------------|
| `figlet` | ASCII banner | `apt install figlet` |
| `subfinder` | Subdomain enumeration | `go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest` |
| `assetfinder` | Subdomain enumeration | `go install -v github.com/tomnomnom/assetfinder@latest` |
| `chaos` | Chaos dataset client | `go install -v github.com/projectdiscovery/chaos-client/cmd/chaos@latest` |
| `crt` | Certificate transparency | `go install -v github.com/projectdiscovery/crt/cmd/crt@latest` |
| `dnsx` | DNS resolution | `go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest` |
| `httpx` | HTTP probing | `go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest` |

> The installer script (`./scripts/install.sh`) attempts to install these automatically.

---

## 📖 Usage Guide

### Starting a Scan
1. Navigate to **Dashboard** (Overview)
2. **Add an Organization** first (required) — click "Organizations" → "Add Organization"
3. Enter target **domain** (e.g., `example.com`)
4. Select the **Organization** from dropdown
5. Click **Start Scan**

### Monitoring a Scan
- **Live Logs** — Real-time output from all reconnaissance tools
- **Status Badge** — Pending → Running → Completed/Failed
- **Stop Scan** — Cancel a running scan at any time

### Viewing Results (after completion)
- **Statistics Cards** — Total subdomains, live hosts, HTTP success/failed, technologies found
- **HTTP Results Table** — Filterable by Status Code, Technology, IP, CNAME
- **Pagination** — 50 results per page
- **"New" Badge** — Subdomains not seen in previous scans of same domain
- **Artifact Downloads** — Raw output files for further analysis

### Managing Organizations
- **Organizations Page** — List all with scan statistics
- **Add/Edit/Delete** — Full CRUD with 17 industry types
- **Program Detail** — Per-domain aggregate metrics + scan history

### Assets & Technology Analysis
- **Assets Page** — Global statistics + technology breakdown
- **Technology Detail** — Click any technology to see all subdomains using it across programs

### AI Reports (MCP)
- **MCP HTTP Server** — Start from Dashboard widget (runs on port 8001)
- **Reports Page** — List all generated reports
- **Report Detail** — View Markdown content + structured JSON findings
- **Download** — Export as `.md` file

---

## 🛠 Development

```bash
# Run tests
python manage.py test

# Check tools (with install hints)
python manage.py check_tools --install-hints

# Run worker only (for debugging)
python manage.py worker --interval 2

# Django shell
python manage.py shell

# Create superuser for admin
python manage.py createsuperuser

# Run development server only
python manage.py runserver 0.0.0.0:8000
```

### Project Structure
```
scanX/
├── manage.py                 # Django CLI
├── scanx/                    # Project settings
│   ├── settings.py           # All config via env vars
│   ├── urls.py               # Root URLconf
│   └── wsgi.py
├── scanner/                  # Main app
│   ├── models.py             # Scan, Program, Report models
│   ├── views.py              # Dashboard, detail, logs, orgs, assets, reports
│   ├── services.py           # ScanExecutor, log streaming, aggregation
│   ├── urls.py               # Scanner URL patterns
│   ├── scanx.sh              # Bash reconnaissance script (source of truth)
│   └── management/commands/
│       ├── worker.py         # Background scan worker
│       └── check_tools.py    # Dependency verification
├── core/                     # Shared utilities
│   ├── validators.py         # Domain validation (RFC + safety)
│   └── middleware.py         # No-cache middleware
├── templates/                # 11 Django templates
├── static/                   # CSS, JS, images
├── scripts/
│   ├── install.sh            # Full installation
│   └── start.sh              # Dev server + worker launcher
├── scan_data/                # Runtime scan outputs (gitignored)
├── .env.example              # Config template
├── requirements.txt
└── README.md
```

---

## 🔒 Security & Scope

> **⚠️ FOR AUTHORIZED SECURITY TESTING ONLY**

| Control | Implementation |
|---------|----------------|
| **Authorization Required** | Every scan requires explicit organization selection |
| **Domain Validation** | RFC 1035/1123 regex + shell metacharacter blocking + path traversal checks |
| **No Shell Injection** | Subprocess args passed as list, never `shell=True` |
| **Isolated Directories** | Each scan in `scan_data/<uuid>/<domain>/` |
| **Secrets in Env Vars** | `CHAOS_API_KEY`, `SECRET_KEY`, `DATABASE_URL` in `.env` (never in code) |
| **Rate Limiting** | Configure at reverse proxy level (Nginx) |
| **No Data Exfiltration** | Only PoC-level output stored; no automatic external transmission |

### Legal & Ethical
- Only test targets you have **explicit written authorization** for
- Respect program scope, rate limits, and testing rules
- Disclose findings responsibly — no public disclosure before patch
- This tool is a **reconnaissance aid**, not an exploitation framework

---

## 🚢 Production Deployment

### 1. Environment
```bash
DEBUG=False
SECRET_KEY=strong-random-key-here
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
SCANX_DATA_DIR=/var/lib/scanx
DATABASE_URL=postgres://user:pass@localhost:5432/scanx
CHAOS_API_KEY=your-production-key
```

### 2. Database (PostgreSQL)
```bash
# Install PostgreSQL client
pip install psycopg2-binary

# Run migrations
python manage.py migrate
```

### 3. Static Files
```bash
python manage.py collectstatic --noinput
# Configure Nginx to serve /static/ from STATIC_ROOT
```

### 4. Gunicorn (Web Process)
```bash
gunicorn scanx.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 3 \
  --timeout 120 \
  --access-logfile /var/log/scanx/access.log \
  --error-logfile /var/log/scanx/error.log
```

### 5. Systemd Service (Worker)
```ini
# /etc/systemd/system/scanx-worker.service
[Unit]
Description=scanX Background Worker
After=network.target

[Service]
Type=simple
User=scanx
WorkingDirectory=/opt/scanX
EnvironmentFile=/opt/scanX/.env
ExecStart=/opt/scanX/venv/bin/python manage.py worker
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now scanx-worker
```

### 6. Nginx Reverse Proxy
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /static/ {
        alias /opt/scanX/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # For long-running scan logs
        proxy_read_timeout 3600s;
        proxy_send_timeout 3600s;
    }
}
```

### 7. SSL (Let's Encrypt)
```bash
sudo certbot --nginx -d your-domain.com
```

---

## 📝 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Dashboard (redirects to overview) |
| `GET` | `/overview/` | Dashboard with scan form + history |
| `POST` | `/start/` | Start new scan |
| `GET` | `/history/` | Scan history (paginated) |
| `GET` | `/scan/<uuid>/` | Scan detail with live logs / results |
| `GET` | `/scan/<uuid>/logs/` | Live log streaming API (polling) |
| `POST` | `/scan/<uuid>/cancel/` | Stop running scan |
| `GET` | `/organizations/` | Organizations list with stats |
| `GET/POST` | `/organizations/add/` | Create organization |
| `GET/POST` | `/organizations/edit/<id>/` | Edit organization |
| `POST` | `/organizations/delete/<id>/` | Delete organization |
| `GET` | `/organizations/<id>/` | Program detail with domain stats |
| `GET` | `/assets/` | Global assets overview + tech breakdown |
| `GET` | `/assets/tech/?tech=<name>` | Technology detail page |
| `GET` | `/reports/` | Reports listing |
| `GET` | `/reports/<uuid>/` | Report detail |
| `GET` | `/reports/<uuid>/download/` | Download report as Markdown |
| `GET` | `/mcp/` | MCP Guide |
| `GET` | `/mcp/status/` | MCP HTTP server status (JSON) |
| `POST` | `/mcp/start/` | Start MCP HTTP server |

---

## 🧪 Testing the Scanner Manually

```bash
# Activate venv
source venv/bin/activate

# Run scanner directly (for debugging)
./scanner/scanx.sh example.com

# Check outputs
cat scan_data/<scan_id>/example.com/alldomains.txt
cat scan_data/<scan_id>/example.com/live.txt
cat scan_data/<scan_id>/example.com/httpx.json | jq .
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make small, focused commits
4. Run tests: `python manage.py test`
5. Run checks: `python manage.py check_tools`
6. Update documentation if needed
7. Submit a Pull Request

### Commit Guidelines
- Keep `main` stable
- Use conventional commits (`feat:`, `fix:`, `docs:`, `refactor:`)
- Never commit `.env`, secrets, databases, or `scan_data/`
- **Do not push to GitHub without explicit permission**

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

> **Disclaimer**: This tool is for **authorized security testing only**. The authors are not responsible for any misuse or damage caused by this software. Always ensure you have explicit written permission before scanning any target.

---

## 🙏 Acknowledgments

- **ProjectDiscovery** — For the excellent reconnaissance toolkit (subfinder, dnsx, httpx, chaos, crt)
- **tomnomnom** — For assetfinder
- **Django** — For the robust web framework
- **Inter & JetBrains Mono** — For the beautiful typography

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-repo/scanX/issues)
- **Documentation**: See `CLAUDE.md` for development guidelines
- **MCP Guide**: Visit `/mcp/` in the running application

---

<p align="center">
  <strong>scanX — Discover. Analyze. Prioritize. Protect.</strong><br>
  <em>"Identify security weaknesses before attackers exploit them."</em>
</p>