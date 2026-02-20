"""
Engagement Service.
Handles user engagement (likes, dislikes) and metric aggregation.
"""
from typing import Dict, List
from django.db.models import Count, F, Q
from django.db import transaction
from django.conf import settings

from ai_blog.apps.core.services.base import BaseService, ServiceError
from ..models import BlogPost, Engagement, PostMetric


class EngagementService(BaseService[Engagement]):
    """
    Service for handling user engagement with blog posts.
    Ensures: session-based deduplication, metric aggregation.
    """

    model_class = Engagement
    logger_name = "engagement"

    def execute(self, *args, **kwargs) -> Dict[str, any]:
        """
        BaseService contract implementation.
        Delegates to the main engagement workflow.
        """
        return self.record_action(*args, **kwargs)

    def record_action(
        self,
        blog_post_id: int,
        session_id: str,
        action: str,
        metadata: Dict = None
    ) -> Dict[str, any]:
        """
        Record a user engagement action with toggle behavior.

        Returns:
            {
                'success': bool,
                'action': str,
                'new_score': int,
                'was_toggle': bool,
                'likes_count': int,
                'dislikes_count': int
            }
        """
        self.log_execution(
            "record_action",
            blog_post_id=blog_post_id,
            action=action
        )

        try:
            # Validate
            self._validate_engagement(blog_post_id, session_id, action)

            # Check for existing engagement for this session+post.
            existing = Engagement.objects.filter(
                blog_post_id=blog_post_id,
                session_id=session_id
            ).first()

            if existing and existing.action == action:
                # Toggle off same action.
                existing.delete()
                was_toggle = True
            else:
                # Upsert single action for (blog_post, session_id).
                Engagement.objects.update_or_create(
                    blog_post_id=blog_post_id,
                    session_id=session_id,
                    defaults={
                        'action': action,
                        'metadata': metadata or {}
                    }
                )
                was_toggle = False

            # Update aggregated metrics
            metrics = self._update_post_metrics(blog_post_id)

            return {
                'success': True,
                'action': action,
                'new_score': metrics['sentiment_score'],
                'was_toggle': was_toggle,
                'likes_count': metrics['likes_count'],
                'dislikes_count': metrics['dislikes_count']
            }

        except ServiceError:
            raise
        except Exception as e:
            raise self.handle_exception(e, context={
                'blog_post_id': blog_post_id,
                'action': action
            })

    def _validate_engagement(self, blog_post_id: int, session_id: str, action: str) -> None:
        """Validate engagement input"""
        if not BlogPost.objects.filter(id=blog_post_id).exists():
            raise ServiceError(
                f"Blog post {blog_post_id} not found",
                code="POST_NOT_FOUND"
            )

        valid_actions = [choice[0] for choice in Engagement.ActionType.choices]
        if action not in valid_actions:
            raise ServiceError(
                f"Invalid action: {action}. Must be one of {valid_actions}",
                code="INVALID_ACTION"
            )

    def _update_post_metrics(self, blog_post_id: int) -> Dict:
        """
        Recalculate and update post metrics atomically.
        Returns metrics dict with counts.
        """
        with transaction.atomic():
            post = BlogPost.objects.select_for_update().get(id=blog_post_id)

            # Calculate counts
            likes = Engagement.objects.filter(
                blog_post_id=blog_post_id,
                action='like'
            ).count()

            dislikes = Engagement.objects.filter(
                blog_post_id=blog_post_id,
                action='dislike'
            ).count()

            sentiment_score = likes - dislikes
            post.sentiment_score = sentiment_score
            post.save(update_fields=['sentiment_score'])

            # Update or create PostMetric
            metric, created = PostMetric.objects.get_or_create(
                blog_post_id=blog_post_id,
                defaults={
                    'likes_count': likes,
                    'dislikes_count': dislikes
                }
            )

            if not created:
                metric.likes_count = likes
                metric.dislikes_count = dislikes
                metric.save()

            return {
                'sentiment_score': sentiment_score,
                'likes_count': likes,
                'dislikes_count': dislikes
            }

    @staticmethod
    def calculate_sentiment(blog_post_id: int) -> int:
        """Static method for quick sentiment calculation"""
        likes = Engagement.objects.filter(
            blog_post_id=blog_post_id,
            action='like'
        ).count()

        dislikes = Engagement.objects.filter(
            blog_post_id=blog_post_id,
            action='dislike'
        ).count()

        return likes - dislikes

    def get_post_metrics(self, blog_post_id: int) -> Dict:
        """
        Get comprehensive metrics for a post.
        """
        try:
            post = BlogPost.objects.get(id=blog_post_id)
            metric = PostMetric.objects.filter(blog_post_id=blog_post_id).first()

            engagements = Engagement.objects.filter(blog_post_id=blog_post_id)

            return {
                'post_id': blog_post_id,
                'title': post.title,
                'sentiment_score': post.sentiment_score,
                'likes': engagements.filter(action='like').count(),
                'dislikes': engagements.filter(action='dislike').count(),
                'total_engagements': engagements.count(),
                'views': metric.views_count if metric else 0,
                'engagement_rate': metric.engagement_rate if metric else 0.0
            }

        except BlogPost.DoesNotExist:
            raise ServiceError(
                f"Blog post {blog_post_id} not found",
                code="POST_NOT_FOUND"
            )

    def get_user_action(self, blog_post_id: int, session_id: str) -> str:
        """
        Get the user's current action on a post.
        Returns 'like', 'dislike', or None.
        """
        try:
            engagement = Engagement.objects.filter(
                blog_post_id=blog_post_id,
                session_id=session_id
            ).first()

            return engagement.action if engagement else None
        except Exception:
            return None

    def get_top_posts(self, limit: int = 10) -> List[Dict]:
        """
        Get top performing posts by sentiment score.
        """
        posts = BlogPost.objects.filter(
            status=BlogPost.PostStatus.COMPLETED
        ).annotate(
            likes_count=Count('engagements', filter=Q(engagements__action='like')),
            dislikes_count=Count('engagements', filter=Q(engagements__action='dislike')),
            total_reactions=Count('engagements')
        ).order_by('-sentiment_score', '-created_at')[:limit]

        return [
            {
                'id': p.id,
                'title': p.title,
                'slug': p.slug,
                'sentiment_score': p.sentiment_score,
                'likes': p.likes_count,
                'dislikes': p.dislikes_count,
                'total_reactions': p.total_reactions,
                'persona': p.persona.name if p.persona else None,
                'created_at': p.created_at.isoformat()
            }
            for p in posts
        ]
