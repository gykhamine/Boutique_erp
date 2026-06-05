from django.urls import path
from . import views
app_name = 'employes'
urlpatterns = [
    path('', views.liste_employes, name='liste'),
    path('ajouter/', views.ajouter_employe, name='ajouter'),
    path('<int:pk>/', views.detail_employe, name='detail'),
    path('conge/', views.demander_conge, name='conge'),
]
