from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Tache
from .forms import TacheForm

@login_required
def kanban(request):
    todo = Tache.objects.filter(statut='todo')
    en_cours = Tache.objects.filter(statut='en_cours')
    fait = Tache.objects.filter(statut='fait')
    return render(request, 'taches/kanban.html', {'todo': todo, 'en_cours': en_cours, 'fait': fait})

@login_required
def ajouter_tache(request):
    if request.method == 'POST':
        form = TacheForm(request.POST)
        if form.is_valid():
            t = form.save(commit=False)
            t.cree_par = request.user
            t.save()
            messages.success(request, 'Tâche créée.')
            return redirect('taches:kanban')
    else:
        form = TacheForm()
    return render(request, 'taches/form.html', {'form': form})

@login_required
def changer_statut(request, pk):
    tache = get_object_or_404(Tache, pk=pk)
    nouveau = request.POST.get('statut')
    if nouveau in dict(Tache.STATUTS):
        tache.statut = nouveau
        tache.save()
    return redirect('taches:kanban')
