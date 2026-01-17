from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from notificaciones.models import Notificacion
from .serializers import NotificacionSerializer

class NotificacionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API para listar y gestionar notificaciones del usuario actual.
    Solo permite lectura (GET) y acciones personalizadas (PATCH).
    """
    serializer_class = NotificacionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Retorna solo las notificaciones pertenecientes al usuario logueado.
        Ordenadas de la más reciente a la más antigua.
        """
        return Notificacion.objects.filter(
            usuario=self.request.user
        ).order_by('-fecha_creacion')

    @action(detail=True, methods=['post'], url_path='marcar-leida')
    def marcar_leida(self, request, pk=None):
        """
        Endpoint para marcar una notificación específica como leída.
        Uso: POST /api/notificaciones/{id}/marcar-leida/
        """
        notificacion = self.get_object()
        
        if not notificacion.leido:
            notificacion.leido = True
            notificacion.save()
            return Response({'status': 'leido'}, status=status.HTTP_200_OK)
        
        return Response({'status': 'ya estaba leida'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='marcar-todas-leidas')
    def marcar_todas_leidas(self, request):
        """
        Marca todas las notificaciones pendientes del usuario como leídas.
        Ideal para el botón 'Marcar todo como leído'.
        """
        self.get_queryset().filter(leido=False).update(leido=True)
        return Response({'status': 'todas leidas'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='badge-count')
    def badge_count(self, request):
        """
        Retorna solo el número de notificaciones sin leer.
        Ideal para actualizar el contador de la campana en el header.
        """
        cantidad = self.get_queryset().filter(leido=False).count()
        return Response({'no_leidas': cantidad}, status=status.HTTP_200_OK)