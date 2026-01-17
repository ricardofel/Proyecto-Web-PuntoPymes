from rest_framework import serializers
from solicitudes.models import TipoAusencia, SolicitudAusencia, AprobacionAusencia, RegistroVacaciones

class TipoAusenciaSerializer(serializers.ModelSerializer):
    """
    Catálogo de tipos de permisos (Vacaciones, Enfermedad, Calamidad, etc.)
    """
    class Meta:
        model = TipoAusencia
        fields = '__all__'

class SolicitudAusenciaSerializer(serializers.ModelSerializer):
    """
    Serializador principal para pedir permisos.
    Incluye campos de lectura para facilitar la visualización en tablas.
    """
    empleado_nombre = serializers.CharField(source='empleado.nombre_completo', read_only=True)
    ausencia_nombre = serializers.CharField(source='ausencia.nombre', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)

    class Meta:
        model = SolicitudAusencia
        fields = '__all__'
        # El empleado y empresa se asignan automáticamente en el backend, no se piden en el JSON
        read_only_fields = ['empleado', 'empresa', 'estado']

class AprobacionAusenciaSerializer(serializers.ModelSerializer):
    """
    Historial de quién aprobó o rechazó.
    """
    aprobador_nombre = serializers.CharField(source='aprobador.nombre_completo', read_only=True)
    
    class Meta:
        model = AprobacionAusencia
        fields = '__all__'

class RegistroVacacionesSerializer(serializers.ModelSerializer):
    """
    Saldo de vacaciones del empleado.
    """
    dias_disponibles = serializers.ReadOnlyField() # Propiedad calculada del modelo

    class Meta:
        model = RegistroVacaciones
        fields = '__all__'