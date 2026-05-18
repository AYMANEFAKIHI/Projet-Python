from django import forms
from .models import Mission


class MissionForm(forms.ModelForm):
    class Meta:
        model  = Mission
        fields = ['destination', 'date_debut', 'date_fin', 'objectif', 'statut']
        widgets = {
            'destination': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Casablanca, Paris...'}),
            'date_debut':  forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_fin':    forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'objectif':    forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': "Décrivez l'objectif du déplacement..."}),
            'statut':      forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Statut non obligatoire à la création — valeur par défaut 'en_cours'
        self.fields['statut'].required = False
        self.fields['statut'].initial  = 'en_cours'

    def clean_statut(self):
        statut = self.cleaned_data.get('statut')
        if not statut:
            return 'en_cours'
        return statut

    def clean(self):
        cleaned = super().clean()
        d1 = cleaned.get('date_debut')
        d2 = cleaned.get('date_fin')
        if d1 and d2:
            if d2 < d1:
                raise forms.ValidationError("La date de fin doit être postérieure ou égale à la date de début.")
        return cleaned