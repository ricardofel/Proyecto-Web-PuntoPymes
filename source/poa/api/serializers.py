from rest_framework import serializers
from poa.models import Objetivo, MetaTactico, Actividad


class ActividadSerializer(serializers.ModelSerializer):
    """Serializer para actividades."""
    class Meta:
        model = Actividad
        fields = '__all__'


class MetaTacticoSerializer(serializers.ModelSerializer):
    """Serializer para metas tácticas."""
    class Meta:
        model = MetaTactico
        fields = '__all__'


class ObjetivoSerializer(serializers.ModelSerializer):
    """Serializer para objetivos estratégicos."""
    avance_calculado = serializers.ReadOnlyField(source='avance')
    empresa_nombre = serializers.CharField(source='empresa.nombre_comercial', read_only=True)

    class Meta:
        model = Objetivo
        fields = '__all__'
