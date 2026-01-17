from django.db import transaction
from notificaciones.models import Notificacion
from notificaciones.constants import TiposNotificacion

class NotificacionService:
    
    @staticmethod
    def crear_notificacion(usuario, titulo, mensaje, tipo=TiposNotificacion.INFO, url=None):
        """Crea una notificación para un usuario."""
        if not usuario:
            return None
            
        return Notificacion.objects.create(
            usuario=usuario,
            titulo=titulo,
            mensaje=mensaje,
            tipo=tipo,
            url_destino=url
        )

    @staticmethod
    def marcar_como_leidas(usuario):
        """Marca todas las notificaciones del usuario como leídas."""
        # UPDATE masivo eficiente (1 sola consulta)
        Notificacion.objects.filter(usuario=usuario, leido=False).update(leido=True)

    @staticmethod
    def obtener_resumen_navbar(usuario):
        """
        Retorna solo lo necesario para el navbar:
        - Número de no leídas (int)
        - Las últimas 5 para el dropdown
        """
        if not usuario.is_authenticated:
            return {'num_no_leidas': 0, 'ultimas': []}
            
        qs = Notificacion.objects.filter(usuario=usuario, leido=False)
        
        return {
            'num_no_leidas': qs.count(), # SELECT COUNT(*) es mucho más rápido que traer objetos
            'ultimas': qs.order_by('-fecha_creacion')[:5] # Solo traemos 5
        }