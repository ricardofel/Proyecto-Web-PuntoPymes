from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from .models import IntegracionErp, Webhook, LogIntegracion
from .serializers import (
    IntegracionErpSerializer, 
    WebhookSerializer, 
    LogIntegracionSerializer
)

class IntegracionErpViewSet(viewsets.ModelViewSet):
    """
    api para gestionar conexiones con sistemas externos (erp, crm).
    """
    queryset = IntegracionErp.objects.all().order_by('nombre')
    serializer_class = IntegracionErpSerializer
    permission_classes = [IsAdminUser] # seguridad: solo admins tocan esto


class WebhookViewSet(viewsets.ModelViewSet):
    """
    api para configurar notificaciones push hacia otros sistemas.
    """
    queryset = Webhook.objects.all().order_by('nombre')
    serializer_class = WebhookSerializer
    permission_classes = [IsAdminUser]


class LogIntegracionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    historial técnico de peticiones http.
    solo lectura para garantizar la integridad de los logs.
    """
    queryset = LogIntegracion.objects.select_related('integracion', 'webhook').all().order_by('-fecha')
    serializer_class = LogIntegracionSerializer
    permission_classes = [IsAdminUser]