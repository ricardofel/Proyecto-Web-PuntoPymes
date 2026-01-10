from rest_framework import viewsets, filters
from poa.models import Objetivo, MetaTactico, Actividad
from .serializers import ObjetivoSerializer, MetaTacticoSerializer, ActividadSerializer

class ObjetivoViewSet(viewsets.ModelViewSet):
    """
    API para Objetivos Estratégicos.
    Incluye el cálculo automático de avance.
    """
    queryset = Objetivo.objects.all().order_by('-anio', 'id')
    serializer_class = ObjetivoSerializer
    
    # Buscador simple
    filter_backends = [filters.SearchFilter]
    search_fields = ['nombre', 'descripcion', 'anio']

class MetaTacticoViewSet(viewsets.ModelViewSet):
    """
    API para Metas Tácticas.
    """
    queryset = MetaTactico.objects.all().order_by('fecha_fin')
    serializer_class = MetaTacticoSerializer
    
    filter_backends = [filters.SearchFilter]
    search_fields = ['nombre', 'indicador']

class ActividadViewSet(viewsets.ModelViewSet):
    """
    API para Actividades Operativas.
    """
    queryset = Actividad.objects.all().order_by('fecha_fin')
    serializer_class = ActividadSerializer
    
    filter_backends = [filters.SearchFilter]
    search_fields = ['nombre']