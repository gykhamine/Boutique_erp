from django.urls import path
from . import views

app_name = 'rapports'
urlpatterns = [
    # Existants
    path('', views.dashboard_rapports, name='dashboard'),
    path('graphique/ventes/', views.graphique_ventes, name='graphique_ventes'),
    path('graphique/categories/', views.graphique_categories, name='graphique_categories'),
    path('excel/', views.rapport_excel_complet, name='excel'),
    path('analyse/', views.rapport_pandas, name='analyse'),

    # Nouveaux — Ontologie NetworkX
    path('ontologie/', views.dashboard_ontologie, name='ontologie'),
    path('graphique/reseau/ventes/', views.graphique_reseau_ventes, name='reseau_ventes'),
    path('graphique/reseau/achats/', views.graphique_reseau_achats, name='reseau_achats'),
    path('graphique/reseau/coachat/', views.graphique_coachat, name='coachat'),
    path('graphique/centralite/', views.graphique_centralite, name='centralite'),
    path('graphique/flux/', views.graphique_flux_financiers, name='flux'),
    path('api/graphe.json', views.api_graphe_json, name='api_graphe'),
]
