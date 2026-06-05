from django.contrib import admin
from .models import SessionCaisse, TransactionCaisse

class TransactionInline(admin.TabularInline):
    model = TransactionCaisse
    extra = 0

@admin.register(SessionCaisse)
class SessionAdmin(admin.ModelAdmin):
    list_display = ['caissier', 'ouverture', 'fermeture', 'fond_ouverture']
    inlines = [TransactionInline]
