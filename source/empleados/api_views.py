from rest_framework import viewsets
from .models import Empleado
from .serializers import EmpleadoSerializer

class EmpleadoViewSet(viewsets.ModelViewSet):
    """
    API endpoint para ver o editar empleados.
    """
    queryset = Empleado.objects.all().order_by('id')
    serializer_class = EmpleadoSerializer
    
    # filtrar solo activos por defecto:
    # queryset = Empleado.objects.filter(estado='Activo').order_by('id')