from rest_framework import serializers
from usuarios.models import Usuario, Rol

class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = '__all__'


class UsuarioSerializer(serializers.ModelSerializer):
    # Roles detallados para lectura
    roles = RolSerializer(source='roles_asignados', many=True, read_only=True)

    # Asignación de roles vía IDs en escritura
    rol_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=Rol.objects.all(),
        source='roles_asignados',
        required=False
    )

    # Password solo escritura (no se expone en responses)
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Usuario
        fields = [
            'id', 'email', 'password', 'estado', 'is_staff',
            'empleado', 'roles', 'rol_ids', 'ultimo_login'
        ]
        read_only_fields = ['ultimo_login']

    def create(self, validated_data):
        # Maneja password y roles manualmente para aplicar hash y asignación M2M
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
            # Aplica hash a la nueva contraseña
            user.set_password(password)
            user.save()

        if roles is not None:
            user.roles_asignados.set(roles)

        return user
