from rest_framework import serializers
from core.models import Empresa, UnidadOrganizacional

class EmpresaSerializer(serializers.ModelSerializer):
    """
    Serializador para la gestión de empresas (multitenancy).
    """
    class Meta:
        model = Empresa
        fields = '__all__'

class UnidadOrganizacionalSerializer(serializers.ModelSerializer):
    """
    Serializador para departamentos, sucursales y áreas.
    Incluye campos de lectura para identificar la jerarquía visualmente.
    """
    padre_nombre = serializers.CharField(source='padre.nombre', read_only=True)
    empresa_nombre = serializers.CharField(source='empresa.nombre_comercial', read_only=True)

    class Meta:
        model = UnidadOrganizacional
        fields = '__all__'