"""
DRF Serializers for AI Blog Generator.
"""
from rest_framework import serializers
from .models import BlogPost, Persona, Engagement, PostMetric, SourceReference, GenerationJob


class PersonaSerializer(serializers.ModelSerializer):
    """Serializer for Persona model"""

    class Meta:
        model = Persona
        fields = [
            'id', 'name', 'slug', 'persona_type', 'description',
            'temperature', 'max_tokens', 'is_active'
        ]


class SourceSerializer(serializers.Serializer):
    """Serializer for source data (JSON field)"""
    title = serializers.CharField()
    url = serializers.URLField()
    domain = serializers.CharField()
    author = serializers.CharField(allow_null=True, required=False)
    is_verified = serializers.BooleanField()
    relevance_score = serializers.FloatField(allow_null=True, required=False)


class ContentStructureSerializer(serializers.Serializer):
    """Serializer for content_structure (JSON field)"""
    word_count = serializers.IntegerField()
    heading_count = serializers.IntegerField()
    reading_time_minutes = serializers.IntegerField()
    headings = serializers.ListField(
        child=serializers.DictField(),
        required=False
    )


class BlogPostSerializer(serializers.ModelSerializer):
    """Serializer for BlogPost model"""

    persona = PersonaSerializer(read_only=True)
    persona_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    word_count = serializers.ReadOnlyField()
    reading_time = serializers.ReadOnlyField()

    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'slug', 'topic_input', 'raw_prompt',
            'generated_content', 'content_structure', 'sources',
            'persona', 'persona_id', 'status', 'sentiment_score',
            'metadata', 'published_at', 'is_featured', 'seo_title',
            'meta_description', 'keywords', 'word_count', 'reading_time',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'slug', 'raw_prompt', 'generated_content',
            'content_structure', 'sentiment_score', 'metadata',
            'published_at', 'created_at', 'updated_at'
        ]


class BlogPostListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing posts"""

    persona = serializers.StringRelatedField()
    word_count = serializers.ReadOnlyField()
    reading_time = serializers.ReadOnlyField()

    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'slug', 'status', 'sentiment_score',
            'persona', 'word_count', 'reading_time', 'created_at'
        ]


class BlogPostDetailSerializer(serializers.ModelSerializer):
    """Full serializer for single post detail"""

    persona = PersonaSerializer(read_only=True)
    word_count = serializers.ReadOnlyField()
    reading_time = serializers.ReadOnlyField()

    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'slug', 'topic_input', 'generated_content',
            'content_structure', 'sources', 'persona', 'status',
            'sentiment_score', 'metadata', 'published_at', 'word_count',
            'reading_time', 'created_at', 'updated_at'
        ]


class EngagementSerializer(serializers.ModelSerializer):
    """Serializer for Engagement model"""

    class Meta:
        model = Engagement
        fields = ['id', 'blog_post', 'session_id', 'action', 'created_at']
        read_only_fields = ['id', 'created_at']


class EngagementActionSerializer(serializers.Serializer):
    """Serializer for engagement action requests"""

    blog_id = serializers.IntegerField()
    action = serializers.ChoiceField(
        choices=['like', 'dislike']
    )
    session_id = serializers.CharField()


class EngagementResponseSerializer(serializers.Serializer):
    """Serializer for engagement action responses"""

    success = serializers.BooleanField()
    action = serializers.CharField()
    new_score = serializers.IntegerField()
    was_toggle = serializers.BooleanField()
    likes_count = serializers.IntegerField()
    dislikes_count = serializers.IntegerField()


class BlogGenerationSerializer(serializers.Serializer):
    """Serializer for blog generation requests"""

    topic = serializers.CharField(
        min_length=5,
        max_length=500,
        help_text="Topic to write about"
    )
    persona = serializers.SlugField(
        help_text="Persona slug to use for generation"
    )
    additional_context = serializers.DictField(
        required=False,
        help_text="Additional context for generation"
    )
    speed = serializers.ChoiceField(
        choices=['fast', 'normal'],
        required=False,
        default='fast',
        help_text="Generation speed mode: 'fast' for lower latency, 'normal' for fuller output"
    )
    session_id = serializers.CharField(required=False, allow_blank=True)


class BlogGenerationResponseSerializer(serializers.Serializer):
    """Serializer for blog generation responses"""

    success = serializers.BooleanField(required=False, default=True)
    job_id = serializers.IntegerField(required=False)
    blog_post_id = serializers.IntegerField(allow_null=True, required=False)
    status = serializers.CharField()
    content = serializers.CharField(allow_null=True, required=False)
    sources = serializers.ListField(
        child=SourceSerializer(),
        required=False
    )
    metadata = serializers.DictField(required=False)
    error = serializers.CharField(allow_null=True, required=False)


class GenerationStatusSerializer(serializers.ModelSerializer):
    blog_post_id = serializers.IntegerField(source='blog_post.id', read_only=True)

    class Meta:
        model = GenerationJob
        fields = [
            'id',
            'status',
            'progress',
            'blog_post_id',
            'error_message',
            'created_at',
            'updated_at',
        ]


class PostMetricSerializer(serializers.ModelSerializer):
    """Serializer for PostMetric model"""

    class Meta:
        model = PostMetric
        fields = [
            'views_count', 'likes_count', 'dislikes_count',
            'shares_count', 'engagement_rate', 'scroll_depth_avg',
            'read_completion_rate', 'seo_score', 'ranking_position'
        ]


class AnalyticsSerializer(serializers.Serializer):
    """Serializer for analytics data"""

    total_posts = serializers.IntegerField()
    total_engagements = serializers.IntegerField()
    total_likes = serializers.IntegerField(required=False, default=0)
    total_dislikes = serializers.IntegerField(required=False, default=0)
    reaction_rate = serializers.FloatField(required=False, default=0.0)
    avg_sentiment_score = serializers.FloatField()
    top_posts = serializers.ListField(
        child=serializers.DictField()
    )
