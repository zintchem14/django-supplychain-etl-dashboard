from django.urls import path
from logistics.views import (
    TauxLivraisonATempsView,
    CoutMoyenExpeditionView,
    PointsDeBlocageView,
    get_kpis_globaux,
    get_ventes_profits,
    get_vouses_globales_enrichies
)

urlpatterns = [
    path('api/taux-livraison/', TauxLivraisonATempsView.as_view(), name='taux-livraison'),
    path('api/cout-moyen/', CoutMoyenExpeditionView.as_view(), name='cout-moyen'),
    path('api/points-de-blocage/', PointsDeBlocageView.as_view(), name='points-de-blocage'),
    path('api/kpis-globaux/', get_kpis_globaux, name='kpis-globaux'),
    path('api/ventes-profits/', get_ventes_profits, name='ventes-profits'),
    path('api/vouses-globales-enrichies/', get_vouses_globales_enrichies, name='vouses-globales-enrichies'),
]