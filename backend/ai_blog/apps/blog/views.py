"""
DRF Views for AI Blog Generator.
Thin API layer that delegates to service layer.
"""
import hashlib
from urllib.parse import urlencode

from rest_framework import mixins, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.throttling import ScopedRateThrottle
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_datetime, parse_date
from django.conf import settings
from django.db.models import Avg, Count, Q
from kombu.exceptions import OperationalError as KombuOperationalError

from .models import BlogPost, Persona, Engagement, GenerationJob
from .serializers import (
    PersonaSerializer,
    BlogPostSerializer,
    BlogPostListSerializer,
    BlogPostDetailSerializer,
    BlogPostUpdateSerializer,
    BlogGenerationSerializer,
    BlogGenerationResponseSerializer,
    GenerationStatusSerializer,
    EngagementActionSerializer,
    EngagementResponseSerializer,
    AnalyticsSerializer
)
from .services.generation import BlogGenerationService
from .services.engagement import EngagementService
from .tasks import generate_post_job
from ai_blog.apps.core.api_errors import error_response, service_error_response


def visible_post_or_404(request, blog_id: int) -> BlogPost:
    """
    Resolve a post the caller is allowed to see: published posts are public,
    everything else is owner-only. Prevents draft enumeration by ID.
    """
    queryset = BlogPost.objects.filter(id=blog_id)
    visible = Q(status=BlogPost.PostStatus.COMPLETED)
    if request.user.is_authenticated:
        visible |= Q(owner=request.user)
    return get_object_or_404(queryset.filter(visible))


class PersonaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for listing and retrieving Personas.
    Public reference data - readable before sign-in.
    """
    queryset = Persona.objects.filter(is_active=True)
    serializer_class = PersonaSerializer
    lookup_field = 'slug'
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        # Persona list is identical for every caller, so it is safe to cache the
        # rendered payload process-wide (unlike any per-user endpoint).
        cache_key = 'personas:active:v1'
        cached = cache.get(cache_key)
        if cached is not None:
            return Response(cached)

        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, settings.CACHE_TTL_SECONDS)
        return response


class BlogPostViewSet(mixins.ListModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    """
    ViewSet for reading, editing and deleting the caller's own posts.

    Creation is deliberately absent: posts are only created by the generation
    pipeline (POST /api/generate/), which is what populates owner, slug and
    raw_prompt.
    """
    lookup_field = 'id'
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return BlogPostListSerializer
        elif self.action == 'retrieve':
            return BlogPostDetailSerializer
        elif self.action in ('update', 'partial_update'):
            return BlogPostUpdateSerializer
        return BlogPostSerializer

    def get_queryset(self):
        """Own posts only, plus filters from query params"""
        queryset = (
            BlogPost.objects
            .select_related('persona')
            .filter(owner=self.request.user)
        )

        if self.action == 'list':
            # The list payload never returns the body, so skip loading the
            # large text/JSON columns; word counts come from content_structure.
            queryset = queryset.defer('generated_content', 'raw_prompt', 'sources', 'metadata')

        status_filter = self.request.query_params.get('status')
        persona = self.request.query_params.get('persona')

        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if persona:
            queryset = queryset.filter(persona__slug=persona)

        return queryset


class BlogGenerationView(APIView):
    """
    API endpoint for generating blog posts.
    Delegates to BlogGenerationService.
    """

    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'generate'

    @staticmethod
    def _run_sync_generation(data, owner):
        service = BlogGenerationService()
        return service.generate_post(
            topic=data['topic'],
            persona_slug=data['persona'],
            owner=owner,
            additional_context=data.get('additional_context'),
            speed=data.get('speed', 'fast')
        )

    def post(self, request):
        """Generate a new blog post"""
        # Validate request
        serializer = BlogGenerationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        try:
            sync = request.query_params.get('sync', 'false').lower() == 'true'
            force_sync = getattr(settings, 'QUEUE_ALWAYS_SYNC', False)

            if sync or force_sync:
                # Backward compatibility path for internal/dev use.
                result = self._run_sync_generation(data, request.user)
                response_serializer = BlogGenerationResponseSerializer(result)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)

            job = GenerationJob.objects.create(
                topic=data['topic'],
                owner=request.user,
                persona_slug=data['persona'],
                session_id=data.get('session_id', ''),
                speed=data.get('speed', 'fast'),
                additional_context=data.get('additional_context') or {},
                status=GenerationJob.JobStatus.QUEUED,
                progress=0
            )
            try:
                task = generate_post_job.delay(job.id)
                job.task_id = task.id or ''
                job.save(update_fields=['task_id', 'updated_at'])
            except (KombuOperationalError, ConnectionError, OSError):
                if getattr(settings, 'QUEUE_SYNC_FALLBACK', False):
                    # Local/dev reliability: continue with sync path if queue is unavailable.
                    result = self._run_sync_generation(data, request.user)
                    response_serializer = BlogGenerationResponseSerializer(result)
                    return Response(response_serializer.data, status=status.HTTP_201_CREATED)
                return Response({
                    'error': {
                        'code': 'QUEUE_UNAVAILABLE',
                        'message': 'Generation queue is unavailable. Start Redis and Celery worker.',
                        'details': {'provider': 'celery'}
                    }
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

            response_serializer = BlogGenerationResponseSerializer({
                'success': True,
                'job_id': job.id,
                'status': GenerationJob.JobStatus.QUEUED
            })
            return Response(response_serializer.data, status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            return service_error_response(
                e,
                'GENERATION_ERROR',
                'Generation failed. Please try again.',
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class GenerationStatusView(APIView):
    """Poll status for asynchronous blog generation jobs."""

    permission_classes = [IsAuthenticated]

    def get(self, request, job_id):
        job = get_object_or_404(GenerationJob, id=job_id, owner=request.user)
        serializer = GenerationStatusSerializer(job)
        return Response(serializer.data)


class EngagementActionView(APIView):
    """
    Record an anonymous like/dislike against a publicly visible post.
    Throttled per client because it is unauthenticated and moves a public score.
    """

    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'engage'

    def post(self, request):
        serializer = EngagementActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        post = visible_post_or_404(request, data['blog_id'])

        try:
            service = EngagementService()
            result = service.record_action(
                blog_post_id=post.id,
                session_id=data['session_id'],
                action=data['action']
            )

            response_serializer = EngagementResponseSerializer(result)
            return Response(response_serializer.data)

        except Exception as e:
            return service_error_response(
                e,
                'ENGAGEMENT_ERROR',
                'Could not record engagement.',
                status.HTTP_400_BAD_REQUEST,
            )


class EngagementMetricsView(APIView):
    """Read like/dislike counts for a publicly visible post."""

    permission_classes = [AllowAny]

    def get(self, request, blog_id):
        post = visible_post_or_404(request, blog_id)
        service = EngagementService()

        session_id = request.query_params.get('session_id')
        metrics = service.get_post_metrics(post.id, post=post)
        metrics['user_action'] = (
            service.get_user_action(post.id, session_id) if session_id else None
        )

        return Response(metrics)


class AnalyticsView(APIView):
    """
    API endpoint for analytics data over the caller's own posts.
    """

    permission_classes = [IsAuthenticated]

    @staticmethod
    def _cache_key(request) -> str:
        """Per-user cache key. Analytics is private, so the user id is part of it."""
        query = urlencode(sorted(request.query_params.items()))
        digest = hashlib.sha256(query.encode('utf-8')).hexdigest()[:16]
        return f'analytics:v1:{request.user.pk}:{digest}'

    @staticmethod
    def _apply_date_bound(queryset, raw_value: str, bound: str):
        """Filter created_at by an ISO datetime or plain date string."""
        parsed = parse_datetime(raw_value)
        if parsed:
            return queryset.filter(**{f'created_at__{bound}': parsed})

        parsed_date = parse_date(raw_value)
        if parsed_date:
            return queryset.filter(**{f'created_at__date__{bound}': parsed_date})

        return queryset

    def get(self, request):
        """Get overall analytics"""
        cache_key = self._cache_key(request)
        cached = cache.get(cache_key)
        if cached is not None:
            return Response(cached)

        order = request.query_params.get('order', 'desc')
        sort = request.query_params.get('sort', 'sentiment')
        raw_limit = request.query_params.get('limit', '20')
        try:
            limit = max(1, min(int(raw_limit), 100))
        except (TypeError, ValueError):
            return error_response(
                'INVALID_LIMIT',
                "Query parameter 'limit' must be an integer between 1 and 100.",
                status.HTTP_400_BAD_REQUEST,
            )

        try:
            posts = BlogPost.objects.filter(
                status=BlogPost.PostStatus.COMPLETED,
                owner=request.user,
            )
            date_from = request.query_params.get('from')
            date_to = request.query_params.get('to')
            if date_from:
                posts = self._apply_date_bound(posts, date_from, 'gte')
            if date_to:
                posts = self._apply_date_bound(posts, date_to, 'lte')

            # One aggregate query instead of loading every post row into Python
            # just to average a single integer column.
            totals = posts.aggregate(
                total_posts=Count('id'),
                avg_sentiment=Avg('sentiment_score'),
            )
            total_posts = totals['total_posts'] or 0
            avg_sentiment = totals['avg_sentiment'] or 0

            reactions = Engagement.objects.filter(blog_post__in=posts).aggregate(
                likes=Count('id', filter=Q(action='like')),
                dislikes=Count('id', filter=Q(action='dislike')),
            )
            total_likes = reactions['likes'] or 0
            total_dislikes = reactions['dislikes'] or 0
            total_engagements = total_likes + total_dislikes

            sort_key_map = {
                'likes': 'likes',
                'dislikes': 'dislikes',
                'reactions': 'total_reactions',
                'sentiment': 'sentiment_score',
            }
            sort_key = sort_key_map.get(sort, 'sentiment_score')
            order_by_field = sort_key if order == 'asc' else f'-{sort_key}'

            # values() before annotate() so only the columns the payload needs
            # are selected - never the full markdown body.
            top_posts = [
                {
                    'id': row['id'],
                    'title': row['title'],
                    'slug': row['slug'],
                    'sentiment_score': row['sentiment_score'],
                    'likes': row['likes'],
                    'dislikes': row['dislikes'],
                    'total_reactions': row['total_reactions'],
                    'persona': row['persona__name'],
                    'created_at': row['created_at'].isoformat(),
                }
                for row in posts.values(
                    'id', 'title', 'slug', 'sentiment_score', 'persona__name', 'created_at'
                ).annotate(
                    likes=Count('engagements', filter=Q(engagements__action='like')),
                    dislikes=Count('engagements', filter=Q(engagements__action='dislike')),
                    total_reactions=Count('engagements'),
                ).order_by(order_by_field, '-created_at')[:limit]
            ]

            reaction_rate = (total_engagements / total_posts) if total_posts else 0

            serializer = AnalyticsSerializer({
                'total_posts': total_posts,
                'total_engagements': total_engagements,
                'total_likes': total_likes,
                'total_dislikes': total_dislikes,
                'reaction_rate': round(reaction_rate, 2),
                'avg_sentiment_score': round(avg_sentiment, 2),
                'top_posts': top_posts
            })
            cache.set(cache_key, serializer.data, settings.CACHE_TTL_SECONDS)
            return Response(serializer.data)

        except Exception as e:
            return error_response(
                'ANALYTICS_ERROR',
                'Could not build analytics.',
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                exc=e,
            )


class PublicBlogPostBySlugView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, slug):
        post = get_object_or_404(
            BlogPost.objects.select_related('persona').defer('raw_prompt'),
            slug=slug,
            status=BlogPost.PostStatus.COMPLETED,
        )
        serializer = BlogPostDetailSerializer(post)
        return Response(serializer.data)
