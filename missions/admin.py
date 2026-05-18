from django.contrib import admin
from .models import Mission


@admin.register(Mission)
class MissionAdmin(admin.ModelAdmin):
    list_display  = ['destination', 'employe', 'date_debut', 'date_fin', 'statut', 'total_frais']
    list_filter   = ['statut', 'date_debut']
    search_fields = ['destination', 'employe__last_name']
    date_hierarchy = 'date_debut'
