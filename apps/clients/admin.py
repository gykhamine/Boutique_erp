from django.contrib import admin
from .models import Client

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['code', 'nom', 'type_client', 'telephone', 'ville']
    search_fields = ['nom', 'code']
