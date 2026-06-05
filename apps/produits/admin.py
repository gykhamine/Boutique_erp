from django.contrib import admin
from .models import Produit, Categorie

@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ['reference', 'nom', 'categorie', 'prix_vente', 'stock_actuel', 'actif']
    list_filter = ['categorie', 'actif']
    search_fields = ['reference', 'nom']

@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ['nom']
