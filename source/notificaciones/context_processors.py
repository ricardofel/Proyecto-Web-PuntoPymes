from notificaciones.models import Notificacion

def notificaciones_globales(request):
    """
    Inyecta el conteo de notificaciones no leídas en TODAS las plantillas.
    Variable disponible: {{ conteo_notificaciones }}
    """
    if request.user.is_authenticated:
        conteo = Notificacion.objects.filter(usuario=request.user, leido=False).count()
        # También podrias devolver las últimas 3 para un mini-dropdown
        ultimas = Notificacion.objects.filter(usuario=request.user).order_by('-fecha_creacion')[:5]
        return {
            'conteo_notificaciones': conteo,
            'ultimas_notificaciones': ultimas
        }
    return {
        'conteo_notificaciones': 0,
        'ultimas_notificaciones': []
    }