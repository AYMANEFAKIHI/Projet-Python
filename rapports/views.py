from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count
from django.http import HttpResponse
from django.utils import timezone
import csv
from frais.models import Frais
from accounts.models import CustomUser
from missions.models import Mission


@login_required
def tableau_de_bord_rapports(request):
    user = request.user
    if not (user.is_admin or user.is_manager_role):
        messages.error(request, 'Accès réservé aux managers et administrateurs.')
        return redirect('dashboard:index')

    if user.is_admin:
        qs = Frais.objects.select_related('employe', 'mission').all()
    else:
        equipe = CustomUser.objects.filter(manager=user)
        qs = Frais.objects.filter(employe__in=equipe).select_related('employe', 'mission')

    # ── Filtres ──────────────────────────────────────────────────────────────
    employe_id = request.GET.get('employe', '')
    periode    = request.GET.get('periode', '')
    type_frais = request.GET.get('type', '')

    if employe_id:
        qs = qs.filter(employe_id=employe_id)
    if type_frais:
        qs = qs.filter(type_frais=type_frais)
    if periode == 'mois':
        now = timezone.now()
        qs  = qs.filter(date_frais__year=now.year, date_frais__month=now.month)
    elif periode == 'annee':
        qs = qs.filter(date_frais__year=timezone.now().year)

    stats_statut = qs.values('statut').annotate(total=Sum('montant'), nb=Count('id'))
    stats_type   = qs.values('type_frais').annotate(total=Sum('montant'), nb=Count('id')).order_by('-total')
    total_global = qs.aggregate(t=Sum('montant'))['t'] or 0

    # Stats par employé (pour admin/manager)
    stats_employe = (
        qs.values('employe__first_name', 'employe__last_name', 'employe__username')
        .annotate(total=Sum('montant'), nb=Count('id'))
        .order_by('-total')[:10]
    )

    if user.is_admin:
        employes = CustomUser.objects.filter(role='employe', is_active=True)
    else:
        employes = CustomUser.objects.filter(manager=user, is_active=True)

    return render(request, 'rapports/rapport.html', {
        'stats_statut':  stats_statut,
        'stats_type':    stats_type,
        'stats_employe': stats_employe,
        'total_global':  total_global,
        'employes':      employes,
        'employe_id':    employe_id,
        'periode':       periode,
        'type_filtre':   type_frais,
        'nb_frais':      qs.count(),
        'type_choices':  Frais.TYPE_CHOICES,
    })


@login_required
def export_csv(request):
    user = request.user
    if not (user.is_admin or user.is_manager_role):
        messages.error(request, 'Accès refusé.')
        return redirect('dashboard:index')

    if user.is_admin:
        qs = Frais.objects.select_related('employe', 'mission').all()
    else:
        equipe = CustomUser.objects.filter(manager=user)
        qs = Frais.objects.filter(employe__in=equipe).select_related('employe', 'mission')

    # Appliquer les mêmes filtres que la vue rapport
    employe_id = request.GET.get('employe', '')
    periode    = request.GET.get('periode', '')
    type_frais = request.GET.get('type', '')
    if employe_id:
        qs = qs.filter(employe_id=employe_id)
    if type_frais:
        qs = qs.filter(type_frais=type_frais)
    if periode == 'mois':
        now = timezone.now()
        qs  = qs.filter(date_frais__year=now.year, date_frais__month=now.month)
    elif periode == 'annee':
        qs = qs.filter(date_frais__year=timezone.now().year)

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="rapport_frais.csv"'
    response.write('\ufeff')  # BOM pour Excel

    writer = csv.writer(response, delimiter=';')
    writer.writerow(['Employé', 'Département', 'Mission', 'Destination', 'Type', 'Montant (MAD)', 'Date', 'Statut', 'Validé par', 'Commentaire'])
    for f in qs.order_by('-date_frais'):
        writer.writerow([
            f.employe.get_full_name() or f.employe.username,
            f.employe.departement or '—',
            str(f.mission),
            f.mission.destination,
            f.get_type_frais_display(),
            str(f.montant),
            f.date_frais.strftime('%d/%m/%Y'),
            f.get_statut_display(),
            f.valide_par.get_full_name() if f.valide_par else '—',
            f.commentaire_manager or '—',
        ])
    return response
