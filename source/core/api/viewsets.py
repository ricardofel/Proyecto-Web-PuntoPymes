from rest_framework import viewsets, filters
# IMPORTANTE: No importamos 'django_filters' porque no está instalado.

from kpi.models import KPI, KPIResultado
from .serializers import KPISerializer, KPIResultadoSerializer

class KPIViewSet(viewsets.ModelViewSet):
    """
    Endpoint para gestionar las definiciones de indicadores.
    """
    queryset = KPI.objects.all().order_by('-id')
    serializer_class = KPISerializer
    
    # Usamos SearchFilter (Búsqueda por texto) que SÍ viene incluido en Django REST Framework
    filter_backends = [filters.SearchFilter]
    search_fields = ['nombre', 'descripcion']
    
    # Eliminamos 'filterset_fields' para evitar el error

class KPIResultadoViewSet(viewsets.ModelViewSet):
    """
    Endpoint para consultar los valores históricos.
    """
    queryset = KPIResultado.objects.all().order_by('-periodo')
    serializer_class = KPIResultadoSerializer