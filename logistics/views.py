from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Expedition

#LES MODULES DE LA DEUXIEME VUE LE COUT MOYEN PAR EXPEDITION
from django.db.models import Avg
from .models import Expedition

#module pour la troisieme vue
from django.db.models import Count, Q



# Create your views here.

# creation vues 1 LE TAUX DE LIVRAISON A TEMP
class TauxLivraisonATempsView(APIView):
    def get(self, request):
        total_expeditions = Expedition.objects.count()
       
        if total_expeditions == 0:
            return Response({"taux_livraison_a_temps": 0, "message": "Aucune expédition en base."})
       
        # On compte les expéditions sans risque de retard ou livrées à temps
        # (Adaptez le filtre selon le champ exact de votre modèle Expedition, par exemple late_delivery_risk == 0)
        expeditions_a_temps = Expedition.objects.filter(late_delivery_risk=0).count()
       
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
                total_retards=Count('commande', filter=Q(late_delivery_risk=1)) # Ou le filtre de retard
            )
            .order_by('-total_retards') # Du plus grand nombre de retards au plus faible
        )
       
        return Response({
            "points_de_blocage_region": list(blocages_par_region)
        })

