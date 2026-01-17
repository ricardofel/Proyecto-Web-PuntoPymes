from rest_framework import serializers
from integraciones.models import IntegracionErp, Webhook, LogIntegracion

class IntegracionErpSerializer(serializers.ModelSerializer):
    """
    serializador para la gestión de configuraciones erp.
    configura la api_key como campo de solo escritura para proteger credenciales.
    """
    class Meta:
        model = IntegracionErp
        fields = '__all__'
        extra_kwargs = {
            'api_key': {'write_only': True}
        }

class WebhookSerializer(serializers.ModelSerializer):
    """
    serializador para la configuración de webhooks salientes.
    protege la secret_key evitando su exposición en respuestas de lectura.
    """
    class Meta:
        model = Webhook
        fields = '__all__'
        extra_kwargs = {
            'secret_key': {'write_only': True}
        }

class LogIntegracionSerializer(serializers.ModelSerializer):
    """
    serializador de solo lectura para el historial técnico de conexiones.
    incluye los nombres de las integraciones relacionadas para facilitar el análisis.
    """
    integracion_nombre = serializers.CharField(source='integracion.nombre', read_only=True)
    webhook_nombre = serializers.CharField(source='webhook.nombre', read_only=True)

    class Meta:
        model = LogIntegracion
        fields = '__all__'