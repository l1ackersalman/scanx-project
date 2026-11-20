"""
docs App URL Patterns
"""
from django.urls import path
from . import views

app_name = "docs"

urlpatterns = [
    # Public documentation
    path("", views.docs_home, name="home"),
    path("export/", views.docs_export, name="export"),
    
    # API endpoints
    path("api/sections/", views.docs_api_sections, name="api_sections"),
    path("api/access/", views.docs_access_status, name="api_access"),
    
    # Admin panel (staff only)
    path("admin/", views.docs_admin, name="admin"),
    path("admin/section/", views.docs_section_edit, name="section_create"),
    path("admin/section/<uuid:section_id>/", views.docs_section_edit, name="section_edit"),
    path("admin/section/<uuid:section_id>/delete/", views.docs_section_delete, name="section_delete"),
    path("admin/team/", views.docs_team_edit, name="team_create"),
    path("admin/team/<uuid:member_id>/", views.docs_team_edit, name="team_edit"),
    path("admin/team/<uuid:member_id>/delete/", views.docs_team_delete, name="team_delete"),
]