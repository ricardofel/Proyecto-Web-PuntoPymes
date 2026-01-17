from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.contrib.auth import get_user_model

from usuarios.models import Rol
from .serializers import UsuarioSerializer, RolSerializer, CambioPasswordSerializer

User = get_user_model()

class RolViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Listado de roles disponibles.
    """
    queryset = Rol.objects.filter(estado=True)
    serializer_class = RolSerializer
    permission_classes = [IsAuthenticated]

class UsuarioViewSet(viewsets.ModelViewSet):
    """
    Gestión de usuarios del sistema.
    """
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filtra usuarios visibles según la empresa del usuario logueado.
        """
        user = self.request.user
        # Usamos el método 'visibles_para' de tu Manager personalizado
        return User.objects.visibles_para(user)

    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        """
        Devuelve el perfil del usuario logueado actualmente.
        Endpoint: /api/usuarios/me/
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='cambiar-password')
    def cambiar_password(self, request):
        """
        Permite al usuario cambiar su propia contraseña.
        """
        serializer = CambioPasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.data.get('password_actual')):
                return Response({'error': 'Contraseña actual incorrecta'}, status=status.HTTP_400_BAD_REQUEST)
            
            user.set_password(serializer.data.get('password_nuevo'))
            user.save()
            return Response({'status': 'Contraseña actualizada correctamente'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)