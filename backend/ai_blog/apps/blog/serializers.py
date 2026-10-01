"""
DRF Serializers for AI Blog Generator.
"""
from django.utils import timezone
from rest_framework import serializers

from .content import compute_content_structure, reading_time_minutes
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


class BlogPostUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating a blog post's editable fields."""

    # Only these two are reachable by an editor. 'generating' and 'failed' are
    # owned by the generation pipeline and must not be settable from the API.
    EDITABLE_STATUSES = (BlogPost.PostStatus.DRAFT, BlogPost.PostStatus.COMPLETED)

    status = serializers.ChoiceField(choices=EDITABLE_STATUSES, required=False)

    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'topic_input', 'generated_content', 'status',
            'word_count', 'reading_time', 'published_at', 'updated_at'
        ]
        read_only_fields = ['id', 'word_count', 'reading_time', 'published_at', 'updated_at']

    def validate(self, attrs):
        """Publishing requires actual content - an empty post cannot go public."""
        new_status = attrs.get('status')
        if new_status == BlogPost.PostStatus.COMPLETED:
            content = attrs.get(
                'generated_content',
                self.instance.generated_content if self.instance else ''
            )
            if not (content or '').strip():
                raise serializers.ValidationError({
                    'status': 'A post with no content cannot be published.'
                })
        return attrs

    def update(self, instance, validated_data):
        updated_fields = ['updated_at']

        for field in ('title', 'topic_input'):
            if field in validated_data:
                setattr(instance, field, validated_data[field])
                updated_fields.append(field)

        if 'generated_content' in validated_data:
            instance.generated_content = validated_data['generated_content']
            instance.content_structure = compute_content_structure(instance.generated_content)
            updated_fields += ['generated_content', 'content_structure']

        if 'status' in validated_data:
            new_status = validated_data['status']
            if new_status != instance.status:
                instance.status = new_status
                updated_fields.append('status')
                # Keep published_at consistent with the published state.
                if new_status == BlogPost.PostStatus.COMPLETED and instance.published_at is None:
                    instance.published_at = timezone.now()
                    updated_fields.append('published_at')
                elif new_status == BlogPost.PostStatus.DRAFT:
                    instance.published_at = None
                    updated_fields.append('published_at')

        instance.save(update_fields=updated_fields)
        return instance


class BlogPostListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing posts"""

    persona = serializers.StringRelatedField()
    word_count = serializers.SerializerMethodField()
    reading_time = serializers.SerializerMethodField()

    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'slug', 'status', 'sentiment_score',
            'persona', 'word_count', 'reading_time', 'created_at'
        ]

    # Read the stored structure instead of the model properties, which would
    # split the full markdown body twice per row for a payload that never
    # includes that body.
    def get_word_count(self, obj) -> int:
        return (obj.content_structure or {}).get('word_count', 0)

    def get_reading_time(self, obj) -> int:
        structure = obj.content_structure or {}
        if structure.get('reading_time_minutes'):
            return structure['reading_time_minutes']
        return reading_time_minutes(structure.get('word_count', 0))


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
