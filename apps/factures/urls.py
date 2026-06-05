from django.urls import path
from . import views
app_name = 'factures'
urlpatterns = [
    path('', views.liste_factures, name='liste'),
    path('creer/<int:vente_pk>/', views.creer_facture, name='creer'),
    path('<int:pk>/', views.detail_facture, name='detail'),
    path('<int:pk>/pdf/', views.telecharger_pdf, name='pdf'),
    path('<int:pk>/regenerer/', views.regenerer_pdf, name='regenerer'),
]
