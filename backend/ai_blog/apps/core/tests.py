from django.contrib.auth import get_user_model
from django.test import TestCase
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
        response = self.client.post('/api/auth/token/', {'username': 'user1', 'password': 'pass1234'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)

