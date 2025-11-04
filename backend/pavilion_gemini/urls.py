"""
URL configuration for pavilion_gemini project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

def api_root(request):
    """Root endpoint that provides API information."""
    return JsonResponse({
        'message': 'Pavilion Gemini API',
        'version': '1.0',
        'endpoints': {
            'admin': '/admin/',
            'authentication': {
                'login': '/api/auth/login/',
                'refresh': '/api/auth/refresh/',
                'verify': '/api/auth/verify/',
            },
            'articles': '/api/articles/',
            'rss_feeds': '/api/rss/feeds/',
        },
        'documentation': 'Access /admin/ for Django admin panel'
    })

urlpatterns = [
    path('', api_root, name='api_root'),
    path('admin/', admin.site.urls),
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/', include('cms.urls')),
    path('api/rss/', include('rss_fetcher.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

