from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from accounts import views as accounts_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),  # Zmień tę linię
    path('', include('ksiazki.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)