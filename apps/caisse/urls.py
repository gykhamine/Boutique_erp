from django.urls import path
from . import views
app_name = 'caisse'
urlpatterns = [
    path('', views.caisse, name='caisse'),
    path('transaction/', views.ajouter_transaction, name='transaction'),
    path('fermer/', views.fermer_caisse, name='fermer'),
    path('historique/', views.historique_caisse, name='historique'),
]
