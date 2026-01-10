from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.apps import apps

@login_required
def dashboard_view(request):
    """
    Vista optimizada: Notificaciones y Perfil de Usuario con diseño Zen.
    """
    Notificacion = apps.get_model('notificaciones', 'Notificacion')
    
    # Solo traemos las últimas 5 notificaciones
    ultimas_notif = Notificacion.objects.filter(usuario=request.user).order_by('-fecha_creacion')[:5]
    
    context = {
        'notificaciones_recientes': ultimas_notif,
    }
    return render(request, "core/dashboard.html", context)