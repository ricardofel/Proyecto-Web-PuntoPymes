from rest_framework import viewsets, filters

from kpi.models import KPI, KPIResultado
from .serializers import KPISerializer, KPIResultadoSerializer


class KPIViewSet(viewsets.ModelViewSet):
    """
    Endpoint para gestionar las definiciones de indicadores (KPI).
    """
    queryset = KPI.objects.all().order_by("-id")
    serializer_class = KPISerializer

    # Búsqueda por texto usando SearchFilter (incluido en DRF).
    filter_backends = [filters.SearchFilter]
    search_fields = ["nombre", "descripcion"]


class KPIResultadoViewSet(viewsets.ModelViewSet):
    """
    Endpoint para consultar los valores históricos de KPIs.
    """
    queryset = KPIResultado.objects.all().order_by("-periodo")
    serializer_class = KPIResultadoSerializer
