from django.urls import path
from .views import TauxLivraisonATempsView, CoutMoyenExpeditionView, PointsDeBlocageView, get_kpis_globaux 

urlpatterns = [
    path('api/taux-livraison/', TauxLivraisonATempsView.as_view(), name='taux-livraison'),
    path('api/cout-moyen/', CoutMoyenExpeditionView.as_view(), name='cout-moyen'),
    path('api/points-de-blocage/', PointsDeBlocageView.as_view(), name='points-de-blocage'),
    path('api/kpis-globaux/', get_kpis_globaux, name='kpis-globaux'),
]