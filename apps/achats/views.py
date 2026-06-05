from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .models import CommandeAchat
from .forms import CommandeAchatForm, LigneAchatFormSet

@login_required
def liste_achats(request):
    commandes = CommandeAchat.objects.select_related('fournisseur').all()
    return render(request, 'achats/liste.html', {'commandes': commandes})

@login_required
def nouvelle_commande(request):
    if request.method == 'POST':
        form = CommandeAchatForm(request.POST)
        formset = LigneAchatFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                cmd = form.save(commit=False)
                cmd.cree_par = request.user
                cmd.save()
                formset.instance = cmd
                formset.save()
                cmd.calculer_total()
                messages.success(request, f'Commande {cmd.numero} créée.')
                return redirect('achats:detail', pk=cmd.pk)
    else:
        form = CommandeAchatForm()
        formset = LigneAchatFormSet()
    return render(request, 'achats/form.html', {'form': form, 'formset': formset})

@login_required
def detail_commande(request, pk):
    cmd = get_object_or_404(CommandeAchat, pk=pk)
    return render(request, 'achats/detail.html', {'cmd': cmd})

@login_required
def recevoir_commande(request, pk):
    cmd = get_object_or_404(CommandeAchat, pk=pk)
    if cmd.statut == 'envoyee':
        with transaction.atomic():
            for ligne in cmd.lignes.all():
                ligne.produit.stock_actuel += ligne.quantite
                ligne.produit.prix_achat = ligne.prix_unitaire
                ligne.produit.save()
            cmd.statut = 'recue'
            cmd.save()
        messages.success(request, 'Commande reçue, stock mis à jour.')
    return redirect('achats:detail', pk=pk)
