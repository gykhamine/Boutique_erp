from django.contrib import admin
from .models import Parametre

@admin.register(Parametre)
class ParametreAdmin(admin.ModelAdmin):
    list_display = ['cle', 'valeur', 'modifie_le']
