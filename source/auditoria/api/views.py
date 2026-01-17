from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from auditoria.models import LogAuditoria
from .serializers import LogAuditoriaSerializer

class LogAuditoriaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    endpoint de solo lectura para consultar el historial de cambios.
    se utiliza readonlymodelviewset para impedir modificaciones o eliminaciones
    vía api y asegurar la inmutabilidad de la auditoría.
    """
    queryset = LogAuditoria.objects.select_related('usuario').all().order_by('-fecha')
    serializer_class = LogAuditoriaSerializer
    
    # recomendación profesional: restringir el acceso solo a administradores
    permission_classes = [IsAdminUser]