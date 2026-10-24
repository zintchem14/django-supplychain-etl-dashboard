from django.conf import settings
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.logistics.models import Commande, Entrepot, EtlRun, Expedition, Transporteur

from . import kpis
from . import serializers as sz
from .filters import CommandeFilter, ExpeditionFilter

# --- Ressources en lecture seule (étape B1) ---


class TransporteurViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Transporteur.objects.all()
    serializer_class = sz.TransporteurSerializer
    pagination_class = None


class EntrepotViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Entrepot.objects.all()
    serializer_class = sz.EntrepotSerializer
    pagination_class = None


class CommandeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Commande.objects.select_related("expedition__transporteur", "expedition__entrepot")
    filterset_class = CommandeFilter
    ordering_fields = ["date_commande", "montant_total", "order_id"]
    ordering = ["-date_commande", "-id"]

    def get_serializer_class(self):
        return sz.CommandeDetailSerializer if self.action == "retrieve" else sz.CommandeSerializer


class ExpeditionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Expedition.objects.select_related("commande", "transporteur", "entrepot")
    serializer_class = sz.ExpeditionSerializer
    filterset_class = ExpeditionFilter
    ordering_fields = ["ecart_jours", "cout_estime", "commande__date_commande"]
    ordering = ["-commande__date_commande", "-id"]


class EtlRunViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EtlRun.objects.all()
    serializer_class = sz.EtlRunSerializer


# --- Indicateurs (étape B2) ---

FILTER_PARAMS = [
    OpenApiParameter("date_min", OpenApiTypes.DATE),
    OpenApiParameter("date_max", OpenApiTypes.DATE),
    OpenApiParameter("region", str),
    OpenApiParameter("marche", str),
    OpenApiParameter("transporteur", str, description="code, ex. first-class"),
    OpenApiParameter("entrepot", str, description="code, ex. europe"),
]


class KpiSummaryView(APIView):
    @extend_schema(parameters=FILTER_PARAMS, responses=OpenApiTypes.OBJECT)
    def get(self, request):
        return Response(kpis.summary(kpis.base_queryset(request.query_params)))


class KpiTimeseriesView(APIView):
    @extend_schema(
        parameters=[*FILTER_PARAMS,
                    OpenApiParameter("granularity", str, description="day|week|month")],
        responses=OpenApiTypes.OBJECT,
    )
    def get(self, request):
        qs = kpis.base_queryset(request.query_params)
        return Response(kpis.timeseries(qs, request.query_params.get("granularity", "week")))


class KpiBottlenecksView(APIView):
    @extend_schema(
        parameters=[*FILTER_PARAMS,
                    OpenApiParameter("by", str,
                                     description="region|transporteur|region_transporteur"),
                    OpenApiParameter("limit", int),
                    OpenApiParameter("min_volume", int)],
        responses=OpenApiTypes.OBJECT,
    )
    def get(self, request):
        q = request.query_params
        qs = kpis.base_queryset(q)
        by = q.get("by", "region_transporteur")
        limit = min(int(q.get("limit", 10)), 100)
        min_volume = int(q.get("min_volume", settings.BOTTLENECK_MIN_VOLUME))
        return Response(kpis.bottlenecks(qs, by, min_volume, limit))