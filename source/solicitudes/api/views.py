from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

# Modelos
from solicitudes.models import TipoAusencia, SolicitudAusencia, AprobacionAusencia, RegistroVacaciones
# Serializadores
from .serializers import (
    TipoAusenciaSerializer, 
    SolicitudAusenciaSerializer, 
    RegistroVacacionesSerializer
)

class TipoAusenciaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Lista los tipos de ausencia disponibles para que el empleado elija en el combo.
    """
    queryset = TipoAusencia.objects.filter(estado=True)
    serializer_class = TipoAusenciaSerializer
    permission_classes = [IsAuthenticated]

class SolicitudAusenciaViewSet(viewsets.ModelViewSet):
    """
    Gestión de solicitudes. 
    - Empleados: Ven y crean sus propias solicitudes.
    - Admins/Jefes: Pueden aprobar o rechazar (vía acciones).
    """
    serializer_class = SolicitudAusenciaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Si es superusuario ve todo, si no, solo lo suyo
        # (Aquí podrías expandir lógica para que los jefes vean a sus subordinados)
        if hasattr(user, 'empleado'):
            return SolicitudAusencia.objects.filter(empleado=user.empleado).order_by('-fecha_creacion')
        return SolicitudAusencia.objects.none()

    def perform_create(self, serializer):
        """
        Asigna automáticamente el empleado logueado y su empresa a la solicitud.
        """
        if hasattr(self.request.user, 'empleado'):
            empleado = self.request.user.empleado
            serializer.save(empleado=empleado, empresa=empleado.empresa, estado='pendiente')

    # --- ACCIONES DE FLUJO DE TRABAJO ---

    @action(detail=True, methods=['post'], url_path='aprobar')
    def aprobar(self, request, pk=None):
        solicitud = self.get_object()
        comentario = request.data.get('comentario', 'Aprobado vía API')
        
        # 1. Actualizar estado
        solicitud.estado = SolicitudAusencia.Estado.APROBADO
        solicitud.save()

        # 2. Registrar historial (Si el usuario que aprueba tiene perfil de empleado)
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
    Permite al empleado consultar su saldo de vacaciones.
    """
    serializer_class = RegistroVacacionesSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if hasattr(self.request.user, 'empleado'):
            return RegistroVacaciones.objects.filter(empleado=self.request.user.empleado)
        return RegistroVacaciones.objects.none()