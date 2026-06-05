from django.urls import path
from . import views
app_name = 'notifications'
urlpatterns = [
    path('', views.liste_notifications, name='liste'),
    path('<int:pk>/lue/', views.marquer_lue, name='lue'),
    path('tout-lire/', views.tout_marquer_lues, name='tout_lire'),
]
