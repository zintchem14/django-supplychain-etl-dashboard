from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.api.permissions import IsAnalystOrReadOnly
from apps.api.serializers import AnomalyReportSerializer

from .models import AnomalyReport
from .services import GRANULARITES, actualiser_anomalies, expliquer_rapport


class AnomalyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AnomalyReport.objects.all()
    serializer_class = AnomalyReportSerializer
    permission_classes = [IsAnalystOrReadOnly]

    @extend_schema(parameters=[OpenApiParameter("granularity", str, enum=list(GRANULARITES))])
    def list(self, request, *args, **kwargs):
        granularite = request.query_params.get("granularity", "week")
        if granularite not in GRANULARITES:
            raise ValidationError({"granularity": f"Valeurs permises : {', '.join(GRANULARITES)}."})
        actualiser_anomalies(granularite)
        return super().list(request, *args, **kwargs)

    @extend_schema(request=None, responses=OpenApiTypes.OBJECT,
                   parameters=[OpenApiParameter("refresh", bool)])
    @action(detail=True, methods=["post"])
    def explain(self, request, pk=None):
        rapport = self.get_object()
        forcer = request.query_params.get("refresh") == "true"
        return Response(expliquer_rapport(rapport, forcer=forcer))