from django.urls import path
from . import views
app_name = 'parametres'
urlpatterns = [
    path('', views.parametres, name='index'),
    path('utilisateur/', views.creer_utilisateur, name='creer_user'),
]
