from .models import Notificacion

def notificaciones_globales(request):
    """
    Inyecta 'notif_count' y 'notif_list' en TODAS las plantillas del sitio.
    """
    # Solo procesamos si hay usuario logueado para evitar errores
    if request.user.is_authenticated:
        try:
            # 1. Globito rojo (No leídas)
            conteo = Notificacion.objects.filter(usuario=request.user, leido=False).count()
            
            # 2. Lista del menú (Últimas 5)
            ultimas = Notificacion.objects.filter(usuario=request.user).order_by('-fecha_creacion')[:5]
            
            return {
                'notif_count': conteo,
                'notif_list': ultimas
            }
        except Exception:
            # Si falla la BD (ej: migración pendiente), no rompemos todo el sitio
            return {}
            
    return {}