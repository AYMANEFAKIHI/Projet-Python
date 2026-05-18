from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import CustomUser
from .forms import LoginForm, RegisterForm, ProfilForm, AdminUserForm, ChangePasswordForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        messages.success(request, f'Bienvenue, {user.get_full_name() or user.username} !')
        return redirect(request.GET.get('next', 'dashboard:index'))
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'Vous avez été déconnecté.')
    return redirect('accounts:login')


def register_view(request):
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, 'Compte créé avec succès !')
        return redirect('dashboard:index')
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profil_view(request):
    form = ProfilForm(request.POST or None, request.FILES or None, instance=request.user)
    pwd_form = ChangePasswordForm(user=request.user, data=request.POST or None)

    if request.method == 'POST':
        if 'update_profil' in request.POST and form.is_valid():
            form.save()
            messages.success(request, 'Profil mis à jour.')
            return redirect('accounts:profil')
        elif 'change_password' in request.POST and pwd_form.is_valid():
            pwd_form.save()
            update_session_auth_hash(request, pwd_form.user)
            request.user.must_change_password = False
            request.user.save(update_fields=['must_change_password'])
            messages.success(request, 'Mot de passe modifié avec succès.')
            return redirect('accounts:profil')

    return render(request, 'accounts/profil.html', {'form': form, 'pwd_form': pwd_form})


@login_required
def gestion_utilisateurs(request):
    if not request.user.is_admin:
        messages.error(request, 'Accès refusé.')
        return redirect('dashboard:index')
    q = request.GET.get('q', '')
    role = request.GET.get('role', '')
    users = CustomUser.objects.all().order_by('last_name', 'first_name')
    if q:
        users = users.filter(
            Q(first_name__icontains=q) | Q(last_name__icontains=q) | Q(email__icontains=q) | Q(username__icontains=q)
        )
    if role:
        users = users.filter(role=role)
    return render(request, 'accounts/gestion_utilisateurs.html', {
        'users': users, 'q': q, 'role': role,
        'role_choices': CustomUser.ROLE_CHOICES,
    })


@login_required
def creer_utilisateur(request):
    if not request.user.is_admin:
        return redirect('dashboard:index')
    form = AdminUserForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        # Mot de passe temporaire — l'utilisateur devra le changer
        temp_password = CustomUser.objects.make_random_password(length=12)
        user.set_password(temp_password)
        user.must_change_password = True
        user.save()
        messages.success(
            request,
            f'Utilisateur {user.username} créé. Mot de passe temporaire : {temp_password} '
            f'(à communiquer à l\'utilisateur)'
        )
        return redirect('accounts:gestion_utilisateurs')
    return render(request, 'accounts/form_utilisateur.html', {'form': form, 'titre': 'Créer un utilisateur'})


@login_required
def modifier_utilisateur(request, pk):
    if not request.user.is_admin:
        return redirect('dashboard:index')
    utilisateur = get_object_or_404(CustomUser, pk=pk)
    form = AdminUserForm(request.POST or None, instance=utilisateur)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Utilisateur mis à jour.')
        return redirect('accounts:gestion_utilisateurs')
    return render(request, 'accounts/form_utilisateur.html', {
        'form': form, 'titre': 'Modifier utilisateur', 'obj': utilisateur
    })


@login_required
def supprimer_utilisateur(request, pk):
    if not request.user.is_admin:
        return redirect('dashboard:index')
    utilisateur = get_object_or_404(CustomUser, pk=pk)
    if utilisateur == request.user:
        messages.error(request, 'Vous ne pouvez pas supprimer votre propre compte.')
        return redirect('accounts:gestion_utilisateurs')
    if request.method == 'POST':
        utilisateur.is_active = False  # désactivation plutôt que suppression
        utilisateur.save()
        messages.success(request, f'Utilisateur {utilisateur.username} désactivé.')
        return redirect('accounts:gestion_utilisateurs')
    return render(request, 'accounts/confirmer_suppression_user.html', {'obj': utilisateur})
