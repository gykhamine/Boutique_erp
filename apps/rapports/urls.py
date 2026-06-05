from django.urls import path
from . import views
app_name = 'rapports'
urlpatterns = [
    path('', views.dashboard_rapports, name='dashboard'),
    path('graphique/ventes/', views.graphique_ventes, name='graphique_ventes'),
    path('graphique/categories/', views.graphique_categories, name='graphique_categories'),
    path('excel/', views.rapport_excel_complet, name='excel'),
    path('analyse/', views.rapport_pandas, name='analyse'),
]
