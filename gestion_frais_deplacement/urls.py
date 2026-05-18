from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('missions/', include('missions.urls', namespace='missions')),
    path('frais/', include('frais.urls', namespace='frais')),
    path('rapports/', include('rapports.urls', namespace='rapports')),
    path('dashboard/', include('accounts.dashboard_urls', namespace='dashboard')),
    path('', RedirectView.as_view(url='/dashboard/', permanent=False)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
