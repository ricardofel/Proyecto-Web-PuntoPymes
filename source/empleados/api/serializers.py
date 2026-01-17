from rest_framework import serializers
from ..models import Empleado

class EmpleadoSerializer(serializers.ModelSerializer):
    """
    transforma los objetos del modelo empleado a formato json para la api.
    permite definir qué datos se exponen y cómo se presentan al cliente.
    """

    # campos personalizados para mostrar nombres legibles en lugar de ids numéricos.
    # usamos 'source' para acceder a los atributos del modelo relacionado.
    empresa_nombre = serializers.CharField(source='empresa.nombre_comercial', read_only=True)
    puesto_nombre = serializers.CharField(source='puesto.nombre', read_only=True)

    class Meta:
        # vinculación con el modelo de base de datos
        model = Empleado
        
        # define qué campos se incluirán en la respuesta json.
        # '__all__' expone toda la estructura del modelo automáticamente.
        fields = '__all__'