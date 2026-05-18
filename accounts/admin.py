from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display  = ['username', 'get_full_name', 'email', 'role', 'departement', 'is_active']
    list_filter   = ['role', 'is_active', 'departement']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    fieldsets     = UserAdmin.fieldsets + (
        ('Informations supplémentaires', {
            'fields': ('role', 'telephone', 'departement', 'manager', 'photo')
        }),
    )
