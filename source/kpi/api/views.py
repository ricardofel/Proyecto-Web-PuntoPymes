from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

# importaciones absolutas
from kpi.models import KPI, KPIResultado
from .serializers import KPISerializer, KPIResultadoSerializer

class KPIViewSet(viewsets.ModelViewSet):
    """
    api para configurar los indicadores (metas, fórmulas, nombres).
    """
    queryset = KPI.objects.all().order_by('nombre')
    serializer_class = KPISerializer
    permission_classes = [IsAdminUser]

class KPIResultadoViewSet(viewsets.ModelViewSet):
    """
    api para gestionar los valores medidos mes a mes.
    """
    # optimización: usamos select_related para traer datos del kpi en la misma consulta
    queryset = KPIResultado.objects.select_related('kpi').all().order_by('-periodo')
    serializer_class = KPIResultadoSerializer
    permission_classes = [IsAdminUser]