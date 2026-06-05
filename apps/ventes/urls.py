from django.urls import path
from . import views
app_name = 'ventes'
urlpatterns = [
    path('', views.liste_ventes, name='liste'),
    path('nouvelle/', views.nouvelle_vente, name='nouvelle'),
    path('<int:pk>/', views.detail_vente, name='detail'),
    path('<int:pk>/annuler/', views.annuler_vente, name='annuler'),
    path('api/produit/<int:pk>/', views.api_prix_produit, name='api_produit'),
]
