from django import forms
from .models import Vente, LigneVente
from apps.produits.models import Produit
from apps.clients.models import Client


class VenteForm(forms.ModelForm):

    client = forms.ModelChoiceField(
        queryset=Client.objects.filter(actif=True).order_by('nom'),
        required=False,
        empty_label="— Client comptant —",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    mode_paiement = forms.ChoiceField(
        choices=Vente.MODES_PAIEMENT,
        initial='especes',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    statut = forms.ChoiceField(
        choices=Vente.STATUTS,
        initial='brouillon',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Vente
        fields = ['client', 'mode_paiement', 'remise', 'notes', 'statut']
        widgets = {
            'remise': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5', 'min': 0, 'max': 100}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Remarques...'}),
        }


class LigneVenteForm(forms.ModelForm):

    produit = forms.ModelChoiceField(
        queryset=Produit.objects.filter(actif=True, stock_actuel__gt=0).order_by('nom'),
        required=False,
        empty_label="— Choisir un produit —",
        widget=forms.Select(attrs={'class': 'form-select produit-select'})
    )

    class Meta:
        model = LigneVente
        fields = ['produit', 'quantite', 'prix_unitaire', 'remise_ligne']
        widgets = {
            'quantite': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'prix_unitaire': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'remise_ligne': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100, 'value': 0}),
        }


LigneVenteFormSet = forms.inlineformset_factory(
    Vente, LigneVente, form=LigneVenteForm,
    extra=3, can_delete=True, min_num=1, validate_min=True
)
