from django.urls import path
from .dashboard_views import dashboard

app_name = 'dashboard'

urlpatterns = [
    path('', dashboard, name='index'),
]
