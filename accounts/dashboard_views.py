from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from frais.models import Frais
from missions.models import Mission
from accounts.models import CustomUser


@login_required
def dashboard(request):
    user = request.user
    ctx = {}

    if user.is_admin:
        ctx['total_users']      = CustomUser.objects.filter(is_active=True).count()
        ctx['total_missions']   = Mission.objects.count()
        ctx['frais_en_attente'] = Frais.objects.filter(statut='en_attente').count()
        ctx['total_rembourse']  = Frais.objects.filter(statut='rembourse').aggregate(t=Sum('montant'))['t'] or 0
        ctx['frais_recents']    = Frais.objects.select_related('employe', 'mission').order_by('-date_creation')[:10]
        ctx['missions_recentes'] = Mission.objects.select_related('employe').order_by('-date_creation')[:5]
        ctx['stats_par_type']   = (
            Frais.objects.values('type_frais')
            .annotate(total=Sum('montant'), nb=Count('id'))
            .order_by('-total')
        )

    elif user.is_manager_role:
        equipe = CustomUser.objects.filter(manager=user)
        qs = Frais.objects.filter(employe__in=equipe)
        ctx['nb_employes']      = equipe.count()
        ctx['frais_en_attente'] = qs.filter(statut='en_attente').count()
        ctx['frais_valides']    = qs.filter(statut='valide').count()
        ctx['total_rembourse']  = qs.filter(statut='rembourse').aggregate(t=Sum('montant'))['t'] or 0
        ctx['frais_recents']    = qs.select_related('employe', 'mission').order_by('-date_creation')[:10]
        ctx['equipe']           = equipe
        ctx['missions_equipe']  = Mission.objects.filter(employe__in=equipe).select_related('employe').order_by('-date_creation')[:5]

    else:
        # Employé
        mes_frais    = Frais.objects.filter(employe=user)
        mes_missions = Mission.objects.filter(employe=user)
        ctx['mes_missions']     = mes_missions.count()
        ctx['frais_en_attente'] = mes_frais.filter(statut='en_attente').count()
        ctx['frais_valides']    = mes_frais.filter(statut='valide').count()
        ctx['total_rembourse']  = mes_frais.filter(statut='rembourse').aggregate(t=Sum('montant'))['t'] or 0
        ctx['frais_recents']    = mes_frais.select_related('mission').order_by('-date_creation')[:5]
        ctx['missions_recentes'] = mes_missions.order_by('-date_creation')[:5]

    return render(request, 'base/dashboard.html', ctx)
