from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse, Http404
from .models import Facture
from apps.ventes.models import Vente
from .utils import generer_pdf_facture

@login_required
def liste_factures(request):
    factures = Facture.objects.select_related('vente__client').all()
    return render(request, 'factures/liste.html', {'factures': factures})

@login_required
def creer_facture(request, vente_pk):
    vente = get_object_or_404(Vente, pk=vente_pk)
    if hasattr(vente, 'facture'):
        return redirect('factures:detail', pk=vente.facture.pk)
    facture = Facture.objects.create(vente=vente)
    generer_pdf_facture(facture)
    facture.statut = 'emise'
    facture.save()
    messages.success(request, f'Facture {facture.numero} générée.')
    return redirect('factures:detail', pk=facture.pk)

@login_required
def detail_facture(request, pk):
    facture = get_object_or_404(Facture, pk=pk)
    return render(request, 'factures/detail.html', {'facture': facture})

@login_required
def telecharger_pdf(request, pk):
    facture = get_object_or_404(Facture, pk=pk)
    if not facture.fichier_pdf:
        generer_pdf_facture(facture)
    try:
        return FileResponse(facture.fichier_pdf.open('rb'), content_type='application/pdf',
                            as_attachment=True, filename=f"facture_{facture.numero}.pdf")
    except Exception:
        raise Http404

@login_required
def regenerer_pdf(request, pk):
    facture = get_object_or_404(Facture, pk=pk)
    if facture.fichier_pdf:
        facture.fichier_pdf.delete(save=False)
    generer_pdf_facture(facture)
    messages.success(request, 'PDF régénéré.')
    return redirect('factures:detail', pk=pk)
