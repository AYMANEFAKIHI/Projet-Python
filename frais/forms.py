from django import forms
from .models import Frais, Justificatif
from missions.models import Mission
import os


class FraisForm(forms.ModelForm):
    class Meta:
        model  = Frais
        fields = ['mission', 'type_frais', 'montant', 'date_frais', 'description']
        widgets = {
            'mission':     forms.Select(attrs={'class': 'form-select'}),
            'type_frais':  forms.Select(attrs={'class': 'form-select'}),
            'montant':     forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'date_frais':  forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description optionnelle...'}),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['mission'].queryset = Mission.objects.filter(employe=user).exclude(statut='annulee')
        self.fields['mission'].empty_label = '— Sélectionner une mission —'

    def clean_montant(self):
        montant = self.cleaned_data.get('montant')
        if montant is not None and montant <= 0:
            raise forms.ValidationError("Le montant doit être supérieur à 0.")
        if montant is not None and montant > 999999.99:
            raise forms.ValidationError("Le montant semble incorrect (max 999 999,99 MAD).")
        return montant

    def clean_date_frais(self):
        date_frais = self.cleaned_data.get('date_frais')
        from django.utils import timezone
        if date_frais and date_frais > timezone.now().date():
            raise forms.ValidationError("La date du frais ne peut pas être dans le futur.")
        return date_frais


class JustificatifForm(forms.ModelForm):
    class Meta:
        model   = Justificatif
        fields  = ['fichier']
        widgets = {
            'fichier': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png'
            })
        }

    def clean_fichier(self):
        fichier = self.cleaned_data.get('fichier')
        if fichier:
            ext = os.path.splitext(fichier.name)[1].lower()
            if ext not in ['.pdf', '.jpg', '.jpeg', '.png']:
                raise forms.ValidationError("Format non autorisé. Utilisez PDF, JPG ou PNG uniquement.")
            if fichier.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Le fichier ne doit pas dépasser 5 Mo.")
        return fichier


class ValidationForm(forms.ModelForm):
    class Meta:
        model  = Frais
        fields = ['statut', 'commentaire_manager']
        widgets = {
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'commentaire_manager': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Commentaire (obligatoire en cas de refus)...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['statut'].choices = [
            ('', '— Choisir une décision —'),
            ('valide', 'Valider la demande'),
            ('refuse', 'Refuser la demande'),
        ]

    def clean(self):
        cleaned = super().clean()
        statut  = cleaned.get('statut')
        commentaire = cleaned.get('commentaire_manager', '').strip()
        if not statut:
            raise forms.ValidationError("Veuillez choisir une décision.")
        if statut == 'refuse' and not commentaire:
            raise forms.ValidationError("Un commentaire est obligatoire en cas de refus.")
        return cleaned
