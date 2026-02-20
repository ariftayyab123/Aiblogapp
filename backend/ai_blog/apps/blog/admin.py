"""
Django Admin configuration for Blog app.
"""
from django.contrib import admin
from .models import BlogPost, Persona, Engagement, PostMetric, SourceReference, GenerationJob


@admin.register(Persona)
class PersonaAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'persona_type', 'is_active', 'display_order']
    list_filter = ['persona_type', 'is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['display_order', 'name']


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'sentiment_score', 'persona', 'created_at']
    list_filter = ['status', 'persona', 'is_featured']
    search_fields = ['title', 'topic_input']
    readonly_fields = ['created_at', 'updated_at', 'published_at']
    prepopulated_fields = {'slug': ('title',)}
    ordering = ['-created_at']

    fieldsets = (
        ('Content', {
            'fields': ('title', 'slug', 'topic_input', 'generated_content')
        }),
        ('Generation', {
            'fields': ('persona', 'status', 'raw_prompt', 'sources', 'metadata')
        }),
        ('SEO', {
            'fields': ('seo_title', 'meta_description', 'keywords'),
            'classes': ('collapse',)
        }),
        ('Publishing', {
            'fields': ('is_featured', 'published_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Engagement)
class EngagementAdmin(admin.ModelAdmin):
    list_display = ['blog_post', 'session_id', 'action', 'created_at']
    list_filter = ['action', 'created_at']
    search_fields = ['blog_post__title', 'session_id']
    readonly_fields = ['created_at']
    ordering = ['-created_at']


@admin.register(PostMetric)
class PostMetricAdmin(admin.ModelAdmin):
    list_display = ['blog_post', 'likes_count', 'dislikes_count', 'engagement_rate']
    list_filter = ['created_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(SourceReference)
class SourceReferenceAdmin(admin.ModelAdmin):
    list_display = ['title', 'domain', 'blog_post', 'is_verified', 'relevance_score']
    list_filter = ['is_verified', 'created_at']
    search_fields = ['title', 'url', 'domain']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(GenerationJob)
class GenerationJobAdmin(admin.ModelAdmin):
    list_display = ['id', 'topic', 'persona_slug', 'status', 'progress', 'blog_post', 'created_at']
    list_filter = ['status', 'persona_slug', 'speed', 'created_at']
    search_fields = ['topic', 'persona_slug', 'session_id', 'task_id']
    readonly_fields = ['created_at', 'updated_at']
