"""
docs App Admin Configuration
"""
from django.contrib import admin
from .models import (
    DocSection, DocVersion, DocAccessControl, TeamMember, DocSettings, DocExport
)


@admin.register(DocSection)
class DocSectionAdmin(admin.ModelAdmin):
    list_display = [
        "section_type", "title", "order", "is_active", "is_pitch_deck", "is_technical", "updated_at"
    ]
    list_filter = ["is_active", "is_pitch_deck", "is_technical", "content_type"]
    search_fields = ["section_type", "title", "content"]
    readonly_fields = ["id", "created_at", "updated_at", "created_by", "updated_by"]
    ordering = ["order", "section_type"]
    list_editable = ["order", "is_active", "is_pitch_deck", "is_technical"]
    list_per_page = 25
    
    fieldsets = (
        ("Identity", {
            "fields": ("id", "section_type", "title", "subtitle")
        }),
        ("Content", {
            "fields": ("content_type", "content", "live_data_source", "live_data_config")
        }),
        ("Display", {
            "fields": ("order", "is_active", "is_pitch_deck", "is_technical")
        }),
        ("Metadata", {
            "fields": ("created_at", "updated_at", "created_by", "updated_by"),
            "classes": ("collapse",)
        }),
    )


@admin.register(DocVersion)
class DocVersionAdmin(admin.ModelAdmin):
    list_display = ["section", "title", "created_at", "created_by", "is_published"]
    list_filter = ["is_published", "created_at"]
    search_fields = ["section__title", "title", "content"]
    readonly_fields = ["id", "created_at", "created_by"]
    ordering = ["-created_at"]
    list_per_page = 25


@admin.register(DocAccessControl)
class DocAccessControlAdmin(admin.ModelAdmin):
    list_display = ["__str__", "is_enabled", "schedule_start", "schedule_end", "updated_at"]
    readonly_fields = ["id", "created_at", "updated_at", "updated_by"]
    fieldsets = (
        ("Master Control", {
            "fields": ("is_enabled",)
        }),
        ("Scheduled Publishing", {
            "fields": ("schedule_start", "schedule_end", "use_duration", "duration_days"),
            "description": "Set a time window for public access. Outside this window, users see a scheduled message."
        }),
        ("Messages", {
            "fields": ("disabled_message", "scheduled_message"),
        }),
        ("Defaults", {
            "fields": ("default_start", "default_end"),
            "classes": ("collapse",)
        }),
        ("Metadata", {
            "fields": ("created_at", "updated_at", "updated_by"),
            "classes": ("collapse",)
        }),
    )
    
    def has_add_permission(self, request):
        # Singleton - only one instance allowed
        return not DocAccessControl.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = [
        "name", "get_display_role", "email", "team_name", "team_order", "order",
        "is_active", "show_in_pitch", "show_in_tech"
    ]
    list_filter = ["role", "is_active", "show_in_pitch", "show_in_tech", "team_name"]
    search_fields = ["name", "email", "custom_role", "bio"]
    readonly_fields = ["id", "created_at", "updated_at"]
    ordering = ["team_order", "order", "name"]
    list_editable = ["order", "team_order", "is_active", "show_in_pitch", "show_in_tech"]
    list_per_page = 25
    
    fieldsets = (
        ("Basic Info", {
            "fields": ("name", "role", "custom_role", "email", "bio")
        }),
        ("Links", {
            "fields": ("linkedin", "github", "twitter"),
            "classes": ("collapse",)
        }),
        ("Profile Image", {
            "fields": ("profile_image", "image_alt"),
            "description": "Recommended: 400x400px square. Will be displayed as circle with uniform styling."
        }),
        ("Display", {
            "fields": ("order", "team_name", "team_order", "is_active", "show_in_pitch", "show_in_tech")
        }),
        ("Metadata", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    
    def get_display_role(self, obj):
        if obj.role == obj.Role.OTHER and obj.custom_role:
            return obj.custom_role
        return obj.get_role_display()
    get_display_role.short_description = "Role"


@admin.register(DocSettings)
class DocSettingsAdmin(admin.ModelAdmin):
    list_display = ["__str__", "site_title", "primary_color", "updated_at"]
    readonly_fields = ["id", "updated_at", "updated_by"]
    fieldsets = (
        ("Branding", {
            "fields": ("site_title", "site_tagline", "logo", "favicon", "og_image")
        }),
        ("Theme", {
            "fields": ("primary_color", "accent_color")
        }),
        ("Features", {
            "fields": ("enable_search", "enable_export_pdf", "enable_export_md", "enable_anchor_links", "enable_toc")
        }),
        ("SEO & Analytics", {
            "fields": ("meta_description", "meta_keywords", "google_analytics_id", "plausible_domain"),
            "classes": ("collapse",)
        }),
        ("Maintenance", {
            "fields": ("maintenance_mode", "maintenance_message"),
            "classes": ("collapse",)
        }),
        ("Metadata", {
            "fields": ("updated_at", "updated_by"),
            "classes": ("collapse",)
        }),
    )
    
    def has_add_permission(self, request):
        return not DocSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(DocExport)
class DocExportAdmin(admin.ModelAdmin):
    list_display = ["format", "created_at", "requested_by", "ip_address", "status"]
    list_filter = ["format", "status", "created_at"]
    readonly_fields = ["id", "created_at", "requested_by", "ip_address", "user_agent", "sections", "file_size", "status"]
    ordering = ["-created_at"]
    list_per_page = 25
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False