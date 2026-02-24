from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from ai_blog.apps.blog.models import BlogPost, Engagement, GenerationJob, Persona
from ai_blog.apps.blog.tasks import generate_post_job


class GenerationApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user('user@test.com', 'user@test.com', 'pass1234')
        self.persona = Persona.objects.create(
            name='Technical Writer',
            slug='technical',
            persona_type='technical',
            system_prompt='Write clearly',
            description='Technical persona',
        )

    @patch('ai_blog.apps.blog.views.generate_post_job.delay')
    def test_generate_returns_queued_job(self, mock_delay):
        token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        mock_delay.return_value = Mock(id='task-123')
        response = self.client.post(
            '/api/generate/',
            {'topic': 'Future of AI', 'persona': 'technical', 'speed': 'fast'},
            format='json',
        )
        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.data['status'], 'queued')
        self.assertIn('job_id', response.data)
        self.assertTrue(GenerationJob.objects.filter(id=response.data['job_id']).exists())

    def test_generate_requires_admin_when_enabled(self):
        response = self.client.post(
            '/api/generate/',
            {'topic': 'Future of AI', 'persona': 'technical'},
            format='json',
        )
        self.assertEqual(response.status_code, 401)

    @patch('ai_blog.apps.blog.views.generate_post_job.delay')
    def test_generate_allows_authenticated_user_token(self, mock_delay):
        token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        mock_delay.return_value = Mock(id='task-123')
        response = self.client.post(
            '/api/generate/',
            {'topic': 'Future of AI', 'persona': 'technical'},
            format='json',
        )
        self.assertEqual(response.status_code, 202)

    @patch('ai_blog.apps.blog.services.generation.BlogGenerationService.generate_post')
    def test_generation_task_transitions_to_completed(self, mock_generate):
        post = BlogPost.objects.create(
            owner=self.user,
            title='Draft',
            slug='draft-task',
            topic_input='Future of AI',
            raw_prompt='prompt',
            persona=self.persona,
            status=BlogPost.PostStatus.COMPLETED,
        )
        mock_generate.return_value = {'blog_post_id': post.id}
        job = GenerationJob.objects.create(
            topic='Future of AI',
            owner=self.user,
            persona_slug='technical',
            speed='fast',
            status=GenerationJob.JobStatus.QUEUED,
        )

        generate_post_job.run(job.id)
        job.refresh_from_db()
        self.assertEqual(job.status, GenerationJob.JobStatus.COMPLETED)
        self.assertEqual(job.blog_post_id, post.id)


class EngagementIntegrityTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user('user2@test.com', 'user2@test.com', 'pass1234')
        self.persona = Persona.objects.create(
            name='Technical Writer',
            slug='technical',
            persona_type='technical',
            system_prompt='Write clearly',
            description='Technical persona',
        )
        self.post = BlogPost.objects.create(
            owner=self.user,
            title='Draft',
            slug='draft-engagement',
            topic_input='Future of AI',
            raw_prompt='prompt',
            persona=self.persona,
            status=BlogPost.PostStatus.COMPLETED,
        )

    def test_single_session_keeps_single_reaction(self):
        payload = {'blog_id': self.post.id, 'session_id': 'session-1', 'action': 'like'}
        r1 = self.client.post('/api/engage/', payload, format='json')
        self.assertEqual(r1.status_code, 200)
        payload['action'] = 'dislike'
        r2 = self.client.post('/api/engage/', payload, format='json')
        self.assertEqual(r2.status_code, 200)

        self.assertEqual(Engagement.objects.filter(blog_post=self.post, session_id='session-1').count(), 1)
        self.assertEqual(Engagement.objects.get(blog_post=self.post, session_id='session-1').action, 'dislike')

    def test_public_slug_endpoint_returns_completed_post(self):
        response = self.client.get(f'/api/posts/slug/{self.post.slug}/public/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['slug'], self.post.slug)

    def test_public_slug_endpoint_hides_non_completed_post(self):
        self.post.status = BlogPost.PostStatus.DRAFT
        self.post.save(update_fields=['status'])
        response = self.client.get(f'/api/posts/slug/{self.post.slug}/public/')
        self.assertEqual(response.status_code, 404)
