"""
Tests for docs_app
"""
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User, AnonymousUser
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from docs_app.models import (
    DocSection, DocAccessControl, TeamMember, DocSettings, DocExport, DocVersion
)
from docs_app.views import docs_home, docs_export, docs_access_status, docs_admin
from docs_app.live_data import get_provider, get_all_providers


class DocAccessControlTests(TestCase):
    """Test access control logic."""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.access_control = DocAccessControl.get_instance()
    
    def test_default_access_control_exists(self):
        """Test that singleton access control is created."""
        ac = DocAccessControl.get_instance()
        self.assertIsNotNone(ac)
        self.assertEqual(str(ac.id), '00000000-0000-0000-0000-000000000001')
    
    def test_access_control_enabled_no_schedule(self):
        """Test access when enabled with no schedule."""
        self.access_control.is_enabled = True
        self.access_control.schedule_start = None
        self.access_control.schedule_end = None
        self.access_control.save()
        
        self.assertTrue(self.access_control.is_accessible(None))
    
    def test_access_control_disabled(self):
        """Test access when disabled."""
        self.access_control.is_enabled = False
        self.access_control.save()
        
        self.assertFalse(self.access_control.is_accessible(None))
        self.assertIn("not available", self.access_control.get_status_message())
    
    def test_access_control_future_schedule(self):
        """Test access when schedule is in future."""
        self.access_control.is_enabled = True
        self.access_control.schedule_start = timezone.now() + timedelta(days=1)
        self.access_control.schedule_end = timezone.now() + timedelta(days=10)
        self.access_control.save()
        
        self.assertFalse(self.access_control.is_accessible(None))
        self.assertIn("will be available", self.access_control.get_status_message())
    
    def test_access_control_active_schedule(self):
        """Test access when schedule is active."""
        self.access_control.is_enabled = True
        self.access_control.schedule_start = timezone.now() - timedelta(days=1)
        self.access_control.schedule_end = timezone.now() + timedelta(days=10)
        self.access_control.save()
        
        self.assertTrue(self.access_control.is_accessible(None))
    
    def test_access_control_expired_schedule(self):
        """Test access when schedule has expired."""
        self.access_control.is_enabled = True
        self.access_control.schedule_start = timezone.now() - timedelta(days=20)
        self.access_control.schedule_end = timezone.now() - timedelta(days=10)
        self.access_control.save()
        
        self.assertFalse(self.access_control.is_accessible(None))
        self.assertIn("ended", self.access_control.get_status_message())
    
    def test_staff_always_has_access(self):
        """Test that staff users always have access regardless of schedule."""
        self.access_control.is_enabled = False
        self.access_control.save()
        
        staff_user = User.objects.create_user('staff', 'staff@test.com', 'password', is_staff=True)
        self.assertTrue(self.access_control.is_accessible(staff_user))
    
    def test_duration_based_schedule(self):
        """Test duration-based scheduling."""
        self.access_control.is_enabled = True
        self.access_control.use_duration = True
        self.access_control.duration_days = 7
        self.access_control.schedule_start = timezone.now() - timedelta(days=1)
        self.access_control.schedule_end = None
        self.access_control.save()
        
        self.assertTrue(self.access_control.is_accessible(None))
        
        # Expired duration
        self.access_control.schedule_start = timezone.now() - timedelta(days=10)
        self.access_control.save()
        
        self.assertFalse(self.access_control.is_accessible(None))


class DocSectionTests(TestCase):
    """Test DocSection model and views."""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.section = DocSection.objects.create(
            section_type='problem',
            title='Test Problem',
            subtitle='Test subtitle',
            content='# Test Content\n\nThis is a test.',
            content_type='markdown',
            order=1,
            is_active=True,
            is_pitch_deck=True,
            is_technical=True,
        )
    
    def test_section_creation(self):
        """Test section is created correctly."""
        self.assertEqual(self.section.title, 'Test Problem')
        self.assertEqual(self.section.section_type, 'problem')
        self.assertTrue(self.section.is_active)
    
    def test_get_content_for_display_markdown(self):
        """Test markdown content rendering."""
        content = self.section.get_content_for_display()
        self.assertIn('<h1', content)
        self.assertIn('Test Content', content)
    
    def test_section_str(self):
        """Test string representation."""
        self.assertIn('Problem', str(self.section))


class TeamMemberTests(TestCase):
    """Test TeamMember model."""
    
    def setUp(self):
        self.member = TeamMember.objects.create(
            name='Test Member',
            role='founder',
            email='test@example.com',
            bio='Test bio',
            order=1,
            team_name='Core Team',
            team_order=1,
        )
    
    def test_member_creation(self):
        """Test member is created correctly."""
        self.assertEqual(self.member.name, 'Test Member')
        self.assertEqual(self.member.get_display_role(), 'Founder')
    
    def test_custom_role(self):
        """Test custom role for 'other'."""
        self.member.role = 'other'
        self.member.custom_role = 'Custom Role'
        self.member.save()
        
        self.assertEqual(self.member.get_display_role(), 'Custom Role')
    
    def test_profile_image_fallback(self):
        """Test fallback avatar URL."""
        url = self.member.get_profile_image_url()
        self.assertIn('avatar-placeholder.svg', url)


class DocSettingsTests(TestCase):
    """Test DocSettings singleton."""
    
    def test_singleton_creation(self):
        """Test settings singleton."""
        settings1 = DocSettings.get_instance()
        settings2 = DocSettings.get_instance()
        self.assertEqual(settings1.id, settings2.id)
        self.assertEqual(str(settings1.id), '00000000-0000-0000-0000-000000000002')


class DocsViewsTests(TestCase):
    """Test documentation views."""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user('testuser', 'test@test.com', 'password')
        self.staff_user = User.objects.create_user('staff', 'staff@test.com', 'password', is_staff=True)
        
        # Ensure access control allows access
        ac = DocAccessControl.get_instance()
        ac.is_enabled = True
        ac.schedule_start = timezone.now() - timedelta(days=1)
        ac.schedule_end = timezone.now() + timedelta(days=30)
        ac.save()
    
    def test_docs_home_anonymous(self):
        """Test public docs view for anonymous user."""
        request = self.factory.get('/docs/')
        request.user = AnonymousUser()
        request.session = {}
        
        response = docs_home(request)
        self.assertEqual(response.status_code, 200)
    
    def test_docs_home_staff(self):
        """Test public docs view for staff user."""
        request = self.factory.get('/docs/')
        request.user = self.staff_user
        request.session = {}
        
        response = docs_home(request)
        self.assertEqual(response.status_code, 200)
    
    def test_docs_export_markdown(self):
        """Test markdown export."""
        request = self.factory.get('/docs/export/?format=markdown')
        request.user = AnonymousUser()
        request.session = {}
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        
        response = docs_export(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/markdown')
        self.assertIn('attachment', response['Content-Disposition'])
    
    def test_docs_export_html(self):
        """Test HTML export."""
        request = self.factory.get('/docs/export/?format=html')
        request.user = AnonymousUser()
        request.session = {}
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        
        response = docs_export(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/html')
    
    def test_docs_access_status(self):
        """Test access status API."""
        request = self.factory.get('/docs/api/access/')
        request.user = AnonymousUser()
        
        response = docs_access_status(request)
        self.assertEqual(response.status_code, 200)
        
        import json
        data = json.loads(response.content)
        self.assertIn('accessible', data)
        self.assertTrue(data['accessible'])
    
    def test_docs_admin_requires_staff(self):
        """Test admin view requires staff."""
        # Anonymous should be redirected to login
        request = self.factory.get('/docs/admin/')
        request.user = AnonymousUser()
        request.session = {}
        
        response = docs_admin(request)
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
        # Staff should have access
        request = self.factory.get('/docs/admin/')
        request.user = self.staff_user
        request.session = {}
        
        response = docs_admin(request)
        self.assertEqual(response.status_code, 200)


class LiveDataProvidersTests(TestCase):
    """Test live data providers."""
    
    def test_all_providers_registered(self):
        """Test all expected providers are registered."""
        providers = get_all_providers()
        expected = [
            'feature_matrix', 'architecture', 'tech_stack', 'api_docs',
            'data_layer', 'ai_layer', 'performance', 'security',
            'roadmap', 'changelog'
        ]
        for exp in expected:
            self.assertIn(exp, providers)
    
    def test_feature_matrix_provider(self):
        """Test feature matrix provider returns data."""
        provider = get_provider('feature_matrix')
        self.assertIsNotNone(provider)
        data = provider()
        self.assertIn('feature_categories', data)
        self.assertIn('stats', data)
    
    def test_architecture_provider(self):
        """Test architecture provider returns data."""
        provider = get_provider('architecture')
        data = provider()
        self.assertIn('components', data)
        self.assertIn('data_flows', data)
    
    def test_tech_stack_provider(self):
        """Test tech stack provider returns data."""
        provider = get_provider('tech_stack')
        data = provider()
        self.assertIn('tech_stack', data)
        self.assertIn('frontend', data['tech_stack'])
        self.assertIn('backend', data['tech_stack'])


class DocsURLTests(TestCase):
    """Test documentation URLs."""
    
    def test_docs_home_url(self):
        """Test docs home URL resolves."""
        url = reverse('docs:home')
        self.assertEqual(url, '/docs/')
    
    def test_docs_export_url(self):
        """Test docs export URL resolves."""
        url = reverse('docs:export')
        self.assertEqual(url, '/docs/export/')
    
    def test_docs_admin_url(self):
        """Test docs admin URL resolves."""
        url = reverse('docs:admin')
        self.assertEqual(url, '/docs/admin/')
    
    def test_docs_section_create_url(self):
        """Test section create URL resolves."""
        url = reverse('docs:section_create')
        self.assertEqual(url, '/docs/admin/section/')
    
    def test_docs_team_create_url(self):
        """Test team create URL resolves."""
        url = reverse('docs:team_create')
        self.assertEqual(url, '/docs/admin/team/')