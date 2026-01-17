from rest_framework import viewsets
from .models import EventoAsistencia  # <--- Nombre correcto
from .serializers import EventoAsistenciaSerializer

class EventoAsistenciaViewSet(viewsets.ModelViewSet):
    """
    API para registrar marcaciones (Check-in / Check-out).
    """
    # Ordenamos por fecha de registro descendente (lo más nuevo primero)
    queryset = EventoAsistencia.objects.all().order_by('-registrado_el')
    serializer_class = EventoAsistenciaSerializer