from django.contrib import admin
from .models import CommandeAchat, LigneAchat

class LigneInline(admin.TabularInline):
    model = LigneAchat
    extra = 0

@admin.register(CommandeAchat)
class CommandeAchatAdmin(admin.ModelAdmin):
    list_display = ['numero', 'fournisseur', 'date', 'total', 'statut']
    inlines = [LigneInline]
