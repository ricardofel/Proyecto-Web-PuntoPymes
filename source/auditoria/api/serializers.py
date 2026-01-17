from rest_framework import serializers
from auditoria.models import LogAuditoria


class LogAuditoriaSerializer(serializers.ModelSerializer):
    """
    Serializa los registros de auditoría a formato JSON.
    Expone campos derivados para mejorar la legibilidad del historial.
    """

    # Muestra el email del usuario en lugar del ID interno
    # Si no existe usuario, se interpreta como acción del sistema
    usuario_identificador = serializers.CharField(
        source="usuario.email",
        default="Sistema/Anónimo",
        read_only=True
    )

    # Expone la representación legible de la acción (choices)
    accion_display = serializers.CharField(
        source="get_accion_display",
        read_only=True
    )

    class Meta:
        model = LogAuditoria
        fields = "__all__"
