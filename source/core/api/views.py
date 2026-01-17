from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser

# Importaciones absolutas
from core.models import Empresa, UnidadOrganizacional
from .serializers import EmpresaSerializer, UnidadOrganizacionalSerializer

class EmpresaViewSet(viewsets.ModelViewSet):
    """
    Gestión maestra de empresas.
    Restringido a administradores del sistema.
    """
    queryset = Empresa.objects.all().order_by('nombre_comercial')
    serializer_class = EmpresaSerializer
    permission_classes = [IsAdminUser]

class UnidadOrganizacionalViewSet(viewsets.ModelViewSet):
    """
    Gestión del organigrama (Áreas, Departamentos).
    """
    queryset = UnidadOrganizacional.objects.select_related('empresa', 'padre').all().order_by('nombre')
    serializer_class = UnidadOrganizacionalSerializer
    permission_classes = [IsAuthenticated]