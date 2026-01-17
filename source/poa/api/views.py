from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from poa.models import Objetivo, MetaTactico, Actividad
from .serializers import ObjetivoSerializer, MetaTacticoSerializer, ActividadSerializer


class ObjetivoViewSet(viewsets.ModelViewSet):
    """CRUD de objetivos estratégicos."""
    queryset = Objetivo.objects.all().order_by('-anio', 'nombre')
    serializer_class = ObjetivoSerializer
    permission_classes = [IsAuthenticated]


class MetaTacticoViewSet(viewsets.ModelViewSet):
    """CRUD de metas tácticas asociadas a objetivos."""
    queryset = MetaTactico.objects.all().order_by('fecha_fin')
    serializer_class = MetaTacticoSerializer
    permission_classes = [IsAuthenticated]


class ActividadViewSet(viewsets.ModelViewSet):
    """CRUD de actividades operativas. Permite filtrar por meta vía querystring."""
    queryset = Actividad.objects.all().order_by('fecha_fin')
    serializer_class = ActividadSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filtro opcional por meta táctica (?meta=<id>)."""
        qs = super().get_queryset()
        meta_id = self.request.query_params.get('meta')
        if meta_id:
            qs = qs.filter(meta_id=meta_id)
        return qs
