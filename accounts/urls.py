from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/',                           views.login_view,             name='login'),
    path('logout/',                          views.logout_view,            name='logout'),
    path('register/',                        views.register_view,          name='register'),
    path('profil/',                          views.profil_view,            name='profil'),
    path('utilisateurs/',                    views.gestion_utilisateurs,   name='gestion_utilisateurs'),
    path('utilisateurs/creer/',              views.creer_utilisateur,      name='creer_utilisateur'),
    path('utilisateurs/<int:pk>/modifier/',  views.modifier_utilisateur,   name='modifier_utilisateur'),
    path('utilisateurs/<int:pk>/supprimer/', views.supprimer_utilisateur,  name='supprimer_utilisateur'),
]
