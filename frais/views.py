from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.http import FileResponse, Http404
from .models import Frais, Justificatif
from .forms import FraisForm, JustificatifForm, ValidationForm
from accounts.models import CustomUser


def _check_access(user, frais):
    """Lève PermissionDenied si l'utilisateur n'a pas accès à ce frais."""
    if not (user.is_admin or user == frais.employe or
            (user.is_manager_role and frais.employe.manager == user)):
        raise PermissionDenied


@login_required
def liste_frais(request):
    user = request.user
    if user.is_admin:
        qs = Frais.objects.select_related('employe', 'mission').all()
    elif user.is_manager_role:
        equipe = CustomUser.objects.filter(manager=user)
        qs = Frais.objects.filter(employe__in=equipe).select_related('employe', 'mission')
    else:
        qs = Frais.objects.filter(employe=user).select_related('mission')

    statut     = request.GET.get('statut', '')
    type_frais = request.GET.get('type', '')
    if statut:
        qs = qs.filter(statut=statut)
    if type_frais:
        qs = qs.filter(type_frais=type_frais)

    return render(request, 'frais/liste.html', {
        'frais_list':     qs,
        'statut_filtre':  statut,
        'type_filtre':    type_frais,
        'statut_choices': Frais.STATUT_CHOICES,
        'type_choices':   Frais.TYPE_CHOICES,
    })


@login_required
def creer_frais(request):
    # Les managers et admins ne déclarent pas de frais
    if request.user.is_admin or request.user.is_manager_role:
        messages.warning(request, 'Seuls les employés peuvent déclarer des frais.')
        return redirect('frais:liste')

    form        = FraisForm(request.user, request.POST or None)
    justif_form = JustificatifForm(request.POST or None, request.FILES or None)

    if request.method == 'POST' and form.is_valid():
        frais = form.save(commit=False)
        frais.employe = request.user
        frais.save()

        # Upload justificatif optionnel
        if request.FILES.get('fichier') and justif_form.is_valid():
            justif = justif_form.save(commit=False)
            justif.frais        = frais
            justif.nom_original = request.FILES['fichier'].name
            justif.save()
        elif request.FILES.get('fichier') and not justif_form.is_valid():
            # Frais sauvé mais justificatif invalide : on prévient
            messages.warning(request, 'Frais créé, mais le justificatif n\'a pas pu être uploadé : ' +
                             str(justif_form.errors.get('fichier', ['Erreur inconnue'])[0]))
            return redirect('frais:detail', pk=frais.pk)

        messages.success(request, 'Frais déclaré avec succès.')
        return redirect('frais:detail', pk=frais.pk)

    return render(request, 'frais/form.html', {
        'form': form, 'justif_form': justif_form, 'titre': 'Déclarer un frais'
    })


@login_required
def detail_frais(request, pk):
    frais = get_object_or_404(Frais, pk=pk)
    _check_access(request.user, frais)
    justificatifs = frais.justificatifs.all()
    justif_form   = JustificatifForm()

    if request.method == 'POST' and 'upload_justif' in request.POST:
        if not frais.peut_modifier:
            messages.warning(request, 'Ce frais ne peut plus être modifié.')
        elif request.user != frais.employe:
            messages.error(request, 'Seul l\'employé peut ajouter des justificatifs.')
        else:
            justif_form = JustificatifForm(request.POST, request.FILES)
            if justif_form.is_valid() and request.FILES.get('fichier'):
                justif = justif_form.save(commit=False)
                justif.frais        = frais
                justif.nom_original = request.FILES['fichier'].name
                justif.save()
                messages.success(request, 'Justificatif ajouté.')
                return redirect('frais:detail', pk=pk)

    return render(request, 'frais/detail.html', {
        'frais': frais, 'justificatifs': justificatifs, 'justif_form': justif_form
    })


@login_required
def modifier_frais(request, pk):
    frais = get_object_or_404(Frais, pk=pk)
    if request.user != frais.employe and not request.user.is_admin:
        messages.error(request, 'Accès refusé.')
        return redirect('frais:liste')
    if not frais.peut_modifier:
        messages.warning(request, 'Ce frais ne peut plus être modifié (statut : ' + frais.get_statut_display() + ').')
        return redirect('frais:detail', pk=pk)
    form = FraisForm(request.user, request.POST or None, instance=frais)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Frais modifié avec succès.')
        return redirect('frais:detail', pk=pk)
    return render(request, 'frais/form.html', {'form': form, 'titre': 'Modifier le frais', 'obj': frais})


@login_required
def supprimer_frais(request, pk):
    frais = get_object_or_404(Frais, pk=pk)
    if request.user != frais.employe and not request.user.is_admin:
        messages.error(request, 'Accès refusé.')
        return redirect('frais:liste')
    if not frais.peut_modifier:
        messages.warning(request, 'Ce frais ne peut plus être supprimé.')
        return redirect('frais:detail', pk=pk)
    if request.method == 'POST':
        frais.delete()
        messages.success(request, 'Frais supprimé.')
        return redirect('frais:liste')
    return render(request, 'frais/confirmer_suppression.html', {'obj': frais, 'type': 'frais'})


@login_required
def valider_frais(request, pk):
    frais = get_object_or_404(Frais, pk=pk)
    user  = request.user
    if not (user.is_admin or (user.is_manager_role and frais.employe.manager == user)):
        messages.error(request, 'Accès refusé.')
        return redirect('frais:liste')
    if frais.statut != 'en_attente':
        messages.warning(request, 'Ce frais a déjà été traité.')
        return redirect('frais:detail', pk=pk)
    form = ValidationForm(request.POST or None, instance=frais)
    if request.method == 'POST' and form.is_valid():
        f = form.save(commit=False)
        f.validé_par      = user
        f.date_validation = timezone.now()
        f.save()
        messages.success(request, f'Frais {f.get_statut_display().lower()} avec succès.')
        return redirect('frais:liste')
    return render(request, 'frais/valider.html', {'form': form, 'frais': frais})


@login_required
def marquer_rembourse(request, pk):
    if not request.user.is_admin:
        messages.error(request, 'Accès refusé.')
        return redirect('frais:liste')
    frais = get_object_or_404(Frais, pk=pk)
    if frais.statut != 'valide':
        messages.warning(request, 'Seuls les frais validés peuvent être marqués comme remboursés.')
        return redirect('frais:detail', pk=pk)
    if request.method == 'POST':
        frais.statut = 'rembourse'
        frais.save()
        messages.success(request, 'Frais marqué comme remboursé.')
    return redirect('frais:detail', pk=pk)


@login_required
def telecharger_justificatif(request, pk):
    justif = get_object_or_404(Justificatif, pk=pk)
    _check_access(request.user, justif.frais)
    try:
        return FileResponse(
            justif.fichier.open('rb'),
            as_attachment=True,
            filename=justif.nom_original
        )
    except Exception:
        raise Http404("Fichier introuvable.")


@login_required
def supprimer_justificatif(request, pk):
    justif = get_object_or_404(Justificatif, pk=pk)
    frais  = justif.frais
    if request.user != frais.employe and not request.user.is_admin:
        messages.error(request, 'Accès refusé.')
        return redirect('frais:detail', pk=frais.pk)
    if not frais.peut_modifier:
        messages.warning(request, 'Ce frais ne peut plus être modifié.')
        return redirect('frais:detail', pk=frais.pk)
    if request.method == 'POST':
        justif.fichier.delete(save=False)
        justif.delete()
        messages.success(request, 'Justificatif supprimé.')
    return redirect('frais:detail', pk=frais.pk)
