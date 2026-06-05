from django import forms
from django.contrib.auth.models import User
from .models import Employe, Conge


class EmployeForm(forms.ModelForm):

    user = forms.ModelChoiceField(
        queryset=User.objects.all().order_by('username'),
        required=False,
        empty_label="— Aucun compte utilisateur —",
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text="Lier à un compte Django (optionnel)"
    )

    poste = forms.ChoiceField(
        choices=Employe.POSTES,
        initial='vendeur',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Employe
        exclude = ['matricule']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'salaire': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'date_embauche': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
        }


class CongeForm(forms.ModelForm):

    employe = forms.ModelChoiceField(
        queryset=Employe.objects.filter(actif=True).order_by('nom'),
        empty_label="— Sélectionner un employé —",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    type_conge = forms.ChoiceField(
        choices=Conge.TYPES,
        initial='annuel',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Conge
        fields = ['employe', 'type_conge', 'date_debut', 'date_fin', 'motif']
        widgets = {
            'date_debut': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'motif': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
