from notificaciones.services.notificacion_service import NotificacionService

def notificaciones_context(request):
    """
    Inyecta las notificaciones en TODAS las plantillas.
    Optimizado para ser ligero.
    """
    if not request.user.is_authenticated:
        return {}
        
    # Delegamos al servicio la lógica de obtención eficiente
    data = NotificacionService.obtener_resumen_navbar(request.user)
    
    return {
        'notificaciones_no_leidas': data['num_no_leidas'],
        'notificaciones_recientes': data['ultimas']
    }