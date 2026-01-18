from rest_framework import serializers
from solicitudes.models import TipoAusencia, SolicitudAusencia, AprobacionAusencia, RegistroVacaciones


class TipoAusenciaSerializer(serializers.ModelSerializer):
    """
    Serializa el catálogo de tipos de ausencia (por empresa).
    """
    class Meta:
        model = TipoAusencia
        fields = '__all__'


class SolicitudAusenciaSerializer(serializers.ModelSerializer):
    """
    Serializa solicitudes de ausencia.
    Incluye campos derivados (solo lectura) útiles para listados.
    """
    empleado_nombre = serializers.CharField(source='empleado.nombre_completo', read_only=True)
    ausencia_nombre = serializers.CharField(source='ausencia.nombre', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)

    class Meta:
        model = SolicitudAusencia
        fields = '__all__'

        # Se asignan desde el backend (seguridad / consistencia)
        read_only_fields = ['empleado', 'empresa', 'estado']


class AprobacionAusenciaSerializer(serializers.ModelSerializer):
    """
    Serializa el historial de acciones (aprobar / rechazar / devolver).
    """
    aprobador_nombre = serializers.CharField(source='aprobador.nombre_completo', read_only=True)

    class Meta:
        model = AprobacionAusencia
        fields = '__all__'


class RegistroVacacionesSerializer(serializers.ModelSerializer):
    """
    Serializa el saldo de vacaciones por empleado y periodo.
    """
    dias_disponibles = serializers.ReadOnlyField()  # Propiedad calculada del modelo

    class Meta:
        model = RegistroVacaciones
        fields = '__all__'
