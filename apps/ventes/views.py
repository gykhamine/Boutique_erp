from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from .models import Vente, LigneVente
from .forms import VenteForm, LigneVenteFormSet
from apps.produits.models import Produit
from apps.notifications.models import Notification


@login_required
def liste_ventes(request):
    ventes = Vente.objects.select_related('client', 'cree_par').all()
    statut = request.GET.get('statut', '')
    if statut:
        ventes = ventes.filter(statut=statut)
    return render(request, 'ventes/liste.html', {'ventes': ventes, 'statut': statut})


@login_required
def nouvelle_vente(request):
    if request.method == 'POST':
        form = VenteForm(request.POST)
        formset = LigneVenteFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                vente = form.save(commit=False)
                vente.cree_par = request.user
                vente.save()
                formset.instance = vente
                lignes = formset.save()
                # Déduire le stock
                for ligne in lignes:
                    prod = ligne.produit
                    prod.stock_actuel -= ligne.quantite
                    prod.save()
                    if prod.en_rupture:
                        Notification.objects.create(
                            titre=f"Stock faible: {prod.nom}",
                            message=f"Le stock de {prod.nom} est passé à {prod.stock_actuel} unités.",
                            type_notif='alerte'
                        )
                vente.calculer_totaux()
                messages.success(request, f'Vente {vente.numero} créée.')
                return redirect('ventes:detail', pk=vente.pk)
    else:
        form = VenteForm()
        formset = LigneVenteFormSet()
    produits = Produit.objects.filter(actif=True, stock_actuel__gt=0)
    return render(request, 'ventes/form.html', {'form': form, 'formset': formset, 'produits': produits})


@login_required
def detail_vente(request, pk):
    vente = get_object_or_404(Vente, pk=pk)
    return render(request, 'ventes/detail.html', {'vente': vente})


@login_required
def annuler_vente(request, pk):
    vente = get_object_or_404(Vente, pk=pk)
    if vente.statut not in ['annulee', 'livree']:
        with transaction.atomic():
            for ligne in vente.lignes.all():
                ligne.produit.stock_actuel += ligne.quantite
                ligne.produit.save()
            vente.statut = 'annulee'
            vente.save()
        messages.success(request, 'Vente annulée, stock restauré.')
    return redirect('ventes:detail', pk=pk)


@login_required
def api_prix_produit(request, pk):
    produit = get_object_or_404(Produit, pk=pk)
    return JsonResponse({'prix': float(produit.prix_vente), 'stock': produit.stock_actuel, 'nom': produit.nom})
