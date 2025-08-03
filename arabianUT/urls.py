from django.contrib import admin
from django.urls import path, include
from django.conf import settings            
from django.conf.urls.static import static  

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('accounts/', include(('accounts.urls', "accounts"), namespace="accounts")),
    path('accounting/', include('accounting.urls')),
    path('reports/', include('reports.urls')),
    path("markdownx/", include("markdownx.urls")),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)