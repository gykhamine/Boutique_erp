from .models import Notification

def notifications_non_lues(request):
    if request.user.is_authenticated:
        notifs = Notification.objects.filter(lue=False).filter(
            destinataire__isnull=True
        ) | Notification.objects.filter(lue=False, destinataire=request.user)
        return {'notifications_count': notifs.count(), 'notifications_recentes': notifs[:5]}
    return {'notifications_count': 0, 'notifications_recentes': []}
