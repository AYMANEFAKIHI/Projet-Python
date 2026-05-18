from django.urls import path
from . import views

app_name = 'rapports'

urlpatterns = [
    path('',        views.tableau_de_bord_rapports, name='index'),
    path('export/', views.export_csv,               name='export_csv'),
]
