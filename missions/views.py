from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Mission
from .forms import MissionForm
from accounts.models import CustomUser


def _check_mission_access(user, mission):
    """Vérifie que l'utilisateur peut accéder à cette mission."""
    return (
        user.is_admin or
        user == mission.employe or
        (user.is_manager_role and mission.employe.manager == user)
    )


@login_required
def liste_missions(request):
    user = request.user
    if user.is_admin:
        missions = Mission.objects.select_related('employe').all()
    elif user.is_manager_role:
        equipe = CustomUser.objects.filter(manager=user)
        missions = Mission.objects.filter(employe__in=equipe).select_related('employe')
    else:
        missions = Mission.objects.filter(employe=user)

    statut = request.GET.get('statut', '')
    if statut:
        missions = missions.filter(statut=statut)

    return render(request, 'missions/liste.html', {
        'missions': missions,
        'statut_filtre': statut,
    })


@login_required
def creer_mission(request):
    form = MissionForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        mission = form.save(commit=False)
        mission.employe = request.user
        mission.save()
        messages.success(request, f'Mission "{mission.destination}" créée avec succès.')
        return redirect('missions:detail', pk=mission.pk)
    return render(request, 'missions/form.html', {'form': form, 'titre': 'Nouvelle mission'})


@login_required
def detail_mission(request, pk):
    mission = get_object_or_404(Mission, pk=pk)
    if not _check_mission_access(request.user, mission):
        messages.error(request, 'Accès refusé.')
        return redirect('missions:liste')
    frais = mission.frais.select_related('employe').all()
    return render(request, 'missions/detail.html', {'mission': mission, 'frais': frais})


@login_required
def modifier_mission(request, pk):
    mission = get_object_or_404(Mission, pk=pk)
    if request.user != mission.employe and not request.user.is_admin:
        messages.error(request, 'Accès refusé.')
        return redirect('missions:liste')
    form = MissionForm(request.POST or None, instance=mission)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Mission modifiée avec succès.')
        return redirect('missions:detail', pk=pk)
    return render(request, 'missions/form.html', {'form': form, 'titre': 'Modifier la mission', 'obj': mission})


@login_required
def supprimer_mission(request, pk):
    mission = get_object_or_404(Mission, pk=pk)
    if request.user != mission.employe and not request.user.is_admin:
        messages.error(request, 'Accès refusé.')
        return redirect('missions:liste')
    if mission.frais.exists():
        messages.warning(request, 'Impossible de supprimer une mission qui contient des frais.')
        return redirect('missions:detail', pk=pk)
    if request.method == 'POST':
        nom = mission.destination
        mission.delete()
        messages.success(request, f'Mission "{nom}" supprimée.')
        return redirect('missions:liste')
    return render(request, 'missions/confirmer_suppression.html', {'obj': mission, 'type': 'mission'})
