from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from notificaciones.services.notificacion_service import NotificacionService
from notificaciones.models import Notificacion

@login_required
def lista_notificaciones(request):
    """Muestra todas y las marca como leídas al entrar."""
    
    # 1. Obtenemos todas antes de marcar como leídas (para el historial)
    todas = Notificacion.objects.filter(usuario=request.user)
    
    # 2. Marcamos todo como leído usando el servicio
    NotificacionService.marcar_como_leidas(request.user)
    
    return render(request, "notificaciones/lista.html", {
        "notificaciones": todas
    })