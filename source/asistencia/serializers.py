from rest_framework import serializers
from .models import EventoAsistencia  # <--- Nombre correcto del modelo

class EventoAsistenciaSerializer(serializers.ModelSerializer):
    # Datos extra para que el JSON sea legible
    empleado_nombre = serializers.CharField(source='empleado.nombres', read_only=True)
    empleado_apellido = serializers.CharField(source='empleado.apellidos', read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)

    class Meta:
        model = EventoAsistencia
        fields = '__all__'