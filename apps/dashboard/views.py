from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta

from apps.ventes.models import Vente
from apps.produits.models import Produit
from apps.clients.models import Client
from apps.taches.models import Tache
from apps.notifications.models import Notification


@login_required
def index(request):

    today = timezone.now().date()
    debut_mois = today.replace(day=1)

    ventes_jour = Vente.objects.filter(
        date__date=today,
        statut__in=['confirmee', 'livree']
    )

    ventes_mois = Vente.objects.filter(
        date__date__gte=debut_mois,
        statut__in=['confirmee', 'livree']
    )

    ca_jour = ventes_jour.aggregate(t=Sum('total'))['t'] or 0
    ca_mois = ventes_mois.aggregate(t=Sum('total'))['t'] or 0

    nb_ventes_jour = ventes_jour.count()

    produits = Produit.objects.filter(actif=True)

    produits_rupture = produits.filter(stock_actuel__lte=0)

    # ⚠️ SAFE: si en_rupture est une property seulement
    produits_alerte = [
        p for p in produits
        if hasattr(p, "en_rupture") and p.en_rupture
    ]

    taches_urgentes = Tache.objects.filter(
        statut__in=['todo', 'en_cours'],
        priorite='urgente'
    )

    # ⚠️ CHANGE ICI SI TON MODEL N'A PAS "lue"
    notifs = Notification.objects.filter(lue=False).count()

    ventes_7j = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        total = Vente.objects.filter(
            date__date=d,
            statut__in=['confirmee', 'livree']
        ).aggregate(t=Sum('total'))['t'] or 0

        ventes_7j.append({
            'date': d.strftime('%d/%m'),
            'total': int(total)
        })

    ctx = {
        'ca_jour': ca_jour,
        'ca_mois': ca_mois,
        'nb_ventes_jour': nb_ventes_jour,
        'nb_clients': Client.objects.filter(actif=True).count(),
        'nb_produits': produits.count(),
        'produits_rupture': produits_rupture[:5],
        'nb_ruptures': produits_rupture.count(),
        'taches_urgentes': taches_urgentes[:5],
        'notifs_count': notifs,
        'ventes_7j': ventes_7j,
        'ventes_recentes': Vente.objects.select_related('client').order_by('-date')[:8],
    }

    return render(request, 'dashboard/index.html', ctx)
