from django.urls import path
from . import views
app_name = 'stock'
urlpatterns = [
    path('', views.tableau_stock, name='tableau'),
    path('ajuster/', views.ajuster_stock, name='ajuster'),
    path('historique/', views.historique, name='historique'),
    path('inventaire/creer/', views.creer_inventaire, name='creer_inventaire'),
    path('inventaire/<int:pk>/', views.inventaire_detail, name='inventaire_detail'),
]
