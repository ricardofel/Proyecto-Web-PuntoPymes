from rest_framework import serializers
from auditoria.models import LogAuditoria

class LogAuditoriaSerializer(serializers.ModelSerializer):
    """
    transforma los registros de auditoria a formato json.
    agrega campos calculados para mejorar la legibilidad del log.
    """
    # mostramos el email o identificador del usuario en lugar del id numérico
    usuario_identificador = serializers.CharField(source='usuario.email', default='Sistema/Anónimo', read_only=True)
    
    # expone el texto legible de la acción (ej: 'Creación' en vez de 'C')
    accion_display = serializers.CharField(source='get_accion_display', read_only=True)

    class Meta:
        model = LogAuditoria
        fields = '__all__'