from django import forms
from .models import CommandeAchat, LigneAchat
from apps.fournisseurs.models import Fournisseur
from apps.produits.models import Produit


class CommandeAchatForm(forms.ModelForm):
    class Meta:
        model = CommandeAchat
        fields = ['fournisseur', 'date_livraison_prevue', 'statut', 'notes']
        widgets = {
            'date_livraison_prevue': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class LigneAchatForm(forms.ModelForm):

    produit = forms.ModelChoiceField(
        queryset=Produit.objects.filter(actif=True).order_by('nom'),
        required=False,
        empty_label="— Choisir un produit —",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = LigneAchat
        fields = ['produit', 'quantite', 'prix_unitaire']
        widgets = {
            'quantite': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'prix_unitaire': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }


LigneAchatFormSet = forms.inlineformset_factory(
    CommandeAchat, LigneAchat, form=LigneAchatForm,
    extra=3, can_delete=True, min_num=1, validate_min=True
)
