from django.db import transaction
from notificaciones.models import Notificacion
from notificaciones.constants import TiposNotificacion

class NotificacionService:
    
    @staticmethod
    def crear_notificacion(usuario, titulo, mensaje, tipo=TiposNotificacion.INFO, url=None):
        # creación de una nueva notificación
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
        # actualización masiva de estado a leído
        Notificacion.objects.filter(usuario=usuario, leido=False).update(leido=True)

    @staticmethod
    def obtener_resumen_navbar(usuario):
        # resumen de notificaciones para la barra de navegación
        if not usuario.is_authenticated:
            return {'num_no_leidas': 0, 'ultimas': []}
            
        qs = Notificacion.objects.filter(usuario=usuario, leido=False)
        
        return {
            'num_no_leidas': qs.count(),
            'ultimas': qs.order_by('-fecha_creacion')[:5]
        }