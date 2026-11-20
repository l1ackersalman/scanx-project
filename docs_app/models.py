"""
docs App Models

Documentation system with YC-style pitch deck, technical documentation,
access control, scheduling, and team showcase.
"""
import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify
from django.core.validators import FileExtensionValidator


class DocSection(models.Model):
    """
    Individual documentation section (Problem, Solution, Architecture, etc.)
    Supports both pitch deck and technical documentation content.
    """
    
    class SectionType(models.TextChoices):
        # Pitch Deck Sections
        PROBLEM = "problem", "Problem"
        SOLUTION = "solution", "Solution"
        WHY_NOW = "why_now", "Why Now"
        PRODUCT_DEMO = "product_demo", "Product Demo"
        MARKET_OPPORTUNITY = "market_opportunity", "Market Opportunity"
        BUSINESS_MODEL = "business_model", "Business Model"
        TRACTION = "traction", "Traction"
        COMPETITION = "competition", "Competition"
        UNIQUE_ADVANTAGE = "unique_advantage", "Unique Advantage"
        GO_TO_MARKET = "go_to_market", "Go-To-Market"
        TEAM = "team", "Team"
        VISION = "vision", "Vision"
        
        # Technical Documentation Sections
        PRODUCT_OVERVIEW = "product_overview", "Product Overview"
        FEATURE_MATRIX = "feature_matrix", "Feature Matrix"
        ARCHITECTURE = "architecture", "Architecture Diagram"
        DATA_FLOW = "data_flow", "Data Flow Diagram"
        TECH_STACK = "tech_stack", "Technology Stack"
        API_DOCS = "api_docs", "API Documentation"
        DATA_LAYER = "data_layer", "Data Layer"
        AI_LAYER = "ai_layer", "AI Layer"
        ROADMAP = "roadmap", "Product Roadmap"
        PERFORMANCE = "performance", "Performance & Scalability"
        SECURITY = "security", "Security"
        ANALYTICS = "analytics", "Analytics"
        CHANGELOG = "changelog", "Changelog"
    
    class ContentType(models.TextChoices):
        MARKDOWN = "markdown", "Markdown"
        MERMAID = "mermaid", "Mermaid Diagram"
        HTML = "html", "HTML"
        JSON = "json", "JSON Data"
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    section_type = models.CharField(
        max_length=50,
        choices=SectionType.choices,
        unique=True,
        db_index=True,
    )
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True, default="")
    content = models.TextField(blank=True, default="")  # Markdown/HTML content
    content_type = models.CharField(
        max_length=20,
        choices=ContentType.choices,
        default=ContentType.MARKDOWN,
    )
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    is_active = models.BooleanField(default=True)
    is_pitch_deck = models.BooleanField(default=True, help_text="Show in pitch deck view")
    is_technical = models.BooleanField(default=True, help_text="Show in technical docs view")
    
    # Live data integration
    live_data_source = models.CharField(
        max_length=100,
        blank=True,
        default="",
        help_text="Python path to live data provider (e.g., 'docs_app.live_data.get_feature_matrix')"
    )
    live_data_config = models.JSONField(default=dict, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_doc_sections",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_doc_sections",
    )
    
    class Meta:
        ordering = ["order", "section_type"]
        verbose_name = "Documentation Section"
        verbose_name_plural = "Documentation Sections"
    
    def __str__(self):
        return f"{self.get_section_type_display()} ({self.section_type})"
    
    def get_content_for_display(self, context=None):
        """Get rendered content with live data injection."""
        from django.template.loader import render_to_string
        from django.template import Context
        
        content = self.content
        
        # Inject live data if source configured
        if self.live_data_source:
            try:
                module_path, func_name = self.live_data_source.rsplit(".", 1)
                module = __import__(module_path, fromlist=[func_name])
                func = getattr(module, func_name)
                live_data = func(self.live_data_config)
                if live_data:
                    # Merge live data into context
                    if context is None:
                        context = {}
                    context.update(live_data)
            except Exception as e:
                # Log error but don't break rendering
                import logging
                logging.getLogger(__name__).warning(f"Live data error for {self.section_type}: {e}")
        
        # Render markdown if needed
        if self.content_type == self.ContentType.MARKDOWN:
            import markdown
            md = markdown.Markdown(extensions=['tables', 'fenced_code', 'toc', 'codehilite'])
            content = md.convert(content)
        elif self.content_type == self.ContentType.MERMAID:
            # Wrap in mermaid div
            content = f'<div class="mermaid">{content}</div>'
        
        return content


class DocVersion(models.Model):
    """Version history for documentation sections."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    section = models.ForeignKey(
        DocSection,
        on_delete=models.CASCADE,
        related_name="versions",
    )
    content = models.TextField()
    content_type = models.CharField(max_length=20, choices=DocSection.ContentType.choices)
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    change_note = models.CharField(max_length=500, blank=True, default="")
    is_published = models.BooleanField(default=False)
    
    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Documentation Version"
        verbose_name_plural = "Documentation Versions"
    
    def __str__(self):
        return f"{self.section} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class DocAccessControl(models.Model):
    """
    Global access control for the /docs endpoint.
    Supports scheduling, toggling, and admin overrides.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Master toggle
    is_enabled = models.BooleanField(
        default=False,
        help_text="Master switch: ON = publicly accessible, OFF = not accessible"
    )
    
    # Scheduling
    schedule_start = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When docs become publicly accessible (if scheduled)"
    )
    schedule_end = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When docs become inaccessible (if scheduled)"
    )
    
    # Duration-based alternative
    use_duration = models.BooleanField(default=False)
    duration_days = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Duration in days from schedule_start (alternative to schedule_end)"
    )
    
    # Access messages
    disabled_message = models.TextField(
        blank=True,
        default="Documentation is currently not available.",
        help_text="Message shown when docs are disabled"
    )
    scheduled_message = models.TextField(
        blank=True,
        default="Documentation will be available from {start} to {end}.",
        help_text="Message shown outside scheduled window. Use {start} and {end} placeholders."
    )
    
    # Default configuration (June 10-14 as specified)
    default_start = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Default schedule start for quick setup"
    )
    default_end = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Default schedule end for quick setup"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    
    class Meta:
        verbose_name = "Documentation Access Control"
        verbose_name_plural = "Documentation Access Control"
    
    def __str__(self):
        status = "Enabled" if self.is_enabled else "Disabled"
        if self.schedule_start and self.schedule_end:
            status += f" (Scheduled: {self.schedule_start:%Y-%m-%d} to {self.schedule_end:%Y-%m-%d})"
        return f"Docs Access: {status}"
    
    def is_accessible(self, user=None):
        """Check if docs are currently accessible."""
        # Admin/superuser always has access
        if user and (user.is_superuser or user.is_staff):
            return True
        
        if not self.is_enabled:
            return False
        
        now = timezone.now()
        
        # Check schedule
        if self.schedule_start and now < self.schedule_start:
            return False
        if self.schedule_end and now > self.schedule_end:
            return False
        
        # Check duration-based
        if self.use_duration and self.schedule_start and self.duration_days:
            end = self.schedule_start + timezone.timedelta(days=self.duration_days)
            if now > end:
                return False
        
        return True
    
    def get_status_message(self):
        """Get appropriate status message for current state."""
        now = timezone.now()
        
        if not self.is_enabled:
            return self.disabled_message
        
        if self.schedule_start and now < self.schedule_start:
            start_str = self.schedule_start.strftime("%Y-%m-%d %H:%M")
            end_str = ""
            if self.schedule_end:
                end_str = self.schedule_end.strftime("%Y-%m-%d %H:%M")
            elif self.use_duration and self.duration_days:
                end = self.schedule_start + timezone.timedelta(days=self.duration_days)
                end_str = end.strftime("%Y-%m-%d %H:%M")
            return self.scheduled_message.format(start=start_str, end=end_str)
        
        if self.schedule_end and now > self.schedule_end:
            return "The documentation viewing period has ended."
        
        if self.use_duration and self.schedule_start and self.duration_days:
            end = self.schedule_start + timezone.timedelta(days=self.duration_days)
            if now > end:
                return "The documentation viewing period has ended."
        
        return ""
    
    def get_effective_window(self):
        """Get the effective start/end datetime for display."""
        start = self.schedule_start
        end = self.schedule_end
        
        if self.use_duration and start and self.duration_days and not end:
            end = start + timezone.timedelta(days=self.duration_days)
        
        return start, end
    
    @classmethod
    def get_instance(cls):
        """Get or create the singleton access control instance."""
        obj, created = cls.objects.get_or_create(id=uuid.UUID('00000000-0000-0000-0000-000000000001'))
        if created:
            # Set default June 10-14 window
            from datetime import datetime
            import pytz
            tz = pytz.timezone('Asia/Dhaka')  # Match project timezone
            obj.default_start = tz.localize(datetime(2026, 6, 10, 0, 0, 0))
            obj.default_end = tz.localize(datetime(2026, 6, 14, 23, 59, 59))
            obj.schedule_start = obj.default_start
            obj.schedule_end = obj.default_end
            obj.save()
        return obj


class TeamMember(models.Model):
    """
    Team member for the Team section showcase.
    Includes profile picture with uniform styling requirements.
    """
    class Role(models.TextChoices):
        FOUNDER = "founder", "Founder"
        CO_FOUNDER = "co_founder", "Co-Founder"
        CTO = "cto", "CTO"
        CEO = "ceo", "CEO"
        LEAD_ENGINEER = "lead_engineer", "Lead Engineer"
        BACKEND_ENGINEER = "backend_engineer", "Backend Engineer"
        FRONTEND_ENGINEER = "frontend_engineer", "Frontend Engineer"
        SECURITY_RESEARCHER = "security_researcher", "Security Researcher"
        AI_ENGINEER = "ai_engineer", "AI Engineer"
        DEVOPS = "devops", "DevOps Engineer"
        DESIGNER = "designer", "Designer"
        PRODUCT_MANAGER = "product_manager", "Product Manager"
        ADVISOR = "advisor", "Advisor"
        OTHER = "other", "Other"
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)
    role = models.CharField(max_length=50, choices=Role.choices, default=Role.OTHER)
    custom_role = models.CharField(max_length=100, blank=True, default="", help_text="Custom role if 'Other' selected")
    email = models.EmailField(blank=True, default="")
    bio = models.TextField(blank=True, default="", help_text="Short bio for hover/tooltip")
    linkedin = models.URLField(blank=True, default="")
    github = models.URLField(blank=True, default="")
    twitter = models.URLField(blank=True, default="")
    
    # Profile picture - uniform styling handled via CSS
    profile_image = models.ImageField(
        upload_to="team/",
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "webp"])],
        help_text="Recommended: 400x400px, square aspect ratio. Will be auto-cropped to circle."
    )
    image_alt = models.CharField(max_length=200, blank=True, default="", help_text="Alt text for accessibility")
    
    # Display
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    show_in_pitch = models.BooleanField(default=True, help_text="Show in pitch deck Team section")
    show_in_tech = models.BooleanField(default=True, help_text="Show in technical docs Team section")
    
    # Team grouping
    team_name = models.CharField(max_length=100, blank=True, default="", help_text="Optional team/group name")
    team_order = models.PositiveIntegerField(default=0, help_text="Order of team groups")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ["team_order", "order", "name"]
        verbose_name = "Team Member"
        verbose_name_plural = "Team Members"
    
    def __str__(self):
        role_display = self.get_role_display()
        if self.role == self.Role.OTHER and self.custom_role:
            role_display = self.custom_role
        return f"{self.name} — {role_display}"
    
    def get_display_role(self):
        if self.role == self.Role.OTHER and self.custom_role:
            return self.custom_role
        return self.get_role_display()
    
    def get_profile_image_url(self):
        """Get profile image URL with fallback."""
        if self.profile_image and hasattr(self.profile_image, 'url'):
            return self.profile_image.url
        # Return SVG placeholder
        from django.templatetags.static import static
        return static('docs/images/avatar-placeholder.svg')
    
    @property
    def team_group(self):
        """Get or create team group name for display."""
        return self.team_name or "Core Team"


class DocSettings(models.Model):
    """Global settings for the documentation system."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Site branding
    site_title = models.CharField(max_length=200, default="scanX Documentation")
    site_tagline = models.CharField(max_length=300, default="AI-Powered Security Reconnaissance Platform")
    logo = models.ImageField(upload_to="docs/", blank=True, null=True)
    favicon = models.ImageField(upload_to="docs/", blank=True, null=True)
    
    # Theme
    primary_color = models.CharField(max_length=7, default="#76B900", help_text="Hex color (e.g., #76B900)")
    accent_color = models.CharField(max_length=7, default="#35B779")
    
    # Features
    enable_search = models.BooleanField(default=True)
    enable_export_pdf = models.BooleanField(default=True)
    enable_export_md = models.BooleanField(default=True)
    enable_anchor_links = models.BooleanField(default=True)
    enable_toc = models.BooleanField(default=True)
    
    # Analytics
    google_analytics_id = models.CharField(max_length=50, blank=True, default="")
    plausible_domain = models.CharField(max_length=100, blank=True, default="")
    
    # SEO
    meta_description = models.TextField(blank=True, default="")
    meta_keywords = models.CharField(max_length=500, blank=True, default="")
    og_image = models.ImageField(upload_to="docs/", blank=True, null=True)
    
    # Maintenance
    maintenance_mode = models.BooleanField(default=False)
    maintenance_message = models.TextField(blank=True, default="Documentation is under maintenance. Please check back later.")
    
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    
    class Meta:
        verbose_name = "Documentation Settings"
        verbose_name_plural = "Documentation Settings"
    
    def __str__(self):
        return "Documentation Settings"
    
    @classmethod
    def get_instance(cls):
        obj, _ = cls.objects.get_or_create(id=uuid.UUID('00000000-0000-0000-0000-000000000002'))
        return obj


class DocExport(models.Model):
    """Track documentation exports for analytics."""
    class ExportFormat(models.TextChoices):
        PDF = "pdf", "PDF"
        MARKDOWN = "markdown", "Markdown"
        HTML = "html", "HTML"
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    format = models.CharField(max_length=20, choices=ExportFormat.choices)
    sections = models.JSONField(default=list)  # List of section types exported
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    file_size = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, default="completed")
    
    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Documentation Export"
        verbose_name_plural = "Documentation Exports"
    
    def __str__(self):
        return f"{self.format.upper()} export - {self.created_at:%Y-%m-%d %H:%M}"