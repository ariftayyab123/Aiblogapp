from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from rest_framework.test import APIClient


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
