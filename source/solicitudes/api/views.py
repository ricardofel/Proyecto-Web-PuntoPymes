from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from solicitudes.models import SolicitudAusencia, RegistroVacaciones
from .serializers import (
    TipoAusenciaSerializer,
    SolicitudAusenciaSerializer,
    RegistroVacacionesSerializer
)


class TipoAusenciaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet de solo lectura para listar tipos de ausencia activos.
    """
    queryset = TipoAusencia.objects.filter(estado=True)
    serializer_class = TipoAusenciaSerializer
    permission_classes = [IsAuthenticated]


class SolicitudAusenciaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de solicitudes de ausencia.
    Incluye acciones de flujo (aprobar / rechazar) vía endpoints custom.
    """
    serializer_class = SolicitudAusenciaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Retorna solicitudes del empleado autenticado (si existe vínculo empleado)
        user = self.request.user
        if hasattr(user, 'empleado'):
            return SolicitudAusencia.objects.filter(empleado=user.empleado).order_by('-fecha_creacion')
        return SolicitudAusencia.objects.none()

    def perform_create(self, serializer):
        """
        Asigna automáticamente empleado y empresa del usuario autenticado.
        """
        if hasattr(self.request.user, 'empleado'):
            empleado = self.request.user.empleado
            serializer.save(empleado=empleado, empresa=empleado.empresa, estado='pendiente')

    @action(detail=True, methods=['post'], url_path='aprobar')
    def aprobar(self, request, pk=None):
        """
        Marca la solicitud como aprobada y registra historial (si el aprobador tiene empleado).
        """
        solicitud = self.get_object()
        comentario = request.data.get('comentario', 'Aprobado vía API')

        solicitud.estado = SolicitudAusencia.Estado.APROBADO
        solicitud.save()

        if hasattr(request.user, 'empleado'):
            AprobacionAusencia.objects.create(
                solicitud=solicitud,
                aprobador=request.user.empleado,
                accion='Aprobado',
                comentario=comentario
            )

        return Response({'status': 'Solicitud Aprobada'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='rechazar')
    def rechazar(self, request, pk=None):
        """
        Marca la solicitud como rechazada y registra historial (si el aprobador tiene empleado).
        """
        solicitud = self.get_object()
        comentario = request.data.get('comentario', 'Rechazado vía API')

        solicitud.estado = SolicitudAusencia.Estado.RECHAZADO
        solicitud.save()

        if hasattr(request.user, 'empleado'):
            AprobacionAusencia.objects.create(
                solicitud=solicitud,
                aprobador=request.user.empleado,
                accion='Rechazado',
                comentario=comentario
            )

        return Response({'status': 'Solicitud Rechazada'}, status=status.HTTP_200_OK)


class RegistroVacacionesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet de solo lectura para consultar saldo de vacaciones del empleado autenticado.
    """
    serializer_class = RegistroVacacionesSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if hasattr(self.request.user, 'empleado'):
            return RegistroVacaciones.objects.filter(empleado=self.request.user.empleado)
        return RegistroVacaciones.objects.none()
