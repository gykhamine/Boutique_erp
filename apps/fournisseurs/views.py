from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Fournisseur
from .forms import FournisseurForm

@login_required
def liste_fournisseurs(request):
    fournisseurs = Fournisseur.objects.filter(actif=True)
    return render(request, 'fournisseurs/liste.html', {'fournisseurs': fournisseurs})

@login_required
def ajouter_fournisseur(request):
    if request.method == 'POST':
        form = FournisseurForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fournisseur ajouté.')
            return redirect('fournisseurs:liste')
    else:
        form = FournisseurForm()
    return render(request, 'fournisseurs/form.html', {'form': form, 'titre': 'Nouveau fournisseur'})

@login_required
def modifier_fournisseur(request, pk):
    f = get_object_or_404(Fournisseur, pk=pk)
    if request.method == 'POST':
        form = FournisseurForm(request.POST, instance=f)
        if form.is_valid():
            form.save()
            messages.success(request, 'Modifié.')
            return redirect('fournisseurs:liste')
    else:
        form = FournisseurForm(instance=f)
    return render(request, 'fournisseurs/form.html', {'form': form, 'titre': 'Modifier', 'obj': f})
