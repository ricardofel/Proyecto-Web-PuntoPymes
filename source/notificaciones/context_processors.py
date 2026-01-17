from notificaciones.services.notificacion_service import NotificacionService

# CAMBIO IMPORTANTE: El nombre debe ser 'notificaciones_globales'
# para que coincida con lo que espera tu settings.py
def notificaciones_globales(request):
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