from rest_framework import serializers
from django.contrib.auth import get_user_model
from usuarios.models import Rol, UsuarioRol

User = get_user_model()

class RolSerializer(serializers.ModelSerializer):
    """
    Catálogo de roles del sistema.
    """
    class Meta:
        model = Rol
        fields = '__all__'

class UsuarioSerializer(serializers.ModelSerializer):
    """
    Perfil de usuario con información de permisos y empleado asociado.
    """
    nombre_completo = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField()
    empresa_nombre = serializers.SerializerMethodField()
    
    # Propiedades de permisos para el frontend
    permisos = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'estado', 'foto_perfil', 'telefono', 
            'nombre_completo', 'roles', 'empresa_nombre', 'permisos',
            'ultimo_login'
        ]
        read_only_fields = ['email', 'ultimo_login']

    def get_nombre_completo(self, obj):
        if obj.empleado:
            return f"{obj.empleado.nombres} {obj.empleado.apellidos}"
        return "Usuario del Sistema"

    def get_roles(self, obj):
        return list(obj.roles_asignados.filter(estado=True).values_list('nombre', flat=True))

    def get_empresa_nombre(self, obj):
        if obj.empleado and obj.empleado.empresa:
            return obj.empleado.empresa.nombre_comercial
        return None

    def get_permisos(self, obj):
        return {
            'es_superadmin': obj.is_superuser or obj.es_superadmin_negocio,
            'es_rrhh': obj.es_admin_rrhh,
            'ver_usuarios': obj.puede_ver_modulo_usuarios
        }

class CambioPasswordSerializer(serializers.Serializer):
    """
    Serializador simple para cambio de contraseña.
    """
    password_actual = serializers.CharField(required=True)
    password_nuevo = serializers.CharField(required=True)