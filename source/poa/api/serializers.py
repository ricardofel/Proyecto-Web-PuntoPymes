from rest_framework import serializers
from poa.models import Objetivo, MetaTactico, Actividad

class ActividadSerializer(serializers.ModelSerializer):
    """
    Serializador para las actividades operativas (tareas diarias).
    """
    class Meta:
        model = Actividad
        fields = '__all__'

class MetaTacticoSerializer(serializers.ModelSerializer):
    """
    Serializador para las metas tácticas.
    Incluye las actividades relacionadas para tener una vista anidada si se requiere.
    """
    # Opcional: Si quieres ver las actividades dentro de la meta, descomenta:
    # actividades = ActividadSerializer(many=True, read_only=True)
    
    class Meta:
        model = MetaTactico
        fields = '__all__'

class ObjetivoSerializer(serializers.ModelSerializer):
    """
    Serializador para los Objetivos Estratégicos.
    Expone el campo calculado 'avance' que viene de la propiedad @property del modelo.
    """
    avance_calculado = serializers.ReadOnlyField(source='avance')
    empresa_nombre = serializers.CharField(source='empresa.nombre_comercial', read_only=True)

    class Meta:
        model = Objetivo
        fields = '__all__'