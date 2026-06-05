from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django import forms as dforms
from .models import SessionCaisse, TransactionCaisse

class OuvertureCaisseForm(dforms.Form):
    fond_ouverture = dforms.DecimalField(max_digits=12, decimal_places=0, widget=dforms.NumberInput(attrs={'class':'form-control'}))

class TransactionForm(dforms.Form):
    type_transaction = dforms.ChoiceField(choices=[('entree','Entrée'),('sortie','Sortie')], widget=dforms.Select(attrs={'class':'form-select'}))
    montant = dforms.DecimalField(max_digits=12, decimal_places=0, widget=dforms.NumberInput(attrs={'class':'form-control'}))
    motif = dforms.CharField(max_length=200, widget=dforms.TextInput(attrs={'class':'form-control'}))

class FermetureCaisseForm(dforms.Form):
    fond_fermeture = dforms.DecimalField(max_digits=12, decimal_places=0, widget=dforms.NumberInput(attrs={'class':'form-control'}))
    notes = dforms.CharField(required=False, widget=dforms.Textarea(attrs={'class':'form-control','rows':3}))

@login_required
def caisse(request):
    session = SessionCaisse.objects.filter(caissier=request.user, fermeture__isnull=True).first()
    form = OuvertureCaisseForm()
    if request.method == 'POST' and 'ouvrir' in request.POST:
        form = OuvertureCaisseForm(request.POST)
        if form.is_valid():
            SessionCaisse.objects.create(
                fond_ouverture=form.cleaned_data['fond_ouverture'],
                caissier=request.user
            )
            messages.success(request, 'Caisse ouverte.')
            return redirect('caisse:caisse')
    trans_form = TransactionForm()
    return render(request, 'caisse/caisse.html', {'session': session, 'form': form, 'trans_form': trans_form})

@login_required
def ajouter_transaction(request):
    session = SessionCaisse.objects.filter(caissier=request.user, fermeture__isnull=True).first()
    if not session:
        messages.error(request, 'Aucune session ouverte.')
        return redirect('caisse:caisse')
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            TransactionCaisse.objects.create(session=session, **form.cleaned_data)
            messages.success(request, 'Transaction enregistrée.')
    return redirect('caisse:caisse')

@login_required
def fermer_caisse(request):
    session = SessionCaisse.objects.filter(caissier=request.user, fermeture__isnull=True).first()
    if request.method == 'POST' and session:
        form = FermetureCaisseForm(request.POST)
        if form.is_valid():
            session.fond_fermeture = form.cleaned_data['fond_fermeture']
            session.notes = form.cleaned_data['notes']
            session.fermeture = timezone.now()
            session.save()
            messages.success(request, 'Caisse fermée.')
    return redirect('caisse:caisse')

@login_required
def historique_caisse(request):
    sessions = SessionCaisse.objects.filter(caissier=request.user).order_by('-ouverture')
    return render(request, 'caisse/historique.html', {'sessions': sessions})
