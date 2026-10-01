from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from ai_blog.apps.blog.models import BlogPost, Engagement, GenerationJob, Persona
from ai_blog.apps.blog.services.generation import BlogGenerationService
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

    def test_public_slug_endpoint_requires_no_auth(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(f'/api/posts/slug/{self.post.slug}/public/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['slug'], self.post.slug)

    def test_public_slug_endpoint_404_for_unknown_slug(self):
        response = self.client.get('/api/posts/slug/does-not-exist/public/')
        self.assertEqual(response.status_code, 404)

    def test_public_share_works_for_another_owners_post(self):
        other_user = get_user_model().objects.create_user(
            'other@test.com', 'other@test.com', 'pass1234'
        )
        other_post = BlogPost.objects.create(
            owner=other_user,
            title='Another Owners Post',
            slug='another-owners-post',
            topic_input='Different topic',
            raw_prompt='prompt',
            persona=self.persona,
            status=BlogPost.PostStatus.COMPLETED,
        )
        response = self.client.get(f'/api/posts/slug/{other_post.slug}/public/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['slug'], other_post.slug)
        self.assertEqual(response.data['title'], 'Another Owners Post')

    def test_engagement_metrics_endpoint_returns_counts_and_user_action(self):
        # Two separate anonymous sessions react to the post.
        self.client.post(
            '/api/engage/',
            {'blog_id': self.post.id, 'session_id': 'sess-a', 'action': 'like'},
            format='json',
        )
        self.client.post(
            '/api/engage/',
            {'blog_id': self.post.id, 'session_id': 'sess-b', 'action': 'dislike'},
            format='json',
        )
        response = self.client.get(
            f'/api/posts/{self.post.id}/engagement/?session_id=sess-a'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['likes'], 1)
        self.assertEqual(response.data['dislikes'], 1)
        self.assertEqual(response.data['user_action'], 'like')
        self.assertEqual(response.data['sentiment_score'], 0)

    def test_engagement_metrics_endpoint_reports_session_without_reaction(self):
        response = self.client.get(
            f'/api/posts/{self.post.id}/engagement/?session_id=no-reaction'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.data['user_action'])
        self.assertEqual(response.data['likes'], 0)
        self.assertEqual(response.data['dislikes'], 0)


class BlogEditTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user('edit@test.com', 'edit@test.com', 'pass1234')
        self.token, _ = Token.objects.get_or_create(user=self.user)
        self.persona = Persona.objects.create(
            name='Technical Writer',
            slug='technical',
            persona_type='technical',
            system_prompt='Write clearly',
            description='Technical persona',
        )
        self.post = BlogPost.objects.create(
            owner=self.user,
            title='Original Title',
            slug='edit-test',
            topic_input='Original topic',
            raw_prompt='prompt',
            generated_content='# Heading\n\nOriginal body content here.',
            content_structure={'word_count': 6, 'reading_time_minutes': 1, 'heading_count': 1, 'headings': []},
            persona=self.persona,
            status=BlogPost.PostStatus.COMPLETED,
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

    def test_update_edits_title_topic_and_content(self):
        response = self.client.patch(
            f'/api/posts/{self.post.id}/',
            {
                'title': 'Updated Title',
                'topic_input': 'Updated topic',
                'generated_content': '# New heading\n\nBrand new body.',
            },
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'Updated Title')
        self.assertEqual(self.post.topic_input, 'Updated topic')
        self.assertEqual(self.post.generated_content, '# New heading\n\nBrand new body.')

    def test_update_recomputes_content_structure(self):
        response = self.client.patch(
            f'/api/posts/{self.post.id}/',
            {'generated_content': '# A\n\n# B\n\n# C\n\none two three four'},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.post.refresh_from_db()
        self.assertEqual(self.post.content_structure['heading_count'], 3)
        # 'A', 'B', 'C', 'one', 'two', 'three', 'four' - the '#' markers are
        # markdown syntax, not prose, so they are not counted.
        self.assertEqual(self.post.content_structure['word_count'], 7)
        self.assertEqual(self.post.content_structure['reading_time_minutes'], 1)

    def test_word_count_ignores_markdown_syntax(self):
        """Model property and stored structure agree, and both exclude syntax."""
        response = self.client.patch(
            f'/api/posts/{self.post.id}/',
            {'generated_content': '## Heading\n\n- **bold** item\n\n| a | b |\n\nplain words here'},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.post.refresh_from_db()
        self.assertEqual(
            self.post.content_structure['word_count'],
            self.post.word_count,
        )
        # Heading, bold, item, a, b, plain, words, here
        self.assertEqual(self.post.word_count, 8)

    def test_headings_inside_code_fences_are_not_counted(self):
        response = self.client.patch(
            f'/api/posts/{self.post.id}/',
            {'generated_content': '# Real heading\n\n```python\n# a comment\n```\n\nbody text'},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.post.refresh_from_db()
        self.assertEqual(self.post.content_structure['heading_count'], 1)

    def test_update_requires_owner(self):
        other_user = get_user_model().objects.create_user('other2@test.com', 'other2@test.com', 'pass1234')
        other_token, _ = Token.objects.get_or_create(user=other_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {other_token.key}')
        response = self.client.patch(
            f'/api/posts/{self.post.id}/',
            {'title': 'Nope'},
            format='json',
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_requires_owner(self):
        other_user = get_user_model().objects.create_user('other3@test.com', 'other3@test.com', 'pass1234')
        other_token, _ = Token.objects.get_or_create(user=other_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {other_token.key}')
        response = self.client.delete(f'/api/posts/{self.post.id}/')
        self.assertEqual(response.status_code, 404)

    def test_update_publishes_draft_and_sets_published_at(self):
        self.post.status = BlogPost.PostStatus.DRAFT
        self.post.published_at = None
        self.post.save(update_fields=['status', 'published_at'])

        response = self.client.patch(
            f'/api/posts/{self.post.id}/',
            {'status': 'completed'},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.post.refresh_from_db()
        self.assertEqual(self.post.status, BlogPost.PostStatus.COMPLETED)
        self.assertIsNotNone(self.post.published_at)

    def test_update_unpublishes_to_draft_and_clears_published_at(self):
        self.post.published_at = timezone.now()
        self.post.save(update_fields=['published_at'])

        response = self.client.patch(
            f'/api/posts/{self.post.id}/',
            {'status': 'draft'},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.post.refresh_from_db()
        self.assertEqual(self.post.status, BlogPost.PostStatus.DRAFT)
        self.assertIsNone(self.post.published_at)

    def test_cannot_publish_post_with_empty_content(self):
        """A draft with no body must not be publishable."""
        self.post.status = BlogPost.PostStatus.DRAFT
        self.post.generated_content = ''
        self.post.published_at = None
        self.post.save(update_fields=['status', 'generated_content', 'published_at'])

        response = self.client.patch(
            f'/api/posts/{self.post.id}/',
            {'status': 'completed'},
            format='json',
        )
        self.assertEqual(response.status_code, 400)
        self.post.refresh_from_db()
        self.assertEqual(self.post.status, BlogPost.PostStatus.DRAFT)
        self.assertIsNone(self.post.published_at)


class ApiContractTests(TestCase):
    """Regressions for endpoints that used to fail with a 500 or leak data."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user('c1@test.com', 'c1@test.com', 'pass1234')
        self.token, _ = Token.objects.get_or_create(user=self.user)
        self.persona = Persona.objects.create(
            name='Technical Writer',
            slug='technical',
            persona_type='technical',
            system_prompt='Write clearly',
            description='Technical persona',
        )
        self.post = BlogPost.objects.create(
            owner=self.user,
            title='Published',
            slug='contract-published',
            topic_input='Topic',
            raw_prompt='prompt',
            persona=self.persona,
            status=BlogPost.PostStatus.COMPLETED,
        )
        self.draft = BlogPost.objects.create(
            owner=self.user,
            title='Draft',
            slug='contract-draft',
            topic_input='Topic',
            raw_prompt='prompt',
            persona=self.persona,
            status=BlogPost.PostStatus.DRAFT,
        )

    def test_engage_endpoint_rejects_get_with_405(self):
        """Used to raise TypeError (500) because one view served both routes."""
        response = self.client.get('/api/engage/')
        self.assertEqual(response.status_code, 405)

    def test_engagement_metrics_endpoint_rejects_post_with_405(self):
        response = self.client.post(
            f'/api/posts/{self.post.id}/engagement/', {}, format='json'
        )
        self.assertEqual(response.status_code, 405)

    def test_engagement_on_draft_post_is_404_not_recorded(self):
        """Drafts must not be reachable by ID from the anonymous engage route."""
        response = self.client.post(
            '/api/engage/',
            {'blog_id': self.draft.id, 'session_id': 'sess-x', 'action': 'like'},
            format='json',
        )
        self.assertEqual(response.status_code, 404)
        self.assertFalse(Engagement.objects.filter(blog_post=self.draft).exists())

    def test_post_list_excludes_other_owners_posts(self):
        other_user = get_user_model().objects.create_user('c2@test.com', 'c2@test.com', 'pass1234')
        BlogPost.objects.create(
            owner=other_user,
            title='Not Yours',
            slug='contract-not-yours',
            topic_input='Topic',
            raw_prompt='prompt',
            persona=self.persona,
            status=BlogPost.PostStatus.COMPLETED,
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.get('/api/posts/')
        self.assertEqual(response.status_code, 200)
        slugs = {row['slug'] for row in response.data['results']}
        self.assertNotIn('contract-not-yours', slugs)
        self.assertIn('contract-published', slugs)

    def test_analytics_requires_authentication(self):
        response = self.client.get('/api/analytics/')
        self.assertEqual(response.status_code, 401)

    def test_analytics_rejects_non_numeric_limit_with_400(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.get('/api/analytics/?limit=abc')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error']['code'], 'INVALID_LIMIT')

    def test_analytics_cache_is_scoped_per_user(self):
        """A cached analytics payload must never be served to another account."""
        cache.clear()
        other_user = get_user_model().objects.create_user('c3@test.com', 'c3@test.com', 'pass1234')
        other_token, _ = Token.objects.get_or_create(user=other_user)

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        mine = self.client.get('/api/analytics/')
        self.assertEqual(mine.status_code, 200)
        self.assertEqual(mine.data['total_posts'], 1)

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {other_token.key}')
        theirs = self.client.get('/api/analytics/')
        self.assertEqual(theirs.status_code, 200)
        self.assertEqual(theirs.data['total_posts'], 0)

    def test_generated_title_replaces_draft_placeholder(self):
        """The parsed headline used to be dropped, leaving 'Draft: <topic>'."""
        post = BlogPost.objects.create(
            owner=self.user,
            title='Draft: Future of AI',
            slug='contract-title-fix',
            topic_input='Future of AI',
            raw_prompt='prompt',
            persona=self.persona,
            status=BlogPost.PostStatus.GENERATING,
        )
        service = BlogGenerationService()
        service._update_post_with_content(
            blog_post=post,
            content='# Real\n\nGenerated body text.',
            sources=[],
            structure={},
            metadata={},
            title='The Real Generated Headline',
        )
        post.refresh_from_db()
        self.assertEqual(post.title, 'The Real Generated Headline')
        self.assertEqual(post.status, BlogPost.PostStatus.COMPLETED)
        self.assertIsNotNone(post.published_at)
