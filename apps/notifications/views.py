from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Notification

@login_required
def liste_notifications(request):
    notifs = Notification.objects.filter(destinataire__isnull=True) | \
             Notification.objects.filter(destinataire=request.user)
    notifs = notifs.order_by('-cree_le')
    return render(request, 'notifications/liste.html', {'notifs': notifs})

@login_required
def marquer_lue(request, pk):
    notif = Notification.objects.filter(pk=pk).first()
    if notif:
        notif.lue = True
        notif.save()
    return redirect('notifications:liste')

@login_required
def tout_marquer_lues(request):
    Notification.objects.filter(lue=False).update(lue=True)
    return redirect('notifications:liste')
