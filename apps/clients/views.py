from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Client
from .forms import ClientForm


@login_required
def liste_clients(request):
    q = request.GET.get('q', '')
    clients = Client.objects.filter(actif=True)
    if q:
        clients = clients.filter(Q(nom__icontains=q) | Q(telephone__icontains=q) | Q(code__icontains=q))
    return render(request, 'clients/liste.html', {'clients': clients, 'q': q})


@login_required
def ajouter_client(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Client ajouté.')
            return redirect('clients:liste')
    else:
        form = ClientForm()
    return render(request, 'clients/form.html', {'form': form, 'titre': 'Nouveau client'})


@login_required
def modifier_client(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, 'Client modifié.')
            return redirect('clients:liste')
    else:
        form = ClientForm(instance=client)
    return render(request, 'clients/form.html', {'form': form, 'titre': 'Modifier client', 'client': client})


@login_required
def detail_client(request, pk):
    client = get_object_or_404(Client, pk=pk)
    ventes = client.ventes.order_by('-date')[:20]
    return render(request, 'clients/detail.html', {'client': client, 'ventes': ventes})
