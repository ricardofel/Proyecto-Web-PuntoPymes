from rest_framework import serializers
from .models import IntegracionErp, Webhook, LogIntegracion

class IntegracionErpSerializer(serializers.ModelSerializer):
    """
    serializador para configuraciones erp.
    protege la api_key para que no sea visible en respuestas de lectura.
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
    """
    class Meta:
        model = Webhook
        fields = '__all__'
        extra_kwargs = {
            'secret_key': {'write_only': True}
        }

class LogIntegracionSerializer(serializers.ModelSerializer):
    """
    serializador de solo lectura para auditoría técnica de conexiones.
    """
    # mostramos nombres en lugar de ids para facilitar el debug
    integracion_nombre = serializers.CharField(source='integracion.nombre', read_only=True)
    webhook_nombre = serializers.CharField(source='webhook.nombre', read_only=True)

    class Meta:
        model = LogIntegracion
        fields = '__all__'