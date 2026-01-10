from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.apps import apps

@login_required
def dashboard_view(request):
    """
    Vista ultra-limpia: Solo notificaciones y el rol real de la BD.
    """
    Notificacion = apps.get_model('notificaciones', 'Notificacion')
    
    # 1. Notificaciones
    ultimas_notif = Notificacion.objects.filter(usuario=request.user).order_by('-fecha_creacion')[:5]

    # 2. Roles reales de la base de datos (relación UsuarioRol)
    mis_roles = [ur.rol.nombre for ur in request.user.usuariorol_set.all()]

    # Nombre para mostrar (Empleado o Email)
    try:
        nombre_display = f"{request.user.empleado.nombres} {request.user.empleado.apellidos}"
    except AttributeError:
        nombre_display = request.user.email

    context = {
        'notificaciones_recientes': ultimas_notif,
        'mis_roles': mis_roles,
        'nombre_display': nombre_display,
    }
    return render(request, "core/dashboard.html", context)