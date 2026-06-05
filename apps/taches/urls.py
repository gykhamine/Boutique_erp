from django.urls import path
from . import views
app_name = 'taches'
urlpatterns = [
    path('', views.kanban, name='kanban'),
    path('ajouter/', views.ajouter_tache, name='ajouter'),
    path('<int:pk>/statut/', views.changer_statut, name='statut'),
]
