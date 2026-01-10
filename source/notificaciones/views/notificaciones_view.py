from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from notificaciones.models import Notificacion

@login_required
def listar_notificaciones(request):
    """Muestra el historial completo de notificaciones del usuario"""
    notificaciones = Notificacion.objects.filter(usuario=request.user)
    
    # Opcional: Marcar todo como leído al entrar a ver el historial
    # notificaciones.update(leido=True) 
    
    return render(request, 'notificaciones/lista.html', {
        'notificaciones': notificaciones
    })

@login_required
def marcar_todas_leidas(request):
    """Acción invisible que limpia el contador rojo"""
    Notificacion.objects.filter(usuario=request.user, leido=False).update(leido=True)
    # Regresa a la página donde estaba el usuario
    return redirect(request.META.get('HTTP_REFERER', '/'))