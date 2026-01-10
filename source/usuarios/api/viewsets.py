from rest_framework import viewsets, filters
from usuarios.models import Usuario, Rol
from .serializers import UsuarioSerializer, RolSerializer

class UsuarioViewSet(viewsets.ModelViewSet):
    """
    API para gestionar Usuarios.
    Permite buscar por email.
    """
    queryset = Usuario.objects.all().order_by('-id')
    serializer_class = UsuarioSerializer
    
    # Búsqueda simple
    filter_backends = [filters.SearchFilter]
    search_fields = ['email']

class RolViewSet(viewsets.ModelViewSet):
    """
    API para gestionar Roles.
    """
    queryset = Rol.objects.all().order_by('nombre')
    serializer_class = RolSerializer
    
    filter_backends = [filters.SearchFilter]
    search_fields = ['nombre']