from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from .models import CustomUser


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Nom d'utilisateur"}),
        label="Nom d'utilisateur"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Mot de passe'}),
        label='Mot de passe'
    )


class RegisterForm(UserCreationForm):
    first_name  = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), label='Prénom', required=True)
    last_name   = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), label='Nom', required=True)
    email       = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}), label='Email', required=True)
    telephone   = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), label='Téléphone', required=False)
    departement = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), label='Département', required=False)

    class Meta:
        model  = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'telephone', 'departement', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Cet email est déjà utilisé.")
        return email


class ProfilForm(forms.ModelForm):
    class Meta:
        model  = CustomUser
        fields = ['first_name', 'last_name', 'email', 'telephone', 'departement', 'photo']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = CustomUser.objects.filter(email=email).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Cet email est déjà utilisé par un autre compte.")
        return email


class ChangePasswordForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        self.fields['old_password'].label    = 'Mot de passe actuel'
        self.fields['new_password1'].label   = 'Nouveau mot de passe'
        self.fields['new_password2'].label   = 'Confirmer le nouveau mot de passe'


class AdminUserForm(forms.ModelForm):
    class Meta:
        model  = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'role',
                  'telephone', 'departement', 'manager', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name == 'is_active':
                field.widget.attrs['class'] = 'form-check-input'
            else:
                field.widget.attrs['class'] = 'form-control'
        self.fields['manager'].queryset = CustomUser.objects.filter(role='manager')
        self.fields['manager'].required = False

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            qs = CustomUser.objects.filter(email=email)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError("Cet email est déjà utilisé.")
        return email
