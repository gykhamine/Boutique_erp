from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django import forms as dforms
from .models import MouvementStock, Inventaire, LigneInventaire
from apps.produits.models import Produit

class AjustementForm(dforms.Form):
    produit = dforms.ModelChoiceField(queryset=Produit.objects.filter(actif=True), widget=dforms.Select(attrs={'class':'form-select'}))
    type_mouvement = dforms.ChoiceField(choices=[('entree','Entrée'),('sortie','Sortie'),('ajustement','Ajustement')], widget=dforms.Select(attrs={'class':'form-select'}))
    quantite = dforms.IntegerField(min_value=1, widget=dforms.NumberInput(attrs={'class':'form-control'}))
    motif = dforms.CharField(max_length=200, widget=dforms.TextInput(attrs={'class':'form-control'}))

@login_required
def tableau_stock(request):
    produits = Produit.objects.filter(actif=True).order_by('stock_actuel')
    ruptures = produits.filter(stock_actuel__lte=dforms.forms.Field().initial or 0)
    alertes = [p for p in produits if p.en_rupture]
    return render(request, 'stock/tableau.html', {'produits': produits, 'alertes': alertes})

@login_required
def ajuster_stock(request):
    if request.method == 'POST':
        form = AjustementForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                prod = form.cleaned_data['produit']
                qte = form.cleaned_data['quantite']
                typ = form.cleaned_data['type_mouvement']
                avant = prod.stock_actuel
                if typ == 'entree':
                    prod.stock_actuel += qte
                elif typ == 'sortie':
                    prod.stock_actuel = max(0, prod.stock_actuel - qte)
                else:
                    prod.stock_actuel = qte
                prod.save()
                MouvementStock.objects.create(
                    produit=prod, type_mouvement=typ, quantite=qte,
                    stock_avant=avant, stock_apres=prod.stock_actuel,
                    motif=form.cleaned_data['motif'], cree_par=request.user
                )
                messages.success(request, 'Stock ajusté.')
                return redirect('stock:tableau')
    else:
        form = AjustementForm()
    return render(request, 'stock/ajustement.html', {'form': form})

@login_required
def historique(request):
    mouvements = MouvementStock.objects.select_related('produit','cree_par').all()[:100]
    return render(request, 'stock/historique.html', {'mouvements': mouvements})

@login_required
def creer_inventaire(request):
    with transaction.atomic():
        inv = Inventaire.objects.create(cree_par=request.user)
        for prod in Produit.objects.filter(actif=True):
            LigneInventaire.objects.create(inventaire=inv, produit=prod, stock_theorique=prod.stock_actuel)
        messages.success(request, f'Inventaire {inv.reference} créé.')
        return redirect('stock:inventaire_detail', pk=inv.pk)

@login_required
def inventaire_detail(request, pk):
    inv = get_object_or_404(Inventaire, pk=pk)
    if request.method == 'POST' and inv.statut == 'en_cours':
        with transaction.atomic():
            for ligne in inv.lignes.all():
                reel = int(request.POST.get(f'reel_{ligne.pk}', ligne.stock_theorique))
                ligne.stock_reel = reel
                ligne.save()
                if reel != ligne.stock_theorique:
                    avant = ligne.produit.stock_actuel
                    ligne.produit.stock_actuel = reel
                    ligne.produit.save()
                    MouvementStock.objects.create(
                        produit=ligne.produit, type_mouvement='ajustement',
                        quantite=abs(reel-avant), stock_avant=avant, stock_apres=reel,
                        motif=f"Inventaire {inv.reference}", cree_par=request.user
                    )
            inv.statut = 'valide'
            inv.save()
            messages.success(request, 'Inventaire validé.')
    return render(request, 'stock/inventaire_detail.html', {'inv': inv})
