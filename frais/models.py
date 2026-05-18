from django.db import models
from django.conf import settings
from missions.models import Mission
import os, uuid


def justificatif_path(instance, filename):
    ext  = os.path.splitext(filename)[1]
    name = f"{uuid.uuid4().hex}{ext}"
    return f"justificatifs/{instance.frais.employe.id}/{name}"


class Frais(models.Model):
    TYPE_CHOICES = [
        ('transport',    'Transport'),
        ('hebergement',  'Hébergement'),
        ('restauration', 'Restauration'),
        ('autre',        'Autres dépenses'),
    ]
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('valide',     'Validé'),
        ('refuse',     'Refusé'),
        ('rembourse',  'Remboursé'),
    ]

    employe             = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                            related_name='frais', verbose_name='Employé')
    mission             = models.ForeignKey(Mission, on_delete=models.CASCADE,
                                            related_name='frais', verbose_name='Mission')
    type_frais          = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name='Type de frais')
    montant             = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Montant (MAD)')
    date_frais          = models.DateField(verbose_name='Date du frais')
    description         = models.TextField(blank=True, verbose_name='Description')
    statut              = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente', verbose_name='Statut')
    commentaire_manager = models.TextField(blank=True, verbose_name='Commentaire manager')
    valide_par          = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                            on_delete=models.SET_NULL, related_name='frais_valides',
                                            verbose_name='Validé par')
    date_validation     = models.DateTimeField(null=True, blank=True, verbose_name='Date de validation')
    date_creation       = models.DateTimeField(auto_now_add=True)
    date_modification   = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Frais'
        verbose_name_plural = 'Frais'
        ordering            = ['-date_creation']

    def __str__(self):
        return f"{self.get_type_frais_display()} – {self.montant} MAD ({self.get_statut_display()})"

    @property
    def peut_modifier(self):
        return self.statut == 'en_attente'


class Justificatif(models.Model):
    frais        = models.ForeignKey(Frais, on_delete=models.CASCADE, related_name='justificatifs')
    fichier      = models.FileField(upload_to=justificatif_path, verbose_name='Fichier')
    nom_original = models.CharField(max_length=255, verbose_name='Nom du fichier')
    date_upload  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Justificatif'

    def __str__(self):
        return self.nom_original

    @property
    def extension(self):
        return os.path.splitext(self.nom_original)[1].lower()

    @property
    def is_image(self):
        return self.extension in ['.jpg', '.jpeg', '.png']
