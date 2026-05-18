from django.contrib import admin
from .models import Frais, Justificatif


class JustificatifInline(admin.TabularInline):
    model  = Justificatif
    extra  = 0
    fields = ['fichier', 'nom_original', 'date_upload']
    readonly_fields = ['date_upload']


@admin.register(Frais)
class FraisAdmin(admin.ModelAdmin):
    list_display   = ['employe', 'mission', 'type_frais', 'montant', 'date_frais', 'statut']
    list_filter    = ['statut', 'type_frais', 'date_frais']
    search_fields  = ['employe__last_name', 'mission__destination']
    inlines        = [JustificatifInline]
    date_hierarchy = 'date_frais'
