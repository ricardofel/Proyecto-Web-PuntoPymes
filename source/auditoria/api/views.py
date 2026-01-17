from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from auditoria.models import LogAuditoria
from .serializers import LogAuditoriaSerializer


class LogAuditoriaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Endpoint de solo lectura para consultar el historial de auditoría.

    Se utiliza ReadOnlyModelViewSet para impedir modificaciones o eliminaciones
    vía API y garantizar la inmutabilidad de los registros.
    """
    queryset = (
        LogAuditoria.objects
        .select_related("usuario")
        .all()
        .order_by("-fecha")
    )
    serializer_class = LogAuditoriaSerializer

    # Acceso restringido a usuarios administradores
    permission_classes = [IsAdminUser]
