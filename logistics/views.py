from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Expedition
from rest_framework.decorators import api_view

#LES MODULES DE LA DEUXIEME VUE LE COUT MOYEN PAR EXPEDITION
from django.db.models import Avg
from .models import Expedition

#module pour la troisieme vue
from django.db.models import Count, Q, Sum, F

from .models import Commande



# Create your views here.

# creation vues 1 LE TAUX DE LIVRAISON A TEMP
class TauxLivraisonATempsView(APIView):
    def get(self, request):
        total_expeditions = Expedition.objects.count()
       
        if total_expeditions == 0:
            return Response({"taux_livraison_a_temps": 0, "message": "Aucune expédition en base."})
       
        # On compte les expéditions sans risque de retard ou livrées à temps
        # (Adaptez le filtre selon le champ exact de votre modèle Expedition, par exemple late_delivery_risk == 0)
        expeditions_a_temps = Expedition.objects.filter(late_delivery_risk=False).count()
       
        taux = (expeditions_a_temps / total_expeditions) * 100
       
        return Response({
            "total_expeditions": total_expeditions,
            "expeditions_a_temps": expeditions_a_temps,
            "taux_livraison_a_temps": round(taux, 2)
        })

#CREATION DE LA CREATION DE LA DEUXIEME CLASSE 

class CoutMoyenExpeditionView(APIView): # (ou CoutMoyenExpeditionView)
    def get(self, request):
        # On calcule la moyenne du champ représentant le coût ou le total de l'expédition
        # (Adaptez 'shipping_cost' ou 'order_item_total' selon le nom exact dans votre modèle)
        resultat = Expedition.objects.aggregate(cout_moyen=Avg('commande__sales'))
       
        cout_moyen = resultat['cout_moyen'] or 0
       
        return Response({
            "cout_moyen_expedition": round(cout_moyen, 2)
        })


# creation  de la troisieme vues
class PointsDeBlocageView(APIView):
    def get(self, request):
        # Exemple d'analyse groupée par région (ou par transporteur selon votre modèle)
        # On compte les expéditions totales et le nombre de retards par région
        blocages_par_region = (
            Expedition.objects.values('commande__order_region') 
            .annotate(
                total_expeditions=Count('commande'),
                total_retards=Count('commande', filter=Q(late_delivery_risk=True)) # Ou le filtre de retard
            )
            .order_by('-total_retards') # Du plus grand nombre de retards au plus faible
        )
       
        return Response({
            "points_de_blocage_region": list(blocages_par_region)
        })


# AJOUTONS D'AUTRES KPI QUI N'ont pas ete demander par l'exercice 
@api_view(['GET'])
def get_kpis_globaux(request):
    stats = Commande.objects.aggregate(
        total_expeditions=Count('order_id'),
        total_profit=Sum('benefit_per_order'),
        total_sales=Sum('sales'),
    )

    total_exp = stats['total_expeditions'] or 0
    total_profit = round(stats['total_profit'] or 0, 2)
    total_sales = stats['total_sales'] or 1.0
    profit_margin = round((total_profit / total_sales) * 100, 2)

    # Calcul du retard moyen via la relation Expedition
    late_orders = Commande.objects.filter(
        expedition__days_for_shipping_real__gt=F('expedition__days_for_shipment_scheduled')
    ).aggregate(
        avg_delay=Avg(F('expedition__days_for_shipping_real') - F('expedition__days_for_shipment_scheduled'))
    )
    avg_delay_days = round(late_orders['avg_delay'] or 0, 1)

    # Top 3 des marchés pour le classement
    top_markets_qs = Commande.objects.values('market').annotate(
        total=Count('order_id')
    ).order_by('-total')[:3]

    top_markets = [
        {"market": item['market'], "total": item['total']}
        for item in top_markets_qs
    ]

    return Response({
        "volume_total_expeditions": total_exp,
        "benefice_total": total_profit,
        "marge_beneficiaire_pct": profit_margin,
        "retard_moyen_jours": avg_delay_days,
        "top_marches": top_markets
    })