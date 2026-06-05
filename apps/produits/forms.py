from django import forms
from .models import Produit, Categorie


class ProduitForm(forms.ModelForm):

    categorie = forms.ModelChoiceField(
        queryset=Categorie.objects.all().order_by('nom'),
        required=False,
        empty_label="— Sélectionner une catégorie —",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    unite = forms.ChoiceField(
        choices=Produit.UNITES,
        initial='pce',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Produit
        exclude = ['qr_code', 'cree_le', 'modifie_le']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Sac de riz 25kg'}),
            'reference': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: SAC001'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'prix_achat': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'prix_vente': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'tva': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100, 'step': '0.5'}),
            'stock_actuel': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'stock_minimum': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CategorieForm(forms.ModelForm):
    class Meta:
        model = Categorie
        fields = '__all__'
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Alimentaire'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
