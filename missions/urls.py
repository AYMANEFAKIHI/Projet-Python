from django.urls import path
from . import views

app_name = 'missions'

urlpatterns = [
    path('',                    views.liste_missions,   name='liste'),
    path('creer/',              views.creer_mission,    name='creer'),
    path('<int:pk>/',           views.detail_mission,   name='detail'),
    path('<int:pk>/modifier/',  views.modifier_mission, name='modifier'),
    path('<int:pk>/supprimer/', views.supprimer_mission,name='supprimer'),
]
