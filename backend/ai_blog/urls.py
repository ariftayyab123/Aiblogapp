"""
URL configuration for AI Blog Generator project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from ai_blog.apps.core.views import TokenAuthView

from ai_blog.apps.blog import views as blog_views

# DRF Router for ViewSets
router = DefaultRouter()
router.register(r'personas', blog_views.PersonaViewSet, basename='persona')
router.register(r'posts', blog_views.BlogPostViewSet, basename='post')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('ai_blog.apps.core.urls')),

    # Router URLs under /api/
    path('api/', include(router.urls)),

    # Custom endpoints
    path('api/generate/', blog_views.BlogGenerationView.as_view(), name='blog-generate'),
    path('api/generation-status/<int:job_id>/', blog_views.GenerationStatusView.as_view(), name='generation-status'),
    path('api/engage/', blog_views.EngagementView.as_view(), name='engage'),
    path('api/posts/<int:blog_id>/engagement/', blog_views.EngagementView.as_view(), name='blog-engagement'),
    path('api/analytics/', blog_views.AnalyticsView.as_view(), name='analytics'),
    path('api/auth/token/', TokenAuthView.as_view(), name='auth-token'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
