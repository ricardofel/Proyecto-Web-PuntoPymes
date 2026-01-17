from rest_framework import viewsets, filters
from usuarios.models import Usuario, Rol
from .serializers import UsuarioSerializer, RolSerializer


class UsuarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet REST para la gestión de usuarios.
    Incluye búsqueda simple por correo electrónico.
    """
    queryset = Usuario.objects.all().order_by('-id')
    serializer_class = UsuarioSerializer

    # Filtro de búsqueda por campos definidos
    filter_backends = [filters.SearchFilter]
    search_fields = ['email']


class RolViewSet(viewsets.ModelViewSet):
    """
    ViewSet REST para la gestión de roles.
    """
    queryset = Rol.objects.all().order_by('nombre')
    serializer_class = RolSerializer

    # Filtro de búsqueda por nombre del rol
    filter_backends = [filters.SearchFilter]
    search_fields = ['nombre']
