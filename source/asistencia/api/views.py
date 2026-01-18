from rest_framework import viewsets
from asistencia.models import EventoAsistencia  
from .serializers import EventoAsistenciaSerializer

class EventoAsistenciaViewSet(viewsets.ModelViewSet):
    queryset = EventoAsistencia.objects.all().order_by('-registrado_el')
    serializer_class = EventoAsistenciaSerializer