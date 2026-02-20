"""
Django models for AI Blog Generator.
Implements the data schema from SYSTEM_DESIGN.md
"""
import re
from urllib.parse import urlparse
from django.db import models
from django.core.validators import URLValidator
from django.contrib.postgres.fields import ArrayField
from django.utils import timezone
from django.utils.text import slugify


class BaseTimestamped(models.Model):
    """Abstract base for created/updated timestamps"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Persona(BaseTimestamped):
    """
    Defines the writing persona/style for blog generation.
    """
    class PersonaType(models.TextChoices):
        TECHNICAL = 'technical', 'Technical Writer'
        NARRATIVE = 'narrative', 'Storyteller'
        ANALYST = 'analyst', 'Industry Analyst'
        EDUCATOR = 'educator', 'Educator'
        CREATIVE = 'creative', 'Creative Writer'

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    persona_type = models.CharField(
        max_length=20,
        choices=PersonaType.choices,
        default=PersonaType.TECHNICAL
    )

    # Prompt Configuration
    system_prompt = models.TextField(
        help_text="Base system prompt for this persona"
    )
    description = models.CharField(
        max_length=300,
        help_text="User-facing description"
    )

    # Generation Parameters
    temperature = models.FloatField(
        default=0.7,
        help_text="Creativity: 0.0-1.0"
    )
    max_tokens = models.IntegerField(
        default=4000,
        help_text="Max output tokens"
    )
    top_p = models.FloatField(
        default=0.9,
        help_text="Nucleus sampling"
    )

    # State
    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0)

    class Meta:
        ordering = ['display_order', 'name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.name


class BlogPost(BaseTimestamped):
    """
    Core blog post entity with extensible metadata storage.
    """
    class PostStatus(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        GENERATING = 'generating', 'Generating'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'

    # Content Fields
    title = models.CharField(
        max_length=300,
        help_text="Generated or user-provided title"
    )
    slug = models.SlugField(max_length=350, unique=True, blank=True)

    # Prompt Tracking
    topic_input = models.CharField(
        max_length=500,
        help_text="Original user topic/keyword input"
    )
    raw_prompt = models.TextField(
        help_text="Full prompt sent to AI (includes persona injection)"
    )

    # Generated Content (stored as Markdown)
    generated_content = models.TextField(
        blank=True,
        help_text="AI-generated blog post in Markdown format"
    )

    # Structure (for front-end rendering control)
    content_structure = models.JSONField(
        default=dict,
        blank=True,
        help_text="Parsed structure: headings, word_count, reading_time"
    )

    # Relationship to Persona
    persona = models.ForeignKey(
        Persona,
        on_delete=models.SET_NULL,
        null=True,
        related_name='blog_posts'
    )

    # Sources (Structured for Authenticity)
    sources = models.JSONField(
        default=list,
        blank=True,
        help_text="Array of source objects with url, title, domain, etc."
    )

    # Status Tracking
    status = models.CharField(
        max_length=20,
        choices=PostStatus.choices,
        default=PostStatus.DRAFT
    )

    # Engagement Score (Computed, stored for performance)
    sentiment_score = models.IntegerField(
        default=0,
        help_text="Derived: likes - dislikes"
    )

    # Metadata (Extensible JSON field)
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Extensible storage for generation metadata"
    )

    # Publishing Control
    published_at = models.DateTimeField(null=True, blank=True)
    is_featured = models.BooleanField(default=False)

    # SEO (Future extensibility)
    seo_title = models.CharField(max_length=300, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    keywords = ArrayField(
        models.CharField(max_length=50),
        blank=True,
        default=list
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['status']),
            models.Index(fields=['-created_at']),
            models.Index(fields=['sentiment_score']),
            models.Index(fields=['persona', 'status']),
        ]

    def __str__(self):
        return self.title

    @property
    def word_count(self):
        """Calculate word count from content"""
        return len(self.generated_content.split()) if self.generated_content else 0

    @property
    def reading_time(self):
        """Estimate reading time (200 words per minute)"""
        return max(1, self.word_count // 200)

    def update_sentiment_score(self):
        """Recalculate sentiment from engagement records"""
        likes = self.engagements.filter(action='like').count()
        dislikes = self.engagements.filter(action='dislike').count()
        self.sentiment_score = likes - dislikes
        self.save(update_fields=['sentiment_score'])


class GenerationJob(BaseTimestamped):
    """Tracks asynchronous blog generation lifecycle."""

    class JobStatus(models.TextChoices):
        QUEUED = 'queued', 'Queued'
        RUNNING = 'running', 'Running'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'

    topic = models.CharField(max_length=500)
    persona_slug = models.SlugField(max_length=50)
    session_id = models.CharField(max_length=100, blank=True)
    speed = models.CharField(max_length=10, default='fast')
    additional_context = models.JSONField(default=dict, blank=True)

    status = models.CharField(
        max_length=20,
        choices=JobStatus.choices,
        default=JobStatus.QUEUED
    )
    progress = models.IntegerField(default=0)
    blog_post = models.ForeignKey(
        BlogPost,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='generation_jobs'
    )
    error_message = models.TextField(blank=True)
    task_id = models.CharField(max_length=100, blank=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['persona_slug']),
        ]

    def __str__(self):
        return f"Job {self.id} - {self.status}"


class SourceReference(BaseTimestamped):
    """
    Normalized source storage for authenticity tracking.
    """
    blog_post = models.ForeignKey(
        BlogPost,
        on_delete=models.CASCADE,
        related_name='source_references'
    )

    # Source Identification
    url = models.CharField(max_length=500, validators=[URLValidator()])
    domain = models.CharField(max_length=200, blank=True)

    # Content Metadata
    title = models.CharField(max_length=300)
    author = models.CharField(max_length=200, blank=True)
    published_date = models.DateField(null=True, blank=True)

    # Verification
    is_verified = models.BooleanField(default=False)
    relevance_score = models.FloatField(
        null=True,
        blank=True,
        help_text="AI-assigned relevance (0.0-1.0)"
    )

    # Usage Tracking
    usage_count = models.IntegerField(default=1)

    class Meta:
        ordering = ['-relevance_score']
        indexes = [
            models.Index(fields=['domain']),
            models.Index(fields=['blog_post', 'relevance_score']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['blog_post', 'url'],
                name='unique_source_per_post',
                violation_error_message='This source is already added to this post.'
            )
        ]

    def __str__(self):
        return f"{self.title} ({self.domain})"

    def save(self, *args, **kwargs):
        """Auto-extract domain from URL if not provided"""
        if self.url and not self.domain:
            parsed = urlparse(self.url)
            self.domain = parsed.netloc.replace('www.', '')
        super().save(*args, **kwargs)


class Engagement(BaseTimestamped):
    """
    User engagement tracking with session-based deduplication.
    """
    class ActionType(models.TextChoices):
        LIKE = 'like', 'Like'
        DISLIKE = 'dislike', 'Dislike'

    # Relationship
    blog_post = models.ForeignKey(
        BlogPost,
        on_delete=models.CASCADE,
        related_name='engagements'
    )

    # Anonymous Session Tracking
    session_id = models.CharField(
        max_length=100,
        db_index=True,
        help_text="UUID from client localStorage"
    )

    # Action
    action = models.CharField(max_length=10, choices=ActionType.choices)

    # Weight (allows for weighted actions in future)
    action_value = models.IntegerField(
        default=1,
        help_text="Weight of this action"
    )

    # Metadata (extensible)
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="User agent, referrer, etc."
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['blog_post', 'action']),
            models.Index(fields=['session_id']),
            models.Index(fields=['created_at']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['blog_post', 'session_id'],
                name='unique_engagement_per_session',
                violation_error_message='Session engagement already exists for this post.'
            )
        ]

    def __str__(self):
        return f"{self.blog_post.title} - {self.action}"


class PostMetric(models.Model):
    """
    Detailed analytics per post.
    Separate from BlogPost to avoid model bloat.
    """
    blog_post = models.OneToOneField(
        BlogPost,
        on_delete=models.CASCADE,
        related_name='metrics'
    )

    # Engagement Counts (denormalized for performance)
    views_count = models.IntegerField(default=0)
    likes_count = models.IntegerField(default=0)
    dislikes_count = models.IntegerField(default=0)
    shares_count = models.IntegerField(default=0)

    # Engagement Rates
    engagement_rate = models.FloatField(
        default=0.0,
        help_text="(likes + shares) / views"
    )

    # Content Performance
    scroll_depth_avg = models.FloatField(null=True, help_text="Avg scroll percentage")
    read_completion_rate = models.FloatField(null=True)

    # SEO Metrics (future)
    seo_score = models.IntegerField(null=True)
    ranking_position = models.IntegerField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Post Metric"
        verbose_name_plural = "Post Metrics"
