from django.contrib import admin
from .models import Vente, LigneVente

class LigneInline(admin.TabularInline):
    model = LigneVente
    extra = 0

@admin.register(Vente)
class VenteAdmin(admin.ModelAdmin):
    list_display = ['numero', 'client', 'date', 'total', 'statut']
    inlines = [LigneInline]
