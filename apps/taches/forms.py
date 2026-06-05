from django import forms
from django.contrib.auth.models import User
from .models import Tache


class TacheForm(forms.ModelForm):

    assigne_a = forms.ModelChoiceField(
        queryset=User.objects.all().order_by('username'),
        required=False,
        empty_label="— Non assignée —",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    priorite = forms.ChoiceField(
        choices=Tache.PRIORITES,
        initial='normale',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    statut = forms.ChoiceField(
        choices=Tache.STATUTS,
        initial='todo',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Tache
        fields = ['titre', 'description', 'assigne_a', 'priorite', 'statut', 'echeance']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre...'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'echeance': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
