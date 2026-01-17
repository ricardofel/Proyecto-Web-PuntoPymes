from rest_framework import serializers
from .models import Empleado

class EmpleadoSerializer(serializers.ModelSerializer):
    # Opcional: Para mostrar el nombre de la empresa en lugar del ID
    empresa_nombre = serializers.CharField(source='empresa.nombre_comercial', read_only=True)
    puesto_nombre = serializers.CharField(source='puesto.nombre', read_only=True)

    class Meta:
        model = Empleado
        fields = '__all__' # Trae todos los campos
        # O especificar:
        # fields = ['id', 'nombres', 'apellidos', 'email', 'empresa_nombre', 'puesto_nombre', 'foto_url']