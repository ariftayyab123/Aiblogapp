from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from ai_blog.apps.core.views import AdminRegisterView, RegisterView, TokenAuthView


class HealthAndAuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_health_live(self):
        response = self.client.get('/health/live')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'ok')

    def test_token_auth_endpoint(self):
        user = get_user_model().objects.create_user('user1', 'user@test.com', 'pass1234')
        response = self.client.post('/api/auth/token/', {'email': 'user@test.com', 'password': 'pass1234'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)
        self.assertIn('user', response.data)

    def test_user_register_endpoint(self):
        response = self.client.post(
            '/api/auth/register/',
            {
                'email': 'newuser@test.com',
                'password': 'StrongerPass123!',
                'confirm_password': 'StrongerPass123!',
            },
            format='json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.data.get('success'))
        self.assertIn('token', response.data)

    @override_settings(ADMIN_INVITE_CODE='local-admin-invite')
    def test_admin_register_with_invite_code(self):
        response = self.client.post(
            '/api/auth/admin/register/',
            {
                'username': 'admin_new',
                'password': 'StrongerPass123!',
                'invite_code': 'local-admin-invite',
            },
            format='json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.data.get('success'))
        self.assertIn('token', response.data)

    @override_settings(ADMIN_INVITE_CODE='local-admin-invite')
    def test_admin_register_rejects_invalid_invite_code(self):
        response = self.client.post(
            '/api/auth/admin/register/',
            {
                'username': 'admin_new2',
                'password': 'StrongerPass123!',
                'invite_code': 'wrong-code',
            },
            format='json'
        )
        self.assertEqual(response.status_code, 400)

    def test_user_register_rejects_weak_password(self):
        """validate_password() is only effective with AUTH_PASSWORD_VALIDATORS set."""
        response = self.client.post(
            '/api/auth/register/',
            {
                'email': 'weak@test.com',
                'password': 'password',
                'confirm_password': 'password',
            },
            format='json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(get_user_model().objects.filter(email='weak@test.com').exists())

    @override_settings(ADMIN_INVITE_CODE='local-admin-invite')
    def test_admin_register_rejects_weak_password(self):
        response = self.client.post(
            '/api/auth/admin/register/',
            {
                'username': 'admin_weak',
                'password': '12345678',
                'invite_code': 'local-admin-invite',
            },
            format='json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(get_user_model().objects.filter(username='admin_weak').exists())

    def test_auth_throttle_scope_has_a_configured_rate(self):
        """
        ScopedRateThrottle raises ImproperlyConfigured at request time when its
        scope is missing from DEFAULT_THROTTLE_RATES, so assert the wiring here
        rather than discovering it in production.
        """
        rates = settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']
        for view in (TokenAuthView, RegisterView, AdminRegisterView):
            with self.subTest(view=view.__name__):
                self.assertIn(view.throttle_scope, rates)
                self.assertTrue(rates[view.throttle_scope])

    def test_logout_requires_authentication(self):
        response = self.client.post('/api/auth/logout/')
        self.assertEqual(response.status_code, 401)

    def test_logout_invalidates_token(self):
        user = get_user_model().objects.create_user('logout', 'logout@test.com', 'pass1234')
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

        response = self.client.post('/api/auth/logout/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data.get('success'))
        self.assertFalse(Token.objects.filter(user=user).exists())

        # The old token must no longer authenticate an authenticated endpoint.
        follow_up = self.client.get('/api/analytics/')
        self.assertEqual(follow_up.status_code, 401)
