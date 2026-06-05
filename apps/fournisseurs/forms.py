from django import forms
from .models import Fournisseur


class FournisseurForm(forms.ModelForm):
    class Meta:
        model = Fournisseur
        exclude = ['code', 'cree_le']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du fournisseur'}),
            'contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du contact'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 06-123-4567'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@exemple.com'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Adresse complète'}),
            'pays': forms.TextInput(attrs={'class': 'form-control'}),
            'delai_livraison': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
