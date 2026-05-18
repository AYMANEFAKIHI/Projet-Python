from django.db import models
from django.conf import settings


class Mission(models.Model):
    STATUT_CHOICES = [
        ('en_cours',  'En cours'),
        ('terminee',  'Terminée'),
        ('annulee',   'Annulée'),
    ]

    employe      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                     related_name='missions', verbose_name='Employé')
    destination  = models.CharField(max_length=200, verbose_name='Destination')
    date_debut   = models.DateField(verbose_name='Date de début')
    date_fin     = models.DateField(verbose_name='Date de fin')
    objectif     = models.TextField(verbose_name='Objectif du déplacement')
    statut       = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_cours', verbose_name='Statut')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Mission'
        verbose_name_plural = 'Missions'
        ordering = ['-date_debut']

    def __str__(self):
        return f"{self.destination} ({self.date_debut} → {self.date_fin})"

    @property
    def duree(self):
        return (self.date_fin - self.date_debut).days + 1

    @property
    def total_frais(self):
        return self.frais.aggregate(total=models.Sum('montant'))['total'] or 0
