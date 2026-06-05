from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Employe, Conge
from .forms import EmployeForm, CongeForm

@login_required
def liste_employes(request):
    employes = Employe.objects.filter(actif=True)
    return render(request, 'employes/liste.html', {'employes': employes})

@login_required
def ajouter_employe(request):
    if request.method == 'POST':
        form = EmployeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Employé ajouté.')
            return redirect('employes:liste')
    else:
        form = EmployeForm()
    return render(request, 'employes/form.html', {'form': form, 'titre': 'Nouvel employé'})

@login_required
def detail_employe(request, pk):
    emp = get_object_or_404(Employe, pk=pk)
    conges = emp.conges.order_by('-date_debut')
    return render(request, 'employes/detail.html', {'emp': emp, 'conges': conges})

@login_required
def demander_conge(request):
    if request.method == 'POST':
        form = CongeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Demande de congé enregistrée.')
            return redirect('employes:liste')
    else:
        form = CongeForm()
    return render(request, 'employes/conge.html', {'form': form})
