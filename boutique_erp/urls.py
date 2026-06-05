from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('connexion/', auth_views.LoginView.as_view(template_name='base/connexion.html'), name='login'),
    path('deconnexion/', auth_views.LogoutView.as_view(), name='logout'),
    path('', include('apps.dashboard.urls')),
    path('produits/', include('apps.produits.urls')),
    path('ventes/', include('apps.ventes.urls')),
    path('achats/', include('apps.achats.urls')),
    path('clients/', include('apps.clients.urls')),
    path('fournisseurs/', include('apps.fournisseurs.urls')),
    path('stock/', include('apps.stock.urls')),
    path('caisse/', include('apps.caisse.urls')),
    path('factures/', include('apps.factures.urls')),
    path('rapports/', include('apps.rapports.urls')),
    path('employes/', include('apps.employes.urls')),
    path('taches/', include('apps.taches.urls')),
    path('notifications/', include('apps.notifications.urls')),
    path('parametres/', include('apps.parametres.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
