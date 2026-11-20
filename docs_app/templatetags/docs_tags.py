"""
Custom template tags for docs app.
"""
import re
from django import template
from django.utils.safestring import mark_safe
from django.utils.text import slugify

register = template.Library()


@register.filter
def markdown_to_html(text):
    """Convert markdown to HTML."""
    try:
        import markdown
        md = markdown.Markdown(extensions=[
            'tables', 'fenced_code', 'toc', 'codehilite', 'attr_list'
        ])
        return mark_safe(md.convert(text))
    except ImportError:
        # Fallback: basic conversion
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
        text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
        text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
        text = re.sub(r'^## (.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
        text = re.sub(r'^# (.+)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
        text = text.replace('\n', '<br>')
        return mark_safe(text)


@register.filter
def slugify_filter(text):
    """Slugify text for anchor links."""
    return slugify(text)


@register.simple_tag
def get_setting(key):
    """Get a DocSettings value."""
    from docs_app.models import DocSettings
    settings = DocSettings.get_instance()
    return getattr(settings, key, "")


@register.inclusion_tag("docs/components/team_card.html")
def team_card(member, size="default"):
    """Render a team member card."""
    return {"member": member, "size": size}


@register.inclusion_tag("docs/components/section_card.html")
def section_card(section, view_mode="pitch"):
    """Render a documentation section card."""
    return {"section": section, "view_mode": view_mode}


@register.simple_tag
def live_data(section_type, config=None):
    """Get live data for a section type."""
    from docs_app.live_data import get_provider
    provider = get_provider(section_type)
    if provider:
        return provider(config or {})
    return {}


@register.filter
def get_item(dictionary, key):
    """Get dictionary item by key."""
    return dictionary.get(key, "")


@register.simple_tag
def docs_version():
    """Get documentation version."""
    from django.conf import settings
    return getattr(settings, 'SCANX_VERSION', '2.0.0')


@register.inclusion_tag("docs/components/breadcrumb.html")
def docs_breadcrumb(sections, current_section=None):
    """Render breadcrumb navigation."""
    return {"sections": sections, "current": current_section}