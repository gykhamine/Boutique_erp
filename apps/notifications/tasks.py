"""
Tâches Celery pour les alertes automatiques.
Lancer le worker: celery -A boutique_erp worker -l info
Lancer le scheduler: celery -A boutique_erp beat -l info
"""
from celery import shared_task
from django.utils import timezone

@shared_task
def verifier_stocks_faibles():
    """Tâche Celery: vérifier et notifier les stocks faibles."""
    from apps.produits.models import Produit
    from .models import Notification

    produits_rupture = Produit.objects.filter(actif=True, stock_actuel__lte=0)
    produits_alerte = Produit.objects.filter(actif=True, stock_actuel__gt=0).filter(
        stock_actuel__lte=models.F('stock_minimum') if False else 5
    )

    for prod in produits_rupture:
        Notification.objects.get_or_create(
            titre=f"RUPTURE: {prod.nom}",
            lue=False,
            defaults={'message': f"Le produit {prod.nom} est en rupture de stock.", 'type_notif': 'erreur'}
        )
    return f"{produits_rupture.count()} ruptures détectées."

@shared_task
def rapport_journalier():
    """Génère un résumé journalier des ventes."""
    from apps.ventes.models import Vente
    from .models import Notification
    from django.db.models import Sum

    today = timezone.now().date()
    ventes = Vente.objects.filter(date__date=today, statut__in=['confirmee','livree'])
    total = ventes.aggregate(t=Sum('total'))['t'] or 0

    Notification.objects.create(
        titre=f"Rapport du {today.strftime('%d/%m/%Y')}",
        message=f"{ventes.count()} ventes aujourd'hui pour un total de {int(total):,} FCFA.".replace(',', ' '),
        type_notif='info'
    )
    return "Rapport généré."
