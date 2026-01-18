from rest_framework import serializers
from integraciones.models import IntegracionErp, Webhook, LogIntegracion


class IntegracionErpSerializer(serializers.ModelSerializer):
    """
    Serializador para la gestión de configuraciones ERP.

    - La api_key se define como write_only para evitar exposición
      de credenciales sensibles en respuestas de lectura.
    """

    class Meta:
        model = IntegracionErp
        fields = "__all__"
        extra_kwargs = {
            "api_key": {"write_only": True},
        }


class WebhookSerializer(serializers.ModelSerializer):
    """
    Serializador para la configuración de webhooks salientes.

    - La secret_key es write_only para evitar que sea visible
      en respuestas de la API.
    """

    class Meta:
        model = Webhook
        fields = "__all__"
        extra_kwargs = {
            "secret_key": {"write_only": True},
        }


class LogIntegracionSerializer(serializers.ModelSerializer):
    """
    Serializador de solo lectura para auditoría técnica de integraciones.

    Incluye nombres legibles de:
    - Integración ERP asociada
    - Webhook asociado
    """

    integracion_nombre = serializers.CharField(
        source="integracion.nombre", read_only=True
    )
    webhook_nombre = serializers.CharField(
        source="webhook.nombre", read_only=True
    )

    class Meta:
        model = LogIntegracion
        fields = "__all__"
