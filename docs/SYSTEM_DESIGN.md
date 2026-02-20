# System Design Document
## AI-Assisted Blog Post Generator (MVP)

**Version:** 1.0.0
**Date:** 2025-02-20
**Architecture Pattern:** Service-Oriented Layer (SOL) with Clean Architecture
**Author:** BMad System Architect

---

## Table of Contents

1. [Architectural Overview](#1-architectural-overview)
2. [Data Modeling](#2-data-modeling)
3. [Service Layer Design](#3-service-layer-design)
4. [Prompt Engineering System](#4-prompt-engineering-system)
5. [State Management Strategy](#5-state-management-strategy)
6. [API Contract Specification](#6-api-contract-specification)
7. [Extensibility Framework](#7-extensibility-framework)
8. [Error Handling & Resilience](#8-error-handling--resilience)

---

## 1. Architectural Overview

### 1.1 System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              PRESENTATION LAYER                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         REACT FRONTEND                               │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │    │
│  │  │  Pages      │  │ Components  │  │  Hooks      │  │  Context    │  │    │
│  │  │  (Views)    │  │  (UI Lib)   │  │  (State)    │  │  (Global)   │  │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  │    │
│  └───────────────────────────────┬─────────────────────────────────────┘    │
└──────────────────────────────────┼──────────────────────────────────────────┘
                                   │ HTTP/REST (JSON)
                                   │
┌──────────────────────────────────┼──────────────────────────────────────────┐
│                              API GATEWAY LAYER                              │
│  ┌───────────────────────────────┴─────────────────────────────────────┐    │
│  │                      DJANGO REST FRAMEWORK                           │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │    │
│  │  │  ViewSets   │  │ Serializers │  │ Permissions │  │  Filters    │  │    │
│  │  │  (Thin)     │  │  (DTO)      │  │  (RBAC)     │  │  (Query)    │  │    │
│  │  └──────┬──────┘  └─────────────┘  └─────────────┘  └─────────────┘  │    │
│  └─────────┼────────────────────────────────────────────────────────────┘    │
└────────────┼──────────────────────────────────────────────────────────────────┘
             │
             │ Calls
             │
┌────────────┼──────────────────────────────────────────────────────────────────┐
│                             SERVICE LAYER                                     │
│  ┌───────────────────────────┬───────────────────────────────────────────┐   │
│  │  BlogGenerationService    │   EngagementService                       │   │
│  │  ┌─────────────────────┐  │   ┌─────────────────────┐                 │   │
│  │  │ - generate_post()   │  │   │ - record_action()   │                 │   │
│  │  │ - stream_content()  │  │   │ - get_metrics()     │                 │   │
│  │  │ - retry_logic()     │  │   │ - aggregate_score() │                 │   │
│  │  └──────────┬──────────┘  │   └─────────────────────┘                 │   │
│  └─────────────┼──────────────┴───────────────────────────────────────────┘   │
│                │                                                              │
│  ┌─────────────┼──────────────────────────────────────────────────────────┐   │
│  │  PromptEngineeringService    │   SourceValidationService                │   │
│  │  ┌─────────────────────┐    │   ┌─────────────────────┐                │   │
│  │  │ - build_prompt()    │    │   │ - validate_url()    │                │   │
│  │  │ - inject_persona()  │    │   │ - extract_meta()    │                │   │
│  │  │ - parse_response()  │    │   │ - format_citation() │                │   │
│  │  └─────────────────────┘    │   └─────────────────────┘                │   │
│  └────────────────────────────────────────────────────────────────────────┘   │
└────────────────────┬──────────────────────────────────────────────────────────┘
                     │
                     │ Uses
                     │
┌────────────────────┼──────────────────────────────────────────────────────────┐
│                         EXTERNAL SERVICES LAYER                                │
│  ┌───────────────────┴───────────────────────────────────────────────────┐    │
│  │                                                                       │    │
│  │  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐   │    │
│  │  │   Anthropic     │    │   (Future)      │    │   (Future)      │   │    │
│  │  │   Claude API     │    │   SEO Service   │    │   Image Gen     │   │    │
│  │  └─────────────────┘    └─────────────────┘    └─────────────────┘   │    │
│  └───────────────────────────────────────────────────────────────────────┘    │
└───────────────────────────────────────────────────────────────────────────────┘
                     │
                     │ Persists
                     │
┌────────────────────┼──────────────────────────────────────────────────────────┐
│                          DATA PERSISTENCE LAYER                               │
│  ┌───────────────────┴─────────────────────────────────────────────────────┐  │
│  │                    POSTGRES DATABASE                                     │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │  │
│  │  │  blog_post   │  │  engagement  │  │   persona    │  │  source_ref  │ │  │
│  │  │              │  │              │  │              │  │              │ │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘ │  │
│  └──────────────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Architectural Principles

| Principle | Implementation | Benefit |
|-----------|----------------|---------|
| **Separation of Concerns** | Views → Services → Models | Testability, maintainability |
| **Dependency Inversion** | Services depend on abstractions (protocols) | Easy mocking, extensibility |
| **Single Responsibility** | Each service has one job | Clear boundaries, reduced coupling |
| **Open/Closed** | Open for extension (new services), closed for modification | Future feature additions |

### 1.3 Request Flow Sequence Diagram

```
User                React UI           API View          Service          Claude      DB
 │                    │                  │                 │                │           │
 │──[Submit Topic]───>│                  │                 │                │           │
 │                    │──[POST /generate]>│                 │                │           │
 │                    │                  │──[create_job]──>│                │           │
 │                    │<──[job_id]───────│                 │                │           │
 │                    │──[POLL /status]──>│                 │                │           │
 │                    │                  │──[check_status]>│                │           │
 │                    │                  │                 │──[API call]───>│           │
 │                    │                  │                 │<──[stream]────│           │
 │                    │<──[progress]─────│<────────────────│                │           │
 │                    │──[POLL /status]──>│                 │                │           │
 │                    │<──[completed]────│<────────────────│                │           │
 │                    │                  │                 │                │──[save]──>│
 │<──[Display Post]───│                  │                 │                │           │
```

---

## 2. Data Modeling

### 2.1 Entity Relationship Diagram (ERD)

```
┌──────────────────────┐         ┌──────────────────────┐
│      PERSONA         │         │      BLOG_POST       │
├──────────────────────┤         ├──────────────────────┤
│ id: PK              │         │ id: PK              │
│ name: UNIQUE        │    1:N  │ title: VARCHAR(300)  │
│ slug: UNIQUE        │<────────│ topic_input: VARCHAR │
│ system_prompt: TEXT │         │ raw_prompt: TEXT     │
│ description: VARCHAR│         │ generated_content:   │
│ temperature: FLOAT  │         │   TEXT (Markdown)    │
│ is_active: BOOLEAN  │         │ status: CHOICE       │
│ created_at: DT      │         │ persona_id: FK       │
│                      │         │ sources: JSON        │
└──────────────────────┘         │ metadata: JSON       │
                                 │ sentiment_score: INT │
                                 │ word_count: INT      │
                                 │ created_at: DT       │
                                 │ updated_at: DT       │
                                 └──────────┬───────────┘
                                            │ 1:N
                                            │
                         ┌──────────────────┴──────────────────┐
                         │                                     │
┌────────────────────┐   │   ┌─────────────────────────────┐   │   ┌──────────────────┐
│    ENGAGEMENT      │   │   │       SOURCE_REFERENCE       │   │   │   POST_METRICS   │ (Future)
├────────────────────┤   │   ├─────────────────────────────┤   │   ├──────────────────┤
│ id: PK            │   │   │ id: PK                      │   │   │ id: PK           │
│ blog_post_id: FK  │───┘   │ blog_post_id: FK            │───┘   │ blog_post_id: FK │
│ session_id: VARCHAR│       │ url: VARCHAR(500)           │       │ seo_score: INT    │
│ action: CHOICE    │       │ title: VARCHAR(300)         │       │ read_time: INT    │
│ action_value: INT │       │ domain: VARCHAR(200)        │       │ share_count: INT  │
│ created_at: DT    │       │ author: VARCHAR(200)        │       │                  │
└────────────────────┘       │ is_verified: BOOLEAN        │       └──────────────────┘
                             │ relevance_score: FLOAT      │
                             │ created_at: DT              │
                             └─────────────────────────────┘
```

### 2.2 Django Model Definitions

```python
# backend/apps/blog/models.py

from django.db import models
from django.core.validators import URLValidator
from django.contrib.postgres.fields import ArrayField
import json


class BaseTimestamped(models.Model):
    """Abstract base for created/updated timestamps"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Persona(BaseTimestamped):
    """
    Defines the writing persona/style for blog generation.
    Extensible for future AI variations.
    """
    class PersonaType(models.TextChoices):
        TECHNICAL = 'technical', 'Technical Writer'
        NARRATIVE = 'narrative', 'Storyteller'
        ANALYST = 'analyst', 'Industry Analyst'
        EDUCATOR = 'educator', 'Educator'
        CREATIVE = 'creative', 'Creative Writer'

    # Primary Fields
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    persona_type = models.CharField(
        max_length=20,
        choices=PersonaType.choices,
        default=PersonaType.TECHNICAL
    )

    # Prompt Configuration
    system_prompt = models.TextField(help_text="Base system prompt for this persona")
    description = models.CharField(max_length=300, help_text="User-facing description")

    # Generation Parameters (Extensible)
    temperature = models.FloatField(default=0.7, help_text="Creativity: 0.0-1.0")
    max_tokens = models.IntegerField(default=4000, help_text="Max output tokens")
    top_p = models.FloatField(default=0.9, help_text="Nucleus sampling")

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
    title = models.CharField(max_length=300, help_text="Generated or user-provided title")
    slug = models.SlugField(max_length=350, unique=True, blank=True)

    # Prompt Tracking (for analysis/optimization)
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
        help_text="""
        Array of source objects:
        [
            {
                "url": "https://example.com/article",
                "title": "Article Title",
                "domain": "example.com",
                "author": "Author Name",
                "published_date": "2025-01-15",
                "relevance_score": 0.95,
                "is_verified": true
            }
        ]
        """
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
        help_text="""
        Extensible storage for:
        {
            "word_count": 1250,
            "reading_time_minutes": 5,
            "generation_time_seconds": 12,
            "model_used": "claude-3-opus-20240229",
            "total_tokens": 3200,
            "retry_count": 0
        }
        """
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
        from .services import EngagementService
        self.sentiment_score = EngagementService.calculate_sentiment(self.id)
        self.save(update_fields=['sentiment_score'])


class SourceReference(BaseTimestamped):
    """
    Normalized source storage for authenticity tracking.
    Enables source reuse across posts and analytics.
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
    usage_count = models.IntegerField(default=1, help_text="Times referenced across posts")

    class Meta:
        ordering = ['-relevance_score']
        indexes = [
            models.Index(fields=['domain']),
            models.Index(fields=['blog_post', 'relevance_score']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['blog_post', 'url'],
                name='unique_source_per_post'
            )
        ]

    def __str__(self):
        return f"{self.title} ({self.domain})"


class Engagement(BaseTimestamped):
    """
    User engagement tracking with session-based deduplication.
    Supports future: comments, shares, bookmarks.
    """
    class ActionType(models.TextChoices):
        LIKE = 'like', 'Like'
        DISLIKE = 'dislike', 'Dislike'
        # Future extensibility
        # BOOKMARK = 'bookmark', 'Bookmark'
        # SHARE = 'share', 'Share'

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
    action_value = models.IntegerField(default=1, help_text="Weight of this action")

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
                fields=['blog_post', 'session_id', 'action'],
                name='unique_engagement_per_session'
            )
        ]

    def __str__(self):
        return f"{self.blog_post.title} - {self.action}"


class PostMetric(models.Model):
    """
    Future extensibility: detailed analytics per post.
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
    read_completion_rate = models.FloatField(null=True, help_text="Reached end")

    # SEO Metrics (future)
    seo_score = models.IntegerField(null=True)
    ranking_position = models.IntegerField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Post Metric"
        verbose_name_plural = "Post Metrics"
```

### 2.3 Database Migrations Strategy

```python
# Generated migration will include:
# - Create tables in dependency order
# - Add indexes for query optimization
# - Set up constraints for data integrity
# - Add triggers for computed fields (optional)

# Recommended: Use Django's makemigrations --empty for custom operations
```

### 2.4 Query Optimization Indexes

```sql
-- Composite indexes for common query patterns

-- Posts by persona and status (dashboard filtering)
CREATE INDEX idx_blog_post_persona_status ON blog_post(persona_id, status, created_at DESC);

-- Engagement aggregation (analytics)
CREATE INDEX idx_engagement_post_action ON engagement(blog_post_id, action, created_at);

-- Source verification (authenticity reporting)
CREATE INDEX idx_source_reference_verified ON source_reference(is_verified, relevance_score);
```

---

## 3. Service Layer Design

### 3.1 Service Layer Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         SERVICE LAYER                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    BaseService (Abstract)                        │  │
│  │  + validate_input()                                              │  │
│  │  + handle_exception()                                            │  │
│  │  + log_execution()                                               │  │
│  └──────────────────────────────┬───────────────────────────────────┘  │
│                                 │                                      │
│  ┌──────────────────────────────┴───────────────────────────────────┐  │
│  │                                                                  │  │
│  │  ┌──────────────────────┐  ┌──────────────────────┐            │  │
│  │  │ BlogGenerationService│  │ EngagementService    │            │  │
│  │  ├─────────────────────┤  ├─────────────────────┤            │  │
│  │  │generate_post()      │  │record_action()       │            │  │
│  │  │stream_content()     │  │get_post_metrics()    │            │  │
│  │  │retry_on_failure()   │  │calculate_sentiment() │            │  │
│  │  │parse_citations()    │  │get_top_posts()       │            │  │
│  │  └─────────────────────┘  └─────────────────────┘            │  │
│  │                                                                  │  │
│  │  ┌──────────────────────┐  ┌──────────────────────┐            │  │
│  │  │PromptService         │  │SourceService         │            │  │
│  │  ├─────────────────────┤  ├─────────────────────┤            │  │
│  │  │build_system_prompt()│  │validate_url()        │            │  │
│  │  │inject_variables()   │  │extract_domain()      │            │  │
│  │  │format_response()    │  │format_citation()     │            │  │
│  │  │parse_markdown()     │  │check_reputation()    │            │  │
│  │  └─────────────────────┘  └─────────────────────┘            │  │
│  │                                                                  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Base Service Class

```python
# backend/core/services/base.py

import logging
from typing import TypeVar, Generic, Type, Optional, Any, Dict
from django.db import models
from django.core.exceptions import ValidationError
from abc import ABC, abstractmethod

T = TypeVar('T', bound=models.Model)

logger = logging.getLogger(__name__)


class ServiceError(Exception):
    """Base exception for service layer errors"""
    def __init__(self, message: str, code: str = "SERVICE_ERROR", details: Dict = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)


class BaseService(ABC, Generic[T]):
    """
    Abstract base service providing common functionality.
    Enforces separation: Services handle business logic, Models handle persistence.
    """

    model_class: Type[T]
    logger_name: str = None

    def __init__(self):
        self._logger = logger.getLogger(self.logger_name or self.__class__.__name__)

    def log_execution(self, method_name: str, **kwargs):
        """Log service method execution with context"""
        self._logger.info(
            f"{self.__class__.__name__}.{method_name} called",
            extra={"context": kwargs}
        )

    def handle_exception(self, exc: Exception, context: Dict = None) -> ServiceError:
        """Convert exceptions to ServiceError with proper context"""
        context = context or {}
        self._logger.error(
            f"Exception in {self.__class__.__name__}: {str(exc)}",
            extra={"context": context},
            exc_info=True
        )
        return ServiceError(str(exc), details=context)

    def validate_input(self, data: Dict, validators: Dict = None) -> None:
        """
        Validate input data before processing.
        validators: {field_name: callable}
        """
        for field, validator in (validators or {}).items():
            if field in data:
                try:
                    validator(data[field])
                except (ValueError, ValidationError) as e:
                    raise ServiceError(
                        f"Validation failed for {field}: {str(e)}",
                        code="VALIDATION_ERROR"
                    )

    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """Main execution method - must be implemented by subclasses"""
        raise NotImplementedError
```

### 3.3 Blog Generation Service

```python
# backend/apps/blog/services/blog_generation.py

import time
import re
from typing import Dict, List, Optional, Any
from anthropic import Anthropic
from anthropic.types import Message
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify

from core.services.base import BaseService, ServiceError
from .models import BlogPost, Persona
from .prompts import PromptService


class BlogGenerationService(BaseService[BlogPost]):
    """
    Service for orchestrating blog post generation with Claude AI.
    Handles: prompt construction, API communication, response parsing.
    """

    model_class = BlogPost
    logger_name = "blog_generation"

    # Claude model configuration
    DEFAULT_MODEL = "claude-3-5-sonnet-20241022"
    MAX_RETRIES = 2
    RETRY_DELAY = 1.0  # seconds

    # Generation timeouts
    GENERATION_TIMEOUT = 60  # seconds

    def __init__(self, api_key: str = None):
        super().__init__()
        self.client = Anthropic(api_key=api_key or settings.ANTHROPIC_API_KEY)
        self.prompt_service = PromptService()

    def generate_post(
        self,
        topic: str,
        persona_slug: str,
        additional_context: Dict = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Main entry point for blog generation.

        Returns:
            {
                'success': bool,
                'blog_post_id': int | None,
                'content': str | None,
                'sources': List[Dict],
                'metadata': Dict,
                'error': str | None
            }
        """
        self.log_execution("generate_post", topic=topic, persona=persona_slug)

        try:
            # 1. Validate inputs
            self._validate_generation_input(topic, persona_slug)

            # 2. Fetch persona
            persona = self._get_persona(persona_slug)

            # 3. Build prompts
            system_prompt, user_prompt = self.prompt_service.build_generation_prompt(
                topic=topic,
                persona=persona,
                additional_context=additional_context or {}
            )

            # 4. Create BlogPost record in GENERATING state
            blog_post = self._create_post_record(
                topic=topic,
                persona=persona,
                raw_prompt=user_prompt
            )

            # 5. Call Claude API with retry logic
            response_data = self._call_claude_with_retry(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=persona.temperature,
                max_tokens=persona.max_tokens
            )

            # 6. Parse response
            parsed_content = self._parse_response(response_data['content'])

            # 7. Update BlogPost with generated content
            self._update_post_with_content(
                blog_post=blog_post,
                content=parsed_content['markdown'],
                sources=parsed_content['sources'],
                metadata=response_data.get('usage', {})
            )

            return {
                'success': True,
                'blog_post_id': blog_post.id,
                'content': parsed_content['markdown'],
                'sources': parsed_content['sources'],
                'metadata': blog_post.metadata
            }

        except ServiceError:
            raise
        except Exception as e:
            self.handle_exception(e, context={'topic': topic, 'persona': persona_slug})
            raise

    def _validate_generation_input(self, topic: str, persona_slug: str) -> None:
        """Validate generation inputs"""
        if not topic or len(topic.strip()) < 5:
            raise ServiceError(
                "Topic must be at least 5 characters long",
                code="INVALID_TOPIC"
            )
        if not persona_slug:
            raise ServiceError(
                "Persona slug is required",
                code="INVALID_PERSONA"
            )

    def _get_persona(self, slug: str) -> Persona:
        """Fetch and validate persona"""
        try:
            persona = Persona.objects.get(slug=slug, is_active=True)
            return persona
        except Persona.DoesNotExist:
            raise ServiceError(
                f"Active persona '{slug}' not found",
                code="PERSONA_NOT_FOUND"
            )

    def _create_post_record(self, topic: str, persona: Persona, raw_prompt: str) -> BlogPost:
        """Create initial BlogPost in GENERATING state"""
        # Generate unique slug
        base_slug = slugify(topic[:50])
        slug = base_slug
        counter = 1
        while BlogPost.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        blog_post = BlogPost.objects.create(
            title=f"Draft: {topic[:50]}...",
            slug=slug,
            topic_input=topic,
            raw_prompt=raw_prompt,
            persona=persona,
            status=BlogPost.PostStatus.GENERATING
        )
        return blog_post

    def _call_claude_with_retry(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        max_tokens: int
    ) -> Dict[str, Any]:
        """
        Call Claude API with exponential backoff retry.
        Returns parsed response with content and usage metadata.
        """
        last_error = None

        for attempt in range(self.MAX_RETRIES + 1):
            try:
                start_time = time.time()

                response = self.client.messages.create(
                    model=self.DEFAULT_MODEL,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_prompt}]
                )

                generation_time = time.time() - start_time

                # Extract content and metadata
                content = response.content[0].text if response.content else ""

                return {
                    'content': content,
                    'usage': {
                        'model': self.DEFAULT_MODEL,
                        'input_tokens': response.usage.input_tokens,
                        'output_tokens': response.usage.output_tokens,
                        'total_tokens': response.usage.input_tokens + response.usage.output_tokens,
                        'generation_time_seconds': round(generation_time, 2),
                        'retry_count': attempt
                    }
                }

            except Exception as e:
                last_error = e
                self._logger.warning(
                    f"Claude API call failed (attempt {attempt + 1}/{self.MAX_RETRIES + 1}): {str(e)}"
                )
                if attempt < self.MAX_RETRIES:
                    time.sleep(self.RETRY_DELAY * (2 ** attempt))  # Exponential backoff

        # All retries exhausted
        raise ServiceError(
            f"Failed to generate content after {self.MAX_RETRIES + 1} attempts: {str(last_error)}",
            code="API_ERROR",
            details={'last_error': str(last_error)}
        )

    def _parse_response(self, raw_content: str) -> Dict[str, Any]:
        """
        Parse Claude response to extract:
        - Main markdown content
        - Sources/citations (if present)
        - Title (extracted from first heading)
        """
        result = {
            'markdown': raw_content,
            'sources': [],
            'title': None,
            'structure': {}
        }

        # Extract title (first # heading)
        title_match = re.search(r'^#\s+(.+)$', raw_content, re.MULTILINE)
        if title_match:
            result['title'] = title_match.group(1).strip()

        # Extract sources from structured format
        # Looking for ## Sources or ## References section
        sources_section = re.search(
            r'##\s*(?:Sources|References|Citations)\s*\n+(.*?)(?=\n##|\n\n*$)',
            raw_content,
            re.DOTALL | re.IGNORECASE
        )

        if sources_section:
            result['sources'] = self._parse_sources(sources_section.group(1))

            # Remove sources section from main content
            result['markdown'] = re.sub(
                r'##\s*(?:Sources|References|Citations).*?(?=\n##|\n\n*$)',
                '',
                raw_content,
                flags=re.DOTALL | re.IGNORECASE
            ).strip()

        # Calculate structure
        result['structure'] = self._analyze_structure(result['markdown'])

        return result

    def _parse_sources(self, sources_text: str) -> List[Dict[str, Any]]:
        """
        Parse sources section into structured list.
        Supports multiple citation formats.
        """
        sources = []

        # Pattern: [Title](url) or - [Title](url)
        citation_pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
        matches = re.findall(citation_pattern, sources_text)

        for title, url in matches:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc.replace('www.', '')

            sources.append({
                'title': title.strip(),
                'url': url.strip(),
                'domain': domain,
                'is_verified': False,  # Will be validated by SourceService
                'relevance_score': None
            })

        return sources

    def _analyze_structure(self, markdown: str) -> Dict[str, Any]:
        """Analyze markdown structure for frontend rendering"""
        headings = re.findall(r'^(#{1,3})\s+(.+)$', markdown, re.MULTILINE)
        word_count = len(markdown.split())

        return {
            'word_count': word_count,
            'heading_count': len(headings),
            'reading_time_minutes': max(1, word_count // 200),
            'headings': [{'level': h[0], 'text': h[1]} for h in headings]
        }

    def _update_post_with_content(
        self,
        blog_post: BlogPost,
        content: str,
        sources: List[Dict],
        metadata: Dict
    ) -> None:
        """Update BlogPost with generated content and complete generation"""
        blog_post.generated_content = content
        blog_post.sources = sources
        blog_post.content_structure = metadata.pop('structure', {})

        # Update title if extracted
        if metadata.get('title'):
            blog_post.title = metadata['title'][:300]

        # Merge metadata
        blog_post.metadata = {**(blog_post.metadata or {}), **metadata}

        # Update status
        blog_post.status = BlogPost.PostStatus.COMPLETED
        blog_post.published_at = timezone.now()

        blog_post.save()

        # Update sentiment score (starts at 0)
        blog_post.update_sentiment_score()

    def stream_content(self, topic: str, persona_slug: str) -> Any:
        """
        Stream generation response for real-time display.
        Returns a generator yielding chunks of content.
        """
        # Implementation for SSE/WebSocket streaming
        # Deferred to v2 based on priority
        raise NotImplementedError("Streaming is planned for v2")


class BlogGenerationServiceV2:
    """
    Future enhancements:
    - Asynchronous task queue (Celery/Dramatiq)
    - Streaming responses
    - Multi-persona A/B testing
    - Image generation integration
    """
    pass
```

### 3.4 Engagement Service

```python
# backend/apps/blog/services/engagement.py

from typing import Dict, List, Optional
from django.db.models import Count, Q, F, Sum
from django.db import transaction

from core.services.base import BaseService, ServiceError
from .models import BlogPost, Engagement, PostMetric


class EngagementService(BaseService[Engagement]):
    """
    Service for handling user engagement with blog posts.
    Ensures: session-based deduplication, metric aggregation.
    """

    model_class = Engagement
    logger_name = "engagement"

    def record_action(
        self,
        blog_post_id: int,
        session_id: str,
        action: str,
        metadata: Dict = None
    ) -> Dict[str, Any]:
        """
        Record a user engagement action.

        Returns:
            {
                'success': bool,
                'action': str,
                'new_score': int,
                'was_toggle': bool  # True if action was toggled off
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

            # Check for existing engagement (toggle behavior)
            existing = Engagement.objects.filter(
                blog_post_id=blog_post_id,
                session_id=session_id,
                action=action
            ).first()

            if existing:
                # Toggle off: delete existing
                existing.delete()
                was_toggle = True
            else:
                # Create new engagement
                Engagement.objects.create(
                    blog_post_id=blog_post_id,
                    session_id=session_id,
                    action=action,
                    metadata=metadata or {}
                )
                was_toggle = False

            # Update aggregated metrics
            new_score = self._update_post_metrics(blog_post_id)

            return {
                'success': True,
                'action': action,
                'new_score': new_score,
                'was_toggle': was_toggle
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

    def _update_post_metrics(self, blog_post_id: int) -> int:
        """
        Recalculate and update post metrics atomically.
        Returns new sentiment score.
        """
        with transaction.atomic():
            post = BlogPost.objects.select_for_update().get(id=blog_post_id)

            # Calculate new sentiment
            likes = Engagement.objects.filter(
                blog_post_id=blog_post_id,
                action='like'
            ).count()

            dislikes = Engagement.objects.filter(
                blog_post_id=blog_post_id,
                action='dislike'
            ).count()

            new_score = likes - dislikes
            post.sentiment_score = new_score
            post.save(update_fields=['sentiment_score'])

            # Update PostMetric (create if doesn't exist)
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

            return new_score

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

    def get_post_metrics(self, blog_post_id: int) -> Dict[str, Any]:
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

    def get_top_posts(self, limit: int = 10) -> List[Dict]:
        """
        Get top performing posts by sentiment score.
        """
        posts = BlogPost.objects.filter(
            status=BlogPost.PostStatus.COMPLETED
        ).order_by('-sentiment_score', '-created_at')[:limit]

        return [
            {
                'id': p.id,
                'title': p.title,
                'sentiment_score': p.sentiment_score,
                'persona': p.persona.name if p.persona else None,
                'created_at': p.created_at.isoformat()
            }
            for p in posts
        ]
```

### 3.5 Prompt Service

```python
# backend/apps/blog/services/prompts.py

from typing import Dict, Tuple, List
from jinja2 import Template

from .models import Persona


class PromptService:
    """
    Service for building and managing AI prompts.
    Uses template-based approach with variable injection.
    """

    # Base System Prompts per Persona
    PERSONA_SYSTEM_PROMPTS = {
        'technical': """You are an expert Technical Writer with deep expertise in technical communication.

Your writing should:
- Use precise, industry-standard terminology accurately
- Structure complex information with clear hierarchies (headings, subheadings, bullet points)
- Provide concrete examples and data to support claims
- Maintain a professional, objective tone throughout
- Include in-text citations for any factual claims using format: [Source Name](url)
- Balance depth with accessibility

Focus on accuracy and clarity over creativity.""",

        'narrative': """You are a master Storyteller who weaves facts into compelling narratives.

Your writing should:
- Begin with an engaging hook or anecdote that draws readers in
- Use vivid, sensory language and metaphor to make concepts memorable
- Build emotional connection while maintaining factual accuracy
- Use narrative arc: setup → conflict → resolution
- End with a memorable takeaway or reflection
- Include sources subtly, woven into the narrative

Focus on resonance and engagement.""",

        'analyst': """You are an Industry Analyst providing data-driven insights and strategic perspectives.

Your writing should:
- Lead with key trends, statistics, and market signals
- Use analytical frameworks (SWOT, Porter's Forces, etc.) where relevant
- Focus on business implications and practical takeaways
- Include forward-looking predictions with confidence levels
- Cite reputable research, reports, and expert opinions
- Use data visualizations in text form when helpful

Focus on actionable intelligence.""",

        'educator': """You are an experienced Educator skilled at making complex topics accessible.

Your writing should:
- Start with clear learning objectives
- Explain concepts step-by-step, building understanding progressively
- Use analogies and real-world examples to anchor abstract ideas
- Check understanding with rhetorical questions
- Include summary takeaways and key points
- Cite beginner-friendly sources

Focus on clarity and learner success."""
    }

    # Variable Template for User Prompt
    USER_PROMPT_TEMPLATE = """
Write a comprehensive blog post about: {{ topic }}

{% if context %}
Additional context to consider:
{% for key, value in context.items() %}
- {{ key }}: {{ value }}
{% endfor %}
{% endif %}

Requirements:
- Length: {{ min_words }}-{{ max_words }} words
- Include a compelling, descriptive headline
- Use markdown formatting (## for subheadings, ** for emphasis)
- End with a summary paragraph of key takeaways
- If specific sources are referenced, format as [Source Name](url)
- {{ style_guidance }}

{% if include_sources %}
After the main content, include a "## Sources" section listing all references.
{% endif %}
"""

    def build_generation_prompt(
        self,
        topic: str,
        persona: Persona,
        additional_context: Dict = None
    ) -> Tuple[str, str]:
        """
        Build system and user prompts for generation.

        Returns:
            (system_prompt, user_prompt)
        """
        # Get base system prompt for persona
        base_system = self.PERSONA_SYSTEM_PROMPTS.get(
            persona.persona_type,
            self.PERSONA_SYSTEM_PROMPTS['technical']
        )

        # Inject persona-specific customizations
        system_prompt = self._inject_persona_variables(
            base_prompt=base_system,
            persona=persona
        )

        # Build user prompt from template
        user_prompt = self._render_user_prompt(
            topic=topic,
            persona=persona,
            additional_context=additional_context or {}
        )

        return system_prompt, user_prompt

    def _inject_persona_variables(self, base_prompt: str, persona: Persona) -> str:
        """
        Inject persona-specific variables into system prompt.
        Extensible for future customization.
        """
        variables = {
            'persona_name': persona.name,
            'temperature': persona.temperature,
        }

        # For extensibility: add custom variables based on persona type
        custom_vars = self._get_persona_custom_variables(persona)
        variables.update(custom_vars)

        # Simple variable injection (can be enhanced with Jinja2)
        for key, value in variables.items():
            base_prompt = base_prompt.replace(f'{{{{ {key} }}}}', str(value))

        return base_prompt

    def _get_persona_custom_variables(self, persona: Persona) -> Dict:
        """Get custom variables for specific persona types"""
        custom_vars = {}

        if persona.persona_type == 'technical':
            custom_vars['style_guidance'] = (
                "Use code blocks for technical examples. "
                "Define technical terms on first use."
            )
        elif persona.persona_type == 'narrative':
            custom_vars['style_guidance'] = (
                "Use storytelling elements. Include personal anecdotes or hypothetical scenarios."
            )
        elif persona.persona_type == 'analyst':
            custom_vars['style_guidance'] = (
                "Include data points. Reference industry reports. "
                "Provide numerical comparisons."
            )
        elif persona.persona_type == 'educator':
            custom_vars['style_guidance'] = (
                "Explain terms simply. Use 'imagine' scenarios. "
                "Include learning checks."
            )
        else:
            custom_vars['style_guidance'] = "Write in a clear, engaging style."

        return custom_vars

    def _render_user_prompt(
        self,
        topic: str,
        persona: Persona,
        additional_context: Dict
    ) -> str:
        """Render user prompt from template with variable injection"""
        template = Template(self.USER_PROMPT_TEMPLATE)

        return template.render(
            topic=topic,
            context=additional_context,
            min_words=800,
            max_words=1200,
            style_guidance=self._get_persona_custom_variables(persona).get('style_guidance', ''),
            include_sources=True
        )

    def format_response(self, raw_response: str) -> str:
        """Format Claude response for consistent output"""
        # Clean up common formatting issues
        formatted = raw_response.strip()

        # Ensure proper spacing around headings
        import re
        formatted = re.sub(r'\n(#{1,3})', r'\n\n\1', formatted)

        return formatted
```

---

## 4. Prompt Engineering System

### 4.1 The "Humanizer" Strategy

The prompt system uses **Variable Injection** to create contextually-aware, human-like output:

```
┌─────────────────────────────────────────────────────────────────┐
│                    PROMPT COMPOSITION                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐                    │
│  │  BASE PERSONA   │  + │  VARIABLES      │                    │
│  │  (Core Voice)   │    │  (Injection)    │                    │
│  │                 │    │                 │                    │
│  │ "You are a      │    │ • topic         │                    │
│  │  Technical      │    │ • word_count    │                    │
│  │  Writer..."     │    │ • style_guide   │                    │
│  └────────┬────────┘    └────────┬────────┘                    │
│           │                      │                             │
│           └──────────┬───────────┘                             │
│                      │                                         │
│                      ▼                                         │
│           ┌──────────────────────┐                             │
│           │  SYSTEM PROMPT       │                             │
│           │  (Claude context)    │                             │
│           └──────────────────────┘                             │
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐                    │
│  │  USER REQUEST   │  + │  CONTEXT        │                    │
│  │  (Topic)        │    │  (Additional)   │                    │
│  └────────┬────────┘    └────────┬────────┘                    │
│           │                      │                             │
│           └──────────┬───────────┘                             │
│                      │                                         │
│                      ▼                                         │
│           ┌──────────────────────┐                             │
│           │  USER PROMPT         │                             │
│           │  (Generation task)   │                             │
│           └──────────────────────┘                             │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Variable Injection Examples

```python
# Base Template
SYSTEM_PROMPT = """
You are a {persona_type} writing about {domain}.
Your tone should be {tone}.
Target audience: {audience}.
"""

# Injection Result
SYSTEM_PROMPT_INJECTED = """
You are a Technical Writer writing about renewable energy.
Your tone should be professional but accessible.
Target audience: Business decision-makers, policy makers.
"""
```

### 4.3 Prompt Template Hierarchy

```
PromptTemplate
├── System Layer (Persona definition)
│   ├── Base personality
│   ├── Writing style parameters
│   └── Domain knowledge injection
│
├── Task Layer (What to generate)
│   ├── Content type instructions
│   ├── Formatting requirements
│   └── Output structure
│
└── Context Layer (Specific to this generation)
    ├── User topic
    ├── Additional keywords
    └── Source references
```

### 4.4 Extensibility: Future Prompt Features

```python
# Future: Dynamic Prompt Chaining
class PromptChainService:
    """
    Chain multiple prompts for complex generation.
    Example: Research → Outline → Draft → Polish
    """

    def chain_prompts(self, chain_config: List[Dict]) -> str:
        """
        chain_config = [
            {'stage': 'research', 'prompt': research_template},
            {'stage': 'outline', 'prompt': outline_template},
            {'stage': 'draft', 'prompt': draft_template}
        ]
        """
        pass
```

---

## 5. State Management Strategy

### 5.1 React State Management Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    STATE MANAGEMENT LAYER                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    CONTEXT LAYER                         │   │
│  │  ┌───────────────┐  ┌───────────────┐  ┌─────────────┐ │   │
│  │  │ SessionContext│  │  ToastContext │  │ ThemeContext│ │   │
│  │  │ (session_id)  │  │ (notifications)│  │ (dark mode) │ │   │
│  │  └───────────────┘  └───────────────┘  └─────────────┘ │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              │ use                               │
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│ │                    COMPONENT STATE                         │   │
│  │  ┌────────────────────────────────────────────────────┐  │   │
│  │  │  BlogGenerator (local form state)                   │  │   │
│  │  │  • topic: string                                    │  │   │
│  │  │  • persona: string                                  │  │   │
│  │  │  • isGenerating: boolean                            │  │   │
│  │  │  • progress: number (0-100)                         │  │   │
│  │  └────────────────────────────────────────────────────┘  │   │
│  │                                                           │   │
│  │  ┌────────────────────────────────────────────────────┐  │   │
│  │  │  BlogViewer (post state)                            │  │   │
│  │  │  • post: BlogPost | null                            │  │   │
│  │  │  • isLoading: boolean                               │  │   │
│  │  │  • userEngagement: 'like' | 'dislike' | null        │  │   │
│  │  └────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              │ sync via                          │
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│ │                    SERVER STATE                            │   │
│  │  • Polling endpoint for generation status                │   │
│  │  • WebSocket (future: real-time updates)                 │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 Loading State Implementation

```typescript
// frontend/src/hooks/useBlogGeneration.ts

import { useState, useCallback, useEffect } from 'react';
import { api } from '../services/api';
import { useSession } from './useSession';

interface GenerationState {
  isGenerating: boolean;
  progress: number;
  currentStage: 'idle' | 'prompting' | 'generating' | 'completed' | 'error';
  error: string | null;
  blogPostId: number | null;
}

interface UseBlogGenerationReturn {
  state: GenerationState;
  generateBlog: (topic: string, persona: string) => Promise<void>;
  resetState: () => void;
}

const POLL_INTERVAL = 1000; // 1 second
const MAX_POLL_ATTEMPTS = 120; // 2 minutes max

export function useBlogGeneration(): UseBlogGenerationReturn {
  const { sessionId } = useSession();

  const [state, setState] = useState<GenerationState>({
    isGenerating: false,
    progress: 0,
    currentStage: 'idle',
    error: null,
    blogPostId: null,
  });

  const pollStatus = useCallback(async (jobId: string, attempts = 0): Promise<void> => {
    try {
      const response = await api.get(`/blog/status/${jobId}`);

      if (response.data.status === 'completed') {
        setState({
          isGenerating: false,
          progress: 100,
          currentStage: 'completed',
          error: null,
          blogPostId: response.data.blog_post_id,
        });
        return;
      }

      if (response.data.status === 'failed') {
        setState({
          isGenerating: false,
          progress: 0,
          currentStage: 'error',
          error: response.data.error || 'Generation failed',
          blogPostId: null,
        });
        return;
      }

      // Still processing - update progress and poll again
      setState(prev => ({
        ...prev,
        progress: response.data.progress || Math.min(90, prev.progress + 10),
        currentStage: response.data.stage || 'generating',
      }));

      if (attempts < MAX_POLL_ATTEMPTS) {
        setTimeout(() => pollStatus(jobId, attempts + 1), POLL_INTERVAL);
      } else {
        setState(prev => ({
          ...prev,
          isGenerating: false,
          currentStage: 'error',
          error: 'Generation timed out',
        }));
      }
    } catch (error) {
      setState(prev => ({
        ...prev,
        isGenerating: false,
        currentStage: 'error',
        error: 'Failed to check generation status',
      }));
    }
  }, []);

  const generateBlog = useCallback(async (topic: string, persona: string) => {
    setState({
      isGenerating: true,
      progress: 0,
      currentStage: 'prompting',
      error: null,
      blogPostId: null,
    });

    try {
      const response = await api.post('/blog/generate/', {
        topic,
        persona,
        session_id: sessionId,
      });

      // If generation is synchronous (completed immediately)
      if (response.data.status === 'completed') {
        setState({
          isGenerating: false,
          progress: 100,
          currentStage: 'completed',
          error: null,
          blogPostId: response.data.blog_post_id,
        });
        return;
      }

      // If asynchronous, start polling
      if (response.data.job_id) {
        setState(prev => ({
          ...prev,
          currentStage: 'generating',
          progress: 20,
        }));
        await pollStatus(response.data.job_id);
      }
    } catch (error: any) {
      setState({
        isGenerating: false,
        progress: 0,
        currentStage: 'error',
        error: error.response?.data?.message || 'Failed to generate blog',
        blogPostId: null,
      });
    }
  }, [sessionId, pollStatus]);

  const resetState = useCallback(() => {
    setState({
      isGenerating: false,
      progress: 0,
      currentStage: 'idle',
      error: null,
      blogPostId: null,
    });
  }, []);

  return {
    state,
    generateBlog,
    resetState,
  };
}
```

### 5.3 Session Management Hook

```typescript
// frontend/src/hooks/useSession.ts

import { useState, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';

const SESSION_STORAGE_KEY = 'ai_blog_session_id';

export function useSession() {
  const [sessionId, setSessionId] = useState<string>(() => {
    // Initialize from localStorage or create new
    const stored = localStorage.getItem(SESSION_STORAGE_KEY);
    if (stored) return stored;

    const newId = uuidv4();
    localStorage.setItem(SESSION_STORAGE_KEY, newId);
    return newId;
  });

  const [isIdentified, setIsIdentified] = useState<boolean>(false);

  useEffect(() => {
    // Validate session format
    try {
      const isValid = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(sessionId);
      setIsIdentified(isValid);

      if (!isValid) {
        const newId = uuidv4();
        localStorage.setItem(SESSION_STORAGE_KEY, newId);
        setSessionId(newId);
      }
    } catch {
      const newId = uuidv4();
      localStorage.setItem(SESSION_STORAGE_KEY, newId);
      setSessionId(newId);
    }
  }, [sessionId]);

  const resetSession = () => {
    const newId = uuidv4();
    localStorage.setItem(SESSION_STORAGE_KEY, newId);
    setSessionId(newId);
  };

  return {
    sessionId,
    isIdentified,
    resetSession,
  };
}
```

### 5.4 Engagement Hook

```typescript
// frontend/src/hooks/useEngagement.ts

import { useState, useCallback } from 'react';
import { api } from '../services/api';
import { useSession } from './useSession';

type EngagementAction = 'like' | 'dislike';
type UserEngagement = 'like' | 'dislike' | null;

interface EngagementState {
  likes: number;
  dislikes: number;
  userEngagement: UserEngagement;
  isSubmitting: boolean;
}

export function useEngagement(blogPostId: number) {
  const { sessionId } = useSession();

  const [state, setState] = useState<EngagementState>({
    likes: 0,
    dislikes: 0,
    userEngagement: null,
    isSubmitting: false,
  });

  const fetchEngagement = useCallback(async () => {
    try {
      const response = await api.get(`/blog/${blogPostId}/engagement/`);
      setState({
        likes: response.data.likes,
        dislikes: response.data.dislikes,
        userEngagement: response.data.user_action || null,
        isSubmitting: false,
      });
    } catch (error) {
      console.error('Failed to fetch engagement:', error);
    }
  }, [blogPostId]);

  const toggleEngagement = useCallback(async (action: EngagementAction) => {
    // Optimistic update
    const isRemoving = state.userEngagement === action;

    setState(prev => ({
      ...prev,
      isSubmitting: true,
      likes: prev.likes + (action === 'like' ? (isRemoving ? -1 : 1) : 0),
      dislikes: prev.dislikes + (action === 'dislike' ? (isRemoving ? -1 : 1) : 0),
      userEngagement: isRemoving ? null : action,
    }));

    try {
      const response = await api.post('/engage/', {
        blog_id: blogPostId,
        action,
        session_id: sessionId,
      });

      // Sync with server response
      setState({
        likes: response.data.likes_count,
        dislikes: response.data.dislikes_count,
        userEngagement: response.data.user_action,
        isSubmitting: false,
      });
    } catch (error) {
      // Rollback on error
      await fetchEngagement();
    }
  }, [blogPostId, sessionId, state.userEngagement, fetchEngagement]);

  return {
    state,
    toggleEngagement,
    fetchEngagement,
  };
}
```

### 5.5 Loading UI Component

```typescript
// frontend/src/components/blog/GenerationProgress.tsx

interface GenerationProgressProps {
  stage: 'prompting' | 'generating' | 'completed' | 'error';
  progress: number;
  error?: string | null;
}

const STAGE_MESSAGES = {
  prompting: 'Preparing your prompt...',
  generating: 'AI is writing your blog post...',
  completed: 'Blog post generated!',
  error: 'Generation failed',
};

export function GenerationProgress({ stage, progress, error }: GenerationProgressProps) {
  if (stage === 'idle' || stage === 'completed') return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg p-8 max-w-md w-full mx-4">
        <div className="flex items-center gap-4 mb-4">
          {stage === 'error' ? (
            <div className="w-12 h-12 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center">
              <svg className="w-6 h-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
          ) : (
            <div className="w-12 h-12 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
              <svg className="w-6 h-6 text-blue-600 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
            </div>
          )}
          <div>
            <h3 className="font-semibold text-gray-900 dark:text-white">
              {STAGE_MESSAGES[stage]}
            </h3>
            {stage !== 'error' && (
              <p className="text-sm text-gray-500 dark:text-gray-400">This may take 10-30 seconds</p>
            )}
          </div>
        </div>

        {stage === 'error' && error && (
          <p className="text-sm text-red-600 dark:text-red-400 mb-4">{error}</p>
        )}

        {stage !== 'error' && (
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        )}
      </div>
    </div>
  );
}
```

---

## 6. API Contract Specification

### 6.1 Complete Endpoint Reference

| Method | Endpoint | Auth | Request | Response |
|--------|----------|------|---------|----------|
| `POST` | `/api/blog/generate/` | None | `{topic, persona, additional_context}` | `{blog_post_id, status, job_id}` |
| `GET` | `/api/blog/status/{job_id}/` | None | — | `{status, progress, blog_post_id}` |
| `GET` | `/api/blog/` | None | `?page=1&persona=technical` | `{count, next, previous, results[]}` |
| `GET` | `/api/blog/{id}/` | None | — | `{BlogPost detail}` |
| `GET` | `/api/blog/{id}/engagement/` | None | — | `{likes, dislikes, user_action}` |
| `POST` | `/api/engage/` | None | `{blog_id, action, session_id}` | `{success, likes_count, dislikes_count}` |
| `GET` | `/api/analytics/` | None | — | `{total_posts, avg_engagement, top_posts[]}` |
| `GET` | `/api/personas/` | None | — | `{results[]}` |
| `DELETE` | `/api/blog/{id}/` | None | — | `{success}` |

### 6.2 Response Schemas

#### BlogPost Detail Response
```json
{
  "id": 1,
  "title": "The Future of Renewable Energy: A Technical Analysis",
  "slug": "future-renewable-energy-technical-analysis",
  "topic_input": "renewable energy future",
  "generated_content": "# The Future of Renewable Energy\n\n...",
  "content_structure": {
    "word_count": 1250,
    "reading_time_minutes": 6,
    "heading_count": 8
  },
  "sources": [
    {
      "title": "IEA World Energy Outlook 2024",
      "url": "https://iea.org/reports/world-energy-outlook-2024",
      "domain": "iea.org",
      "is_verified": true,
      "relevance_score": 0.95
    }
  ],
  "persona": {
    "id": 1,
    "name": "Technical Writer",
    "slug": "technical"
  },
  "status": "completed",
  "sentiment_score": 5,
  "metadata": {
    "model_used": "claude-3-5-sonnet-20241022",
    "generation_time_seconds": 12.5,
    "total_tokens": 3200
  },
  "created_at": "2025-02-20T10:30:00Z",
  "published_at": "2025-02-20T10:30:15Z"
}
```

---

## 7. Extensibility Framework

### 7.1 Plugin Architecture (Future)

```python
# backend/core/plugins/base.py

from abc import ABC, abstractmethod


class BlogPlugin(ABC):
    """
    Base class for extensible blog post features.
    Examples: SEO Analysis, Image Generation, Translation
    """

    plugin_name: str
    version: str = "1.0.0"

    @abstractmethod
    def process(self, blog_post: BlogPost) -> Dict:
        """
        Process a blog post and return metadata.
        Called after generation completes.
        """
        pass

    @abstractmethod
    def get_ui_components(self) -> Dict:
        """
        Return UI component specifications for frontend.
        Enables dynamic UI extension.
        """
        pass


class SEOAnalysisPlugin(BlogPlugin):
    """Future: Analyze and optimize post for SEO"""

    plugin_name = "seo_analysis"

    def process(self, blog_post: BlogPost) -> Dict:
        # Analyze keywords, readability, meta tags
        return {
            "seo_score": 85,
            "keywords": ["renewable", "energy", "sustainability"],
            "readability_score": 72
        }


class ImageGenerationPlugin(BlogPlugin):
    """Future: Generate featured image for post"""

    plugin_name = "image_generation"

    def process(self, blog_post: BlogPost) -> Dict:
        # Generate image based on title/content
        return {
            "image_url": "https://...",
            "image_prompt_used": "..."
        }
```

### 7.2 Data Model Extensibility

```python
# Using JSONField for future compatibility without migrations

class BlogPost(models.Model):
    # ... existing fields ...

    # Extensible metadata for future features
    extensions = models.JSONField(
        default=dict,
        blank=True,
        help_text="""
        Extensible storage for plugin data:
        {
            "seo": {...},
            "images": [...],
            "translations": {...},
            "analytics": {...}
        }
        """
    )
```

---

## 8. Error Handling & Resilience

### 8.1 Error Response Format

```json
{
  "error": {
    "code": "GENERATION_FAILED",
    "message": "Failed to generate blog post",
    "details": {
      "stage": "claude_api_call",
      "retry_count": 2,
      "original_error": "Rate limit exceeded"
    }
  }
}
```

### 8.2 Circuit Breaker Pattern (Future)

```python
# backend/core/resilience/circuit_breaker.py

class CircuitBreaker:
    """
    Circuit breaker for external API calls.
    Prevents cascading failures when Claude API is down.
    """

    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'closed'  # closed, open, half-open

    def call(self, func, *args, **kwargs):
        if self.state == 'open':
            if self._should_attempt_reset():
                self.state = 'half-open'
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
```

---

## Appendix A: Django Settings Configuration

```python
# backend/ai_blog/settings.py

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.postgres',  # For JSONField support

    # Third party
    'rest_framework',
    'corsheaders',

    # Local apps
    'apps.blog',
    'apps.core',
]

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
    'EXCEPTION_HANDLER': 'core.exceptions.custom_exception_handler',
}

CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',
    'http://localhost:3000',
]

CORS_ALLOW_CREDENTIALS = True
```

---

**Document Version:** 1.0.0
**Last Updated:** 2025-02-20
**Status:** Ready for Implementation
