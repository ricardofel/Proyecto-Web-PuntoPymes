from rest_framework import serializers
from usuarios.models import Usuario, Rol
# Intentamos importar Empleado para mostrar info extra, si no existe no falla crítico
try:
    from empleados.models import Empleado
except ImportError:
    Empleado = None

class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = '__all__'

class UsuarioSerializer(serializers.ModelSerializer):
    # Mostramos los roles completos al leer
    roles = RolSerializer(source='roles_asignados', many=True, read_only=True)
    
    # Permitimos asignar roles enviando una lista de IDs (Ej: [1, 2])
    rol_ids = serializers.PrimaryKeyRelatedField(
        many=True, write_only=True, queryset=Rol.objects.all(), source='roles_asignados', required=False
    )
    
    # La contraseña solo se escribe, nunca se lee (seguridad)
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Usuario
        fields = [
            'id', 'email', 'password', 'estado', 'is_staff', 
            'empleado', 'roles', 'rol_ids', 'ultimo_login'
        ]
        read_only_fields = ['ultimo_login']

    def create(self, validated_data):
        # Extraemos password y roles para manejarlos aparte
        password = validated_data.pop('password', None)
        roles = validated_data.pop('roles_asignados', [])
        
        user = super().create(validated_data)
        
        if password:
            user.set_password(password)
            user.save()
            
        if roles:
            user.roles_asignados.set(roles)
            
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        roles = validated_data.pop('roles_asignados', None)
        
        user = super().update(instance, validated_data)
        
        if password:
            user.set_password(password) # Hasheamos la nueva password
            user.save()
            
        if roles is not None:
            user.roles_asignados.set(roles)
            
        return user