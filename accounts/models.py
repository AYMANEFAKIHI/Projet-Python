from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin',   'Administrateur'),
        ('manager', 'Manager'),
        ('employe', 'Employé'),
    ]

    role                 = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employe', verbose_name='Rôle')
    telephone            = models.CharField(max_length=20, blank=True, verbose_name='Téléphone')
    departement          = models.CharField(max_length=100, blank=True, verbose_name='Département')
    manager              = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='equipe',
        limit_choices_to={'role': 'manager'},
        verbose_name='Manager'
    )
    photo                = models.ImageField(upload_to='photos/', blank=True, null=True, verbose_name='Photo de profil')
    must_change_password = models.BooleanField(default=False, verbose_name='Doit changer le mot de passe')
    date_creation        = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_manager_role(self):
        return self.role == 'manager'

    @property
    def is_employe(self):
        return self.role == 'employe'
