from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from notificaciones.models import Notificacion
from .serializers import NotificacionSerializer

class NotificacionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificacionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notificacion.objects.filter(
            usuario=self.request.user
        ).order_by('-fecha_creacion')

    # marca una notificación específica como leída
    @action(detail=True, methods=['post'], url_path='marcar-leida')
    def marcar_leida(self, request, pk=None):
        notificacion = self.get_object()
        
        if not notificacion.leido:
            notificacion.leido = True
            notificacion.save()
            return Response({'status': 'leido'}, status=status.HTTP_200_OK)
        
        return Response({'status': 'ya estaba leida'}, status=status.HTTP_200_OK)

    # marca todas las notificaciones como leídas
    @action(detail=False, methods=['post'], url_path='marcar-todas-leidas')
    def marcar_todas_leidas(self, request):
        self.get_queryset().filter(leido=False).update(leido=True)
        return Response({'status': 'todas leidas'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='badge-count')
    def badge_count(self, request):
        cantidad = self.get_queryset().filter(leido=False).count()
        return Response({'no_leidas': cantidad}, status=status.HTTP_200_OK)