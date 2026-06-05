from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django import forms as dforms
from .models import Parametre

class ParametreForm(dforms.Form):
    nom_boutique = dforms.CharField(max_length=200, widget=dforms.TextInput(attrs={'class':'form-control'}), label='Nom de la boutique')
    adresse = dforms.CharField(max_length=300, required=False, widget=dforms.TextInput(attrs={'class':'form-control'}))
    telephone = dforms.CharField(max_length=30, required=False, widget=dforms.TextInput(attrs={'class':'form-control'}))
    email = dforms.EmailField(required=False, widget=dforms.EmailInput(attrs={'class':'form-control'}))
    tva_defaut = dforms.DecimalField(max_digits=5, decimal_places=2, initial=18, widget=dforms.NumberInput(attrs={'class':'form-control'}))

@login_required
def parametres(request):
    if request.method == 'POST':
        form = ParametreForm(request.POST)
        if form.is_valid():
            for cle, valeur in form.cleaned_data.items():
                Parametre.objects.update_or_create(cle=cle, defaults={'valeur': str(valeur)})
            messages.success(request, 'Paramètres enregistrés.')
            return redirect('parametres:index')
    else:
        initial = {p.cle: p.valeur for p in Parametre.objects.all()}
        form = ParametreForm(initial=initial)
    users = User.objects.all()
    return render(request, 'parametres/index.html', {'form': form, 'users': users})

@login_required
def creer_utilisateur(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email', '')
        if username and password:
            user = User.objects.create_user(username=username, password=password, email=email)
            messages.success(request, f'Utilisateur {username} créé.')
        return redirect('parametres:index')
