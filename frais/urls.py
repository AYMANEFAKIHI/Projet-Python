from django.urls import path
from . import views

app_name = 'frais'

urlpatterns = [
    path('',                                   views.liste_frais,              name='liste'),
    path('creer/',                             views.creer_frais,              name='creer'),
    path('<int:pk>/',                          views.detail_frais,             name='detail'),
    path('<int:pk>/modifier/',                 views.modifier_frais,           name='modifier'),
    path('<int:pk>/supprimer/',                views.supprimer_frais,          name='supprimer'),
    path('<int:pk>/valider/',                  views.valider_frais,            name='valider'),
    path('<int:pk>/rembourse/',                views.marquer_rembourse,        name='rembourse'),
    path('justificatif/<int:pk>/dl/',          views.telecharger_justificatif, name='telecharger_justif'),
    path('justificatif/<int:pk>/supprimer/',   views.supprimer_justificatif,   name='supprimer_justif'),
]
