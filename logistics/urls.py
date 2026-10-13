from django.urls import path
from .views import TauxLivraisonATempsView, CoutMoyenExpeditionView, PointsDeBlocageView

urlpatterns = [
    path('api/taux-livraison/', TauxLivraisonATempsView.as_view(), name='taux-livraison'),
    path('api/cout-moyen/', CoutMoyenExpeditionView.as_view(), name='cout-moyen'),
    path('api/points-de-blocage/', PointsDeBlocageView.as_view(), name='points-de-blocage'),
]