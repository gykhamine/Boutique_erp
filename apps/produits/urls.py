from django.urls import path
from . import views

app_name = 'produits'

urlpatterns = [
    path('', views.liste_produits, name='liste'),
    path('ajouter/', views.ajouter_produit, name='ajouter'),
    path('<int:pk>/', views.detail_produit, name='detail'),
    path('<int:pk>/modifier/', views.modifier_produit, name='modifier'),
    path('<int:pk>/supprimer/', views.supprimer_produit, name='supprimer'),
    path('<int:pk>/qr/', views.regenerer_qr, name='qr'),
    path('exporter/', views.exporter_excel, name='exporter'),
    path('categories/', views.liste_categories, name='categories'),
    path('categories/ajouter/', views.ajouter_categorie, name='ajouter_categorie'),
]
