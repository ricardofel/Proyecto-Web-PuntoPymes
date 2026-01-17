from rest_framework import viewsets
from empleados.models import Empleado
from .serializers import EmpleadoSerializer

class EmpleadoViewSet(viewsets.ModelViewSet):
    """
    Vista de API (ViewSet) para la gestión integral de Empleados.
    
    Heredar de ModelViewSet proporciona automáticamente la implementación 
    estándar para las operaciones CRUD:
    - GET /api/empleados/ (Listar)
    - POST /api/empleados/ (Crear)
    - GET /api/empleados/{id}/ (Recuperar detalle)
    - PUT/PATCH /api/empleados/{id}/ (Actualizar)
    - DELETE /api/empleados/{id}/ (Eliminar)
    """
    
    # define el conjunto de datos base (queryset) sobre el que actuará la vista.
    # se ordena por 'id' para garantizar consistencia en la paginación de resultados.
    queryset = Empleado.objects.all().order_by('id')
    
    # especifica la clase serializadora responsable de validar la entrada
    # y transformar los objetos del modelo a formato json (y viceversa).
    serializer_class = EmpleadoSerializer