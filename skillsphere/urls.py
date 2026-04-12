from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import custom_permission_denied_view

handler403 = custom_permission_denied_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)