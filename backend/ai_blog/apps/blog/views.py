"""
DRF Views for AI Blog Generator.
Thin API layer that delegates to service layer.
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from django.views.decorators.cache import cache_page
from django.utils.dateparse import parse_datetime, parse_date
from django.conf import settings
from django.db.models import Count, Q
from kombu.exceptions import OperationalError as KombuOperationalError

from .models import BlogPost, Persona, Engagement, GenerationJob
from .serializers import (
    PersonaSerializer,
    BlogPostSerializer,
    BlogPostListSerializer,
    BlogPostDetailSerializer,
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
from ai_blog.apps.core.permissions import IsAdminOrDevOpen


class PersonaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for listing and retrieving Personas.
    """
    queryset = Persona.objects.filter(is_active=True)
    serializer_class = PersonaSerializer
    lookup_field = 'slug'

    @method_decorator(cache_page(settings.CACHE_TTL_SECONDS))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class BlogPostViewSet(viewsets.ModelViewSet):
    """
    ViewSet for BlogPost CRUD operations.
    """
    queryset = BlogPost.objects.select_related('persona').all()
    lookup_field = 'id'

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return BlogPostListSerializer
        elif self.action == 'retrieve':
            return BlogPostDetailSerializer
        return BlogPostSerializer

    def get_queryset(self):
        """Apply filters from query params"""
        queryset = super().get_queryset()
        status_filter = self.request.query_params.get('status')
        persona = self.request.query_params.get('persona')

        if getattr(settings, 'ADMIN_AUTH_REQUIRED', False):
            if not (self.request.user and self.request.user.is_authenticated and self.request.user.is_staff):
                queryset = queryset.filter(status=BlogPost.PostStatus.COMPLETED)

        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if persona:
            queryset = queryset.filter(persona__slug=persona)

        return queryset

    def get_permissions(self):
        if self.action in {'destroy', 'create', 'update', 'partial_update'}:
            return [IsAdminOrDevOpen()]
        return [AllowAny()]


class BlogGenerationView(APIView):
    """
    API endpoint for generating blog posts.
    Delegates to BlogGenerationService.
    """

    permission_classes = [IsAdminOrDevOpen]

    @staticmethod
    def _run_sync_generation(data):
        service = BlogGenerationService()
        return service.generate_post(
            topic=data['topic'],
            persona_slug=data['persona'],
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

            if sync:
                # Backward compatibility path for internal/dev use.
                result = self._run_sync_generation(data)
                response_serializer = BlogGenerationResponseSerializer(result)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)

            job = GenerationJob.objects.create(
                topic=data['topic'],
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
                    result = self._run_sync_generation(data)
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
            if hasattr(e, 'to_dict'):
                return Response(e.to_dict(), status=status.HTTP_400_BAD_REQUEST)

            return Response({
                'error': {
                    'code': 'GENERATION_ERROR',
                    'message': str(e),
                    'details': {}
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GenerationStatusView(APIView):
    """Poll status for asynchronous blog generation jobs."""

    permission_classes = [IsAdminOrDevOpen]

    def get(self, request, job_id):
        job = get_object_or_404(GenerationJob, id=job_id)
        serializer = GenerationStatusSerializer(job)
        return Response(serializer.data)


class EngagementView(APIView):
    """
    API endpoint for recording user engagement (likes/dislikes).
    Delegates to EngagementService.
    """

    def post(self, request):
        """Record an engagement action"""
        # Validate request
        serializer = EngagementActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        try:
            # Call service layer
            service = EngagementService()
            result = service.record_action(
                blog_post_id=data['blog_id'],
                session_id=data['session_id'],
                action=data['action']
            )

            response_serializer = EngagementResponseSerializer(result)
            return Response(response_serializer.data)

        except Exception as e:
            if hasattr(e, 'to_dict'):
                return Response(e.to_dict(), status=status.HTTP_400_BAD_REQUEST)

            return Response({
                'error': {
                    'code': 'ENGAGEMENT_ERROR',
                    'message': str(e),
                    'details': {}
                }
            }, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, blog_id):
        """Get engagement metrics for a post"""
        try:
            service = EngagementService()

            # Get session_id from query params
            session_id = request.query_params.get('session_id')
            if session_id:
                user_action = service.get_user_action(blog_id, session_id)
            else:
                user_action = None

            metrics = service.get_post_metrics(blog_id)
            metrics['user_action'] = user_action

            return Response(metrics)

        except Exception as e:
            return Response({
                'error': {
                    'code': 'METRICS_ERROR',
                    'message': str(e),
                    'details': {}
                }
            }, status=status.HTTP_400_BAD_REQUEST)


class AnalyticsView(APIView):
    """
    API endpoint for analytics data.
    """

    permission_classes = [IsAdminOrDevOpen]

    @method_decorator(cache_page(settings.CACHE_TTL_SECONDS))
    def get(self, request):
        """Get overall analytics"""
        try:
            order = request.query_params.get('order', 'desc')
            sort = request.query_params.get('sort', 'sentiment')
            limit = int(request.query_params.get('limit', '20'))
            limit = max(1, min(limit, 100))
            date_from = request.query_params.get('from')
            date_to = request.query_params.get('to')

            posts_queryset = BlogPost.objects.filter(
                status=BlogPost.PostStatus.COMPLETED
            )
            if date_from:
                parsed_from = parse_datetime(date_from)
                if parsed_from:
                    posts_queryset = posts_queryset.filter(created_at__gte=parsed_from)
                else:
                    parsed_from_date = parse_date(date_from)
                    if parsed_from_date:
                        posts_queryset = posts_queryset.filter(created_at__date__gte=parsed_from_date)
            if date_to:
                parsed_to = parse_datetime(date_to)
                if parsed_to:
                    posts_queryset = posts_queryset.filter(created_at__lte=parsed_to)
                else:
                    parsed_to_date = parse_date(date_to)
                    if parsed_to_date:
                        posts_queryset = posts_queryset.filter(created_at__date__lte=parsed_to_date)

            total_posts = posts_queryset.count()
            posts_with_metrics = posts_queryset.annotate(
                likes=Count('engagements', filter=Q(engagements__action='like')),
                dislikes=Count('engagements', filter=Q(engagements__action='dislike')),
                total_reactions=Count('engagements')
            )

            post_ids = posts_queryset.values_list('id', flat=True)
            total_likes = Engagement.objects.filter(
                blog_post_id__in=post_ids,
                action='like'
            ).count()
            total_dislikes = Engagement.objects.filter(
                blog_post_id__in=post_ids,
                action='dislike'
            ).count()
            total_engagements = total_likes + total_dislikes
            avg_sentiment = (
                sum(p.sentiment_score for p in posts_with_metrics) / total_posts
                if total_posts > 0 else 0
            )

            sort_key_map = {
                'likes': 'likes',
                'dislikes': 'dislikes',
                'reactions': 'total_reactions',
                'sentiment': 'sentiment_score',
            }
            sort_key = sort_key_map.get(sort, 'sentiment_score')
            reverse = order != 'asc'
            order_by_field = f"-{sort_key}" if reverse else sort_key
            top_posts_qs = posts_with_metrics.order_by(order_by_field, '-created_at')[:limit]
            top_posts = [
                {
                    'id': p.id,
                    'title': p.title,
                    'slug': p.slug,
                    'sentiment_score': p.sentiment_score,
                    'likes': p.likes,
                    'dislikes': p.dislikes,
                    'total_reactions': p.total_reactions,
                    'persona': p.persona.name if p.persona else None,
                    'created_at': p.created_at.isoformat()
                }
                for p in top_posts_qs
            ]

            reaction_rate = (total_engagements / total_posts) if total_posts else 0

            data = {
                'total_posts': total_posts,
                'total_engagements': total_engagements,
                'total_likes': total_likes,
                'total_dislikes': total_dislikes,
                'reaction_rate': round(reaction_rate, 2),
                'avg_sentiment_score': round(avg_sentiment, 2),
                'top_posts': top_posts
            }

            serializer = AnalyticsSerializer(data)
            return Response(serializer.data)

        except Exception as e:
            return Response({
                'error': {
                    'code': 'ANALYTICS_ERROR',
                    'message': str(e),
                    'details': {}
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Simple list views for ViewSets
def persona_list(request):
    """List all personas"""
    if request.method == 'GET':
        queryset = Persona.objects.filter(is_active=True)
        serializer = PersonaSerializer(queryset, many=True)
        return Response(serializer.data)


def blogpost_list(request):
    """List and create blog posts"""
    if request.method == 'GET':
        queryset = BlogPost.objects.select_related('persona').all()
        serializer = BlogPostListSerializer(queryset, many=True)
        return Response(serializer.data)


def blogpost_detail(request, id):
    """Get a single blog post"""
    if request.method == 'GET':
        queryset = BlogPost.objects.select_related('persona').all()
        post = get_object_or_404(queryset, id=id)
        serializer = BlogPostDetailSerializer(post)
        return Response(serializer.data)
