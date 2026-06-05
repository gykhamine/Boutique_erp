from django.urls import path
from . import views
app_name = 'achats'
urlpatterns = [
    path('', views.liste_achats, name='liste'),
    path('nouvelle/', views.nouvelle_commande, name='nouvelle'),
    path('<int:pk>/', views.detail_commande, name='detail'),
    path('<int:pk>/recevoir/', views.recevoir_commande, name='recevoir'),
]
