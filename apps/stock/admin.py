from django.contrib import admin
from .models import MouvementStock, Inventaire

@admin.register(MouvementStock)
class MouvementAdmin(admin.ModelAdmin):
    list_display = ['produit', 'type_mouvement', 'quantite', 'stock_avant', 'stock_apres', 'date']

@admin.register(Inventaire)
class InventaireAdmin(admin.ModelAdmin):
    list_display = ['reference', 'statut', 'date']
