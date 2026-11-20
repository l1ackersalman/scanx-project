"""
docs App Views

Public documentation view, admin editing, exports, and access control.
"""
import json
import logging
from datetime import datetime
from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

from .models import (
    DocSection, DocVersion, DocAccessControl, TeamMember, DocSettings, DocExport
)
from .live_data import get_provider, get_all_providers

logger = logging.getLogger(__name__)


def check_docs_access(request):
    """Check if user can access /docs based on access control rules."""
    access_control = DocAccessControl.get_instance()
    
    # Staff/superuser always have access
    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
        return True, None
    
    # Check access control
    if not access_control.is_accessible(request.user):
        return False, access_control.get_status_message()
    
    return True, None


def docs_home(request):
    """
    Main /docs endpoint - serves pitch deck + technical documentation.
    Access controlled via DocAccessControl.
    """
    # Check access
    has_access, message = check_docs_access(request)
    if not has_access:
        return render(request, "docs/access_denied.html", {
            "message": message,
            "page_title": "Documentation Not Available",
        }, status=403)
    
    # Get settings
    doc_settings = DocSettings.get_instance()
    
    # Get active sections for pitch deck view
    pitch_sections = DocSection.objects.filter(
        is_active=True,
        is_pitch_deck=True
    ).order_by("order")
    
    # Get active sections for technical view
    tech_sections = DocSection.objects.filter(
        is_active=True,
        is_technical=True
    ).order_by("order")
    
    # Get team members for pitch deck
    pitch_team = TeamMember.objects.filter(
        is_active=True,
        show_in_pitch=True
    ).order_by("team_order", "order")
    
    # Get team members for technical view
    tech_team = TeamMember.objects.filter(
        is_active=True,
        show_in_tech=True
    ).order_by("team_order", "order")
    
    # Group team members by team_name
    def group_team(members):
        groups = {}
        for member in members:
            group = member.team_group
            if group not in groups:
                groups[group] = []
            groups[group].append(member)
        return groups
    
    pitch_team_groups = group_team(pitch_team)
    tech_team_groups = group_team(tech_team)
    
    # Prepare section data with live content
    def prepare_sections(sections):
        result = []
        for section in sections:
            live_content = section.get_content_for_display()
            result.append({
                "section": section,
                "content": live_content,
                "anchor": slugify(section.section_type),
            })
        return result
    
    from django.utils.text import slugify
    
    context = {
        "settings": doc_settings,
        "pitch_sections": prepare_sections(pitch_sections),
        "tech_sections": prepare_sections(tech_sections),
        "pitch_team_groups": pitch_team_groups,
        "tech_team_groups": tech_team_groups,
        "access_control": DocAccessControl.get_instance(),
        "page_title": doc_settings.site_title,
        "page_tagline": doc_settings.site_tagline,
        "view_mode": request.GET.get("view", "pitch"),  # pitch or tech
    }
    
    return render(request, "docs/home.html", context)


@staff_member_required
def docs_admin(request):
    """Admin panel for managing documentation."""
    access_control = DocAccessControl.get_instance()
    doc_settings = DocSettings.get_instance()
    
    sections = DocSection.objects.all().order_by("order")
    team_members = TeamMember.objects.all().order_by("team_order", "order")
    
    # Handle POST actions
    if request.method == "POST":
        action = request.POST.get("action")
        
        if action == "update_access":
            access_control.is_enabled = request.POST.get("is_enabled") == "on"
            access_control.schedule_start = parse_datetime(request.POST.get("schedule_start"))
            access_control.schedule_end = parse_datetime(request.POST.get("schedule_end"))
            access_control.use_duration = request.POST.get("use_duration") == "on"
            access_control.duration_days = int(request.POST.get("duration_days") or 0) or None
            access_control.disabled_message = request.POST.get("disabled_message", "")
            access_control.scheduled_message = request.POST.get("scheduled_message", "")
            access_control.updated_by = request.user
            access_control.save()
            messages.success(request, "Access control updated.")
            return redirect("docs:admin")
        
        elif action == "update_settings":
            doc_settings.site_title = request.POST.get("site_title", "")
            doc_settings.site_tagline = request.POST.get("site_tagline", "")
            doc_settings.primary_color = request.POST.get("primary_color", "#76B900")
            doc_settings.accent_color = request.POST.get("accent_color", "#35B779")
            doc_settings.enable_search = request.POST.get("enable_search") == "on"
            doc_settings.enable_export_pdf = request.POST.get("enable_export_pdf") == "on"
            doc_settings.enable_export_md = request.POST.get("enable_export_md") == "on"
            doc_settings.meta_description = request.POST.get("meta_description", "")
            doc_settings.meta_keywords = request.POST.get("meta_keywords", "")
            doc_settings.maintenance_mode = request.POST.get("maintenance_mode") == "on"
            doc_settings.maintenance_message = request.POST.get("maintenance_message", "")
            doc_settings.updated_by = request.user
            doc_settings.save()
            messages.success(request, "Settings updated.")
            return redirect("docs:admin")
        
        elif action == "reorder_sections":
            # Handle drag-drop reorder
            order_data = json.loads(request.POST.get("order_data", "[]"))
            for item in order_data:
                DocSection.objects.filter(id=item["id"]).update(order=item["order"])
            return JsonResponse({"status": "ok"})
        
        elif action == "toggle_section":
            section_id = request.POST.get("section_id")
            field = request.POST.get("field")  # is_active, is_pitch_deck, is_technical
            section = get_object_or_404(DocSection, id=section_id)
            setattr(section, field, not getattr(section, field))
            section.updated_by = request.user
            section.save()
            return JsonResponse({"status": "ok", "value": getattr(section, field)})
    
    context = {
        "access_control": access_control,
        "settings": doc_settings,
        "sections": sections,
        "team_members": team_members,
        "section_types": DocSection.SectionType.choices,
        "content_types": DocSection.ContentType.choices,
        "page_title": "Documentation Admin",
    }
    return render(request, "admin/docs/admin.html", context)


@staff_member_required
def docs_section_edit(request, section_id=None):
    """Create or edit a documentation section."""
    if section_id:
        section = get_object_or_404(DocSection, id=section_id)
    else:
        section = None
    
    if request.method == "POST":
        section_type = request.POST.get("section_type")
        title = request.POST.get("title", "")
        subtitle = request.POST.get("subtitle", "")
        content = request.POST.get("content", "")
        content_type = request.POST.get("content_type", "markdown")
        order = int(request.POST.get("order", 0))
        is_active = request.POST.get("is_active") == "on"
        is_pitch_deck = request.POST.get("is_pitch_deck") == "on"
        is_technical = request.POST.get("is_technical") == "on"
        live_data_source = request.POST.get("live_data_source", "")
        live_data_config = request.POST.get("live_data_config", "{}")
        
        try:
            live_data_config = json.loads(live_data_config)
        except json.JSONDecodeError:
            live_data_config = {}
        
        if section:
            # Create version before updating
            DocVersion.objects.create(
                section=section,
                content=section.content,
                content_type=section.content_type,
                title=section.title,
                subtitle=section.subtitle,
                created_by=request.user,
                change_note=request.POST.get("change_note", "Updated via admin"),
            )
            
            section.section_type = section_type
            section.title = title
            section.subtitle = subtitle
            section.content = content
            section.content_type = content_type
            section.order = order
            section.is_active = is_active
            section.is_pitch_deck = is_pitch_deck
            section.is_technical = is_technical
            section.live_data_source = live_data_source
            section.live_data_config = live_data_config
            section.updated_by = request.user
            section.save()
            messages.success(request, f"Section '{title}' updated.")
        else:
            section = DocSection.objects.create(
                section_type=section_type,
                title=title,
                subtitle=subtitle,
                content=content,
                content_type=content_type,
                order=order,
                is_active=is_active,
                is_pitch_deck=is_pitch_deck,
                is_technical=is_technical,
                live_data_source=live_data_source,
                live_data_config=live_data_config,
                created_by=request.user,
                updated_by=request.user,
            )
            messages.success(request, f"Section '{title}' created.")
        
        return redirect("docs:admin")
    
    # GET - show edit form
    context = {
        "section": section,
        "section_types": DocSection.SectionType.choices,
        "content_types": DocSection.ContentType.choices,
        "live_data_providers": get_all_providers(),
        "page_title": f"Edit Section: {section.title if section else 'New'}",
    }
    return render(request, "admin/docs/section_edit.html", context)


@staff_member_required
def docs_section_delete(request, section_id):
    """Delete a documentation section."""
    section = get_object_or_404(DocSection, id=section_id)
    if request.method == "POST":
        title = section.title
        section.delete()
        messages.success(request, f"Section '{title}' deleted.")
    return redirect("docs:admin")


@staff_member_required
def docs_team_edit(request, member_id=None):
    """Create or edit a team member."""
    if member_id:
        member = get_object_or_404(TeamMember, id=member_id)
    else:
        member = None
    
    if request.method == "POST":
        name = request.POST.get("name", "")
        role = request.POST.get("role", "other")
        custom_role = request.POST.get("custom_role", "")
        email = request.POST.get("email", "")
        bio = request.POST.get("bio", "")
        linkedin = request.POST.get("linkedin", "")
        github = request.POST.get("github", "")
        twitter = request.POST.get("twitter", "")
        order = int(request.POST.get("order", 0))
        team_name = request.POST.get("team_name", "")
        team_order = int(request.POST.get("team_order", 0))
        is_active = request.POST.get("is_active") == "on"
        show_in_pitch = request.POST.get("show_in_pitch") == "on"
        show_in_tech = request.POST.get("show_in_tech") == "on"
        
        # Handle image upload
        profile_image = request.FILES.get("profile_image")
        
        if member:
            member.name = name
            member.role = role
            member.custom_role = custom_role
            member.email = email
            member.bio = bio
            member.linkedin = linkedin
            member.github = github
            member.twitter = twitter
            member.order = order
            member.team_name = team_name
            member.team_order = team_order
            member.is_active = is_active
            member.show_in_pitch = show_in_pitch
            member.show_in_tech = show_in_tech
            if profile_image:
                member.profile_image = profile_image
            member.save()
            messages.success(request, f"Team member '{name}' updated.")
        else:
            member = TeamMember.objects.create(
                name=name,
                role=role,
                custom_role=custom_role,
                email=email,
                bio=bio,
                linkedin=linkedin,
                github=github,
                twitter=twitter,
                order=order,
                team_name=team_name,
                team_order=team_order,
                is_active=is_active,
                show_in_pitch=show_in_pitch,
                show_in_tech=show_in_tech,
                profile_image=profile_image,
            )
            messages.success(request, f"Team member '{name}' created.")
        
        return redirect("docs:admin")
    
    context = {
        "member": member,
        "roles": TeamMember.Role.choices,
        "page_title": f"Edit Team Member: {member.name if member else 'New'}",
    }
    return render(request, "admin/docs/team_edit.html", context)


@staff_member_required
def docs_team_delete(request, member_id):
    """Delete a team member."""
    member = get_object_or_404(TeamMember, id=member_id)
    if request.method == "POST":
        name = member.name
        member.delete()
        messages.success(request, f"Team member '{name}' deleted.")
    return redirect("docs:admin")


def docs_export(request):
    """Export documentation as PDF, Markdown, or HTML."""
    format = request.GET.get("format", "markdown")
    view = request.GET.get("view", "all")  # pitch, tech, all
    sections_param = request.GET.get("sections", "")
    
    # Check access (allow staff always)
    has_access, message = check_docs_access(request)
    if not has_access and not (request.user.is_authenticated and request.user.is_staff):
        return HttpResponseForbidden(message)
    
    # Get sections to export
    if sections_param:
        section_ids = sections_param.split(",")
        sections = DocSection.objects.filter(id__in=section_ids, is_active=True)
    else:
        if view == "pitch":
            sections = DocSection.objects.filter(is_active=True, is_pitch_deck=True)
        elif view == "tech":
            sections = DocSection.objects.filter(is_active=True, is_technical=True)
        else:
            sections = DocSection.objects.filter(is_active=True)
    
    sections = sections.order_by("order")
    
    # Get team members
    team_members = TeamMember.objects.filter(is_active=True).order_by("team_order", "order")
    team_groups = {}
    for member in team_members:
        group = member.team_group
        if group not in team_groups:
            team_groups[group] = []
        team_groups[group].append(member)
    
    # Prepare content
    doc_settings = DocSettings.get_instance()
    content_sections = []
    for section in sections:
        content_sections.append({
            "section": section,
            "content": section.get_content_for_display(),
        })
    
    # Generate export
    if format == "markdown":
        content = generate_markdown_export(doc_settings, content_sections, team_groups, view)
        response = HttpResponse(content, content_type="text/markdown")
        response["Content-Disposition"] = f'attachment; filename="scanx-docs-{view}-{datetime.now():%Y%m%d}.md"'
    
    elif format == "html":
        content = generate_html_export(doc_settings, content_sections, team_groups, view)
        response = HttpResponse(content, content_type="text/html")
        response["Content-Disposition"] = f'attachment; filename="scanx-docs-{view}-{datetime.now():%Y%m%d}.html"'
    
    elif format == "pdf":
        # For PDF, return HTML that can be printed to PDF
        content = generate_html_export(doc_settings, content_sections, team_groups, view, for_pdf=True)
        response = HttpResponse(content, content_type="text/html")
        response["Content-Disposition"] = f'inline; filename="scanx-docs-{view}-{datetime.now():%Y%m%d}.html"'
    
    else:
        return HttpResponse("Invalid format", status=400)
    
    # Log export
    DocExport.objects.create(
        format=format,
        sections=[s["section"].section_type for s in content_sections],
        requested_by=request.user if request.user.is_authenticated else None,
        ip_address=get_client_ip(request),
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
    )
    
    return response


def generate_markdown_export(settings, sections, team_groups, view):
    """Generate Markdown export."""
    lines = [
        f"# {settings.site_title}",
        f"*{settings.site_tagline}*",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**View:** {view.title()}",
        "",
        "---",
        "",
    ]
    
    for item in sections:
        section = item["section"]
        content = item["content"]
        lines.append(f"## {section.title}")
        if section.subtitle:
            lines.append(f"*{section.subtitle}*")
        lines.append("")
        # Strip HTML tags for markdown export (basic)
        import re
        clean_content = re.sub(r'<[^>]+>', '', content)
        lines.append(clean_content)
        lines.append("")
        lines.append("---")
        lines.append("")
    
    # Team section
    if team_groups:
        lines.append("# Team")
        lines.append("")
        for group_name, members in team_groups.items():
            lines.append(f"## {group_name}")
            lines.append("")
            for member in members:
                role = member.get_display_role()
                lines.append(f"### {member.name}")
                lines.append(f"**Role:** {role}")
                if member.email:
                    lines.append(f"**Email:** {member.email}")
                if member.bio:
                    lines.append(f"**Bio:** {member.bio}")
                lines.append("")
    
    return "\n".join(lines)


def generate_html_export(settings, sections, team_groups, view, for_pdf=False):
    """Generate HTML export."""
    from django.template.loader import render_to_string
    
    context = {
        "settings": settings,
        "sections": sections,
        "team_groups": team_groups,
        "view": view,
        "generated_at": datetime.now(),
        "for_pdf": for_pdf,
    }
    return render_to_string("docs/export.html", context)


def docs_api_sections(request):
    """API endpoint for section data (for live editing preview)."""
    section_id = request.GET.get("section_id")
    if section_id:
        section = get_object_or_404(DocSection, id=section_id)
        return JsonResponse({
            "id": str(section.id),
            "section_type": section.section_type,
            "title": section.title,
            "subtitle": section.subtitle,
            "content": section.content,
            "content_type": section.content_type,
            "order": section.order,
            "is_active": section.is_active,
            "is_pitch_deck": section.is_pitch_deck,
            "is_technical": section.is_technical,
            "live_data_source": section.live_data_source,
            "live_data_config": section.live_data_config,
        })
    
    sections = DocSection.objects.filter(is_active=True).order_by("order")
    data = [{
        "id": str(s.id),
        "section_type": s.section_type,
        "title": s.title,
        "order": s.order,
        "is_pitch_deck": s.is_pitch_deck,
        "is_technical": s.is_technical,
    } for s in sections]
    return JsonResponse({"sections": data})


def docs_access_status(request):
    """API endpoint to check current access status."""
    access_control = DocAccessControl.get_instance()
    has_access, message = check_docs_access(request)
    start, end = access_control.get_effective_window()
    
    return JsonResponse({
        "accessible": has_access,
        "message": message,
        "is_enabled": access_control.is_enabled,
        "schedule_start": start.isoformat() if start else None,
        "schedule_end": end.isoformat() if end else None,
        "use_duration": access_control.use_duration,
        "duration_days": access_control.duration_days,
    })


# Helper functions
def parse_datetime(value):
    """Parse datetime string from form input."""
    if not value:
        return None
    try:
        # Handle datetime-local input format: YYYY-MM-DDTHH:MM
        return datetime.fromisoformat(value)
    except ValueError:
        try:
            return datetime.strptime(value, "%Y-%m-%d %H:%M")
        except ValueError:
            return None


def get_client_ip(request):
    """Get client IP address."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def slugify(text):
    """Simple slugify for anchors."""
    import re
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text.strip('-')