# scanX Documentation App

A comprehensive, live documentation system for scanX that combines:

1. **YC-Style Pitch Deck** — Business-focused presentation
2. **Technical Documentation** — Deep-dive engineering reference
3. **Live Data Integration** — Real-time system state
4. **Admin-Controlled Publishing** — Scheduling, visibility toggles, access control
5. **Team Showcase** — Uniform profile cards with consistent styling
6. **Export Capabilities** — PDF, Markdown, HTML

## Features

### Pitch Deck View (`/docs/?view=pitch`)
- Problem, Solution, Why Now, Product Demo, Market Opportunity
- Business Model, Traction, Competition, Unique Advantage
- Go-To-Market, Team, Vision

### Technical Docs View (`/docs/?view=tech`)
- Product Overview, Feature Matrix (live)
- Architecture Diagram (live Mermaid), Data Flow
- Technology Stack (live), API Documentation (live)
- Data Layer, AI Layer, Product Roadmap
- Performance & Scalability, Security, Analytics
- Changelog (live)

### Access Control & Scheduling
- **Master Toggle**: Enable/disable public access instantly
- **Scheduled Publishing**: Start/end dates with timezone support
- **Duration-Based**: Alternative to end date (e.g., "7 days from start")
- **Default Window**: Pre-configured June 10-14 judging window
- **Custom Messages**: Disabled message, scheduled message with placeholders
- **Admin Override**: Staff always have access
- **Quick Presets**: Judging window, investor preview, always on, turn off

### Team Showcase
- Uniform profile cards (circular avatars, consistent sizing)
- Role-based categorization (17 predefined roles + custom)
- Team grouping (Core Team, Security Research, Advisors, etc.)
- Social links (LinkedIn, GitHub, Twitter)
- Fallback avatar for missing images
- Separate visibility controls for pitch vs tech views

### Live Data Integration
Each technical section can pull real-time data:
- `feature_matrix` — Current feature status from scanner
- `architecture` — System components and data flows
- `tech_stack` — Actual versions from environment
- `api_docs` — Endpoints from URL patterns
- `data_layer` — Storage stats and privacy info
- `ai_layer` — MCP tools and report stats
- `performance` — Benchmarks and bottlenecks
- `security` — Auth, validation, execution safety
- `roadmap` — Short/mid/long term plans
- `changelog` — Version history

### Export Options
- **Markdown** — Clean, version-control friendly
- **HTML** — Self-contained with styling, printable to PDF
- **PDF** — Via browser print (HTML export optimized for print)

### Admin Interface (`/docs/admin/`)
- Section management (CRUD, drag-drop reorder, live data config)
- Team member management (CRUD, image upload, visibility toggles)
- Access control panel (schedule, presets, messages)
- Global settings (branding, theme colors, features, SEO)
- Version history for sections

## Installation

The docs app is included in the main scanX project:

```python
# scanx/settings.py
INSTALLED_APPS = [
    ...
    "docs_app",
]
```

```python
# scanx/urls.py
urlpatterns = [
    ...
    path("docs/", include("docs_app.urls")),
]
```

Run migrations:
```bash
python manage.py migrate
```

Initialize default content:
```bash
python manage.py init_docs
```

Collect static files:
```bash
python manage.py collectstatic
```

## Usage

### Public Documentation
Visit `/docs/` — switches between pitch deck and technical views via header toggle.

### Admin Panel
Visit `/docs/admin/` (staff only) — manage all content, access control, settings.

### API Endpoints
- `GET /docs/api/sections/` — List active sections
- `GET /docs/api/access/` — Current access status
- `GET /docs/export/?format=markdown|html|pdf&view=pitch|tech` — Export documentation

### Access Control Examples

**Enable for judging (June 10-14):**
```python
from docs_app.models import DocAccessControl
from django.utils import timezone
import pytz

ac = DocAccessControl.get_instance()
tz = pytz.timezone('Asia/Dhaka')
ac.is_enabled = True
ac.schedule_start = tz.localize(datetime(2026, 6, 10, 0, 0))
ac.schedule_end = tz.localize(datetime(2026, 6, 14, 23, 59, 59))
ac.save()
```

**Investor preview (7 days from now):**
```python
ac = DocAccessControl.get_instance()
ac.is_enabled = True
ac.schedule_start = timezone.now()
ac.use_duration = True
ac.duration_days = 7
ac.save()
```

**Disable completely:**
```python
ac = DocAccessControl.get_instance()
ac.is_enabled = False
ac.save()
```

## Models

### DocSection
Individual documentation section with:
- Section type (25 predefined types for pitch + tech)
- Markdown/HTML/Mermaid content
- Live data source integration
- Pitch deck / technical view visibility
- Version history

### DocAccessControl
Singleton for access control:
- Master enabled/disabled toggle
- Schedule start/end datetime
- Duration-based alternative
- Custom messages
- Default window presets

### TeamMember
Team showcase with:
- Name, role (17 types + custom), email, bio
- Profile image (auto-cropped to circle)
- Social links (LinkedIn, GitHub, Twitter)
- Team grouping and ordering
- Per-view visibility (pitch/tech)

### DocSettings
Global settings singleton:
- Site title, tagline, logo, favicon
- Primary/accent colors
- Feature toggles (search, export, TOC)
- SEO meta, analytics
- Maintenance mode

### DocVersion
Section version history:
- Content snapshots
- Change notes
- Published status

### DocExport
Export audit trail:
- Format, sections, requester
- IP, user agent, timestamp

## Live Data Providers

Located in `docs_app/live_data.py`. Each provider is a function that takes a config dict and returns a context dict for template rendering.

To add a new provider:
```python
# In live_data.py
def get_my_data(config=None):
    return {"my_key": "my_value"}

LIVE_DATA_PROVIDERS = {
    ...
    "my_data": get_my_data,
}
```

Then in admin, set section's `live_data_source` to `docs_app.live_data.get_my_data`.

## Customization

### Adding New Section Types
1. Add to `DocSection.SectionType` choices
2. Create default content via `init_docs` command or admin
3. Update templates if needed

### Adding Team Roles
1. Add to `TeamMember.Role` choices
2. Run migration

### Styling
CSS variables in `docs_app/static/docs/css/docs.css`:
- `--sx-primary` — Lime green (default #76B900)
- `--sx-accent` — Emerald (default #35B779)
- Dark-first color scheme
- Responsive breakpoints at 1200px, 768px

### Export Styling
Export templates in `docs_app/templates/docs/export.html` use same CSS variables, optimized for print.

## Testing

```bash
# Run docs app tests
python manage.py test docs_app

# Run all tests
python manage.py test
```

## Architecture

```
docs_app/
├── management/commands/init_docs.py  # Initialize default content
├── live_data.py                      # Live data providers
├── models.py                         # DocSection, DocAccessControl, TeamMember, etc.
├── views.py                          # Public views, admin, exports, APIs
├── urls.py                           # URL routing
├── admin.py                          # Django admin config
├── templatetags/docs_tags.py         # Custom template tags
├── static/docs/
│   ├── css/docs.css                  # Main styles
│   ├── css/docs-admin.css            # Admin styles
│   └── js/docs.js                    # Client-side JS
└── templates/docs/
    ├── base.html                     # Base template
    ├── home.html                     # Main docs view
    ├── export.html                   # Export template
    ├── access_denied.html            # Access denied page
    └── admin/docs/admin.html         # Admin panel
```

## Security

- Access control enforced at view level
- Staff users bypass schedule (for preview)
- No sensitive data in public views
- Image upload validation (Pillow)
- CSRF protection on admin forms
- SQL injection prevention via ORM

## Performance

- Database indexes on frequently queried fields
- Live data cached per-request (not persisted)
- Static assets versioned for cache busting
- Lazy-loaded images for team avatars
- Mermaid diagrams rendered client-side

## Future Enhancements

- [ ] WebSocket-based live log streaming in docs
- [ ] GraphRAG-powered documentation search
- [ ] Multi-language support (i18n)
- [ ] Plugin system for custom section types
- [ ] Analytics dashboard in admin
- [ ] Scheduled content publishing (not just access)
- [ ] Webhook notifications on access changes